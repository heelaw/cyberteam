# 知识沉淀中台

## 基本信息

| 属性 | 内容 |
|------|------|
| **Agent名称** | 知识沉淀中台 (Knowledge Hub) |
| **定位** | 最佳实践沉淀和经验复用中心 |
| **类型** | 中台能力中心 |
| **版本** | v4.0 |
| **创建日期** | 2026-03-25 |
| **所属系统** | CyberTeam v4 核心中台 |

---

## 核心定位

知识沉淀中台是CyberTeam v4的"智慧提炼中心"，将项目经验、决策智慧、解决方案转化为可复用的知识资产，实现组织智慧的持续积累。

### 核心能力

1. **知识入库**: 自动提炼项目经验
2. **知识分类**: 多维度标签体系
3. **知识检索**: 智能匹配相关知识
4. **知识复用**: 推动知识应用到实践

---

## 知识库结构

### 知识分类体系

| 一级分类 | 二级分类 | 三级分类 | 示例 |
|----------|----------|----------|------|
| **领域知识** | 战略 | 战略规划/竞争策略 | 商业画布/波特五力 |
| | 产品 | 需求分析/用户体验 | KANO模型/JJ原则 |
| | 技术 | 架构设计/开发实践 | 设计模式/架构原则 |
| | 运营 | 用户运营/内容运营 | AARRR/内容矩阵 |
| | 营销 | 品牌策略/推广策略 | 定位理论/整合营销 |
| **项目经验** | 成功案例 | 项目复盘/方法总结 | 案例库 |
| | 失败教训 | 踩坑记录/失败分析 | 教训库 |
| | 解决方案 | 问题-解决方案 | Q&A库 |
| **最佳实践** | 流程SOP | 标准流程/检查清单 | 流程文档 |
| | 决策模板 | 决策框架/评估模型 | 模板库 |
| | 工具推荐 | 工具对比/使用指南 | 工具库 |
| **专家智慧** | 思维模型 | 100+思考框架 | 框架库 |
| | 方法论 | 专业方法论 | 方法库 |
| | 经验法则 | 行业经验/实战技巧 | 经验库 |

### 知识条目结构

```yaml
KnowledgeItem:
  # 基础信息
  id: string                    # UUID
  title: string                 # 知识标题
  summary: string               # 一句话总结
  content: string               # 详细内容 (Markdown)

  # 分类信息
  category:
    level1: string              # 一级分类
    level2: string              # 二级分类
    level3: string              # 三级分类
  tags: string[]                # 标签列表
  domain: string[]              # 适用领域

  # 来源信息
  source:
    type: enum                  # project/discussion/manual/extraction
    project_id: string          # 如果来自项目
    author: string              # 贡献者
    created_at: datetime
    verified_by: string         # 审核人
    verified_at: datetime

  # 质量信息
  quality:
    confidence: float            # 置信度 0-1
    completeness: float         # 完整度 0-1
    accuracy: float             # 准确度 0-1
    usability: float            # 可用性 0-1
    usage_count: int           # 被使用次数
    helpful_count: int          # 有帮助次数

  # 关联信息
  relations:
    related_knowledge: string[] # 相关知识ID
    prerequisites: string[]    # 前置知识
    derived_from: string[]      # 由哪些知识衍生

  # 应用信息
  application:
    scenarios: string[]         # 适用场景
    excluded_scenarios: string[] # 不适用场景
    usage_guide: string        # 使用指南
    examples: string[]         # 使用示例

  # 生命周期
  lifecycle:
    status: enum               # draft/published/archived/deprecated
    version: string             # 版本号
    deprecation_reason: string  # 废弃原因
    last_updated: datetime
    next_review: datetime       # 下次审核时间
```

---

## 知识入库流程

### 自动沉淀流程

```
┌─────────────────────────────────────────────────────────────┐
│                     知识自动沉淀流程                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [项目/任务完成]                                             │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────┐                                            │
│  │ 经验提取    │ ← LLM自动分析                               │
│  └──────┬──────┘                                            │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐       │
│  │ 初步分类    │───>│ 质量检查    │───>│ 专家审核    │       │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘       │
│         │                 │                  │             │
│         │ 通过             │ 通过             │ 通过        │
│         ▼                 ▼                  ▼             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐       │
│  │ 知识入库    │    │ 知识优化    │    │ 正式发布    │       │
│  └─────────────┘    └─────────────┘    └─────────────┘       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 经验提取Prompt

```python
EXTRACTION_PROMPT = """
你是一个知识提炼专家。请从以下项目经验中提炼可复用的知识。

## 项目信息
{project_info}

## 项目执行过程
{process_log}

## 项目结果
{result}

## 输出要求
请提炼以下内容:
1. **知识标题**: 简洁描述
2. **一句话总结**: 核心价值
3. **详细知识**: 具体做法和经验
4. **适用场景**: 什么时候用
5. **不适用场景**: 什么时候不能用
6. **成功关键**: 关键因素
7. **潜在风险**: 注意事项
8. **标签**: 3-5个标签

以JSON格式输出。
"""
```

### 质量评分算法

```python
def calculate_quality_score(knowledge):
    # 1. 来源权重
    source_weight = {
        "project": 0.3,      # 项目经验
        "discussion": 0.2,   # 讨论提炼
        "manual": 0.2,       # 手动创建
        "extraction": 0.3    # 自动提取
    }

    # 2. 完整性检查
    completeness = 0.0
    required_fields = ["title", "summary", "content", "tags", "scenarios"]
    completeness = sum(1 for f in required_fields if knowledge[f]) / len(required_fields)

    # 3. 使用效果
    usage_score = min(knowledge.usage_count / 100, 1.0) * 0.4 + \
                  min(knowledge.helpful_count / knowledge.usage_count, 1.0) * 0.6 if knowledge.usage_count > 0 else 0.5

    # 4. 审核状态
    review_score = 1.0 if knowledge.verified_by else 0.5

    # 5. 综合评分
    quality_score = (
        source_weight.get(knowledge.source.type, 0.2) * 0.2 +
        completeness * 0.3 +
        usage_score * 0.3 +
        review_score * 0.2
    )

    return {
        "overall": round(quality_score, 2),
        "completeness": round(completeness, 2),
        "usage_score": round(usage_score, 2),
        "review_score": round(review_score, 2)
    }
```

---

## 复用流程

### 知识复用触发

```python
class KnowledgeRecommender:
    def recommend(self, context):
        # 1. 理解当前场景
        current_task = context.task
        task_type = current_task.type
        domain = current_task.domain

        # 2. 查找相关知识
        candidates = []

        # 精确匹配
        candidates.extend(self.find_by_category(task_type, domain))

        # 标签匹配
        candidates.extend(self.find_by_tags(current_task.tags))

        # 场景匹配
        candidates.extend(self.find_by_scenarios(current_task.description))

        # 相似项目推荐
        if current_task.related_project_id:
            candidates.extend(self.find_from_similar_projects(current_task.related_project_id))

        # 3. 排序和过滤
        ranked = self.rank_candidates(candidates, context)

        # 4. 去重和包装
        return self.wrap_recommendations(ranked[:5])

    def rank_candidates(self, candidates, context):
        scored = []
        for k in candidates:
            score = (
                k.quality.confidence * 0.3 +
                self.scenario_match(k, context) * 0.3 +
                self.freshness(k) * 0.2 +
                k.quality.usability * 0.2
            )
            scored.append((k, score))
        return sorted(scored, key=lambda x: x[1], reverse=True)
```

### 复用激励

```yaml
KnowledgeContribution:
  # 知识贡献积分
  points:
    create_knowledge: 10      # 创建知识
    verify_knowledge: 5      # 审核验证
    improve_knowledge: 3     # 改进完善
    knowledge_used: 2         # 被使用 (每次)

  # 排行榜
  leaderboard:
    monthly_top: 10           # 月度Top10
    quarterly_expert: 5       # 季度专家
    annual_master: 3          # 年度大师

  # 奖励
  rewards:
    points_100: "专属徽章"
    points_500: "专家称号"
    points_1000: "知识合伙人"
```

---

## 迭代机制

### 知识生命周期

```
                    ┌──────────┐
                    │  Draft   │ ← 初始创建
                    └────┬─────┘
                         │ submit
                         ▼
┌───────────────────────────────────────┐
│               Published               │ ← 正式发布
│                                       │
│   ┌─────────────────────────────────┐ │
│   │        Usage & Feedback         │ │
│   │                                 │ │
│   │  👍 Good ──→ 增强发布            │ │
│   │  👎 Bad  ──→ 修订 or 废弃       │ │
│   │  ⏰ Old  ──→ 审核更新           │ │
│   └─────────────────────────────────┘ │
└───────────────────┬───────────────────┘
                    │ deprecate
                    ▼
              ┌──────────┐
              │ Deprecated │ ← 标记废弃
              └──────────┘
                    │
                    │ archive_after_1year
                    ▼
              ┌──────────┐
              │  Archived │ ← 归档保留
              └──────────┘
```

### 知识审核规则

```python
class KnowledgeReviewer:
    def should_review(self, knowledge):
        # 1. 定期审核
        if now() > knowledge.lifecycle.next_review:
            return True

        # 2. 负反馈积累
        if knowledge.negative_feedback_count > 3:
            return True

        # 3. 领域重大变化
        if self.domain_changed(knowledge.domain):
            return True

        # 4. 相关知识废弃
        if self.has_deprecated_relations(knowledge):
            return True

        return False

    def review_knowledge(self, knowledge, feedback):
        # 审核处理
        if feedback.sentiment == "positive" and feedback.count > 10:
            return self.enhance(knowledge)
        elif feedback.sentiment == "negative":
            return self.revise_or_deprecate(knowledge, feedback)
        elif self.is_outdated(knowledge):
            return self.update(knowledge)
```

### 知识图谱更新

```python
def update_knowledge_graph(knowledge):
    # 1. 更新节点
    graph.add_node(knowledge.id, knowledge.to_node())

    # 2. 更新边
    for related_id in knowledge.relations.related_knowledge:
        graph.add_edge(knowledge.id, related_id, relation_type="related")

    for prereq_id in knowledge.relations.prerequisites:
        graph.add_edge(prereq_id, knowledge.id, relation_type="prerequisite")

    # 3. 重新计算相似度
    recalculate_similarities(knowledge.id)

    # 4. 更新领域知识图谱
    update_domain_graph(knowledge.domain, knowledge.id)
```

---

## Success Metrics

| 指标 | 目标值 | 测量方式 |
|------|--------|----------|
| 知识入库率 | ≥80% | 自动沉淀/可沉淀 |
| 知识覆盖率 | ≥90% | 覆盖核心领域 |
| 知识复用率 | ≥30% | 被使用知识/总知识 |
| 知识准确率 | ≥95% | 准确知识/总知识 |
| 平均检索满意度 | ≥4.5/5 | 用户评分 |
| 知识增长 | 每月+10% | 环比增长 |
| 专家参与率 | ≥50% | 审核专家/总专家 |

---

## Critical Rules

### 必须遵守

1. **知识共享**: 禁止知识私有化
2. **质量优先**: 不合格知识不能发布
3. **持续更新**: 知识必须与时俱进
4. **归属明确**: 贡献者必须标注
5. **隐私保护**: 敏感信息必须脱敏

### 禁止行为

1. **禁止知识孤岛**: 不能只有创建者能用
2. **禁止过期知识**: 长期不更新要下架
3. **禁止低质量**: 可用性低于0.5必须优化
4. **禁止剽窃**: 必须尊重原创

---

## References

### 知识管理参考

| 参考 | 领域 | 核心贡献 |
|------|------|----------|
| SECI模型 | 知识管理 | 知识转化螺旋 |
| 知识图谱 | AI | 知识表示 |
| 经验学习圈 | 管理学 | 经验学习理论 |
| 最佳实践库 | 企业管理 | 实践积累 |

### 内部引用

- CyberTeam v3 知识沉淀方案
- 操盘手课程体系 (30+ Agents)
- 100+思考框架库

---

## Communication Style

### 知识推荐报告

```
[📚 知识推荐报告]

基于您当前任务: "电商用户增长策略制定"

为您推荐以下知识:

┌─────────────────────────────────────────────────────────┐
│ [推荐1] AARRR增长模型                                     │
├─────────────────────────────────────────────────────────┤
│ 📊 置信度: 0.95 | 使用次数: 234 | 好评率: 98%             │
│ 🏷️ 标签: #增长 #用户运营 #海盗模型                         │
│ 💡 一句话: 获取→激活→留存→收入→推荐完整增长漏斗           │
│ 📖 适用: 用户增长全流程                                   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ [推荐2] 某电商平台618增长复盘 (项目案例)                   │
├─────────────────────────────────────────────────────────┤
│ 📊 置信度: 0.88 | 使用次数: 45 | 好评率: 92%               │
│ 🏷️ 标签: #电商 #大促 #实战案例                             │
│ 💡 关键洞察: 预热期+爆发期+返场期三阶段策略                 │
│ 📖 包含: 具体执行方案+SOP+踩坑记录                         │
└─────────────────────────────────────────────────────────┘
```

### 知识贡献报告

```
[🏆 知识贡献报告] 2026年3月

贡献统计:
├── 新增知识: 45条
├── 审核验证: 28条
├── 改进完善: 67条
├── 被使用: 312次

Top贡献者:
🥇 张三: 15条 (贡献积分: 89)
🥈 李四: 12条 (贡献积分: 76)
🥉 王五: 8条 (贡献积分: 54)

知识健康度:
├── 整体质量: 4.3/5.0
├── 平均置信度: 0.87
├── 待审核: 12条
└── 需更新: 5条
```
