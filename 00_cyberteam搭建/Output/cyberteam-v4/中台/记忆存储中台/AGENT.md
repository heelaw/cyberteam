# 记忆存储中台

## 基本信息

| 属性 | 内容 |
|------|------|
| **Agent名称** | 记忆存储中台 (Memory Hub) |
| **定位** | 向量数据库和上下文管理中枢 |
| **类型** | 中台能力中心 |
| **版本** | v4.0 |
| **创建日期** | 2026-03-25 |
| **所属系统** | CyberTeam v4 核心中台 |

---

## 核心定位

记忆存储中台是CyberTeam v4的"智慧记忆中心"，管理多层次记忆体系，支持向量检索和上下文管理，让每个Agent都能获取历史智慧。

### 核心能力

1. **记忆分层**: 短期/中期/长期/永久四级存储
2. **向量检索**: 基于语义的高效相似度搜索
3. **上下文管理**: 跨会话上下文追踪
4. **记忆召回**: 智能召回相关记忆

---

## 向量数据库设计

### 向量存储架构

```
┌─────────────────────────────────────────────────────────┐
│                    Vector Database                       │
├─────────────────────────────────────────────────────────┤
│  Collection: conversations                              │
│  ├── id: string                                         │
│  ├── vector: float[1536]  (embedding)                  │
│  ├── content: string                                    │
│  ├── metadata:                                         │
│  │     session_id: string                               │
│  │     agent_id: string                                 │
│  │     timestamp: datetime                              │
│  │     importance: float (0-1)                           │
│  │     tags: string[]                                   │
│  │     access_count: int                               │
│  └── expires_at: datetime (TTL)                         │
├─────────────────────────────────────────────────────────┤
│  Collection: documents                                  │
│  ├── id: string                                         │
│  ├── vector: float[1536]                                │
│  ├── content: string                                    │
│  ├── metadata:                                         │
│  │     doc_type: enum                                  │
│  │     source: string                                   │
│  │     created_at: datetime                             │
│  │     version: string                                  │
│  │     author: string                                   │
│  └── category: string[]                                 │
├─────────────────────────────────────────────────────────┤
│  Collection: knowledge                                  │
│  ├── id: string                                         │
│  ├── vector: float[1536]                                │
│  ├── content: string                                    │
│  ├── metadata:                                         │
│  │     knowledge_type: enum                            │
│  │     domain: string                                   │
│  │     confidence: float                               │
│  │     verified: boolean                               │
│  │     contributor: string                             │
│  └── tags: string[]                                     │
└─────────────────────────────────────────────────────────┘
```

### 向量模型配置

| 配置项 | 值 | 说明 |
|--------|-----|------|
| **模型** | text-embedding-3-small | OpenAIembedding |
| **维度** | 1536 | 向量维度 |
| **距离度量** | cosine | 余弦相似度 |
| **索引类型** | HNSW | 高效近邻搜索 |
| **M** | 16 | HNSW参数 |
| **efConstruction** | 200 | HNSW参数 |

### 索引策略

```python
# 分层索引设计
indexes = {
    "conversations": {
        "primary": "vector",           # 主索引: 向量
        "secondary": [                  # 二级索引
            "session_id",
            "agent_id",
            "timestamp",
            "tags"
        ],
        "filterable": ["importance", "expires_at"]
    },
    "documents": {
        "primary": "vector",
        "secondary": ["doc_type", "category", "source"],
        "filterable": ["version", "created_at"]
    },
    "knowledge": {
        "primary": "vector",
        "secondary": ["knowledge_type", "domain", "verified"],
        "filterable": ["confidence", "contributor"]
    }
}
```

---

## 记忆分层

### 四层记忆体系

| 层级 | 名称 | 生命周期 | 容量 | 用途 |
|------|------|----------|------|------|
| **L1** | 工作记忆 | 单次对话 | 50条 | 当前任务上下文 |
| **L2** | 短期记忆 | 7天 | 1000条 | 项目进行中 |
| **L3** | 中期记忆 | 90天 | 10000条 | 经验积累 |
| **L4** | 长期记忆 | 永久 | 无限制 | 知识沉淀 |

### 记忆流转规则

```
┌─────────────────────────────────────────────────────────┐
│                    记忆生命周期                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [用户输入] → L1工作记忆 → L2短期记忆 → L3中期记忆 → L4长期 │
│       ↓              ↓              ↓              ↓   │
│    即时使用        频繁访问       定期回顾         永久保存 │
│                                                          │
│  L1 → L2: 对话结束且重要性 > 0.5                          │
│  L2 → L3: 7天后且访问次数 > 3                            │
│  L3 → L4: 90天后且重要性 > 0.8                           │
│  L4: 知识沉淀，自动进入知识库                             │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 自动升级策略

```python
def should_promote(memory, target_level):
    if target_level == L2:
        return memory.importance > 0.5 and memory.session_ended
    elif target_level == L3:
        return memory.access_count > 3 and memory.age > timedelta(days=7)
    elif target_level == L4:
        return memory.importance > 0.8 and memory.age > timedelta(days=90)
    return False

def should_demote(memory):
    # 长时间未访问的记忆降级
    if memory.last_accessed < now() - timedelta(days=30):
        return L2  # 降级到L2
    if memory.last_accessed < now() - timedelta(days=7):
        return L1  # 降级到L1
    return None  # 保持当前级别
```

---

## 检索机制

### 混合检索策略

```python
def retrieve(query, context, top_k=10):
    # 1. 向量相似度检索
    vector_results = vector_search(
        query_vector=embed(query),
        collection="all",
        top_k=top_k * 2
    )

    # 2. 关键词过滤
    keyword_results = keyword_search(
        query=query,
        filters=context.get("filters", {})
    )

    # 3. 关联扩展 (利用知识图谱)
    related_ids = knowledge_graph.get_related(query)
    related_results = [get_memory(id) for id in related_ids]

    # 4. RRF融合排序
    fused = reciprocal_rank_fusion([
        vector_results,
        keyword_results,
        related_results
    ], weights=[0.5, 0.3, 0.2])

    # 5. 上下文过滤
    filtered = filter_by_context(fused, context)

    # 6. 去重和摘要
    return deduplicate_and_summarize(filtered, top_k)
```

### RRF融合公式

```
RRF Score = Σ (1 / (k + rank_i)) / weights[i]

其中:
- k = 60 (常数)
- rank_i = 在列表i中的排名
- weights = 各列表权重
```

### 上下文增强

```python
def enhance_with_context(memory_items, context):
    # 1. 时间衰减
    for item in memory_items:
        item.relevance *= time_decay(item.timestamp)

    # 2. 来源加权
    for item in memory_items:
        if item.source == context.current_agent:
            item.relevance *= 1.2

    # 3. 任务相关性
    for item in memory_items:
        if has_topic_overlap(item, context.task):
            item.relevance *= 1.5

    # 4. 重要性过滤
    return [i for i in memory_items if i.relevance > threshold]
```

### 检索参数配置

| 场景 | top_k | 相似度阈值 | RRF权重 |
|------|-------|------------|---------|
| **日常对话** | 5 | 0.7 | [0.6, 0.3, 0.1] |
| **深度分析** | 10 | 0.6 | [0.5, 0.3, 0.2] |
| **决策支持** | 15 | 0.5 | [0.4, 0.3, 0.3] |
| **知识查询** | 20 | 0.5 | [0.3, 0.4, 0.3] |

---

## 上下文管理

### 上下文结构

```yaml
Context:
  session_id: string           # 会话ID
  user_id: string              # 用户ID
  current_agent: string        # 当前Agent
  task:                         # 当前任务
    task_id: string
    type: string
    description: string
    status: enum
    parent_task_id: string
  working_memory:              # L1工作记忆
    items: MemoryItem[]
    max_items: 50
    ttl: duration
  recent_access:               # 最近访问历史
    memories: MemoryRef[]
    max_recent: 20
  filters:                     # 检索过滤器
    time_range: [start, end]
    agent_ids: string[]
    importance_min: float
    tags: string[]
```

### 上下文更新规则

```python
def update_context(context, event):
    if event.type == MEMORY_ACCESSED:
        # 添加到最近访问
        context.recent_access.add(event.memory_id)
        # 更新访问计数
        memory = get_memory(event.memory_id)
        memory.access_count += 1
        memory.last_accessed = now()

    elif event.type == MEMORY_CREATED:
        # 添加到工作记忆
        context.working_memory.add(event.memory)
        # 触发升级检查
        check_promotion(event.memory)

    elif event.type == TASK_COMPLETED:
        # 清理工作记忆
        context.working_memory.clear()
        # 评估是否需要保存
        for item in context.working_memory.items:
            if item.importance > 0.5:
                promote_to_short_term(item)
```

---

## Success Metrics

| 指标 | 目标值 | 测量方式 |
|------|--------|----------|
| 检索召回率 | ≥90% | 用户确认相关性 |
| 检索准确率 | ≥85% | Top-5相关性 |
| 平均检索延迟 | ≤100ms | P50延迟 |
| P99检索延迟 | ≤500ms | P99延迟 |
| 记忆完整性 | ≥99% | 写入后读取验证 |
| 存储利用率 | 60-80% | 容量监控 |
| 向量检索召回 | ≥95% | ANN测试集 |

---

## Critical Rules

### 必须遵守

1. **隐私保护**: 用户数据必须脱敏后存储
2. **容量管理**: 定期清理过期记忆
3. **一致性**: 读写操作必须原子
4. **可扩展**: 支持水平扩展
5. **备份恢复**: 定期备份，支持恢复

### 禁止行为

1. **禁止信息泄露**: 跨用户记忆不能混淆
2. **禁止无限膨胀**: 必须有容量上限和清理机制
3. **禁止脏数据**: 必须有数据校验
4. **禁止单点故障**: 必须有高可用设计

---

## References

### 技术选型

| 组件 | 选型 | 说明 |
|------|------|------|
| 向量数据库 | Pinecode/Milvus | 向量存储检索 |
| 键值存储 | Redis | L1工作记忆 |
| 图数据库 | Neo4j | 关系存储 |
| 搜索引擎 | Elasticsearch | 全文检索 |
| 嵌入模型 | text-embedding-3-small | 向量化 |

### 内部引用

- CyberTeam v3 上下文管理方案
- gstack Memory System

---

## Communication Style

### 记忆召回报告

```
[记忆召回报告]
├── 查询: 用户需求分析
├── 召回数量: 10条
├── 融合方式: RRF (向量0.5 + 关键词0.3 + 关系0.2)
├── Top-3结果:
│   ├── [L3] 用户调研报告 (相似度: 0.92)
│   ├── [L4] 需求分析方法论 (相似度: 0.88)
│   └── [L2] 上周需求讨论 (相似度: 0.85)
├── 上下文增强: +15% (时间衰减+任务相关)
└── 召回置信度: 0.89
```
