---
name: knowledge-graph
version: "1.0.0"
category: "core"
sub_category: "infrastructure"
tags: ["knowledge-graph", "rag", "reasoning", "infrastructure", "知识图谱"]
difficulty: "高级"
estimated_time: "35分钟"

# 元数据
dependencies: []
related_skills:
  - "plan-mode-enforcement"
  - "critical-systems-thinking"
---

# 知识图谱基础设施

## 概述

知识图谱是用于表示实体间关系的结构化数据模型，是实现高级 RAG（检索增强生成）和多跳推理的核心基础设施。

## 核心定义

### 什么是知识图谱？

**知识图谱 = 实体 (节点) + 关系 (边) + 属性**

```
┌─────────────────────────────────────────────────────────────┐
│                     知识图谱示例                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   [Glocalization] ──(核心概念)──> [品牌全球化]                │
│        │                             │                      │
│   (应用场景)                    (依赖关系)                    │
│        ▼                             ▼                      │
│   [市场进入] <────(需要)─── [用户洞察]                       │
│        │                             │                      │
│   (相关方法)                    (提供数据)                    │
│        ▼                             ▼                      │
│   [增长黑客] <───(优化)─── [数据分析]                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 知识图谱的价值

| 价值 | 描述 | 应用 |
|------|------|------|
| **关系发现** | 发现知识间的隐式关联 | 推荐相关知识 |
| **多跳推理** | 跨多个知识点推理 | 复杂问题解答 |
| **知识补全** | 基于关系推断缺失知识 | 完善知识体系 |
| **可视化** | 直观展示知识结构 | 学习路径规划 |

## 知识图谱架构

### 三层架构

```
┌─────────────────────────────────────────────────────────────┐
│                   应用层 (Application)                       │
│  - 知识查询 API                                             │
│  - 推理引擎                                                 │
│  - 可视化界面                                               │
├─────────────────────────────────────────────────────────────┤
│                   逻辑层 (Logical)                          │
│  - 本体模型 (Ontology)                                      │
│  - 推理规则                                                 │
│  - 知识图谱                                                 │
├─────────────────────────────────────────────────────────────┤
│                   数据层 (Data)                             │
│  - 向量数据库 (Chroma)                                      │
│  - 图数据库 (Neo4j)                                         │
│  - 文档存储 (JSON)                                          │
└─────────────────────────────────────────────────────────────┘
```

## 数据模型

### 节点类型

```yaml
KnowledgeNode:
  id: string                      # 唯一标识
  name: string                    # 知识点名称
  type: enum                      # 类型: concept|framework|method|case|tool
  category: string                # 所属领域
  description: string             # 描述
  definition: string              # 定义
  examples: list                  # 示例列表
  difficulty: enum                # 难度: beginner|intermediate|advanced
  estimated_time: string          # 学习时间

  # 元数据
  created_at: timestamp
  updated_at: timestamp
  version: string

  # 向量嵌入
  embedding: vector               # 语义向量

  # 统计
  usage_count: int                # 使用次数
  effectiveness_score: float      # 有效性评分
```

### 关系类型

```yaml
KnowledgeEdge:
  id: string
  source: string                  # 源节点ID
  target: string                  # 目标节点ID
  type: enum                      # 关系类型
  strength: float                 # 关系强度 (0-1)
  confidence: float               # 置信度 (0-1)

  # 关系类型定义
  RelationType:
    # 层次关系
    - PARENT_OF: "父概念"
    - CHILD_OF: "子概念"
    - PART_OF: "组成部分"

    # 关联关系
    - RELATED_TO: "相关"
    - SIMILAR_TO: "相似"
    - OPPOSITE_OF: "相反"

    # 依赖关系
    - DEPENDS_ON: "依赖"
    - PREREQUISITE_FOR: "前置知识"
    - ENHANCES: "增强"

    # 应用关系
    - APPLIES_TO: "应用于"
    - SOLVES: "解决"
    - IMPROVES: "改进"

    # 实例关系
    - EXAMPLE_OF: "示例"
    - CASE_STUDY_OF: "案例"

    # 流程关系
    - INPUT_FOR: "作为输入"
    - OUTPUT_OF: "作为输出"
    - NEXT_STEP: "下一步"
```

### 属性定义

```yaml
NodeAttributes:
  # 领域属性
  domain: string                  # 所属领域
  sub_domain: string              # 子领域
  tags: list                      # 标签

  # 学习属性
  difficulty_level: int           # 难度等级 (1-5)
  learning_order: int             # 学习顺序
  importance: float               # 重要性 (0-1)

  # 质量属性
  quality_score: float            # 质量评分
  completeness: float             # 完整性 (0-1)
  accuracy: float                 # 准确性 (0-1)

  # 使用属性
  popularity: int                 # 受欢迎程度
  last_used: timestamp            # 最后使用时间
  user_ratings: list              # 用户评分
```

## 推理机制

### 多跳推理

**推理链构建**:
```python
def multi_hop_reasoning(start_node, query, max_hops=3):
    """
    多跳推理：从起始节点开始，沿着关系链进行推理

    Args:
        start_node: 起始知识点
        query: 推理查询
        max_hops: 最大跳数

    Returns:
        推理链和结论
    """
    reasoning_chain = []
    current_nodes = [start_node]
    visited = set()

    for hop in range(max_hops):
        next_nodes = []
        for node in current_nodes:
            if node.id in visited:
                continue
            visited.add(node.id)

            # 获取相关节点
            related = get_related_nodes(node, relation_types, strength_threshold)
            reasoning_chain.append({
                'hop': hop + 1,
                'node': node,
                'related': related
            })
            next_nodes.extend(related)

        current_nodes = next_nodes
        if not current_nodes:
            break

    # 基于推理链生成结论
    conclusion = generate_conclusion(reasoning_chain, query)
    return reasoning_chain, conclusion
```

### 推理示例

**查询**: "本地化运营如何影响用户留存？"

```
推理链:
┌─────────────────────────────────────────────────────────────┐
│ Hop 1: [本地化运营]                                         │
│   ├─ RELATED_TO → [用户留存] (strength: 0.85)              │
│   ├─ REQUIRES → [用户洞察] (strength: 0.92)                │
│   └─ IMPROVES → [用户体验] (strength: 0.88)                │
├─────────────────────────────────────────────────────────────┤
│ Hop 2: [用户体验]                                          │
│   ├─ DIRECTLY_IMPACTS → [用户留存] (strength: 0.95)        │
│   ├─ DEPENDS_ON → [内容质量] (strength: 0.78)              │
│   └─ ENHANCED_BY → [个性化服务] (strength: 0.82)           │
├─────────────────────────────────────────────────────────────┤
│ Hop 3: [用户洞察]                                          │
│   ├─ GUIDES → [本地化策略] (strength: 0.90)                │
│   ├─ INFORMS → [内容创作] (strength: 0.85)                 │
│   └─ IMPROVES → [用户满意度] (strength: 0.87)              │
└─────────────────────────────────────────────────────────────┘

结论:
本地化运营通过提升用户体验来正向影响用户留存。
具体路径：
1. 本地化运营 → 用户体验 (提升 0.88)
2. 用户体验 → 用户留存 (影响 0.95)
3. 本地化运营需要用户洞察支持 (依赖 0.92)
```

## 知识图谱构建

### 构建流程

```
┌─────────────────────────────────────────────────────────────┐
│                    Phase 1: 数据收集                         │
│  - 从 Skill 文件提取知识点                                  │
│  - 解析元数据和标签                                         │
│  - 识别概念和关系                                           │
├─────────────────────────────────────────────────────────────┤
│                    Phase 2: 实体识别                         │
│  - 命名实体识别 (NER)                                       │
│  - 概念抽取                                                 │
│  - 实体链接和去重                                           │
├─────────────────────────────────────────────────────────────┤
│                    Phase 3: 关系抽取                         │
│  - 基于规则的关系抽取                                       │
│  - 基于学习的关系抽取                                       │
│  - 关系强度计算                                             │
├─────────────────────────────────────────────────────────────┤
│                    Phase 4: 图谱构建                         │
│  - 节点创建                                                 │
│  - 边关系建立                                               │
│  - 属性标注                                                 │
├─────────────────────────────────────────────────────────────┤
│                    Phase 5: 质量验证                         │
│  - 一致性检查                                               │
│  - 完整性验证                                               │
│  - 准确性审核                                               │
└─────────────────────────────────────────────────────────────┘
```

### 关系抽取方法

**基于规则**:
```yaml
rules:
  - 基于关键词: "相关技能"、"依赖"、"前置知识"
  - 基于结构: SKILL.md 中的 related_skills 字段
  - 基于分类: 同一 category/sub_category 的技能

  extraction:
    - keyword_match: "识别关系关键词"
    - field_parsing: "解析结构化字段"
    - categorization: "基于分类推断关系"
```

**基于学习**:
```yaml
ml_extraction:
  model: "关系分类模型"
  features:
    - "文本相似度"
    - "语义相似度"
    - "共现频率"
    - "上下文特征"

  training:
    - "标注训练数据"
    - "训练关系分类器"
    - "评估和优化"
```

## 知识检索

### 混合检索策略

```python
def hybrid_retrieval(query, top_k=10):
    """
    混合检索：结合关键词、向量和图谱检索

    Returns:
        融合的检索结果
    """
    # 1. 关键词检索
    keyword_results = keyword_search(query, top_k=top_k)

    # 2. 向量检索
    vector_results = vector_search(query, top_k=top_k)

    # 3. 图谱检索
    graph_results = graph_traversal(query, top_k=top_k)

    # 4. 结果融合
    fused_results = reciprocal_rank_fusion(
        [keyword_results, vector_results, graph_results],
        k=60
    )

    return fused_results[:top_k]
```

### 检索策略选择

| 查询类型 | 策略 | 权重 |
|---------|------|------|
| **精确查询** | 关键词为主 | 关键词: 60%, 向量: 30%, 图谱: 10% |
| **语义查询** | 向量为主 | 向量: 60%, 关键词: 20%, 图谱: 20% |
| **关联查询** | 图谱为主 | 图谱: 60%, 向量: 30%, 关键词: 10% |
| **复杂查询** | 均衡融合 | 关键词: 33%, 向量: 33%, 图谱: 34% |

## 知识推荐

### 推荐策略

```yaml
recommendation_strategies:
  context_aware:
    method: "基于当前上下文推荐"
    factors:
      - current_topic: "当前主题"
      - user_history: "用户历史"
      - session_context: "会话上下文"

  collaborative:
    method: "基于协同过滤推荐"
    factors:
      - similar_users: "相似用户"
      - popular_items: "热门内容"

  content_based:
    method: "基于内容相似度推荐"
    factors:
      - semantic_similarity: "语义相似度"
      - category_match: "类别匹配"

  knowledge_graph:
    method: "基于图谱关系推荐"
    factors:
      - direct_relations: "直接关系"
      - multi_hop_relations: "多跳关系"
      - relation_strength: "关系强度"
```

### 学习路径规划

```python
def generate_learning_path(target_knowledge, user_profile):
    """
    基于知识图谱生成学习路径

    Args:
        target_knowledge: 目标知识点
        user_profile: 用户画像（已掌握知识、学习偏好等）

    Returns:
        优化的学习路径
    """
    # 1. 获取前置知识
    prerequisites = get_prerequisites(target_knowledge)

    # 2. 过滤用户已掌握的知识
    to_learn = [p for p in prerequisites if p not in user_profile.mastered]

    # 3. 拓扑排序确定学习顺序
    learning_order = topological_sort(to_learn)

    # 4. 考虑用户偏好优化
    optimized_path = optimize_for_user(learning_order, user_profile)

    return optimized_path
```

## 质量管理

### 数据质量

```yaml
quality_metrics:
  completeness:
    definition: "知识覆盖的完整性"
    measure: "必填字段完整率"

  accuracy:
    definition: "知识的准确性"
    measure: "专家审核通过率"

  consistency:
    definition: "知识的一致性"
    measure: "冲突检测"

  freshness:
    definition: "知识的新鲜度"
    measure: "最后更新时间"

  relevance:
    definition: "知识的相关性"
    measure: "用户满意度评分"
```

### 更新机制

```yaml
update_triggers:
  time_based: "定期更新（月度/季度）"
  usage_based: "基于使用频率更新"
  feedback_based: "基于用户反馈更新"
  source_based: "源内容更新触发"

update_process:
  detect: "检测更新需求"
  validate: "验证更新内容"
  approve: "审核批准"
  deploy: "部署更新"
  monitor: "监控效果"
```

## 延伸阅读

- **相关技能**:
  - `plan-mode-enforcement`: 计划模式执行
  - `critical-systems-thinking`: 系统思维

## 检查清单

在构建知识图谱时，请确认：

- [ ] 定义了清晰的数据模型
- [ ] 确定了节点和关系类型
- [ ] 建立了抽取规则
- [ ] 实现了多跳推理
- [ ] 配置了混合检索
- [ ] 建立了质量管理机制
- [ ] 规划了更新维护流程
- [ ] 准备了监控和评估指标

---

*本技能定义知识图谱基础设施规范*
