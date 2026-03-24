# CyberTeam Memory System

## 概述

基于 PentAGI Memory System 设计，为 CyberTeam 实现的智能记忆系统。

## 架构

### 三大核心模块

```
┌─────────────────────────────────────────────────────────────────┐
│                      CyberTeam Memory System                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │  Long-term       │  │  Working         │  │  Episodic    │ │
│  │  Memory          │  │  Memory          │  │  Memory      │ │
│  │  ─────────────   │  │  ─────────────   │  │  ──────────  │ │
│  │  向量存储经验库    │  │  当前任务状态     │  │  历史成功模式 │ │
│  │                  │  │                  │  │              │ │
│  │  • pgvector      │  │  • 任务上下文     │  │  • 成功案例  │ │
│  │  • 语义搜索      │  │  • Agent 状态     │  │  • 模式提取  │ │
│  │  • 经验复用      │  │  • 会话管理       │  │  • 经验复用  │ │
│  │                  │  │  • 临时缓存       │  │  • 成功率    │ │
│  └────────┬─────────┘  └────────┬─────────┘  └──────┬───────┘ │
│           │                       │                    │        │
│           └───────────────────────┼────────────────────┘        │
│                                   │                             │
│                    ┌──────────────▼──────────────┐              │
│                    │       Memory Manager        │              │
│                    │       统一调度与协调          │              │
│                    └─────────────────────────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 参考 PentAGI 设计

- **向量存储**: 使用 pgvector 进行语义相似性搜索
- **过滤器**: 支持 flow_id, task_id, agent_type 等多维度过滤
- **fallback 机制**: 特定搜索无结果时回退到全局搜索

## 模块详细设计

### 1. Long-term Memory (长期记忆)

```go
// 经验文档结构
type MemoryDocument struct {
    ID            string                 // 唯一标识
    Content       string                 // 内容
    Embedding     []float64              // 向量嵌入
    AgentType     string                 // Agent 类型
    SkillID       string                 // 技能 ID
    TaskType     string                 // 任务类型
    Tags          []string               // 标签
    SuccessRate   float64                // 成功率
    UsageCount    int                    // 使用次数
    CreatedAt     time.Time              // 创建时间
    UpdatedAt     time.Time              // 更新时间
    Metadata      map[string]interface{} // 扩展元数据
}
```

### 2. Working Memory (工作记忆)

```go
// 任务上下文
type TaskContext struct {
    TaskID        string                 // 任务 ID
    ParentTaskID  string                 // 父任务 ID
    AgentType     string                 // 当前 Agent
    Status        TaskStatus             // 任务状态
    Input         map[string]interface{} // 输入参数
    Output        map[string]interface{} // 输出结果
    History       []AgentAction          // 操作历史
    TempData      map[string]interface{} // 临时数据
    CreatedAt     time.Time
    UpdatedAt     time.Time
}
```

### 3. Episodic Memory (情景记忆)

```go
// 成功案例
type SuccessEpisode struct {
    ID            string                 // 案例 ID
    TaskType      string                 // 任务类型
    InputPattern  string                 // 输入模式
    Solution      string                 // 解决方案
    Steps         []ActionStep           // 执行步骤
    Outcome       EpisodeOutcome         // 执行结果
    Duration      time.Duration          // 执行时长
    AgentType     string                 // 使用的 Agent
    Skills        []string               // 使用的技能
    Tags          []string               // 标签
    CreatedAt     time.Time
}

// 模式提取
type ExtractedPattern struct {
    ID          string
    Pattern     string
    Frequency   int
    SuccessRate float64
    Agents      []string
    Skills      []string
}
```

## 使用示例

```go
// 初始化记忆系统
memSystem := memory.NewSystem(memory.Config{
    VectorStoreURL: "postgres://user:pass@localhost:5432/cyberteam",
    EmbeddingModel: "text-embedding-3-small",
    CacheSize:     1000,
})

// 存储经验到长期记忆
err := memSystem.LongTerm.Store(ctx, memory.MemoryDocument{
    AgentType: "eng-agent",
    SkillID:   "frontend-developer",
    Content:   "使用 React + TypeScript 构建现代 Web 应用",
    Tags:      []string{"react", "typescript", "web"},
    SuccessRate: 0.85,
})

// 搜索相关经验
results, err := memSystem.LongTerm.Search(ctx, memory.SearchQuery{
    Query:     "如何构建 React 组件",
    AgentType: "eng-agent",
    Limit:     5,
    Threshold: 0.7,
})

// 创建任务上下文
ctx, err := memSystem.Working.CreateContext(ctx, memory.TaskContext{
    TaskID:    "task-001",
    AgentType: "gsd-planner",
    Input:     map[string]interface{}{"goal": "构建 Web 应用"},
})

// 记录成功案例
err := memSystem.Episodic.Record(ctx, memory.SuccessEpisode{
    TaskType: "web-development",
    Solution: "使用 Next.js + TailwindCSS",
    Steps:    []memory.ActionStep{...},
    Outcome:  memory.EpisodeOutcomeSuccess,
})
```

## 技术栈

- **向量存储**: PostgreSQL + pgvector
- **缓存**: Redis (Working Memory)
- **嵌入模型**: OpenAI Embedding / MiniMax Embedding
- **接口**: REST API + GraphQL

## 性能优化

1. **批量嵌入**: 批量处理减少 API 调用
2. **缓存**: 热数据使用 Redis 缓存
3. **异步**: 非关键操作异步执行
4. **索引**: 优化 pgvector 索引
