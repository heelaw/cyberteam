# Cyber 数字军团知识图谱架构

## 架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                    Knowledge Graph Architecture                 │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    Query Layer                            │ │
│  │  - Knowledge Orchestrator Agent                          │ │
│  │  - Multi-hop Reasoning Engine                            │ │
│  │  - Recommendation Engine                                 │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    Service Layer                          │ │
│  │  - Knowledge Retrieval API                               │ │
│  │  - Relationship Traversal API                            │ │
│  │  - Learning Path API                                     │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    Storage Layer                          │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │ │
│  │  │  Vector DB  │  │   Graph DB  │  │  Document   │      │ │
│  │  │  (Chroma)   │  │  (Neo4j)    │  │   Store     │      │ │
│  │  │             │  │             │  │  (JSON)     │      │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 知识领域分类

### 全球化战略 (Globalization)
```
glocalization-core (Glocalization核心)
    ├── RELATED_TO → brand-localization (品牌本地化)
    ├── RELATED_TO → market-entry (市场进入)
    ├── REQUIRES → cross-culture (跨文化管理)
    └── APPLIES_TO → overseas-ops (海外运营)

brand-localization (品牌本地化)
    ├── PART_OF → glocalization-core
    ├── REQUIRES → user-insight (用户洞察)
    ├── GUIDED_BY → market-entry (市场进入策略)
    └── IMPROVES → user-retention (用户留存)

market-entry (市场进入)
    ├── PART_OF → glocalization-core
    ├── DEPENDS_ON → user-insight (市场洞察)
    ├── INFORMS → brand-localization (品牌策略)
    └── REQUIRES → localization (本地化运营)
```

### 产品运营 (Product-Ops)
```
user-insight (用户洞察)
    ├── FOUNDATION_FOR → product-framework (产品框架)
    ├── INPUT_TO → demand-analysis (需求分析)
    ├── GUIDES → growth-hacking (增长策略)
    └── ENHANCED_BY → data-decision (数据决策)

demand-analysis (需求分析)
    ├── DEPENDS_ON → user-insight
    ├── INFORMS → product-framework (产品设计)
    ├── PRIORITIZES → growth-hacking (增长重点)
    └── VALIDATED_BY → data-decision (数据验证)

product-framework (产品方法论)
    ├── BUILT_ON → user-insight
    ├── INFORMED_BY → demand-analysis
    ├── ENABLES → growth-hacking
    └── MEASURED_BY → data-decision

growth-hacking (增长黑客)
    ├── TARGETS → user-retention (用户留存)
    ├── LEVERAGES → data-decision
    ├── APPLIES → product-framework
    └── DRIVEN_BY → user-insight

data-decision (数据驱动决策)
    ├── SUPPORTS → product-framework
    ├── INFORMS → growth-hacking
    ├── VALIDATES → demand-analysis
    └── REQUIRES → user-insight (用户行为数据)
```

### 技能映射表

| 技能名称 | 类别 | 难度 | 预估时间 | 依赖技能 |
|---------|------|------|----------|----------|
| glocalization-core | globalization | 中级 | 20分钟 | - |
| brand-localization | globalization | 高级 | 30分钟 | glocalization-core, cross-culture |
| market-entry | globalization | 高级 | 30分钟 | glocalization-core, user-insight |
| user-insight | product-ops | 中级 | 25分钟 | - |
| demand-analysis | product-ops | 中级 | 25分钟 | user-insight |
| product-framework | product-ops | 中级 | 20分钟 | user-insight, demand-analysis |
| growth-hacking | product-ops | 中级 | 25分钟 | data-decision, user-insight |
| data-decision | product-ops | 中级 | 25分钟 | - |

## 推理模式示例

### 推理模式 1: 战略决策推理
```
Query: "如何制定品牌全球化战略？"

Reasoning Path:
[品牌全球化战略]
  ↓ (REQUIRES)
[Glocalization核心方法论]
  ↓ (INFORMS)
[市场进入策略选择]
  ↓ (GUIDES)
[品牌本地化执行]
  ↓ (VALIDATED_BY)
[用户洞察反馈]

结论: 品牌全球化战略需要从Glocalization方法论开始，
选择合适的市场进入模式，制定品牌本地化策略，
并通过持续的用户洞察来验证和优化。
```

### 推理模式 2: 产品优化推理
```
Query: "如何提升用户留存？"

Reasoning Path:
[用户留存问题]
  ↓ (ANALYZE_BY)
[用户洞察]
  ↓ (INFORMS)
[需求分析]
  ↓ (IMPROVES)
[产品体验]
  ↓ (ACCELERATED_BY)
[增长黑客策略]
  ↓ (MEASURED_BY)
[数据驱动决策]

结论: 提升用户留存需要从用户洞察出发，
通过需求分析优化产品体验，
配合增长黑客策略加速，
并用数据持续衡量和优化。
```

## 知识图谱API

### 获取相关知识
```python
GET /api/knowledge/related/{skill_id}
Response: {
  "skill_id": "glocalization-core",
  "related_skills": [
    {"id": "brand-localization", "relation": "RELATED_TO", "strength": 0.9},
    {"id": "market-entry", "relation": "RELATED_TO", "strength": 0.85}
  ]
}
```

### 获取学习路径
```python
GET /api/knowledge/path/{target_skill}
Response: {
  "target": "brand-localization",
  "path": [
    {"step": 1, "skill": "glocalization-core", "reason": "核心基础"},
    {"step": 2, "skill": "cross-culture", "reason": "文化理解"},
    {"step": 3, "skill": "brand-localization", "reason": "目标技能"}
  ]
}
```

### 多跳推理
```python
POST /api/knowledge/reason
Body: {
  "query": "本地化运营如何影响用户留存？",
  "max_hops": 3
}
Response: {
  "reasoning_chain": [...],
  "conclusion": "..."
}
```

## 维护和更新

### 定期维护任务
- [ ] 每月检查知识节点完整性
- [ ] 每季度更新关系强度
- [ ] 每半年重新计算节点向量
- [ ] 每年进行全面审核和优化

### 触发式更新任务
- 新增 Skill 时自动建立节点
- 更新 Skill 时更新元数据
- 用户反馈时调整关系强度
- 发现错误时立即修正
