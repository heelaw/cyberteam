# upstream - 记忆存储中台

## 直接上游

| 上游Agent | 关系 | 说明 |
|-----------|------|------|
| 所有Agent | 记忆写入 | 各Agent写入执行记忆 |
| CEO | 上下文获取 | 路由决策时获取历史上下文 |
| PM协调器 | 历史任务 | 获取历史任务状态 |

## 数据依赖

| 数据源 | 格式 | 刷新频率 | 说明 |
|--------|------|----------|------|
| Agent执行记录 | JSON | 实时 | 任务执行记忆 |
| 会话数据 | JSON | 每次会话 | 对话历史 |
| 文档库 | markdown | 按需 | 知识文档 |
| 外部知识 | API | 按需 | 外部知识补充 |

## 向量数据库上游

| 组件 | 说明 |
|------|------|
| Pinecode/Milvus | 向量存储检索 |
| Redis | L1工作记忆 |
| Neo4j | 关系存储 |
| Elasticsearch | 全文检索 |
| text-embedding-3-small | 向量化模型 |

## 嵌入模型上游

| 模型 | 维度 | 说明 |
|------|------|------|
| text-embedding-3-small | 1536 | OpenAI embedding |

## 索引策略上游

```yaml
indexes:
  conversations:
    primary: vector
    secondary: [session_id, agent_id, timestamp, tags]
    filterable: [importance, expires_at]
  documents:
    primary: vector
    secondary: [doc_type, category, source]
    filterable: [version, created_at]
  knowledge:
    primary: vector
    secondary: [knowledge_type, domain, verified]
    filterable: [confidence, contributor]
```

## 上游数据流

```
Agent执行 → 记忆写入 → 记忆中台
    ↓                   ↑
用户对话 → 会话数据 ────┘
    ↓
外部知识 → 知识补充 ────┘
    ↓
向量数据库 ← 嵌入模型
    │
记忆中台 → 向量检索 → RRF融合 → 上下文输出
```
