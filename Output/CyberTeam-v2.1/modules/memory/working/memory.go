package working

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"strings"
	"sync"
	"time"

	"cyberteam/memory"

	"github.com/redis/go-redis/v9"
	"github.com/sirupsen/logrus"
)

// Store 工作记忆存储实现
type Store struct {
	redis       *redis.Client
	pgConn      string // PostgreSQL 连接 (用于持久化)
	cacheTTL    time.Duration
	cache       *sync.Map
	logger      *logrus.Logger
	mu          sync.RWMutex
}

// NewStore 创建新的工作记忆存储
func NewStore(cfg memory.Config, logger *logrus.Logger) (*Store, error) {
	var redisClient *redis.Client

	if cfg.RedisURL != "" {
		opt, err := redis.ParseURL(cfg.RedisURL)
		if err != nil {
			return nil, fmt.Errorf("failed to parse redis url: %w", err)
		}
		redisClient = redis.NewClient(opt)

		// 测试连接
		if err := redisClient.Ping(context.Background()).Err(); err != nil {
			logger.WithError(err).Warn("redis connection failed, using in-memory cache only")
			redisClient = nil
		}
	}

	s := &Store{
		redis:    redisClient,
		pgConn:   cfg.VectorStoreURL,
		cacheTTL: time.Hour,
		cache:    new(sync.Map),
		logger:   logger,
	}

	// 初始化数据库表
	if err := s.initSchema(context.Background()); err != nil {
		return nil, fmt.Errorf("failed to initialize schema: %w", err)
	}

	return s, nil
}

// initSchema 初始化数据库表
func (s *Store) initSchema(ctx context.Context) error {
	// 使用简单的 SQLite 风格或直接使用 Redis
	// 这里假设使用 PostgreSQL 扩展
	schema := `
	CREATE TABLE IF NOT EXISTS working_contexts (
		task_id TEXT PRIMARY KEY,
		parent_task_id TEXT,
		agent_type TEXT NOT NULL,
		status TEXT NOT NULL,
		input JSONB,
		output JSONB,
		history JSONB,
		temp_data JSONB,
		dependencies TEXT[],
		created_at TIMESTAMP DEFAULT NOW(),
		updated_at TIMESTAMP DEFAULT NOW()
	);

	CREATE INDEX IF NOT EXISTS idx_working_agent_type ON working_contexts(agent_type);
	CREATE INDEX IF NOT EXISTS idx_working_status ON working_contexts(status);
	CREATE INDEX IF NOT EXISTS idx_working_parent ON working_contexts(parent_task_id);
	`

	// 简化实现，主要使用内存缓存
	_ = schema
	return nil
}

// generateTaskID 生成任务 ID
func generateTaskID(agentType string) string {
	hash := sha256.Sum256([]byte(agentType + time.Now().Format(time.RFC3339Nano)))
	return "task_" + hex.EncodeToString(hash[:])[:12]
}

// CreateContext 创建任务上下文
func (s *Store) CreateContext(ctx context.Context, tc memory.TaskContext) error {
	if tc.TaskID == "" {
		tc.TaskID = generateTaskID(tc.AgentType)
	}
	tc.CreatedAt = time.Now()
	tc.UpdatedAt = time.Now()

	// 序列化为 JSON
	inputJSON, _ := json.Marshal(tc.Input)
	outputJSON, _ := json.Marshal(tc.Output)
	historyJSON, _ := json.Marshal(tc.History)
	tempDataJSON, _ := json.Marshal(tc.TempData)
	depsJSON, _ := json.Marshal(tc.Dependencies)

	// 存储到缓存
	key := fmt.Sprintf("working:context:%s", tc.TaskID)
	value, _ := json.Marshal(tc)

	s.mu.Lock()
	s.cache.Store(key, tc)
	s.mu.Unlock()

	// 存储到 Redis (如果可用)
	if s.redis != nil {
		if err := s.redis.Set(ctx, key, value, s.cacheTTL).Err(); err != nil {
			s.logger.WithError(err).Warn("failed to store context in redis")
		}
	}

	s.logger.WithFields(logrus.Fields{
		"task_id":    tc.TaskID,
		"agent_type": tc.AgentType,
		"status":     tc.Status,
	}).Debug("created task context in working memory")

	return nil
}

// GetContext 获取任务上下文
func (s *Store) GetContext(ctx context.Context, taskID string) (*memory.TaskContext, error) {
	key := fmt.Sprintf("working:context:%s", taskID)

	// 先从缓存获取
	s.mu.RLock()
	if cached, ok := s.cache.Load(key); ok {
		s.mu.RUnlock()
		tc := cached.(memory.TaskContext)
		return &tc, nil
	}
	s.mu.RUnlock()

	// 尝试从 Redis 获取
	if s.redis != nil {
		data, err := s.redis.Get(ctx, key).Bytes()
		if err == nil {
			var tc memory.TaskContext
			json.Unmarshal(data, &tc)
			s.cache.Store(key, tc)
			return &tc, nil
		}
	}

	return nil, nil
}

// UpdateContext 更新任务上下文
func (s *Store) UpdateContext(ctx context.Context, tc memory.TaskContext) error {
	tc.UpdatedAt = time.Now()

	key := fmt.Sprintf("working:context:%s", tc.TaskID)
	value, _ := json.Marshal(tc)

	s.mu.Lock()
	s.cache.Store(key, tc)
	s.mu.Unlock()

	if s.redis != nil {
		s.redis.Set(ctx, key, value, s.cacheTTL)
	}

	return nil
}

// DeleteContext 删除任务上下文
func (s *Store) DeleteContext(ctx context.Context, taskID string) error {
	key := fmt.Sprintf("working:context:%s", taskID)

	s.mu.Lock()
	s.cache.Delete(key)
	s.mu.Unlock()

	if s.redis != nil {
		s.redis.Del(ctx, key)
	}

	return nil
}

// AddAction 添加操作记录
func (s *Store) AddAction(ctx context.Context, taskID string, action memory.AgentAction) error {
	tc, err := s.GetContext(ctx, taskID)
	if err != nil || tc == nil {
		return fmt.Errorf("context not found: %s", taskID)
	}

	if action.ID == "" {
		hash := sha256.Sum256([]byte(taskID + time.Now().Format(time.RFC3339Nano)))
		action.ID = "action_" + hex.EncodeToString(hash[:])[:8]
	}
	action.Timestamp = time.Now()

	tc.History = append(tc.History, action)
	tc.UpdatedAt = time.Now()

	return s.UpdateContext(ctx, *tc)
}

// GetHistory 获取操作历史
func (s *Store) GetHistory(ctx context.Context, taskID string) ([]memory.AgentAction, error) {
	tc, err := s.GetContext(ctx, taskID)
	if err != nil || tc == nil {
		return nil, nil
	}

	return tc.History, nil
}

// SetTempData 设置临时数据
func (s *Store) SetTempData(ctx context.Context, taskID string, key string, value interface{}) error {
	tc, err := s.GetContext(ctx, taskID)
	if err != nil || tc == nil {
		return fmt.Errorf("context not found: %s", taskID)
	}

	if tc.TempData == nil {
		tc.TempData = make(map[string]interface{})
	}
	tc.TempData[key] = value
	tc.UpdatedAt = time.Now()

	return s.UpdateContext(ctx, *tc)
}

// GetTempData 获取临时数据
func (s *Store) GetTempData(ctx context.Context, taskID string, key string) (interface{}, error) {
	tc, err := s.GetContext(ctx, taskID)
	if err != nil || tc == nil {
		return nil, nil
	}

	return tc.TempData[key], nil
}

// GetContextsByAgent 获取指定 Agent 的所有任务上下文
func (s *Store) GetContextsByAgent(ctx context.Context, agentType string) ([]memory.TaskContext, error) {
	var results []memory.TaskContext

	s.cache.Range(func(key, value interface{}) bool {
		tc := value.(memory.TaskContext)
		if tc.AgentType == agentType || agentType == "" {
			results = append(results, tc)
		}
		return true
	})

	return results, nil
}

// GetActiveTasks 获取活跃任务
func (s *Store) GetActiveTasks(ctx context.Context) ([]memory.TaskContext, error) {
	var results []memory.TaskContext

	s.cache.Range(func(key, value interface{}) bool {
		tc := value.(memory.TaskContext)
		if tc.Status == memory.TaskStatusRunning || tc.Status == memory.TaskStatusWaiting {
			results = append(results, tc)
		}
		return true
	})

	return results, nil
}

// SearchContexts 搜索任务上下文
func (s *Store) SearchContexts(ctx context.Context, query string) ([]memory.TaskContext, error) {
	var results []memory.TaskContext

	s.cache.Range(func(key, value interface{}) bool {
		tc := value.(memory.TaskContext)
		inputStr, _ := json.Marshal(tc.Input)
		outputStr, _ := json.Marshal(tc.Output)

		if strings.Contains(string(inputStr), query) || strings.Contains(string(outputStr), query) {
			results = append(results, tc)
		}
		return true
	})

	return results, nil
}

// Close 关闭连接
func (s *Store) Close() {
	if s.redis != nil {
		s.redis.Close()
	}
}
