package episodic

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"math"
	"sync"
	"time"

	"cyberteam/memory"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/sirupsen/logrus"
)

// Store 情景记忆存储实现
type Store struct {
	pool      *pgxpool.Pool
	cache     *sync.Map
	logger    *logrus.Logger
	mu        sync.RWMutex
}

// NewStore 创建新的情景记忆存储
func NewStore(cfg memory.Config, logger *logrus.Logger) (*Store, error) {
	if cfg.VectorStoreURL == "" {
		// 无持久化，使用内存
		s := &Store{
			cache:  new(sync.Map),
			logger: logger,
		}
		return s, nil
	}

	poolConfig, err := pgxpool.ParseConfig(cfg.VectorStoreURL)
	if err != nil {
		return nil, fmt.Errorf("failed to parse config: %w", err)
	}

	pool, err := pgxpool.NewWithConfig(context.Background(), poolConfig)
	if err != nil {
		return nil, fmt.Errorf("failed to create pool: %w", err)
	}

	if err := pool.Ping(context.Background()); err != nil {
		logger.WithError(err).Warn("database ping failed, using in-memory store")
		pool = nil
	}

	s := &Store{
		pool:   pool,
		cache:  new(sync.Map),
		logger: logger,
	}

	if pool != nil {
		if err := s.initSchema(context.Background()); err != nil {
			return nil, fmt.Errorf("failed to initialize schema: %w", err)
		}
	}

	return s, nil
}

// initSchema 初始化数据库表
func (s *Store) initSchema(ctx context.Context) error {
	schema := `
	CREATE TABLE IF NOT EXISTS success_episodes (
		id TEXT PRIMARY KEY,
		task_type TEXT NOT NULL,
		input_pattern TEXT,
		solution TEXT NOT NULL,
		steps JSONB,
		outcome TEXT NOT NULL,
		duration BIGINT,
		agent_type TEXT,
		skills TEXT[],
		tags TEXT[],
		created_at TIMESTAMP DEFAULT NOW()
	);

	CREATE TABLE IF NOT EXISTS extracted_patterns (
		id TEXT PRIMARY KEY,
		pattern TEXT NOT NULL,
		frequency INT DEFAULT 1,
		success_rate FLOAT DEFAULT 0,
		agents TEXT[],
		skills TEXT[],
		created_at TIMESTAMP DEFAULT NOW()
	);

	CREATE INDEX IF NOT EXISTS idx_episodes_task_type ON success_episodes(task_type);
	CREATE INDEX IF NOT EXISTS idx_episodes_outcome ON success_episodes(outcome);
	CREATE INDEX IF NOT EXISTS idx_episodes_agent ON success_episodes(agent_type);
	CREATE INDEX IF NOT EXISTS idx_patterns_pattern ON extracted_patterns(pattern);
	`

	_, err := s.pool.Exec(ctx, schema)
	return err
}

// generateID 生成案例 ID
func generateID(taskType, solution string) string {
	hash := sha256.Sum256([]byte(taskType + solution + time.Now().Format(time.RFC3339Nano)))
	return "ep_" + hex.EncodeToString(hash[:])[:12]
}

// Record 记录成功案例
func (s *Store) Record(ctx context.Context, episode memory.SuccessEpisode) error {
	if episode.ID == "" {
		episode.ID = generateID(episode.TaskType, episode.Solution)
	}
	episode.CreatedAt = time.Now()

	// 序列化为 JSON
	stepsJSON, _ := json.Marshal(episode.Steps)
	skillsJSON, _ := json.Marshal(episode.Skills)
	tagsJSON, _ := json.Marshal(episode.Tags)

	// 存储到缓存
	s.cache.Store(episode.ID, episode)

	// 存储到数据库
	if s.pool != nil {
		query := `
			INSERT INTO success_episodes
				(id, task_type, input_pattern, solution, steps, outcome, duration, agent_type, skills, tags, created_at)
			VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
			ON CONFLICT (id) DO UPDATE SET
				task_type = EXCLUDED.task_type,
				input_pattern = EXCLUDED.input_pattern,
				solution = EXCLUDED.solution,
				steps = EXCLUDED.steps,
				outcome = EXCLUDED.outcome,
				duration = EXCLUDED.duration,
				agent_type = EXCLUDED.agent_type,
				skills = EXCLUDED.skills,
				tags = EXCLUDED.tags
		`

		_, err := s.pool.Exec(ctx, query,
			episode.ID, episode.TaskType, episode.InputPattern, episode.Solution,
			stepsJSON, episode.Outcome, episode.Duration.Milliseconds(),
			episode.AgentType, skillsJSON, tagsJSON, episode.CreatedAt,
		)
		if err != nil {
			s.logger.WithError(err).Warn("failed to store episode in database")
		}

		// 更新模式提取
		s.updatePatterns(ctx, episode)
	}

	s.logger.WithFields(logrus.Fields{
		"id":         episode.ID,
		"task_type":  episode.TaskType,
		"outcome":    episode.Outcome,
		"agent_type": episode.AgentType,
	}).Debug("recorded success episode")

	return nil
}

// updatePatterns 更新提取的模式
func (s *Store) updatePatterns(ctx context.Context, episode memory.SuccessEpisode) {
	if s.pool == nil {
		return
	}

	// 简化：基于任务类型创建/更新模式
	patternID := fmt.Sprintf("pattern_%s", episode.TaskType)
	isSuccess := episode.Outcome == memory.EpisodeOutcomeSuccess

	// 查找现有模式
	var existingFreq int
	var existingRate float64

	err := s.pool.QueryRow(ctx, `
		SELECT frequency, success_rate FROM extracted_patterns WHERE id = $1
	`, patternID).Scan(&existingFreq, &existingRate)

	if err != nil {
		// 创建新模式
		agentsJSON, _ := json.Marshal([]string{episode.AgentType})
		skillsJSON, _ := json.Marshal(episode.Skills)

		rate := 1.0
		if !isSuccess {
			rate = 0.0
		}

		s.pool.Exec(ctx, `
			INSERT INTO extracted_patterns (id, pattern, frequency, success_rate, agents, skills)
			VALUES ($1, $2, 1, $3, $4, $5)
		`, patternID, episode.TaskType, rate, agentsJSON, skillsJSON)
	} else {
		// 更新现有模式
		newFreq := existingFreq + 1
		var newRate float64
		if isSuccess {
			newRate = (existingRate*float64(existingFreq) + 1.0) / float64(newFreq)
		} else {
			newRate = (existingRate * float64(existingFreq)) / float64(newFreq)
		}

		s.pool.Exec(ctx, `
			UPDATE extracted_patterns SET frequency = $2, success_rate = $3 WHERE id = $1
		`, patternID, newFreq, newRate)
	}
}

// GetByID 根据 ID 获取案例
func (s *Store) GetByID(ctx context.Context, id string) (*memory.SuccessEpisode, error) {
	// 先检查缓存
	if cached, ok := s.cache.Load(id); ok {
		ep := cached.(memory.SuccessEpisode)
		return &ep, nil
	}

	if s.pool == nil {
		return nil, nil
	}

	var episode memory.SuccessEpisode
	var stepsJSON []byte
	var skillsJSON []byte
	var tagsJSON []byte

	err := s.pool.QueryRow(ctx, `
		SELECT id, task_type, input_pattern, solution, steps, outcome, duration, agent_type, skills, tags, created_at
		FROM success_episodes WHERE id = $1
	`, id).Scan(
		&episode.ID, &episode.TaskType, &episode.InputPattern, &episode.Solution,
		&stepsJSON, &episode.Outcome, &episode.Duration, &episode.AgentType,
		&skillsJSON, &tagsJSON, &episode.CreatedAt,
	)

	if err != nil {
		return nil, err
	}

	json.Unmarshal(stepsJSON, &episode.Steps)
	json.Unmarshal(skillsJSON, &episode.Skills)
	json.Unmarshal(tagsJSON, &episode.Tags)

	s.cache.Store(id, episode)
	return &episode, nil
}

// Search 搜索案例
func (s *Store) Search(ctx context.Context, taskType string) ([]memory.SuccessEpisode, error) {
	if s.pool == nil {
		// 从缓存搜索
		var results []memory.SuccessEpisode
		s.cache.Range(func(key, value interface{}) bool {
			ep := value.(memory.SuccessEpisode)
			if taskType == "" || ep.TaskType == taskType {
				results = append(results, ep)
			}
			return true
		})
		return results, nil
	}

	rows, err := s.pool.Query(ctx, `
		SELECT id, task_type, input_pattern, solution, steps, outcome, duration, agent_type, skills, tags, created_at
		FROM success_episodes
		WHERE task_type = $1 OR $1 = ''
		ORDER BY created_at DESC
		LIMIT 50
	`, taskType)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var results []memory.SuccessEpisode
	for rows.Next() {
		var episode memory.SuccessEpisode
		var stepsJSON []byte
		var skillsJSON []byte
		var tagsJSON []byte

		err := rows.Scan(
			&episode.ID, &episode.TaskType, &episode.InputPattern, &episode.Solution,
			&stepsJSON, &episode.Outcome, &episode.Duration, &episode.AgentType,
			&skillsJSON, &tagsJSON, &episode.CreatedAt,
		)
		if err != nil {
			continue
		}

		json.Unmarshal(stepsJSON, &episode.Steps)
		json.Unmarshal(skillsJSON, &episode.Skills)
		json.Unmarshal(tagsJSON, &episode.Tags)
		results = append(results, episode)
	}

	return results, nil
}

// GetPatterns 获取提取的模式
func (s *Store) GetPatterns(ctx context.Context) ([]memory.ExtractedPattern, error) {
	if s.pool == nil {
		return nil, nil
	}

	rows, err := s.pool.Query(ctx, `
		SELECT id, pattern, frequency, success_rate, agents, skills, created_at
		FROM extracted_patterns
		ORDER BY frequency DESC, success_rate DESC
		LIMIT 20
	`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var results []memory.ExtractedPattern
	for rows.Next() {
		var pattern memory.ExtractedPattern
		var agentsJSON []byte
		var skillsJSON []byte

		err := rows.Scan(
			&pattern.ID, &pattern.Pattern, &pattern.Frequency, &pattern.SuccessRate,
			&agentsJSON, &skillsJSON, &pattern.CreatedAt,
		)
		if err != nil {
			continue
		}

		json.Unmarshal(agentsJSON, &pattern.Agents)
		json.Unmarshal(skillsJSON, &pattern.Skills)
		results = append(results, pattern)
	}

	return results, nil
}

// UpdateUsage 更新使用统计
func (s *Store) UpdateUsage(ctx context.Context, id string) error {
	// 在实际实现中，这里可以增加使用计数
	_ = id
	return nil
}

// GetStats 获取统计信息
func (s *Store) GetStats(ctx context.Context) (memory.EpisodicStats, error) {
	stats := memory.EpisodicStats{
		TopAgents: []memory.AgentStat{},
		TopSkills: []memory.SkillStat{},
	}

	if s.pool == nil {
		// 从缓存计算
		var totalDuration int64
		var successCount int

		s.cache.Range(func(key, value interface{}) bool {
			ep := value.(memory.SuccessEpisode)
			stats.TotalEpisodes++
			totalDuration += ep.Duration.Milliseconds()
			if ep.Outcome == memory.EpisodeOutcomeSuccess {
				successCount++
			}
			return true
		})

		if stats.TotalEpisodes > 0 {
			stats.SuccessRate = float64(successCount) / float64(stats.TotalEpisodes)
			stats.AverageDuration = float64(totalDuration) / float64(stats.TotalEpisodes)
		}

		return stats, nil
	}

	// 从数据库查询
	err := s.pool.QueryRow(ctx, `
		SELECT
			COUNT(*) as total,
			COALESCE(AVG(CASE WHEN outcome = 'success' THEN 1.0 ELSE 0.0 END), 0) as success_rate,
			COALESCE(AVG(duration), 0) as avg_duration
		FROM success_episodes
	`).Scan(&stats.TotalEpisodes, &stats.SuccessRate, &stats.AverageDuration)

	if err != nil {
		return stats, err
	}

	stats.AverageDuration = stats.AverageDuration / 1000.0 // 转换为秒

	// 获取 Top Agents
	agentRows, _ := s.pool.Query(ctx, `
		SELECT agent_type, COUNT(*) as count,
			   COALESCE(AVG(CASE WHEN outcome = 'success' THEN 1.0 ELSE 0.0 END), 0) as success_rate
		FROM success_episodes
		WHERE agent_type IS NOT NULL
		GROUP BY agent_type
		ORDER BY count DESC
		LIMIT 5
	`)
	if agentRows != nil {
		defer agentRows.Close()
		for agentRows.Next() {
			var stat memory.AgentStat
			agentRows.Scan(&stat.AgentType, &stat.Count, &stat.SuccessRate)
			stats.TopAgents = append(stats.TopAgents, stat)
		}
	}

	// 获取 Top Skills
	skillRows, _ := s.pool.Query(ctx, `
		SELECT skill, COUNT(*) as count
		FROM success_episodes, unnest(skills) as skill
		GROUP BY skill
		ORDER BY count DESC
		LIMIT 5
	`)
	if skillRows != nil {
		defer skillRows.Close()
		for skillRows.Next() {
			var stat memory.SkillStat
			skillRows.Scan(&stat.SkillID, &stat.Count)
			stats.TopSkills = append(stats.TopSkills, stat)
		}
	}

	return stats, nil
}

// GetBestEpisode 获取最佳案例
func (s *Store) GetBestEpisode(ctx context.Context, taskType string) (*memory.SuccessEpisode, error) {
	if s.pool == nil {
		// 从缓存搜索最佳
		var best *memory.SuccessEpisode
		s.cache.Range(func(key, value interface{}) bool {
			ep := value.(memory.SuccessEpisode)
			if taskType == "" || ep.TaskType == taskType {
				if best == nil || ep.Duration < best.Duration {
					best = &ep
				}
			}
			return true
		})
		return best, nil
	}

	var episode memory.SuccessEpisode
	var stepsJSON []byte
	var skillsJSON []byte
	var tagsJSON []byte

	err := s.pool.QueryRow(ctx, `
		SELECT id, task_type, input_pattern, solution, steps, outcome, duration, agent_type, skills, tags, created_at
		FROM success_episodes
		WHERE task_type = $1 AND outcome = 'success'
		ORDER BY duration ASC
		LIMIT 1
	`, taskType).Scan(
		&episode.ID, &episode.TaskType, &episode.InputPattern, &episode.Solution,
		&stepsJSON, &episode.Outcome, &episode.Duration, &episode.AgentType,
		&skillsJSON, &tagsJSON, &episode.CreatedAt,
	)

	if err != nil {
		return nil, err
	}

	json.Unmarshal(stepsJSON, &episode.Steps)
	json.Unmarshal(skillsJSON, &episode.Skills)
	json.Unmarshal(tagsJSON, &episode.Tags)

	return &episode, nil
}

// Close 关闭连接
func (s *Store) Close() {
	if s.pool != nil {
		s.pool.Close()
	}
}

// ==================== 辅助函数 ====================

// CalculateSimilarity 计算案例相似度
func CalculateSimilarity(ep1, ep2 memory.SuccessEpisode) float64 {
	score := 0.0
	weights := 0.0

	// 任务类型匹配
	if ep1.TaskType == ep2.TaskType {
		score += 0.4
	}
	weights += 0.4

	// Agent 类型匹配
	if ep1.AgentType == ep2.AgentType {
		score += 0.2
	}
	weights += 0.2

	// 技能匹配
	ep1Skills := make(map[string]bool)
	for _, s := range ep1.Skills {
		ep1Skills[s] = true
	}
	skillMatch := 0
	for _, s := range ep2.Skills {
		if ep1Skills[s] {
			skillMatch++
		}
	}
	if len(ep2.Skills) > 0 {
		score += 0.2 * float64(skillMatch) / float64(len(ep2.Skills))
	}
	weights += 0.2

	// 标签匹配
	ep1Tags := make(map[string]bool)
	for _, t := range ep1.Tags {
		ep1Tags[t] = true
	}
	tagMatch := 0
	for _, t := range ep2.Tags {
		if ep1Tags[t] {
			tagMatch++
		}
	}
	if len(ep2.Tags) > 0 {
		score += 0.2 * float64(tagMatch) / float64(len(ep2.Tags))
	}
	weights += 0.2

	if weights == 0 {
		return 0
	}
	return score / weights
}

// RoundDuration 四舍五入时间
func RoundDuration(d time.Duration) time.Duration {
	return time.Duration(math.Round(float64(d))) * time.Millisecond
}
