# interfaces - 记忆存储中台

## 输入接口

| 接口 | 类型 | 说明 |
|------|------|------|
| `action` | enum | 操作类型（store/retrieve/search/update/delete） |
| `memory_item` | MemoryItem | 要存储的记忆项（store时） |
| `query` | string | 检索查询（retrieve/search时） |
| `context` | Context | 检索上下文（可选） |
| `filters` | dict | 过滤条件（可选） |

## 输出接口

| 接口 | 类型 | 说明 |
|------|------|------|
| `result` | MemoryResult | 操作结果 |
| `retrieved_memories` | MemoryItem[] | 召回的记忆列表 |
| `confidence` | float | 召回置信度（0-1） |

## MemoryItem 结构

```yaml
MemoryItem:
  id: string              # 记忆唯一ID
  content: string         # 记忆内容
  vector: float[1536]    # 向量embedding
  metadata:
    session_id: string    # 会话ID
    agent_id: string     # 创建Agent
    timestamp: datetime   # 创建时间
    importance: float    # 重要性 (0-1)
    tags: string[]       # 标签
    access_count: int     # 访问次数
  level: enum            # L1(工作记忆)/L2(短期)/L3(中期)/L4(长期)
  expires_at: datetime   # TTL过期时间
```

## MemoryResult 结构

```yaml
MemoryResult:
  success: boolean        # 操作是否成功
  memory_id: string      # 记忆ID（store时）
  count: int             # 召回数量
  memories: MemoryItem[]  # 召回的记忆
  latency_ms: float      # 操作延迟
```

## 检索参数配置

| 场景 | top_k | 相似度阈值 | RRF权重 |
|------|-------|------------|---------|
| 日常对话 | 5 | 0.7 | [0.6, 0.3, 0.1] |
| 深度分析 | 10 | 0.6 | [0.5, 0.3, 0.2] |
| 决策支持 | 15 | 0.5 | [0.4, 0.3, 0.3] |
| 知识查询 | 20 | 0.5 | [0.3, 0.4, 0.3] |

## 四层记忆体系

| 层级 | 名称 | 生命周期 | 容量 | 用途 |
|------|------|----------|------|------|
| L1 | 工作记忆 | 单次对话 | 50条 | 当前任务上下文 |
| L2 | 短期记忆 | 7天 | 1000条 | 项目进行中 |
| L3 | 中期记忆 | 90天 | 10000条 | 经验积累 |
| L4 | 长期记忆 | 永久 | 无限制 | 知识沉淀 |

## 调用示例

```python
from agents.middle-tier.memory import MemoryHub

memory = MemoryHub()

# 存储记忆
result = memory.store(memory_item={
    "content": "用户反馈支付成功率低",
    "agent_id": "growth-bg",
    "importance": 0.8,
    "tags": ["支付", "用户反馈", "bug"]
})

# 检索记忆
result = memory.retrieve(
    query="支付成功率低的问题",
    context={"current_agent": "product-bg", "task_type": "需求分析"},
    top_k=5
)

# 返回示例
{
    "success": True,
    "count": 5,
    "memories": [
        {"id": "mem-001", "content": "用户反馈支付成功率低", "importance": 0.8, "level": "L2"},
        {"id": "mem-002", "content": "上周支付接口超时", "importance": 0.6, "level": "L2"}
    ],
    "confidence": 0.89,
    "latency_ms": 45
}
```
