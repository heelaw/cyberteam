# 专家Agent能力对比与推荐机制设计

**文档编号**: Q25
**创建日期**: 2026-03-20
**前置参考**: Q23-能力边界分析、Q24-能力评级体系

---

## 一、对比机制概述

### 1.1 设计目标

为思考天团的14个思维专家建立对比与推荐机制，帮助用户：
- 理解各专家的差异化能力
- 在多专家场景下做出选择
- 获得个性化的专家推荐

### 1.2 核心挑战

| 挑战 | 描述 |
|------|------|
| **能力重叠** | 多个专家可能处理相似问题，如Kahneman和SixHats都涉及决策 |
| **场景交叉** | 某些问题可被多个专家处理，需要优先级排序 |
| **用户意图模糊** | 用户描述的问题可能不明确需要哪个专家 |
| **组合推荐** | 复杂问题可能需要多个专家协同 |

---

## 二、对比维度体系

### 2.1 六大核心维度

基于Q24评级体系，定义对比维度：

| 维度 | 英文标识 | 说明 | 评分范围 |
|------|----------|------|----------|
| **适用场景** | Scenario | 问题类型匹配度 | 1-5 |
| **处理速度** | Speed | 平均分析耗时 | 1-5 |
| **输出深度** | Depth | 分析的深度和全面性 | 1-5 |
| **创新程度** | Innovation | 突破常规的能力 | 1-5 |
| **协作风格** | Collaboration | 与其他专家配合能力 | 1-5 |
| **风险意识** | Risk Awareness | 对潜在风险的敏感性 | 1-5 |

### 2.2 维度详细定义

#### 2.2.1 适用场景 (Scenario)

评估专家与问题类型的匹配程度：

| 评分 | 描述 |
|------|------|
| 5 | 完美匹配，专业领域问题 |
| 4 | 高度匹配，相关领域 |
| 3 | 中等匹配，边缘场景 |
| 2 | 低匹配，需要调整 |
| 1 | 不匹配，超出能力边界 |

#### 2.2.2 处理速度 (Speed)

评估分析效率：

| 评分 | 描述 | 典型时间 |
|------|------|----------|
| 5 | 即时响应 | < 30秒 |
| 4 | 快速分析 | 30秒-2分钟 |
| 3 | 标准分析 | 2-5分钟 |
| 2 | 深度分析 | 5-15分钟 |
| 1 | 全面推演 | > 15分钟 |

#### 2.2.3 输出深度 (Depth)

评估分析的深度和全面性：

| 评分 | 描述 |
|------|------|
| 5 | 系统级分析，多层嵌套 |
| 4 | 深度分析，多维度 |
| 3 | 标准分析，结构化 |
| 2 | 浅层分析，框架式 |
| 1 | 基础分析，点到为止 |

#### 2.2.4 创新程度 (Innovation)

评估突破常规的能力：

| 评分 | 描述 |
|------|------|
| 5 | 颠覆性创新，突破框架 |
| 4 | 突破性思路，跳出常规 |
| 3 | 适度创新，框架内优化 |
| 2 | 标准输出，遵循框架 |
| 1 | 保守输出，机械执行 |

#### 2.2.5 协作风格 (Collaboration)

评估与其他专家配合的能力：

| 评分 | 描述 |
|------|------|
| 5 | 主导型，可领导多专家协作 |
| 4 | 主动型，可与其他专家双向输出 |
| 3 | 配合型，能接受其他专家输入 |
| 2 | 独立型，单独使用效果最好 |
| 1 | 封闭型，不适合协作 |

#### 2.2.6 风险意识 (Risk Awareness)

对潜在风险的敏感性：

| 评分 | 描述 |
|------|------|
| 5 | 风险专家，擅长识别风险 |
| 4 | 风险敏感，主动提示风险 |
| 3 | 标准风险评估 |
| 2 | 风险意识一般 |
| 1 | 忽略风险，乐观导向 |

---

## 三、14个专家对比矩阵

### 3.1 对比数据表

| 专家 | 适用场景 | 处理速度 | 输出深度 | 创新程度 | 协作风格 | 风险意识 |
|------|----------|----------|----------|----------|----------|----------|
| **Kahneman** | 4 | 3 | 4 | 2 | 3 | 5 |
| **FirstPrinciple** | 4 | 2 | 5 | 5 | 3 | 2 |
| **SixHats** | 5 | 3 | 4 | 3 | 5 | 3 |
| **SWOTTows** | 5 | 4 | 4 | 2 | 3 | 4 |
| **FiveWhy** | 3 | 3 | 5 | 1 | 2 | 3 |
| **Goldlin** | 3 | 4 | 3 | 3 | 2 | 2 |
| **GROW** | 4 | 4 | 3 | 2 | 3 | 2 |
| **KISS** | 3 | 4 | 3 | 3 | 3 | 2 |
| **McKinsey** | 4 | 3 | 5 | 2 | 4 | 3 |
| **AIboard** | 3 | 4 | 3 | 3 | 2 | 2 |
| **ReverseThinking** | 3 | 3 | 4 | 5 | 3 | 5 |
| **FiveDimension** | 4 | 4 | 4 | 2 | 3 | 3 |
| **WBS** | 4 | 4 | 3 | 1 | 4 | 2 |
| **ManagerLeap** | 3 | 4 | 3 | 2 | 4 | 2 |

### 3.2 专家分类标签

| 分类 | 专家列表 | 核心特点 |
|------|----------|----------|
| **决策型** | Kahneman, FiveDimension | 选择纠结、风险评估 |
| **创新型** | FirstPrinciple, ReverseThinking | 突破常规、颠覆思维 |
| **分析型** | SixHats, McKinsey, SWOTTows | 多角度、结构化 |
| **诊断型** | FiveWhy, Goldlin | 根因挖掘、问题定义 |
| **执行型** | GROW, WBS, ManagerLeap | 目标落地、任务分解 |
| **简化型** | KISS | 复杂问题简化 |
| **趋势型** | AIboard | AI/科技趋势洞察 |

---

## 四、对比结果量化方法

### 4.1 综合得分计算

```
综合得分 = Σ(维度评分 × 维度权重)

默认权重配置：
- 适用场景: 25% (最重要，必须匹配)
- 处理速度: 15% (效率考量)
- 输出深度: 20% (质量保障)
- 创新程度: 15% (突破需求)
- 协作风格: 10% (组合需求)
- 风险意识: 15% (安全考量)
```

### 4.2 场景权重预设

不同场景下调整权重：

| 场景 | 适用场景 | 处理速度 | 输出深度 | 创新程度 | 协作风格 | 风险意识 |
|------|----------|----------|----------|----------|----------|----------|
| **快速决策** | 20% | 30% | 15% | 10% | 10% | 15% |
| **深度分析** | 20% | 10% | 30% | 15% | 10% | 15% |
| **创新突破** | 15% | 10% | 20% | 30% | 10% | 15% |
| **风险评估** | 20% | 15% | 15% | 10% | 10% | 30% |
| **团队协作** | 20% | 15% | 15% | 10% | 30% | 10% |

### 4.3 相似度计算

用于问题与专家的匹配度计算：

#### 4.3.1 关键词匹配法

```python
# 伪代码示例
def calculate_keyword_similarity(question, expert):
    # 提取问题关键词
    question_keywords = extract_keywords(question)

    # 获取专家擅长关键词
    expert_keywords = expert.specialized_keywords

    # 计算交集
    matching = question_keywords ∩ expert_keywords

    # Jaccard相似度
    similarity = len(matching) / len(question_keywords ∪ expert_keywords)

    return similarity
```

#### 4.3.2 向量相似度法

```python
# 伪代码示例
def calculate_vector_similarity(question, expert):
    # 问题向量化
    question_vector = embed_model.encode(question)

    # 专家能力向量化
    expert_vector = embed_model.encode(expert.capability_description)

    # 余弦相似度
    similarity = cosine_similarity(question_vector, expert_vector)

    return similarity
```

---

## 五、推荐理由生成机制

### 5.1 理由结构模板

推荐时自动生成结构化理由：

```
═══════════════════════════════════════════
      专家推荐报告
═══════════════════════════════════════════

【推荐专家】: [专家名称] ([级别])
【匹配度】: ★★★★☆ (85%)

【核心优势】
  ✓ [优势1]: [解释]
  ✓ [优势2]: [解释]
  ✓ [优势3]: [解释]

【与问题匹配度】
  • 适用场景: ★★★★☆ (4/5)
  • 输出深度: ★★★★☆ (4/5)
  • 创新程度: ★★★☆☆ (3/5)
  • 风险意识: ★★★★★ (5/5)

【推荐理由】
  [针对用户问题的具体解释]

【组合建议】
  建议配合: [专家B], [专家C]
  原因: [解释协同价值]
```

### 5.2 理由类型

| 理由类型 | 触发条件 | 示例 |
|----------|----------|------|
| **场景匹配** | 问题类型与专家核心能力直接对应 | "您的问题是关于决策选择，卡尼曼擅长..." |
| **深度满足** | 问题需要深度分析 | "这个问题需要深入根因，5Why更适合..." |
| **创新需求** | 问题涉及创新突破 | "您需要突破性方案，第一性原理..." |
| **风险警示** | 问题涉及风险评估 | "涉及风险评估，逆向思维可以..." |
| **效率优先** | 用户强调快速响应 | "您希望快速决策，SWOT分析更快..." |
| **协作增强** | 问题复杂需要多专家 | "建议配合六顶思考帽进行多角度..."

### 5.3 动态理由生成

```python
# 伪代码示例
def generate_recommendation_reason(question, expert, match_score):
    reasons = []

    # 场景匹配理由
    if expert.scenario_match_score > 0.8:
        reasons.append(f"您的{question.type}问题正是{expert.name}的专长")

    # 差异化优势
    if expert.risk_awareness >= 4:
        reasons.append(f"该问题涉及风险考量，{expert.name}风险意识强")

    # 创新需求匹配
    if question.requires_innovation and expert.innovation >= 4:
        reasons.append(f"需要创新思路，{expert.name}创新程度高")

    # 协作增强
    if question.complexity >= 4:
        reasons.append(f"建议{expert.name}与{get_best_collaborator(expert)}配合")

    return reasons
```

---

## 六、自动推荐算法

### 6.1 推荐流程

```
用户问题输入
      │
      ▼
问题特征提取 ─────────────┐
      │                    │
      ▼                    │
问题类型判断               │
      │                    │
      ▼                    │
关键词提取                 │
      │                    │
      ▼                    │
向量化处理 ────────────────┼──→ 多策略融合
      │                    │
      ▼                    │
专家候选列表生成           │
      │                    │
      ▼                    │
过滤与排序 ────────────────┘
      │
      ▼
推荐结果输出
      │
      ▼
理由生成
```

### 6.2 特征提取规则

#### 6.2.1 问题类型识别

| 关键词 | 问题类型 | 推荐专家 |
|--------|----------|----------|
| 选择、纠结、该选 | 决策选择 | Kahneman, FiveDimension |
| 风险、有什么风险 | 风险评估 | ReverseThinking, Kahneman |
| 为什么、根本原因 | 根因分析 | FiveWhy, Goldlin |
| 创新、突破、颠覆 | 创新突破 | FirstPrinciple, ReverseThinking |
| 目标、规划、发展 | 目标设定 | GROW, ManagerLeap |
| 分解、执行、落地 | 任务分解 | WBS, GROW |
| 简化、复杂、混乱 | 问题简化 | KISS, SixHats |
| 多角度、全面分析 | 多维分析 | SixHats, FiveDimension |
| 战略、竞争、优势 | 战略分析 | SWOTTows, McKinsey |
| 复盘、总结、反思 | 经验总结 | KISS, ManagerLeap |
| AI趋势、技术洞察 | 科技趋势 | AIboard |
| 为什么（动机） | 动机挖掘 | Goldlin |

#### 6.2.2 问题复杂度判断

| 特征 | 复杂度 |
|------|--------|
| 单一个问题 | 低 |
| 多个选项对比 | 中 |
| 涉及多个因素 | 中 |
| 跨领域问题 | 高 |
| 需要创新突破 | 高 |
| 长期战略规划 | 高 |

### 6.3 推荐算法实现

#### 6.3.1 基础推荐算法

```python
# 伪代码示例
def recommend_expert(question, experts):
    # 1. 提取问题特征
    question_type = classify_question_type(question)
    complexity = assess_complexity(question)
    keywords = extract_keywords(question)

    # 2. 计算每个专家的匹配度
    candidates = []
    for expert in experts:
        # 场景匹配分
        scenario_score = calculate_scenario_match(question_type, expert)

        # 关键词匹配分
        keyword_score = calculate_keyword_match(keywords, expert)

        # 复杂度适配分
        complexity_score = calculate_complexity_match(complexity, expert)

        # 综合得分
        total_score = (
            scenario_score * 0.4 +
            keyword_score * 0.3 +
            complexity_score * 0.3
        )

        candidates.append({
            'expert': expert,
            'score': total_score,
            'reason': generate_reason(question, expert, total_score)
        })

    # 3. 排序并返回Top-N
    candidates.sort(key=lambda x: x['score'], reverse=True)

    return candidates[:3]  # 返回前3名推荐
```

#### 6.3.2 场景示例推荐

**场景1: "如何提升DAU"**

```
问题分析:
- 类型: 目标设定 + 增长策略
- 复杂度: 中高
- 关键词: 提升、DAU、增长

推荐结果:
┌─────────────────────────────────────────┐
│ 1. Kahneman + GROW                      │
│    匹配度: 88%                           │
│    理由: 需要决策分析选择增长策略，GROW   │
│    帮助设定目标和路径                    │
├─────────────────────────────────────────┤
│ 2. FirstPrinciple                       │
│    匹配度: 82%                           │
│    理由: 需要突破性增长思路              │
├─────────────────────────────────────────┤
│ 3. SWOTTows                             │
│    匹配度: 78%                           │
│    理由: 可做竞争分析找增长机会          │
└─────────────────────────────────────────┘
```

**场景2: "有什么创新方案"**

```
问题分析:
- 类型: 创新突破
- 复杂度: 高
- 关键词: 创新、方案、突破

推荐结果:
┌─────────────────────────────────────────┐
│ 1. FirstPrinciple                       │
│    匹配度: 95%                           │
│    理由: 创新突破是第一性原理的核心能力  │
├─────────────────────────────────────────┤
│ 2. ReverseThinking                      │
│    匹配度: 88%                           │
│    理由: 逆向思维可发现隐藏创新机会      │
├─────────────────────────────────────────┤
│ 3. SixHats                              │
│    匹配度: 75%                           │
│    理由: 多角度思考可激发创新灵感        │
└─────────────────────────────────────────┘
```

**场景3: "有什么风险"**

```
问题分析:
- 类型: 风险评估
- 复杂度: 中
- 关键词: 风险、隐患、问题

推荐结果:
┌─────────────────────────────────────────┐
│ 1. ReverseThinking                      │
│    匹配度: 95%                           │
│    理由: 逆向思维是风险识别的专业工具    │
├─────────────────────────────────────────┤
│ 2. Kahneman                             │
│    匹配度: 88%                           │
│    理由: 卡尼曼擅长识别认知偏差和风险    │
├─────────────────────────────────────────┤
│ 3. SixHats                              │
│    匹配度: 72%                           │
│    理由: 黑帽视角专门用于风险分析        │
└─────────────────────────────────────────┘
```

### 6.4 组合推荐机制

#### 6.4.1 组合触发条件

| 条件 | 触发组合 |
|------|----------|
| 复杂问题 | 主专家 + SixHats（多角度） |
| 创新+风险 | FirstPrinciple + ReverseThinking |
| 战略+执行 | SWOTTows + GROW + WBS |
| 决策+风险 | Kahneman + ReverseThinking |
| 个人成长 | GROW + ManagerLeap |

#### 6.4.2 组合推荐示例

```
问题: "我想做一个创新产品，但担心有风险"

【推荐组合】: FirstPrinciple + ReverseThinking

【协同说明】:
  FirstPrinciple 负责:
    → 从本质重构产品思路
    → 突破现有品类限制
    → 找到颠覆性创新机会

  ReverseThinking 负责:
    → 从用户痛点倒推解决方案
    → 识别潜在风险和陷阱
    → 确保创新方向可行

【协作流程】:
  1. 先用第一性原理定义核心价值
  2. 再用逆向思维检验风险点
  3. 最后综合形成创新方案
```

---

## 七、对比与推荐数据存储

### 7.1 数据结构设计

```json
{
  "version": "1.0",
  "lastUpdated": "2026-03-20",
  "dimensions": {
    "scenario": {"name": "适用场景", "weight": 0.25},
    "speed": {"name": "处理速度", "weight": 0.15},
    "depth": {"name": "输出深度", "weight": 0.20},
    "innovation": {"name": "创新程度", "weight": 0.15},
    "collaboration": {"name": "协作风格", "weight": 0.10},
    "risk_awareness": {"name": "风险意识", "weight": 0.15}
  },
  "experts": {
    "kahneman": {
      "nameCN": "卡尼曼决策",
      "category": "决策型",
      "level": "L2",
      "scores": {
        "scenario": 4,
        "speed": 3,
        "depth": 4,
        "innovation": 2,
        "collaboration": 3,
        "risk_awareness": 5
      },
      "keywords": ["选择", "决策", "风险", "判断", "偏差"],
      "bestWith": ["SixHats", "ReverseThinking", "GROW"],
      "avoidWith": ["WBS"]
    },
    "first_principle": {
      "nameCN": "第一性原理",
      "category": "创新型",
      "level": "L3",
      "scores": {
        "scenario": 4,
        "speed": 2,
        "depth": 5,
        "innovation": 5,
        "collaboration": 3,
        "risk_awareness": 2
      },
      "keywords": ["创新", "突破", "颠覆", "本质", "重构"],
      "bestWith": ["ReverseThinking", "KISS"],
      "avoidWith": ["GROW", "WBS"]
    },
    "reverse_thinking": {
      "nameCN": "逆向思维",
      "category": "创新型",
      "level": "L3",
      "scores": {
        "scenario": 3,
        "speed": 3,
        "depth": 4,
        "innovation": 5,
        "collaboration": 3,
        "risk_awareness": 5
      },
      "keywords": ["风险", "倒推", "隐患", "问题", "避免"],
      "bestWith": ["FirstPrinciple", "Kahneman"],
      "avoidWith": ["GROW"]
    }
    // ... 其他专家
  },
  "questionPatterns": [
    {
      "pattern": "如何提升*",
      "type": "目标增长",
      "recommended": ["GROW", "Kahneman", "FirstPrinciple"],
      "weights": {"GROW": 0.4, "Kahneman": 0.3, "FirstPrinciple": 0.3}
    },
    {
      "pattern": "有什么风险",
      "type": "风险评估",
      "recommended": ["ReverseThinking", "Kahneman", "SixHats"],
      "weights": {"ReverseThinking": 0.5, "Kahneman": 0.3, "SixHats": 0.2}
    },
    {
      "pattern": "*创新*",
      "type": "创新突破",
      "recommended": ["FirstPrinciple", "ReverseThinking", "SixHats"],
      "weights": {"FirstPrinciple": 0.5, "ReverseThinking": 0.3, "SixHats": 0.2}
    }
  ]
}
```

### 7.2 存储位置

```
思考天团/
├── 01_系统配置/
│   ├── expert-comparison/
│   │   ├── comparison-matrix.json    # 对比矩阵
│   │   ├── recommendation-rules.json # 推荐规则
│   │   └── question-patterns.json    # 问题模式库
```

---

## 八、可视化展示

### 8.1 雷达图对比

为每个专家生成六维雷达图，直观展示能力差异：

```
        适用场景
            │
     5  ────┼────
        │   │   │
     4  ─┼───┼───┤
        │   │   │
     3  ─┼───┼───┤  ← Kahneman
        │   │   │
     2  ─┼───┼───┤
        │   │   │
     1  ────┼────
           │
  处理←──────────→创新
  速度            程度
```

### 8.2 对比表格展示

| 维度 | Kahneman | FirstPrinciple | ReverseThinking | SixHats |
|------|----------|----------------|-----------------|----------|
| 适用场景 | ★★★★☆ | ★★★★☆ | ★★★☆☆ | ★★★★★ |
| 处理速度 | ★★★☆☆ | ★★☆☆☆ | ★★★☆☆ | ★★★☆☆ |
| 输出深度 | ★★★★☆ | ★★★★★ | ★★★★☆ | ★★★★☆ |
| 创新程度 | ★★☆☆☆ | ★★★★★ | ★★★★★ | ★★★☆☆ |
| 协作风格 | ★★★☆☆ | ★★★☆☆ | ★★★☆☆ | ★★★★★ |
| 风险意识 | ★★★★★ | ★★☆☆☆ | ★★★★★ | ★★★☆☆ |

---

## 九、总结

### 9.1 核心设计要点

1. **六大对比维度**: 适用场景、处理速度、输出深度、创新程度、协作风格、风险意识
2. **量化评分体系**: 1-5分制，可配置权重
3. **多策略匹配**: 关键词匹配 + 向量相似度 + 规则引擎
4. **动态理由生成**: 基于问题特征生成个性化推荐理由
5. **组合推荐**: 支持多专家协同推荐

### 9.2 与Q24的关系

| Q24内容 | Q25扩展 |
|---------|---------|
| 6个能力评级维度 | 6个对比维度（名称略有不同，更面向用户） |
| 专家定级结果 | 专家对比矩阵（更细粒度） |
| 评级应用场景 | 自动推荐算法（ actionable） |

### 9.3 后续迭代

1. **实际使用反馈**: 收集推荐准确率数据
2. **模式库扩展**: 持续补充问题模式
3. **权重调优**: 根据用户满意度调整权重
4. **新专家接入**: 14个之外的专家如何融入

---

**文档状态**: 设计完成
**下一步**: 实现推荐算法代码
