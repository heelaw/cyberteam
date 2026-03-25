# CyberTeam v2 架构设计

**版本**: v2.0
**日期**: 2026-03-23
**状态**: 全新架构设计

---

## 核心变化

| 旧架构 | 新架构 |
|--------|--------|
| 14位专家独立前置层 | 100+思维专家库，按需注入 |
| 专家作为独立Agent | 思维注入到所有Agent |
| 思考天团前置辩论 | CEO用5W1H1Y/MECE直接拆解 |
| 三层分离 | 三层都有思维注入 |

---

## 新架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           用户输入                                      │
│                    "我想做一个在线教育平台"                              │
└────────────────────────────────────┬────────────────────────────────────┘
                                     ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                        CEO (总指挥)                                    │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │ 思维注入：100+思维专家模型库                                        │  │
│  │ - 5W1H1Y拆解 → What/Why/Who/When/Where/How/Y              │  │
│  │ - MECE分类 → 相互独立，完全穷尽                                 │  │
│  │ - 自动触发相关思维专家（根据上下文）                            │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│  CEO同时具备：                                                       │
│  - ClawTeam底层（任务管理、团队协作）                                │
│  - PUA监督机制（防止偷懒）                                          │
│  - Goal-Driven循环（持续执行直到达成）                               │
└────────────────────────────────────┬────────────────────────────────────┘
                                     ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                         管理层讨论                                    │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │ 思维注入：相关思维专家自动激活                                    │  │
│  │ - 战略问题 → SWOT/Porter五力                                 │  │
│  │ - 决策问题 → 卡尼曼/第一性原理                                 │  │
│  │ - 执行问题 → WBS/GROW                                        │  │
│  │ - 团队问题 → McKinsey7S/Kotter变革                           │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│  管理层Agent：                                                       │
│  - 运营总监、Product负责人、设计总监、技术总监...                     │
│  - 每个都有 agency-agents 的完整人设                               │
└────────────────────────────────────┬────────────────────────────────────┘
                                     ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                          执行层                                       │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │ 思维注入：执行层专有思维模型                                     │  │
│  │ - 代码实现 → 工程最佳实践                                       │  │
│  │ - 设计稿 → 品牌/UX原则                                        │  │
│  │ - 文案 → 内容策略                                             │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│  执行层Agent：                                                       │
│  - 180个 agency-agents 的执行专家                                 │
│  - 持续学习（everything-claude-code）                               │
│  - PUA监督（pua-main）                                             │
└────────────────────────────────────────────────────────────────────┘
```

---

## 思维注入机制

### 思维模型分类（100+）

| 类别 | 数量 | 思维模型示例 |
|------|------|--------------|
| **分析思维** | 20+ | 5W1H1Y、MECE、SWOT、PEST、波特五力 |
| **决策思维** | 15+ | 卡尼曼、第一性原理、逆向思维、博弈论 |
| **执行思维** | 25+ | WBS、GROW、OKR、PDCA、敏捷 |
| **创意思维** | 20+ | 六顶思考帽、设计思维、精益创业 |
| **管理思维** | 20+ | McKinsey7S、Kotter变革、情境领导 |
| **专业思维** | 30+ | 各行业专业分析框架 |

### 自动触发规则

```python
INTENT_TRIGGERS = {
    # 决策类
    "选择|决策|纠结|风险": ["kahneman", "bayes", "game_theory"],
    "创新|突破|颠覆": ["first_principle", "lateral_thinking"],
    "战略|竞争|规划": ["swot", "porter", "bcg_matrix"],

    # 分析类
    "为什么|原因|诊断": ["five_why", "fishbone", "root_cause"],
    "怎么做|实施|执行": ["wbs", "grow", "a3"],
    "全面|多维度": ["six_hats", "five_dimensions"],

    # 管理类
    "组织|团队|变革": ["mckinsey_7s", "kotter", "adkar"],
    "目标|达成|提升": ["grow", "okr", "kpi"],

    # 专业类
    "用户|增长|获客": ["aarrr", "pirate_metrics", "growth_loop"],
    "技术|架构|系统": ["system_design", "tradeoff", "12_factor"],
    "财务|预算|收益": ["dcf", "unit_economics", "ltv_cac"],
}
```

---

## 集成仓库清单

### 底层框架
| 仓库 | 功能 | 集成方式 |
|------|------|----------|
| **ClawTeam** | 多Agent协作底层 | 任务管理、团队创建、消息传递、Worktree隔离 |
| **everything-claude-code** | Agent性能优化 | 27个专家Agent、114个Skill、Hooks系统 |

### 专家Agent库
| 仓库 | 功能 | 集成方式 |
|------|------|----------|
| **agency-agents-zh** | 180个专业Agent | 直接复用工程/设计/营销/销售等人设 |

### 激励机制
| 仓库 | 功能 | 集成方式 |
|------|------|----------|
| **pua-main** | PUA监督机制 | L1-L4压力升级、三条铁律、多种味道 |

### 目标驱动
| 仓库 | 功能 | 集成方式 |
|------|------|----------|
| **goal-driven** | 目标循环执行 | Master-Agent评估循环直到达成 |

---

## 目录结构

```
cyberteam-v2/
├── layers/                    # 三层架构
│   ├── ceo/                  # CEO层
│   │   ├── ceo-agent.md      # CEO Agent定义
│   │   ├── thinking_engine.py # 思维注入引擎
│   │   └── intent_classifier.py # 意图分类器
│   ├── management/            # 管理层
│   │   ├── strategy_director.md
│   │   ├── product_director.md
│   │   ├── tech_director.md
│   │   └── ...
│   └── execution/            # 执行层
│       ├── frontend_dev.md
│       ├── backend_dev.md
│       ├── designer.md
│       └── ...
├── experts/                  # 100+思维专家库
│   ├── analysis/             # 分析思维
│   │   ├── five_why.md
│   │   ├── mece.md
│   │   ├── swot.md
│   │   └── ...
│   ├── decision/             # 决策思维
│   │   ├── kahneman.md
│   │   ├── first_principle.md
│   │   └── ...
│   ├── execution/            # 执行思维
│   ├── creative/             # 创意思维
│   ├── management/           # 管理思维
│   └── professional/        # 专业思维
├── integration/               # 集成适配器
│   ├── clawteam_adapter.py  # ClawTeam适配
│   ├── agency_adapter.py     # agency-agents适配
│   ├── pua_adapter.py        # PUA适配
│   └── goal_driver_adapter.py # Goal-Driven适配
├── engine/                   # 核心引擎
│   ├── thinking_injector.py  # 思维注入引擎
│   ├── debate_engine.py      # 辩论引擎（保留）
│   └── scoring_engine.py      # 评分引擎
└── config/
    └── cyberteam-v2.toml    # 配置文件
```

---

## CEO Agent 定义

```yaml
# CEO Agent - 总指挥
name: cyberteam-ceo
type: orchestrator
model: claude-opus-4-6

## 思维注入
thinking_injection:
  enabled: true
  auto_trigger: true
  max_active_models: 5

## 集成能力
integrations:
  clawteam: true
  agency_agents: true
  pua: true
  goal_driven: true

## 工作流程
workflow:
  1. 接收用户输入
  2. 5W1H1Y拆解
  3. MECE分类
  4. 自动触发相关思维专家
  5. 创建管理团队（ClawTeam）
  6. 分发任务（Goal-Driven）
  7. PUA监督执行
  8. 持续直到达成目标
```

---

## 思维注入引擎

```python
class ThinkingInjector:
    """思维注入引擎"""

    def __init__(self):
        self.experts = load_expert_library()  # 100+专家
        self.intent_classifier = IntentClassifier()
        self.active_thinking = []

    def process(self, user_input: str, agent_context: AgentContext) -> ThinkingContext:
        """处理用户输入，注入相关思维"""

        # 1. 意图分类
        intents = self.intent_classifier.classify(user_input)

        # 2. 选择思维专家
        selected_experts = self._select_experts(intents, agent_context)

        # 3. 生成思维提示
        thinking_prompt = self._generate_prompt(selected_experts, user_input)

        # 4. 返回思维上下文
        return ThinkingContext(
            experts=selected_experts,
            prompt=thinking_prompt,
            injection_points=self._find_injection_points(agent_context)
        )

    def _select_experts(self, intents: List[Intent], context: AgentContext) -> List[Expert]:
        """根据意图选择最相关的思维专家"""
        # 基于意图和上下文的智能选择
        pass

    def _generate_prompt(self, experts: List[Expert], question: str) -> str:
        """生成包含思维专家的提示词"""
        prompt_parts = [
            "你是一个拥有以下思维能力的专家：",
            *[f"\n## {exp.name}\n{exp.description}" for exp in experts],
            f"\n当前问题：{question}",
            "\n请运用以上思维模型进行分析。"
        ]
        return "\n".join(prompt_parts)
```

---

## CEO 5W1H1Y 拆解示例

```
用户输入："我想做一个在线教育平台，目标是1年内做到10万付费用户"

5W1H1Y 拆解：
├── What（做什么？）
│   └── 在线教育平台
├── Why（为什么？）
│   └── [用户没有说，需要追问]
├── Who（谁来做？）
│   └── [团队规模/能力待定]
├── When（什么时候？）
│   └── 1年内
├── Where（在哪里？）
│   └── 线上平台
├── How（怎么做？）
│   └── [需要多轮讨论]
└── Y（ Yield，产出什么？）
    └── 10万付费用户

MECE 分类：
├── 用户获取
│   ├── 渠道策略
│   └── 转化优化
├── 用户留存
│   ├── 内容质量
│   └── 体验优化
└── 商业变现
    ├── 定价策略
    └── 付费转化
```

---

## 执行示例

```bash
# 使用 clawteam 启动 CyberTeam v2
clawteam launch cyberteam \
  --goal "我想做一个在线教育平台，目标是1年内做到10万付费用户"

# CEO 自动执行：
# 1. 5W1H1Y 拆解用户输入
# 2. 识别需要的管理层角色
# 3. 创建管理层团队（运营/产品/技术/设计）
# 4. 分发任务到执行层
# 5. PUA 监督执行
# 6. 持续直到达成目标
```

---

## 版本对比

| 特性 | v1 | v2 |
|------|-----|-----|
| 思维专家数量 | 14 | 100+ |
| 思维注入方式 | 独立前置层 | 注入到Agent思维 |
| CEO能力 | 主持人 | 总指挥+思维注入 |
| 专业Agent | 6个部门 | 180个agency-agents |
| 激励机制 | 基础 | 完整PUA机制 |
| 目标达成 | 一次执行 | Goal-Driven循环 |

---

**设计日期**: 2026-03-23
**版本**: v2.0
