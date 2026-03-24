package memory

import (
	"context"
	"fmt"
	"sync"

	"cyberteam/memory/episodic"
	"cyberteam/memory/long_term"
	"cyberteam/memory/working"

	"github.com/sirupsen/logrus"
)

// System 统一记忆系统
type System struct {
	config     Config
	logger     *logrus.Logger
	longTerm   LongTermMemory
	working    WorkingMemory
	episodic   EpisodicMemory
	mu         sync.RWMutex
	closed     bool
}

// NewSystem 创建新的记忆系统
func NewSystem(cfg Config, logger *logrus.Logger) (*System, error) {
	if logger == nil {
		logger = logrus.New()
		logger.SetLevel(logrus.InfoLevel)
	}

	s := &System{
		config: cfg,
		logger: logger,
	}

	// 初始化 Long-term Memory
	lt, err := long_term.NewStore(cfg, logger)
	if err != nil {
		logger.WithError(err).Warn("long-term memory initialization failed, using fallback")
		// 使用简单的内存实现作为后备
		lt = newFallbackLongTerm()
	}
	s.longTerm = lt

	// 初始化 Working Memory
	wm, err := working.NewStore(cfg, logger)
	if err != nil {
		logger.WithError(err).Warn("working memory initialization failed, using fallback")
		wm = newFallbackWorking()
	}
	s.working = wm

	// 初始化 Episodic Memory
	em, err := episodic.NewStore(cfg, logger)
	if err != nil {
		logger.WithError(err).Warn("episodic memory initialization failed, using fallback")
		em = newFallbackEpisodic()
	}
	s.episodic = em

	logger.Info("memory system initialized successfully")
	return s, nil
}

// LongTerm 获取长期记忆模块
func (s *System) LongTerm() LongTermMemory {
	return s.longTerm
}

// Working 获取工作记忆模块
func (s *System) Working() WorkingMemory {
	return s.working
}

// Episodic 获取情景记忆模块
func (s *System) Episodic() EpisodicMemory {
	return s.episodic
}

// Close 关闭记忆系统
func (s *System) Close() {
	s.mu.Lock()
	defer s.mu.Unlock()

	if s.closed {
		return
	}
	s.closed = true

	if lt, ok := s.longTerm.(*long_term.Store); ok {
		lt.Close()
	}
	if wm, ok := s.working.(*working.Store); ok {
		wm.Close()
	}
	if em, ok := s.episodic.(*episodic.Store); ok {
		em.Close()
	}

	s.logger.Info("memory system closed")
}

// ==================== 高级功能 ====================

// SmartSearch 智能搜索 - 综合三大记忆的搜索
func (s *System) SmartSearch(ctx context.Context, query SmartSearchQuery) (*SmartSearchResult, error) {
	result := &SmartSearchResult{
		LongTerm: make([]SearchResult, 0),
		Working:  make([]TaskContext, 0),
		Episodic: make([]SuccessEpisode, 0),
	}

	// 并行搜索
	var wg sync.WaitGroup
	var longTermErr, workingErr, episodicErr error

	// 搜索长期记忆
	if query.EnableLongTerm {
		wg.Add(1)
		go func() {
			defer wg.Done()
			longTermResults, err := s.longTerm.Search(ctx, SearchQuery{
				Query:     query.Query,
				AgentType: query.AgentType,
				SkillID:   query.SkillID,
				TaskType:  query.TaskType,
				Limit:     query.LongTermLimit,
				Threshold: query.Threshold,
			})
			if err != nil {
				longTermErr = err
				return
			}
			result.LongTerm = longTermResults
		}()
	}

	// 搜索工作记忆
	if query.EnableWorking {
		wg.Add(1)
		go func() {
			defer wg.Done()
			workingResults, err := s.working.SearchContexts(ctx, query.Query)
			if err != nil {
				workingErr = err
				return
			}
			result.Working = workingResults
		}()
	}

	// 搜索情景记忆
	if query.EnableEpisodic {
		wg.Add(1)
		go func() {
			defer wg.Done()
			episodicResults, err := s.episodic.Search(ctx, query.TaskType)
			if err != nil {
				episodicErr = err
				return
			}
			result.Episodic = episodicResults
		}()
	}

	wg.Wait()

	// 汇总错误
	if longTermErr != nil || workingErr != nil || episodicErr != nil {
		return result, fmt.Errorf("search errors: lt=%v, wm=%v, em=%v",
			longTermErr, workingErr, episodicErr)
	}

	// 计算综合得分
	result.Score = s.calculateScore(result)

	return result, nil
}

// SmartSearchQuery 智能搜索查询
type SmartSearchQuery struct {
	Query          string // 搜索文本
	AgentType      string // Agent 类型
	SkillID        string // 技能 ID
	TaskType       string // 任务类型
	Threshold      float64
	LongTermLimit  int
	WorkingLimit   int
	EpisodicLimit  int
	EnableLongTerm bool
	EnableWorking  bool
	EnableEpisodic bool
}

// SmartSearchResult 智能搜索结果
type SmartSearchResult struct {
	LongTerm []SearchResult
	Working  []TaskContext
	Episodic []SuccessEpisode
	Score    float64
}

// calculateScore 计算综合得分
func (s *System) calculateScore(r *SmartSearchResult) float64 {
	score := 0.0

	if len(r.LongTerm) > 0 {
		score += 0.4 * r.LongTerm[0].Score
	}
	if len(r.Working) > 0 {
		score += 0.3
	}
	if len(r.Episodic) > 0 {
		for _, ep := range r.Episodic {
			if ep.Outcome == EpisodeOutcomeSuccess {
				score += 0.3
				break
			}
		}
	}

	return score
}

// RecordExperience 记录经验 - 同时写入长期和情景记忆
func (s *System) RecordExperience(ctx context.Context, req RecordExperienceRequest) error {
	var wg sync.WaitGroup

	// 写入长期记忆
	if req.Content != "" {
		wg.Add(1)
		go func() {
			defer wg.Done()
			err := s.longTerm.Store(ctx, MemoryDocument{
				AgentType:   req.AgentType,
				SkillID:     req.SkillID,
				TaskType:    req.TaskType,
				Content:     req.Content,
				Tags:        req.Tags,
				SuccessRate: req.SuccessRate,
			})
			if err != nil {
				s.logger.WithError(err).Warn("failed to store in long-term memory")
			}
		}()
	}

	// 写入情景记忆
	if req.Episode != nil {
		wg.Add(1)
		go func() {
			defer wg.Done()
			err := s.episodic.Record(ctx, *req.Episode)
			if err != nil {
				s.logger.WithError(err).Warn("failed to record episode")
			}
		}()
	}

	wg.Wait()
	return nil
}

// RecordExperienceRequest 记录经验请求
type RecordExperienceRequest struct {
	AgentType   string
	SkillID     string
	TaskType    string
	Content     string
	Tags        []string
	SuccessRate float64
	Episode     *SuccessEpisode
}

// GetContext 获取任务上下文（自动创建如果不存在）
func (s *System) GetContext(ctx context.Context, taskID string) (*TaskContext, error) {
	// 先从工作记忆获取
	tc, err := s.working.GetContext(ctx, taskID)
	if err == nil && tc != nil {
		return tc, nil
	}

	// 如果不存在，尝试从情景记忆获取相关案例
	episodes, err := s.episodic.Search(ctx, "")
	if err == nil && len(episodes) > 0 {
		// 返回最近的案例作为参考
		return &TaskContext{
			TaskID:   taskID,
			Status:   TaskStatusPending,
			TempData: map[string]interface{}{"reference_episode": episodes[0].ID},
		}, nil
	}

	return nil, fmt.Errorf("context not found: %s", taskID)
}

// GetStats 获取记忆系统统计
func (s *System) GetStats(ctx context.Context) (map[string]interface{}, error) {
	stats := make(map[string]interface{})

	// 获取情景记忆统计
	if em, ok := s.episodic.(*episodic.Store); ok {
		epStats, err := em.GetStats(ctx)
		if err == nil {
			stats["episodic"] = epStats
		}
	}

	return stats, nil
}

// ==================== Fallback 实现 ====================

// fallbackLongTerm 后备长期记忆
type fallbackLongTerm struct {
	cache *sync.Map
}

func newFallbackLongTerm() LongTermMemory {
	return &fallbackLongTerm{cache: new(sync.Map)}
}

func (f *fallbackLongTerm) Store(ctx context.Context, doc MemoryDocument) error {
	f.cache.Store(doc.ID, doc)
	return nil
}

func (f *fallbackLongTerm) Search(ctx context.Context, query SearchQuery) ([]SearchResult, error) {
	return nil, nil
}

func (f *fallbackLongTerm) Delete(ctx context.Context, id string) error {
	f.cache.Delete(id)
	return nil
}

func (f *fallbackLongTerm) Update(ctx context.Context, doc MemoryDocument) error {
	f.cache.Store(doc.ID, doc)
	return nil
}

func (f *fallbackLongTerm) GetByID(ctx context.Context, id string) (*MemoryDocument, error) {
	if v, ok := f.cache.Load(id); ok {
		doc := v.(MemoryDocument)
		return &doc, nil
	}
	return nil, nil
}

func (f *fallbackLongTerm) GetByTag(ctx context.Context, tag string) ([]MemoryDocument, error) {
	return nil, nil
}

// fallbackWorking 后备工作记忆
type fallbackWorking struct {
	cache *sync.Map
}

func newFallbackWorking() WorkingMemory {
	return &fallbackWorking{cache: new(sync.Map)}
}

func (f *fallbackWorking) CreateContext(ctx context.Context, tc TaskContext) error {
	f.cache.Store(tc.TaskID, tc)
	return nil
}

func (f *fallbackWorking) GetContext(ctx context.Context, taskID string) (*TaskContext, error) {
	if v, ok := f.cache.Load(taskID); ok {
		tc := v.(TaskContext)
		return &tc, nil
	}
	return nil, nil
}

func (f *fallbackWorking) UpdateContext(ctx context.Context, tc TaskContext) error {
	f.cache.Store(tc.TaskID, tc)
	return nil
}

func (f *fallbackWorking) DeleteContext(ctx context.Context, taskID string) error {
	f.cache.Delete(taskID)
	return nil
}

func (f *fallbackWorking) AddAction(ctx context.Context, taskID string, action AgentAction) error {
	tc, err := f.GetContext(ctx, taskID)
	if err != nil || tc == nil {
		return fmt.Errorf("context not found: %s", taskID)
	}
	tc.History = append(tc.History, action)
	f.cache.Store(taskID, *tc)
	return nil
}

func (f *fallbackWorking) GetHistory(ctx context.Context, taskID string) ([]AgentAction, error) {
	tc, err := f.GetContext(ctx, taskID)
	if err != nil || tc == nil {
		return nil, nil
	}
	return tc.History, nil
}

func (f *fallbackWorking) SetTempData(ctx context.Context, taskID string, key string, value interface{}) error {
	tc, err := f.GetContext(ctx, taskID)
	if err != nil || tc == nil {
		return fmt.Errorf("context not found: %s", taskID)
	}
	if tc.TempData == nil {
		tc.TempData = make(map[string]interface{})
	}
	tc.TempData[key] = value
	f.cache.Store(taskID, *tc)
	return nil
}

func (f *fallbackWorking) GetTempData(ctx context.Context, taskID string, key string) (interface{}, error) {
	tc, err := f.GetContext(ctx, taskID)
	if err != nil || tc == nil {
		return nil, nil
	}
	return tc.TempData[key], nil
}

func (f *fallbackWorking) SearchContexts(ctx context.Context, query string) ([]TaskContext, error) {
	return nil, nil
}

func (f *fallbackWorking) GetActiveTasks(ctx context.Context) ([]TaskContext, error) {
	return nil, nil
}

func (f *fallbackWorking) GetContextsByAgent(ctx context.Context, agentType string) ([]TaskContext, error) {
	return nil, nil
}

// fallbackEpisodic 后备情景记忆
type fallbackEpisodic struct {
	cache *sync.Map
}

func newFallbackEpisodic() EpisodicMemory {
	return &fallbackEpisodic{cache: new(sync.Map)}
}

func (f *fallbackEpisodic) Record(ctx context.Context, episode SuccessEpisode) error {
	f.cache.Store(episode.ID, episode)
	return nil
}

func (f *fallbackEpisodic) GetByID(ctx context.Context, id string) (*SuccessEpisode, error) {
	if v, ok := f.cache.Load(id); ok {
		ep := v.(SuccessEpisode)
		return &ep, nil
	}
	return nil, nil
}

func (f *fallbackEpisodic) Search(ctx context.Context, taskType string) ([]SuccessEpisode, error) {
	return nil, nil
}

func (f *fallbackEpisodic) GetPatterns(ctx context.Context) ([]ExtractedPattern, error) {
	return nil, nil
}

func (f *fallbackEpisodic) UpdateUsage(ctx context.Context, id string) error {
	return nil
}

func (f *fallbackEpisodic) GetStats(ctx context.Context) (EpisodicStats, error) {
	return EpisodicStats{}, nil
}
