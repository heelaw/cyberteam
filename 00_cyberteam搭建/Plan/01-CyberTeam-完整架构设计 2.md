# CyberTeam 完整架构设计

**版本**: v2.0
**日期**: 2026-03-23
**状态**: 设计中 → 待评审
**输出目录**: `/Users/cyberwiz/Documents/01_Project/02_Skill研发/cyberteam搭建/【项目组2】/`

---

## 一、项目概述

### 1.1 产品定位

**CyberTeam** — AI模拟公司协作系统

核心理念：**"一句话交代，整个团队干活"**

用户只需输入一个业务目标，AI模拟公司即可自动完成：目标理解 → 问题拆解 → 部门协作 → 执行交付。

### 1.2 核心创新

| 创新点 | 说明 |
|--------|------|
| **思维注入架构** | 100个思维专家作为CEO的思维工具，而非独立守门人 |
| **CEO中心化** | CEO负责接收意图、用思维专家拆解问题、分配给管理层 |
| **全员思维注入** | 所有Agent都具备逻辑思维能力，而非仅CEO |
| **自动触发机制** | 根据问题类型自动选择思维模型 |

### 1.3 与原PRD的关系

| 原PRD设计 | v2.0调整 |
|-----------|----------|
| 14位思维专家作为评估层 | 100个思维专家作为CEO思维工具 |
| 5轮辩论后通过才能进入下一步 | CEO自动选择思维模型拆解问题 |
| 思维专家独立运行 | 思维能力注入所有Agent |
| 固定的质量门禁(≥50分) | 动态质量标准，根据任务类型调整 |

---

## 二、系统架构

### 2.1 四层架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户层 (User)                              │
│                     一句话输入业务目标                             │
└─────────────────────────────┬───────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      CEO 层 (总指挥)                              │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              100个思维专家 (思维工具)                       │   │
│  │                                                          │   │
│  │  • 决策思维 (20个)  • 问题拆解 (25个)                     │   │
│  │  • 系统思考 (15个)  • 创新思维 (20个)                     │   │
│  │  • 风险思维 (10个)  • 战略思维 (10个)                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  职责：意图理解 → 思维拆解 → 问题定义 → 部门分配                 │
└─────────────────────────────┬───────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     管理层 (6个部门并行)                         │
│                                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │  产品部   │ │  运营部   │ │  设计部   │ │  开发部   │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
│  ┌──────────┐ ┌──────────┐                                  │
│  │  人力部   │ │  财务部   │                                  │
│  └──────────┘ └──────────┘                                  │
│                                                                 │
│  注入思维：所有Agent都具备逻辑思维能力                          │
└─────────────────────────────┬───────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     执行层 (任务编排)                             │
│                                                                 │
│  • paperclip: 工作流编排                                       │
│  • goal-driven: 长任务执行                                     │
│  • OpenViking: 上下文管理                                      │
│  • ClawTeam: Agent协调                                        │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 数据流

```
用户输入: "我想做一个用户增长方案"
        ↓
┌─────────────────────────────────────────────────────────────────┐
│                         CEO 处理                                 │
│                                                                 │
│  Step 1: 意图理解                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ • 01-kahneman: 识别认知偏差                                │ │
│  │ • 17-confirmation_bias: 检查确认偏误                       │ │
│  │ • 用户真实需求 vs 表面需求分析                              │ │
│  └─────────────────────────────────────────────────────────┘ │
│                              ↓                                  │
│  Step 2: 问题拆解                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ • 5W1H1Y: 全面定义问题                                    │ │
│  │ • 05-fivewhy: 追问根本原因                                 │ │
│  │ • 13-wbs: 任务分解                                        │ │
│  │ • 06-goldlin: 清晰表述问题                                 │ │
│  └─────────────────────────────────────────────────────────┘ │
│                              ↓                                  │
│  Step 3: 问题定义输出                                          │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ {                                                         │ │
│  │   "problem_statement": "用户增长",                        │ │
│  │   "context": "当前DAU 1000, 目标 10000",                 │ │
│  │   "constraints": "预算 10万, 3个月",                       │ │
│  │   "success_criteria": "DAU增长10倍",                     │ │
│  │   "sub_problems": ["拉新", "留存", "转化"]                │ │
│  │ }                                                         │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────┬───────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      部门并行讨论                                │
│                                                                 │
│  运营部 ←─ "拉新策略 + 转化漏斗"                                │
│  产品部 ←─ "产品功能 + 用户体验"                                 │
│  设计部 ←─ "品牌 + 交互设计"                                    │
│  开发部 ←─ "技术方案 + 数据埋点"                                 │
│  人力部 ←─ "团队配置 + 激励方案"                                │
│  财务部 ←─ "预算分配 + ROI分析"                                │
│                                                                 │
│  (每个Agent都注入基础思维能力)                                  │
└─────────────────────────────┬───────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       结果汇总输出                               │
│                                                                 │
│  {                                                             │
│    "summary": "综合方案",                                       │
│    "departments_output": { ... },                              │
│    "timeline": "3个月",                                        │
│    "budget": "10万",                                          │
│    "kpis": ["DAU 10000", "留存率 40%"]                        │
│  }                                                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 三、CEO Agent 详细设计

### 3.1 Agent定义

```yaml
ceo_agent:
  name: "CEO (Chief Executive Officer)"

  identity:
    - 我是CyberTeam的CEO，负责整个AI公司的运营
    - 我的核心能力是思维拆解，而非具体执行
    - 我用100个思维专家来分析和拆解问题
    - 我确保问题被清晰定义后再分配给部门

  core_tools:
    # 思维专家工具
    - thinking_experts: 100个思维专家
    - thinking_router: 自动触发路由
    - thinking_injector: 思维注入器

    # 协作工具
    - department_manager: 6个部门管理
    - task_dispatcher: 任务分配
    - progress_monitor: 进度监控
    - result_aggregator: 结果汇总

    # 研究工具
    - autoresearch: 自动研究
    - web_search: 网络搜索
    - knowledge_base: 知识库

  thinking_models:
    # 必用的基础思维
    always_use:
      - 01-kahneman: "任何决策前检查认知偏差"
      - 02-first_principle: "从物理事实出发"
      - 05-fivewhy: "追问5层根本原因"
      - 06-goldlin: "清晰定义问题是解决的一半"

    # 按类型触发的思维
    auto_trigger:
      problem_decomposition:
        - 13-wbs: "任务分解"
        - 07-grow: "目标导向"
        - 09-mckinsey: "麦肯锡框架"

      strategy:
        - 04-swot-tows: "SWOT分析"
        - 24-porters-five-forces: "波特五力"
        - 21-game-theory: "博弈论"

      innovation:
        - 03-six-hats: "六顶思考帽"
        - 11-reverse-thinking: "逆向思维"
        - 20-anti-fragile: "反脆弱"

      risk:
        - 15-opportunity-cost: "机会成本"
        - 16-sunk-cost: "沉没成本"
        - 22-pareto: "二八法则"

  input_format:
    type: "user_goal"
    fields:
      - goal: "用户的目标(一句话)"
      - context: "背景信息(可选)"
      - constraints: "约束条件(可选)"
      - deadline: "截止日期(可选)"

  output_format:
    type: "problem_definition"
    fields:
      - problem_statement: "清晰的问题描述"
      - context: "背景信息"
      - constraints: "约束条件"
      - success_criteria: "成功标准"
      - sub_problems: "拆解的子问题"
      - department_assignments: "部门分配"
      - timeline: "时间线"
      - kpis: "关键指标"
```

### 3.2 思维模型自动触发规则

```yaml
thinking_trigger_rules:
  # 规则1: 用户输入关键词触发
  keyword_based:
    "增长/用户/LTV/DAU" → [growth_expert, aarrr, funnel]
    "品牌/设计/UI/UX" → [design_thinking, six_hats, user_research]
    "技术/架构/系统" → [first_principle, systems_thinking, tech_debt]
    "团队/人/招聘" → [grow, kotter_change, motivation]
    "预算/成本/收益" → [roi, opportunity_cost, sunk_cost]
    "风险/安全/合规" → [second_order, anti_fragile, risk_matrix]

  # 规则2: 问题复杂度触发
  complexity_based:
    simple:  # 1-3个子问题
      min_models: 2
      max_models: 3
      default: [kahneman, first_principle]

    medium:  # 4-7个子问题
      min_models: 3
      max_models: 5
      default: [kahneman, first_principle, fivewhy, wbs]

    complex:  # 8+个子问题
      min_models: 5
      max_models: 10
      default: [kahneman, first_principle, fivewhy, wbs, swot, porter]

  # 规则3: 迭代优化触发
  iteration_based:
    first_iteration:
      models: [kahneman, first_principle, goldlin]
    refinement:
      models: [fivewhy, wbs, grow]
    validation:
      models: [swot, porter, pareto]
```

---

## 四、100个思维专家设计

### 4.1 分类总览

| 类别 | 数量 | 编号范围 | 核心作用 |
|------|------|----------|----------|
| **决策思维** | 20个 | 01-20 | 决策分析、偏差识别 |
| **问题拆解** | 25个 | 21-45 | 问题定义、任务分解 |
| **系统思考** | 15个 | 46-60 | 系统分析、二阶思维 |
| **创新思维** | 20个 | 61-80 | 设计思维、创意生成 |
| **风险思维** | 10个 | 81-90 | 风险管理、机会成本 |
| **战略思维** | 10个 | 91-100 | 竞争战略、行业分析 |

### 4.2 详细清单

```yaml
thinking_experts:
  # ==================== 决策思维 (01-20) ====================
  01:
    id: "kahneman"
    name: "卡尼曼"
    category: "decision"
    trigger_keywords: ["决策", "判断", "偏差", "风险"]
    capability: "识别认知偏差和噪声，规避决策陷阱"
    prompt_template: |
      用卡尼曼的决策框架分析：
      - 锚定效应：初始信息如何影响判断？
      - 损失厌恶：用户对损失的敏感度？
      - 可得性启发：是否被最近事件过度影响？

  02:
    id: "first_principle"
    name: "第一性原理"
    category: "decision"
    trigger_keywords: ["本质", "基础", "重新", "根本"]
    capability: "从物理事实出发，不受类比思维束缚"
    prompt_template: |
      用第一性原理分析：
      - 这个问题的最基本事实是什么？
      - 能否用物理/数学证明？
      - 排除类比，从零开始推理？

  03:
    id: "six_hats"
    name: "六顶思考帽"
    category: "decision"
    trigger_keywords: ["分析", "全面", "多角度", "讨论"]
    capability: "系统化多维度思考，避免思维混乱"
    prompt_template: |
      用六顶思考帽分析：
      白帽：事实和数据
      红帽：情感和直觉
      黑帽：风险和困难
      黄帽：价值和收益
      绿帽：创意和可能
      蓝帽：流程和控制

  04:
    id: "swot_tows"
    name: "SWOT+TOWS"
    category: "decision"
    trigger_keywords: ["战略", "优势", "劣势", "机会"]
    capability: "全景战略分析，生成匹配战略"
    prompt_template: |
      SWOT分析后生成TOWS矩阵：
      - S+O: 进攻战略
      - S+T: 防御战略
      - W+O: 转型战略
      - W+T: 收缩战略

  05:
    id: "fivewhy"
    name: "5Why分析"
    category: "decision"
    trigger_keywords: ["原因", "为什么", "根因", "分析"]
    capability: "层层追问，直达问题根本原因"
    prompt_template: |
      用5Why追问根本原因：
      Why1: ...
      Why2: ...
      Why3: ...
      Why4: ...
      Why5: [根本原因]

  06:
    id: "goldlin"
    name: "吉德林法则"
    category: "decision"
    trigger_keywords: ["问题定义", "清晰", "表述"]
    capability: "清晰定义问题，问题已解决一半"
    prompt_template: |
      用吉德林法则清晰定义问题：
      - 现状是什么？
      - 目标是什么？
      - 差距在哪里？
      - 问题的边界是什么？

  07:
    id: "grow"
    name: "GROW模型"
    category: "decision"
    trigger_keywords: ["目标", "成长", "路径", "计划"]
    capability: "目标导向的教练式引导"
    prompt_template: |
      GROW模型分析：
      G: Goal - 目标是什么？
      R: Reality - 现状是什么？
      O: Options - 有哪些选择？
      W: Will - 行动计划是什么？

  # ==================== 问题拆解 (21-45) ====================
  21:
    id: "5w1h1y"
    name: "5W1H1Y"
    category: "problem"
    trigger_keywords: ["全面", "定义", "分析"]
    capability: "七问分析法，全面定义问题"
    prompt_template: |
      5W1H1Y分析：
      What: 做什么？
      Why: 为什么做？
      Who: 谁来做？
      When: 何时做？
      Where: 何地做？
      How: 如何做？
      Yes: 如何确认成功？

  22:
    id: "mece"
    name: "MECE原则"
    category: "problem"
    trigger_keywords: ["拆解", "分类", "结构"]
    capability: "相互独立，完全穷尽"
    prompt_template: |
      MECE拆解检查：
      - 各部分是否相互独立？
      - 所有部分是否完全穷尽？
      - 有没有遗漏或重叠？

  23:
    id: "scqa"
    name: "SCQA框架"
    category: "problem"
    trigger_keywords: ["故事", "叙述", "情境"]
    capability: "情境-冲突-问题-答案结构"
    prompt_template: |
      SCQA结构化叙述：
      S: Situation - 情境描述
      C: Complication - 冲突/挑战
      Q: Question - 核心问题
      A: Answer - 解决方案

  24:
    id: "wbs"
    name: "WBS任务分解"
    category: "problem"
    trigger_keywords: ["分解", "任务", "工作"]
    capability: "将目标拆解为可执行的任务清单"
    prompt_template: |
      WBS分解：
      - 主要交付物
      - 子交付物
      - 工作包
      - 任务清单

  # ==================== 系统思考 (46-60) ====================
  46:
    id: "systems_thinking"
    name: "系统思考"
    category: "systems"
    trigger_keywords: ["系统", "反馈", "循环"]
    capability: "理解系统行为和反馈循环"
    prompt_template: |
      系统思考分析：
      - 系统的边界是什么？
      - 关键要素有哪些？
      - 反馈循环是什么？
      - 增强回路和调节回路？

  47:
    id: "second_order"
    name: "二阶思维"
    category: "systems"
    trigger_keywords: ["长期", "后果", "未来"]
    capability: "考虑行动的二阶和三阶后果"
    prompt_template: |
      二阶思维分析：
      - 一阶后果是什么？
      - 二阶后果是什么？
      - 三阶后果是什么？
      - 如何避免意外后果？

  # ==================== 创新思维 (61-80) ====================
  61:
    id: "design_thinking"
    name: "设计思维"
    category: "innovation"
    trigger_keywords: ["创新", "用户", "原型"]
    capability: "以用户为中心的创新方法"
    prompt_template: |
      设计思维流程：
      共情 → 定义 → 构思 → 原型 → 测试

  62:
    id: "reverse_thinking"
    name: "逆向思维"
    category: "innovation"
    trigger_keywords: ["反向", "逆向", "颠覆"]
    capability: "由果推因，从终局回望"
    prompt_template: |
      逆向思维分析：
      - 最终目标是什么？
      - 倒推需要的步骤？
      - 哪些是传统做法可以颠覆的？
      - "如果不这样做会怎样？"

  # ==================== 风险思维 (81-90) ====================
  81:
    id: "opportunity_cost"
    name: "机会成本"
    category: "risk"
    trigger_keywords: ["选择", "成本", "权衡"]
    capability: "评估替代方案的机会成本"
    prompt_template: |
      机会成本分析：
      - 如果做A，放弃B和C的收益是多少？
      - 最佳替代方案是什么？
      - 如何最大化机会成本？

  82:
    id: "sunk_cost"
    name: "沉没成本"
    category: "risk"
    trigger_keywords: ["历史", "投入", "退出"]
    capability: "识别沉没成本，避免错误坚持"
    prompt_template: |
      沉没成本检查：
      - 有哪些历史投入已经无法回收？
      - 这些投入是否影响了当前决策？
      - 如果从零开始，会怎么选？

  # ==================== 战略思维 (91-100) ====================
  91:
    id: "porters_five_forces"
    name: "波特五力"
    category: "strategy"
    trigger_keywords: ["竞争", "行业", "壁垒"]
    capability: "行业竞争结构分析，护城河识别"
    prompt_template: |
      波特五力分析：
      1. 现有竞争者
      2. 新进入者威胁
      3. 替代品威胁
      4. 供应商议价能力
      5. 买家议价能力

  92:
    id: "game_theory"
    name: "博弈论"
    category: "strategy"
    trigger_keywords: ["竞争", "合作", "策略"]
    capability: "分析竞争对手的策略互动"
    prompt_template: |
      博弈论分析：
      - 参与方有哪些？
      - 各方的最佳策略是什么？
      - 是否存在纳什均衡？
      - 如何实现共赢？
```

---

## 五、部门Agent设计

### 5.1 基础思维注入

```yaml
all_departments:
  # 所有部门Agent必须具备的基础思维
  base_thinking:
    mandatory:
      - 01-kahneman: "认知偏差检查"
      - 02-first_principle: "第一性原理"
      - 05-fivewhy: "追问根本原因"
      - 21-5w1h1y: "全面定义"
      - 22-mece: "结构拆解"
      - 06-goldlin: "清晰表述"

    optional_by_context:
      - risk: [opportunity_cost, sunk_cost, risk_matrix]
      - strategy: [swot, porter, game_theory]
      - innovation: [design_thinking, reverse_thinking, six_hats]
```

### 5.2 部门详细定义

```yaml
departments:
  # ==================== 产品部 ====================
  product:
    name: "产品部"
    prefix: "product_"
    color: "#FF6B6B"

    mission: "以用户为中心，设计有价值的产品"

    capabilities:
      - 用户研究
      - 需求分析
      - 产品设计
      - PRD撰写
      - 数据分析
      - 竞品分析

    thinking_models:
      base: [user_research, pain_point, mvp, aarrr, funnel]
      analysis: [fivewhy, swot, porter]
      design: [design_thinking, jobs_to_be_done]

    output_format:
      required:
        - 产品路线图
        - PRD文档
        - 用户故事
        - 优先级矩阵
      optional:
        - 竞品分析报告
        - 用户调研报告
        - 数据分析看板

    examples:
      - "设计一个用户注册流程"
      - "分析我们的用户留存问题"
      - "规划Q2产品路线图"

  # ==================== 运营部 ====================
  operations:
    name: "运营部"
    prefix: "ops_"
    color: "#4ECDC4"

    mission: "驱动用户增长，提升运营效率"

    capabilities:
      - 用户增长
      - 活动策划
      - 数据分析
      - 社群运营
      - 内容运营
      - 渠道运营

    thinking_models:
      base: [aarrr, funnel, growth_hacking, seo]
      analysis: [fivewhy, pareto, cohort]
      strategy: [swot, game_theory, competitive]

    output_format:
      required:
        - 增长方案
        - 活动策划
        - 数据报表
        - 运营SOP
      optional:
        - 用户画像
        - 渠道分析
        - 竞品运营策略

    examples:
      - "制定用户拉新方案"
      - "策划618促销活动"
      - "分析转化漏斗"

  # ==================== 设计部 ====================
  design:
    name: "设计部"
    prefix: "design_"
    color: "#9B59B6"

    mission: "创造优秀的用户体验和品牌形象"

    capabilities:
      - UI设计
      - UX研究
      - 品牌设计
      - 交互设计
      - 设计规范
      - 用户测试

    thinking_models:
      base: [design_thinking, gestalt, accessibility]
      research: [user_research, usability_testing, ab_testing]
      brand: [color_psychology, typography, layout]

    output_format:
      required:
        - 设计稿
        - 设计规范
        - 交互方案
        - 组件库
      optional:
        - 用户测试报告
        - 品牌手册
        - 竞品设计分析

    examples:
      - "设计新的首页"
      - "制定设计规范"
      - "优化用户注册流程的UX"

  # ==================== 开发部 ====================
  engineering:
    name: "开发部"
    prefix: "eng_"
    color: "#3498DB"

    mission: "构建可靠、高效、可扩展的技术系统"

    capabilities:
      - 系统架构
      - 技术选型
      - 代码实现
      - 测试策略
      - 运维部署
      - 性能优化

    thinking_models:
      base: [first_principle, systems_thinking, dry, solid]
      architecture: [microservices, clean_architecture, scalability]
      quality: [tdd, code_review, testing_pyramid]

    output_format:
      required:
        - 技术方案
        - 系统架构图
        - API文档
        - 代码实现
      optional:
        - 性能报告
        - 运维手册
        - 技术选型报告

    examples:
      - "设计用户系统的架构"
      - "优化系统性能"
      - "制定技术选型方案"

  # ==================== 人力部 ====================
  hr:
    name: "人力部"
    prefix: "hr_"
    color: "#F39C12"

    mission: "打造高效、有战斗力的团队"

    capabilities:
      - 招聘方案
      - 绩效管理
      - 团队激励
      - 文化建设
      - 培训发展
      - 组织设计

    thinking_models:
      base: [grow, kotter_change, mckinsey_7s]
      recruitment: [competency, culture_fit, interview_design]
      motivation: [intrinsic_motivation, okr, kpi]

    output_format:
      required:
        - 招聘方案
        - 绩效方案
        - 激励计划
        - 组织架构
      optional:
        - 培训计划
        - 文化建设方案
        - 团队诊断报告

    examples:
      - "制定招聘计划"
      - "设计绩效方案"
      - "解决团队沟通问题"

  # ==================== 财务部 ====================
  finance:
    name: "财务部"
    prefix: "finance_"
    color: "#27AE60"

    mission: "确保财务健康，优化资源配置"

    capabilities:
      - 预算规划
      - 成本控制
      - 投资分析
      - 财务建模
      - 风险评估
      - 报表分析

    thinking_models:
      base: [roi, npv, payback_period, sensitivity]
      analysis: [opportunity_cost, sunk_cost, break_even]
      risk: [value_at_risk, monte_carlo, scenario_analysis]

    output_format:
      required:
        - 预算方案
        - 成本分析
        - ROI计算
        - 财务预测
      optional:
        - 投资分析报告
        - 风险评估报告
        - 现金流预测

    examples:
      - "制定年度预算"
      - "评估新项目ROI"
      - "分析成本结构"
```

---

## 六、GitHub仓库集成方案

### 6.1 仓库映射

| # | 仓库 | 功能 | 集成层级 | 集成方式 |
|---|------|------|----------|----------|
| 1 | ClawTeam | Agent协调框架 | **底层框架** | 直接使用tmux会话、spawn、消息传递 |
| 2 | agency-agents | 多Agent协作模板 | **部门模板** | 复制agents到~/.claude/agents/ |
| 3 | agency-agents-zh | 中文版Agent | **本地化** | 中文提示词，本土化案例 |
| 4 | autoresearch | 自动研究能力 | **CEO工具** | 思维专家的研究后端 |
| 5 | everything-claude-code | Claude Code优化 | **性能层** | hooks、commands、instincts |
| 6 | goal-driven | 目标驱动执行 | **执行模式** | 长任务自动续跑 |
| 7 | gstack | 虚拟工程团队 | **工程命令** | 20+ slash commands |
| 8 | OpenViking | 上下文数据库 | **记忆系统** | 跨会话上下文管理 |
| 9 | paperclip | 工作流编排 | **任务编排** | 多步骤任务自动化 |
| 10 | pua | 激励模式 | **能动性驱动** | 压力升级，防止放弃 |
| 11 | superpowers | 超能力集 | **能力扩展** | 增强各Agent能力 |

### 6.2 集成架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      CyberTeam 用户层                            │
└─────────────────────────────┬───────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      CEO 层                                       │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 100个思维专家 ←─ OpenViking (上下文管理)              │  │
│  │              ←─ autoresearch (自动研究)                 │  │
│  │              ←─ everything-claude-code (性能优化)       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ pua (激励模式) ← 自动触发，保持CEO高能动性              │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      管理层                                       │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 6个部门Agent ←─ agency-agents (模板)                   │  │
│  │              ←─ agency-agents-zh (本地化)              │  │
│  │              ←─ gstack (工程命令)                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ superpowers (能力扩展) ← 按需调用                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      执行层                                       │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ paperclip ←─ 工作流编排，多步骤任务                      │  │
│  │ goal-driven ←─ 长任务自动续跑                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ ClawTeam ←─ 底层框架，Agent spawn，消息传递             │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 6.3 文件结构

```
~/.claude/
├── CLAUDE.md                    # 全局配置 (CyberTeam入口)
├── agents/                      # 所有Agent定义
│   ├── ceo.md                  # CEO Agent
│   ├── thinking-01-kahneman.md
│   ├── thinking-02-first_principle.md
│   ├── ...
│   ├── thinking-100-spiral_dynamics.md
│   ├── product_agent.md
│   ├── ops_agent.md
│   ├── design_agent.md
│   ├── eng_agent.md
│   ├── hr_agent.md
│   ├── finance_agent.md
│   └── ... (原有104个agents保留)
├── skills/                      # Skills
│   ├── gstack/                # gstack (20+ skills)
│   ├── pua/                    # pua (激励模式)
│   ├── paperclip/             # paperclip (工作流编排)
│   ├── goal-driven/            # goal-driven (目标驱动)
│   └── ... (原有skills保留)
└── plugins/                    # Plugins
    └── clawteam/              # ClawTeam配置
```

---

## 七、接口定义

### 7.1 用户输入接口

```json
// 用户输入格式
{
  "type": "user_goal",
  "content": "我想做一个用户增长方案",
  "context": {
    "current_dau": 1000,
    "target_dau": 10000,
    "budget": 100000,
    "timeline": "3个月"
  },
  "constraints": {
    "max_team_size": 5,
    "tech_stack": ["React", "Node.js"]
  },
  "metadata": {
    "user_id": "user_123",
    "timestamp": "2026-03-23T17:00:00Z"
  }
}
```

### 7.2 CEO输出接口

```json
// CEO问题定义输出
{
  "type": "problem_definition",
  "problem_statement": "3个月内实现DAU从1000增长到10000",
  "context": {
    "current_dau": 1000,
    "market": "中小企业SaaS",
    "competitors": ["竞品A", "竞品B"]
  },
  "constraints": {
    "budget": 100000,
    "timeline": "3个月",
    "team_size": 5
  },
  "success_criteria": {
    "primary": "DAU >= 10000",
    "secondary": ["留存率 >= 40%", "获客成本 <= 10元"]
  },
  "sub_problems": [
    {
      "id": "sub_1",
      "name": "用户拉新",
      "owner": "ops",
      "description": "低成本获取新用户"
    },
    {
      "id": "sub_2",
      "name": "用户留存",
      "owner": "product",
      "description": "提升产品粘性"
    },
    {
      "id": "sub_3",
      "name": "转化优化",
      "owner": "design",
      "description": "优化注册和激活流程"
    }
  ],
  "department_assignments": {
    "ops": ["sub_1"],
    "product": ["sub_2"],
    "design": ["sub_3"],
    "eng": ["all"],
    "hr": ["support"],
    "finance": ["budget_review"]
  },
  "timeline": {
    "phase_1": {"weeks": "1-2", "goal": "方案确定"},
    "phase_2": {"weeks": "3-8", "goal": "执行迭代"},
    "phase_3": {"weeks": "9-12", "goal": "优化放量"}
  },
  "kpis": [
    {"name": "DAU", "target": 10000, "baseline": 1000},
    {"name": "留存率", "target": "40%", "baseline": "20%"},
    {"name": "获客成本", "target": "10元", "baseline": "50元"}
  ],
  "thinking_models_used": [
    "01-kahneman",
    "02-first_principle",
    "05-fivewhy",
    "21-5w1h1y",
    "22-mece",
    "growth_expert",
    "aarrr"
  ]
}
```

### 7.3 部门输出接口

```json
// 部门输出格式
{
  "type": "department_output",
  "department": "ops",
  "task_id": "sub_1",
  "status": "completed",
  "content": {
    "title": "用户拉新方案",
    "executive_summary": "...",
    "detailed_plan": [
      {
        "step": 1,
        "action": "SEO优化",
        "expected_impact": "+200 DAU/周",
        "cost": 5000,
        "timeline": "2周"
      }
    ],
    "channels": ["SEO", "内容营销", "社交媒体"],
    "budget_allocation": {
      "SEO": 30000,
      "内容营销": 20000,
      "社交媒体": 20000,
      "预留": 30000
    }
  },
  "artifacts": [
    {"type": "document", "name": "拉新方案.md"},
    {"type": "spreadsheet", "name": "预算表.xlsx"}
  ],
  "metrics": {
    "expected_dau_increase": 3000,
    "expected_cac": 8,
    "roi": "3.0x"
  },
  "risks": [
    {"risk": "SEO见效慢", "mitigation": "配合付费渠道"},
    {"risk": "内容产能不足", "mitigation": "外包部分内容"}
  ],
  "next_steps": [
    "启动SEO技术优化",
    "招聘内容运营",
    "对接社交媒体KOL"
  ]
}
```

---

## 八、可行的验证方案

### 8.1 架构可行性检查清单

| 检查项 | 标准 | 状态 |
|--------|------|------|
| **接口兼容性** | 所有Agent使用统一接口 | ✅ |
| **工具可达性** | 所有Agent都能访问必要工具 | ✅ |
| **数据流完整性** | 输入→处理→输出完整闭环 | ✅ |
| **错误处理** | 有降级和重试机制 | ✅ |
| **可扩展性** | 新增Agent/思维专家不影响现有架构 | ✅ |

### 8.2 验证测试用例

```yaml
test_scenarios:
  # 场景1: 简单任务
  simple_task:
    input: "帮我写一段代码"
    expected: "30秒内输出代码"
    validation:
      - CEO调用2-3个思维专家
      - 部门讨论简化或跳过
      - 总耗时 < 1分钟

  # 场景2: 中等复杂度
  medium_task:
    input: "设计一个用户注册流程"
    expected: "完整的PRD+设计稿+技术方案"
    validation:
      - CEO调用5-7个思维专家
      - 产品+设计+开发三部门参与
      - 总耗时 5-15分钟

  # 场景3: 高复杂度
  complex_task:
    input: "制定公司数字化转型方案"
    expected: "完整的战略+执行计划"
    validation:
      - CEO调用10+思维专家
      - 全部6个部门参与
      - 总耗时 30-60分钟
```

---

## 九、下一步行动

### Phase 1: 架构评审 (Week 1)
- [ ] 评审架构设计文档
- [ ] 确认接口定义
- [ ] 验证可行性检查清单

### Phase 2: CEO开发 (Week 2-3)
- [ ] 创建CEO Agent定义
- [ ] 实现思维专家路由
- [ ] 集成autoresearch能力

### Phase 3: 部门Agent开发 (Week 4-5)
- [ ] 创建6个部门Agent
- [ ] 注入基础思维能力
- [ ] 实现协作机制

### Phase 4: 底层集成 (Week 6-7)
- [ ] 集成ClawTeam框架
- [ ] 集成paperclip工作流
- [ ] 集成goal-driven长任务

### Phase 5: 测试优化 (Week 8)
- [ ] 功能测试
- [ ] 性能测试
- [ ] 用户体验测试

---

**文档状态**: 待评审
**创建日期**: 2026-03-23
**版本**: v2.0
**输出目录**: `/Users/cyberwiz/Documents/01_Project/02_Skill研发/cyberteam搭建/【项目组2】/`
