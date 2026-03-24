package memory

import (
	"time"
)

// ==================== 基础类型定义 ====================

// TaskStatus 任务状态
type TaskStatus string

const (
	TaskStatusPending   TaskStatus = "pending"
	TaskStatusRunning   TaskStatus = "running"
	TaskStatusWaiting   TaskStatus = "waiting"
	TaskStatusFinished TaskStatus = "finished"
	TaskStatusFailed    TaskStatus = "failed"
)

// EpisodeOutcome 执行结果
type EpisodeOutcome string

const (
	EpisodeOutcomeSuccess    EpisodeOutcome = "success"
	EpisodeOutcomePartial    EpisodeOutcome = "partial"
	EpisodeOutcomeFailed     EpisodeOutcome = "failed"
	EpisodeOutcomeUnknown    EpisodeOutcome = "unknown"
)

// VecstoreActionType 向量存储操作类型
type VecstoreActionType string

const (
	VecstoreActionTypeStore     VecstoreActionType = "store"
	VecstoreActionTypeRetrieve  VecstoreActionType = "retrieve"
	VecstoreActionTypeDelete    VecstoreActionType = "delete"
)

// ==================== Long-term Memory 类型 ====================

// MemoryDocument 经验文档
type MemoryDocument struct {
	ID          string                 `json:"id"`           // 唯一标识
	Content     string                 `json:"content"`      // 内容
	Embedding   []float64             `json:"-"`            // 向量嵌入 (不存储)
	AgentType   string                 `json:"agent_type"`   // Agent 类型
	SkillID     string                 `json:"skill_id"`     // 技能 ID
	TaskType    string                 `json:"task_type"`    // 任务类型
	Tags        []string               `json:"tags"`         // 标签
	SuccessRate float64                `json:"success_rate"` // 成功率
	UsageCount  int                    `json:"usage_count"`  // 使用次数
	CreatedAt   time.Time              `json:"created_at"`   // 创建时间
	UpdatedAt   time.Time              `json:"updated_at"`   // 更新时间
	Metadata    map[string]interface{} `json:"metadata"`     // 扩展元数据
}

// SearchQuery 搜索查询
type SearchQuery struct {
	Query      string   `json:"query"`       // 查询文本
	AgentType  string   `json:"agent_type"` // Agent 类型过滤
	SkillID    string   `json:"skill_id"`  // 技能 ID 过滤
	TaskType   string   `json:"task_type"` // 任务类型过滤
	Tags       []string `json:"tags"`       // 标签过滤
	Limit      int      `json:"limit"`      // 返回结果数量
	Threshold  float64  `json:"threshold"`  // 相似度阈值
	TaskID     string   `json:"task_id"`    // 任务 ID (可选)
	Global     bool     `json:"global"`     // 是否全局搜索
}

// SearchResult 搜索结果
type SearchResult struct {
	Document  MemoryDocument `json:"document"`
	Score     float64        `json:"score"`
	Reason    string         `json:"reason,omitempty"`
}

// ==================== Working Memory 类型 ====================

// TaskContext 任务上下文
type TaskContext struct {
	TaskID       string                 `json:"task_id"`        // 任务 ID
	ParentTaskID string                 `json:"parent_task_id"` // 父任务 ID
	AgentType    string                 `json:"agent_type"`     // 当前 Agent
	Status       TaskStatus             `json:"status"`         // 任务状态
	Input        map[string]interface{} `json:"input"`          // 输入参数
	Output       map[string]interface{} `json:"output"`         // 输出结果
	History      []AgentAction           `json:"history"`        // 操作历史
	TempData     map[string]interface{} `json:"temp_data"`      // 临时数据
	Dependencies []string                `json:"dependencies"`   // 依赖任务
	CreatedAt    time.Time               `json:"created_at"`
	UpdatedAt    time.Time               `json:"updated_at"`
}

// AgentAction Agent 操作记录
type AgentAction struct {
	ID          string                 `json:"id"`           // 操作 ID
	ActionType  string                 `json:"action_type"`  // 操作类型
	AgentType   string                 `json:"agent_type"`   // Agent 类型
	Input       map[string]interface{} `json:"input"`        // 输入
	Output      map[string]interface{} `json:"output"`       // 输出
	Result      string                 `json:"result"`       // 结果描述
	Duration    time.Duration          `json:"duration"`     // 执行时长
	Error       string                 `json:"error,omitempty"` // 错误信息
	Timestamp   time.Time              `json:"timestamp"`
}

// ==================== Episodic Memory 类型 ====================

// SuccessEpisode 成功案例
type SuccessEpisode struct {
	ID          string        `json:"id"`           // 案例 ID
	TaskType    string        `json:"task_type"`   // 任务类型
	InputPattern string       `json:"input_pattern"` // 输入模式
	Solution    string        `json:"solution"`    // 解决方案
	Steps       []ActionStep  `json:"steps"`       // 执行步骤
	Outcome     EpisodeOutcome `json:"outcome"`    // 执行结果
	Duration    time.Duration `json:"duration"`    // 执行时长
	AgentType   string        `json:"agent_type"`  // 使用的 Agent
	Skills      []string      `json:"skills"`      // 使用的技能
	Tags        []string      `json:"tags"`        // 标签
	CreatedAt   time.Time     `json:"created_at"`
}

// ActionStep 执行步骤
type ActionStep struct {
	StepNumber int                    `json:"step_number"` // 步骤编号
	Action     string                 `json:"action"`      // 动作描述
	AgentType  string                 `json:"agent_type"`  // 执行 Agent
	Input      map[string]interface{} `json:"input"`       // 输入参数
	Output     map[string]interface{} `json:"output"`       // 输出结果
	Duration   time.Duration         `json:"duration"`     // 执行时长
	Success    bool                   `json:"success"`      // 是否成功
}

// ExtractedPattern 提取的模式
type ExtractedPattern struct {
	ID          string   `json:"id"`           // 模式 ID
	Pattern     string   `json:"pattern"`     // 模式描述
	Frequency   int      `json:"frequency"`   // 出现频率
	SuccessRate float64  `json:"success_rate"` // 成功率
	Agents      []string `json:"agents"`       // 涉及的 Agent
	Skills      []string `json:"skills"`       // 涉及的技能
	CreatedAt   time.Time `json:"created_at"`
}

// ==================== 配置类型 ====================

// Config 记忆系统配置
type Config struct {
	VectorStoreURL  string        // PostgreSQL pgvector 连接地址
	RedisURL        string        // Redis 连接地址 (可选)
	EmbeddingModel string        // 嵌入模型
	EmbeddingURL   string        // 嵌入模型 API 地址
	APIKey         string        // API Key
	CacheSize      int           // 缓存大小
	SimilarityThreshold float64   // 相似度阈值 (默认 0.7)
	MaxResults     int           // 最大结果数 (默认 5)
}

// ==================== 接口定义 ====================

// LongTermMemory 长期记忆接口
type LongTermMemory interface {
	Store(ctx context.Context, doc MemoryDocument) error
	Search(ctx context.Context, query SearchQuery) ([]SearchResult, error)
	Delete(ctx context.Context, id string) error
	Update(ctx context.Context, doc MemoryDocument) error
	GetByID(ctx context.Context, id string) (*MemoryDocument, error)
	GetByTag(ctx context.Context, tag string) ([]MemoryDocument, error)
}

// WorkingMemory 工作记忆接口
type WorkingMemory interface {
	CreateContext(ctx context.Context, tc TaskContext) error
	GetContext(ctx context.Context, taskID string) (*TaskContext, error)
	UpdateContext(ctx context.Context, tc TaskContext) error
	DeleteContext(ctx context.Context, taskID string) error
	AddAction(ctx context.Context, taskID string, action AgentAction) error
	GetHistory(ctx context.Context, taskID string) ([]AgentAction, error)
	SetTempData(ctx context.Context, taskID string, key string, value interface{}) error
	GetTempData(ctx context.Context, taskID string, key string) (interface{}, error)
	SearchContexts(ctx context.Context, query string) ([]TaskContext, error)
	GetActiveTasks(ctx context.Context) ([]TaskContext, error)
	GetContextsByAgent(ctx context.Context, agentType string) ([]TaskContext, error)
}

// EpisodicMemory 情景记忆接口
type EpisodicMemory interface {
	Record(ctx context.Context, episode SuccessEpisode) error
	GetByID(ctx context.Context, id string) (*SuccessEpisode, error)
	Search(ctx context.Context, taskType string) ([]SuccessEpisode, error)
	GetPatterns(ctx context.Context) ([]ExtractedPattern, error)
	UpdateUsage(ctx context.Context, id string) error
	GetStats(ctx context.Context) (EpisodicStats, error)
}

// EpisodicStats 统计信息
type EpisodicStats struct {
	TotalEpisodes   int     `json:"total_episodes"`
	SuccessRate     float64 `json:"success_rate"`
	AverageDuration float64 `json:"average_duration"`
	TopAgents       []AgentStat `json:"top_agents"`
	TopSkills       []SkillStat `json:"top_skills"`
}

// AgentStat Agent 统计
type AgentStat struct {
	AgentType   string  `json:"agent_type"`
	Count       int     `json:"count"`
	SuccessRate float64 `json:"success_rate"`
}

// SkillStat 技能统计
type SkillStat struct {
	SkillID     string  `json:"skill_id"`
	Count       int     `json:"count"`
	SuccessRate float64 `json:"success_rate"`
}
