# CyberTeam v2.0.1 (融合版)

> 企业级 AI Agent 协作系统 - 融合 v2 + v2.1 双版本优势
> **v2 核心**: Python 引擎 + 100 思维专家 + ClawTeam 集成
> **v2.1 补充**: 25 Agent + 60 Skills + 中国平台专家体系

## 核心特性

- **100+ 思维专家**: 内置丰富的思维模型库，自动根据上下文注入
- **25 个 Agent 定义**: CEO + 8 专家 + 6 部门 + 10 中国平台专家
- **60 个 Skills**: 33 运营 Skills + 26 中国平台 Skills + 质量工作流
- **4 大引擎**: 思维注入 / 路由引擎 / Dev-QA 循环 / 三级质量门控
- **三层架构**: CEO → 管理层 → 执行层，层层思维注入
- **智能集成**: ClawTeam / PUA / Goal-Driven 无缝集成
- **目标驱动**: Master-Agent 评估循环，直到达成目标

## 架构概览

```
┌─────────────────────────────────────────────────────────┐
│                        用户输入                          │
└─────────────────────────┬───────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    CEO (总指挥)                          │
│  • 5W1H1Y 问题拆解                                      │
│  • MECE 分类                                            │
│  • 100+ 思维专家注入                                     │
│  • 组建管理团队                                          │
│  • 目标驱动监督                                          │
└─────────────────────────┬───────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   管理层 (自动思维注入)                   │
│  战略总监 / 产品总监 / 技术总监 / 设计总监               │
│  运营总监 / 财务总监 / 市场总监 / 人力总监              │
└─────────────────────────┬───────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   执行层 (专业技能注入)                    │
│  40+ 工程专家 / 20+ 设计专家 / 30+ 营销专家             │
│  180+ agency-agents 专业能力                            │
└─────────────────────────────────────────────────────────┘
```

## 快速开始

### 安装

```bash
# 克隆项目
git clone <repo>
cd cyberteam-v2

# 安装依赖
pip install toml -q

# 安装 ClawTeam (可选)
npm install -g clawteam
```

### 使用

#### 方式1: 命令行

```bash
# 完整分析 + 启动
python engine/launcher.py --goal "我想做一个在线教育平台"

# 仅分析
python engine/launcher.py --goal "帮我分析竞争对手" --analyze-only

# 交互模式
python engine/launcher.py --interactive
```

#### 方式2: Python API

```python
from engine.thinking_injector import ThinkingInjector, CEOThinkingEngine
from integration.agency_adapter import AgencyAdapter

# 初始化
injector = ThinkingInjector()
ceo = CEOThinkingEngine(injector)
agency = AgencyAdapter()

# 分析目标
result = ceo.decompose("我想做一个在线教育平台，目标是一年内10万付费用户")

# 推荐专家
experts = agency.recommend_agents("做一个增长方案")
```

## 目录结构

```
cyberteam-v2/
├── layers/                    # 三层架构
│   ├── ceo/                  # CEO 层
│   │   └── ceo-agent.md
│   ├── management/            # 管理层
│   │   └── management-agents.md
│   └── execution/            # 执行层
│       └── execution-agents.md
├── experts/                   # 100+ 思维专家库
│   ├── analysis/             # 分析思维
│   ├── decision/             # 决策思维
│   ├── execution/            # 执行思维
│   ├── creative/             # 创意思维
│   ├── management/           # 管理思维
│   └── professional/        # 专业思维
├── integration/               # 集成适配器
│   ├── clawteam_adapter.py
│   ├── agency_adapter.py
│   ├── pua_adapter.py
│   └── goal_driver_adapter.py
├── engine/                    # 核心引擎
│   ├── thinking_injector.py  # 思维注入引擎
│   └── launcher.py           # 启动器
├── config/
│   └── cyberteam-v2.toml    # 配置文件
└── ARCHITECTURE.md           # 架构文档
```

## 思维专家库

| 类别 | 数量 | 示例 |
|------|------|------|
| 分析思维 | 20+ | 五问法、MECE、SWOT、PEST、鱼骨图 |
| 决策思维 | 15+ | 卡尼曼、第一性原理、贝叶斯、博弈论 |
| 执行思维 | 25+ | WBS、GROW、OKR、PDCA、A3 |
| 创意思维 | 20+ | 六顶思考帽、设计思维、SCAMPER |
| 管理思维 | 20+ | McKinsey 7S、Kotter、ADKAR |
| 专业思维 | 30+ | AARRR、LTV/CAC、系统设计 |

## 集成组件

| 组件 | 功能 | 集成方式 |
|------|------|----------|
| **ClawTeam** | 多Agent协作底层 | 任务管理、团队创建、消息传递 |
| **agency-agents-zh** | 180个专业Agent | 工程/设计/营销等专业能力 |
| **pua-main** | PUA监督机制 | L1-L4 压力升级 |
| **goal-driven** | 目标循环执行 | 评估-反馈-重试 |

## PUA 机制

| 等级 | 触发 | 风格示例 (阿里味) |
|------|------|-----------------|
| L1 | 失败2次 | "这个结果让我有点失望" |
| L2 | 失败3次 | "你能告诉我为什么是这个结果吗？" |
| L3 | 失败4次 | "我觉得你的能力可能不够胜任" |
| L4 | 失败5次 | "重新做，这次给我一个让我眼前一亮的方案" |

## 配置

编辑 `config/cyberteam-v2.toml` 自定义系统行为：

```toml
[thinking]
enabled = true
max_active_experts = 5
confidence_threshold = 0.6

[pua]
flavor = "ali"  # ali, bytedance, huawei, tencent, musk

[goal_driver]
max_iterations = 10
min_success_score = 75.0
```

## 开发

### 运行测试

```bash
# 测试思维注入引擎
python engine/thinking_injector.py

# 测试 PUA 机制
python integration/pua_adapter.py

# 测试 Goal Driver
python integration/goal_driver_adapter.py

# 测试 Agency Adapter
python integration/agency_adapter.py
```

### 添加新的思维专家

1. 在 `experts/<category>/` 创建 `expert-xxx.md`
2. 定义触发关键词和注入模板
3. 专家自动被思维库加载

## License

MIT

---

*CyberTeam v2 - 让 AI 协作像指挥军队一样高效*
