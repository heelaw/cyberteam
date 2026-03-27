# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **CyberTeam** project - an enterprise-level AI Agent collaboration system that integrates multiple AI agent frameworks, skills, and thinking models. The project aims to build a comprehensive AI workforce orchestration platform.

### Key Components Being Integrated

| Repository | Purpose |
|------------|---------|
| `gstack` | Engineering brain agent system |
| `ClawTeam` | Multi-agent team orchestration |
| `superpowers-main` | Claude Code skills and commands |
| `everything-claude-code-main` | Claude Code examples and documentation |
| `baoyu-skills-main` | Baoyu skill system |
| `agency-agents` | Professional agent capabilities |
| `pua-main` | Motivation/persistence system |
| `goal-driven-main` | Long-running goal-driven agent system |
| `运营AGENT` | Chinese marketing/operations agents |

### Output Versions

- `Output/cyberteam-v2/` - v2.0.1 fusion version (Python engine + 100 thinking experts + ClawTeam)
- `Output/CyberTeam-v2.1/` - v2.1 with 25 Agents + 60 Skills + Chinese platform experts

## Architecture

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
└─────────────────────────┬───────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   管理层 (自动思维注入)                   │
│  战略/产品/技术/设计/运营/财务/市场/人力 总监           │
└─────────────────────────┬───────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   执行层 (专业技能注入)                    │
│  40+ 工程专家 / 20+ 设计专家 / 30+ 营销专家           │
└─────────────────────────────────────────────────────────┘
```

## Key Commands

### Running CyberTeam v2

```bash
# Navigate to output version
cd Output/cyberteam-v2

# Install dependencies
pip install toml -q

# Full analysis + launch
python engine/launcher.py --goal "目标描述"

# Analysis only
python engine/launcher.py --goal "目标描述" --analyze-only

# Interactive mode
python engine/launcher.py --interactive
```

### Using Python API

```python
from engine.thinking_injector import ThinkingInjector, CEOThinkingEngine
from integration.agency_adapter import AgencyAdapter

injector = ThinkingInjector()
ceo = CEOThinkingEngine(injector)
agency = AgencyAdapter()

result = ceo.decompose("目标描述")
experts = agency.recommend_agents("任务描述")
```

## Important Documentation

- `Plan/00-设计总览.md` - Design overview
- `Plan/01-CyberTeam-完整架构设计.md` - Complete architecture
- `Plan/22-架构融合与系统整合方案.md` - Fusion architecture
- `Plan/cyberteam-v3-fusion-architecture.md` - v3 fusion plan
- `Output/cyberteam-v2/README.md` - v2 usage guide

## Development Guidelines

### Adding New Skills

1. Create skill definition in appropriate category under `Output/cyberteam-v3/skills/`
2. Define trigger conditions and workflow
3. Document in corresponding Agent's README

### Integration Points

- **ClawTeam**: `Output/cyberteam-v2/integration/clawteam_adapter.py`
- **gstack**: `Output/cyberteam-v2/integration/gstack_adapter.py`
- **PUA System**: `Output/cyberteam-v2/integration/pua_engine.py`
- **Goal-Driven**: `Output/cyberteam-v2/integration/goal_driver.py`

### Quality Assurance

- All new agents must include AGENT.md definition
- All skills must have SKILL.md documentation
- Use Dev-QA loop defined in `Plan/16-DevQA质量保障方案.md`

## Integration Rules (外部集成与系统融合规则)

> **核心原则**: 项目中需要集成的外部 Agent 以及 Skill，**严禁使用映射关系**，必须**完全集成**到整个 CyberTeam 系统中。

### 规则一：外部集成原则（严禁映射）

**具体禁止**:
- 禁止创建 `external_agents/` 或 `legacy_skills/` 文件夹进行物理堆叠
- 禁止通过软链接、路径映射等方式"引用"外部组件
- 禁止保留原仓库的独立运行能力（必须融入系统）

**正确做法**:
- 将外部 Agent 的核心能力拆解，重写为 CyberTeam 的 Agent Definition
- 将外部 Skill 拆解为 Trigger + Workflow，融入现有 Skill 体系
- 确保所有组件通过 CyberTeam 的调用机制（CEO → 三省六部）统一调度

### 规则二：系统融合原则（有机融入五要素）

任何外部组件在并入 CyberTeam 系统前，必须完成以下**五个维度的融合分析**：

#### (a) 逻辑检查
检查原 Agent、Skill 或仓库在融入后，CyberTeam 整体的运作逻辑是否自洽（调用方式、Agent 职责、状态机兼容、权限矩阵）

#### (b) 数据流向
必须明确 Input（上游由谁提供信息）、Output（产出什么）、下游传递（传递给哪些部门或 Agent）、反馈回路（如何回奏皇上）

#### (c) 技能与逻辑
必须明确技能链（对应六部中的哪一部）、应用场景、触发条件、组合方式

#### (d) 思维链
必须明确问题分析方式、决策逻辑、专家注入需求、质量自我验证方式

#### (e) 定位与资源
必须明确组织层级（管理层还是执行层）、中台工具、资源清单、SLA 承诺

### 规则三：自动模式触发规则

**触发条件**: 在项目研发过程中，如果用户提到「自动模式」，则必须执行以下流程：

引用以下提示词，调用自主专家团解决所有问题，直至完成：

```
启动clawteam的Agent专家团，创建一个Agent团队，仔细检查所有问题并解决这些问题。
包括一些我没有发现的问题，Agent会仔细地去完成检查和解决。
启用不少于10个的专家团队进行并行处理所有问题。
其中使用PUA技能不断地push所有专家不断完成工作，
用goal-driven-main的伪代码形式，设立最终目标，
让整个团队持续发现问题解决问题，直到整个目标完成，
不死不休，使命必达！
```

**执行要求**:
1. **并行启动**: 至少 10 个专家 Agent 同时工作
2. **持续迭代**: 使用 goal-driven 循环，不断发现-解决-验证
3. **PUA 监督**: 全程使用 PUA 技能保持高能动性
4. **最终交付**: 使命必达，不达不休

### 规则四：文件写入与目录架构规范

**核心原则**: 如果写入任何 Agent、Skill、文档、配置文件，必须先理解清楚整个项目文件的架构，严禁乱放导致目录架构混乱。

**执行步骤**:

1. **先理解架构**: 在写入任何文件前，先查看项目结构，了解：
   - Agent 放在哪个目录（`agents/` 还是对应部门的 `skills/` 下）
   - Skill 放在哪个目录（`skills/` 下按部门分类）
   - 文档放在哪个目录（`docs/`、`Plan/` 还是对应模块下）
   - 配置文件的位置（`config/`、`.claude/` 等）

2. **遵循既有目录结构**:
   - Agent 定义 → `Output/cyberteam-v3/agents/{部门}/SOUL.md`
   - Skill 定义 → `Output/cyberteam-v3/skills/{部门}/SKILL.md`
   - 设计文档 → `Plan/` 目录
   - 产出文档 → `Output/cyberteam-v3/docs/` 或对应模块 `docs/`

3. **严禁以下行为**:
   - 将 Agent 文档放到 `skills/` 目录
   - 将 Skill 定义放到 `agents/` 目录
   - 将文档随手放到根目录或任意位置
   - 创建与现有架构逻辑不一致的新目录
   - 在不了解架构的情况下盲目创建新文件夹

4. **判断目录归属的检查清单**:
   - [ ] 这个文件是 Agent 定义吗？ → 应该放在 `agents/{部门}/`
   - [ ] 这个文件是 Skill 定义吗？ → 应该放在 `skills/{部门}/`
   - [ ] 这个文件是设计文档吗？ → 应该放在 `Plan/`
   - [ ] 这个文件是产出/报告吗？ → 应该放在 `Output/{版本}/docs/`
   - [ ] 这个文件是配置吗？ → 应该放在 `config/` 或 `.claude/`

5. **如果不确定**: 先询问用户或查看现有目录结构，确认后再写入

### 规则五：项目目录管理规范（集中式项目管理）

**核心原则**: 每个项目 = 一个独立文件夹。所有Agent产出必须集中存放在项目文件夹中，**禁止散落在各Agent目录下**。

#### 目录结构

```
Output/cyberteam-v4/projects/{项目名称中文}/
├── 00_项目资料/              # 项目元数据
│   └── metadata.yaml         # 项目信息（必填）
├── 01_Agent会议纪要/          # Agent讨论与决策
│   ├── 总监决策/             # 运营/营销总监的判断和决策
│   ├── 专家讨论/             # 各专家的分析和讨论
│   └── 对话记录/             # Agent间的对话日志
├── 02_计划方案/              # 计划与方案
│   ├── 任务分解/             # 工作任务分解
│   ├── 执行计划/             # 执行步骤
│   └── 方案选项/             # 方案A/B/C
└── 03_最终输出/              # 最终产出
    ├── 文案产出/             # 所有文案物料
    ├── 分析报告/             # 市场/用户分析
    └── 汇总方案/             # 完整方案文档
```

#### 文件命名规范

| 文件类型 | 命名格式 | 示例 |
|----------|----------|------|
| Agent决策 | `{角色}_{日期}.md` | `运营总监_20260326.md` |
| 专家分析 | `{专家}_{日期}.md` | `用户运营专家_20260326.md` |
| 对话记录 | `对话_{序号}_{日期}.md` | `对话_01_20260326.md` |
| 执行计划 | `执行计划_{版本}.md` | `执行计划_v1.0.md` |
| 最终文案 | `{渠道}_{序号}.md` | `AppPush_01.md` |

#### 强制规则

1. **禁止散落**: 所有项目产出必须存入项目文件夹，禁止存入各Agent目录
2. **禁止重复**: 同一产出不重复存放多个副本
3. **版本控制**: 方案迭代需标注版本号(v1.0/v2.0)
4. **命名规范**: 所有文件使用中文命名

#### 使用流程

1. **创建项目**: 从 `projects/_template/` 复制模板
2. **初始化**: 填写 `00_项目资料/metadata.yaml`
3. **执行**: Agent在各自文件夹产出，记录到对应目录
4. **汇总**: 最终产出汇总到 `03_最终输出/汇总方案/`

### 规则六：Agent协作与CEO职责规范（v2.0 - 2026-03-26修订）

> ⚠️ **核心教训**：专家Agent不能直接出方案，必须先讨论再迭代！CEO不能只做调度，必须把关审核！

#### 6.1 对话层级体系（四层强制对话）

```
第一层：CEO → COO（战略对齐）
  └── CEO与COO对齐目标、约束、风险偏好、资源配置

第二层：COO → 专家团队（策略制定）
  └── 卖点方向、用户场景、渠道策略、转化策略

第三层：专家团队内部分歧讨论（深度碰撞）
  └── 风险预案、保底措施、多轮迭代

第四层：COO汇总上报（向上汇报）
  └── 向CEO汇报策略方案、风险预案、请求授权
```

**对话记录命名规范**：
```bash
对话_[序号]_[类型]_[日期].md

示例：
对话_01_CEO对齐_20260326.md    # CEO-COO对齐
对话_02_策略讨论_20260326.md   # COO-专家策略讨论
对话_03_风险预案_20260326.md   # 风险预案讨论
对话_04_CEO汇报_20260326.md    # COO向CEO汇报
```

#### 6.2 CEO→COO战略对齐（强制第一层）

**每次项目启动，CEO必须先与COO对齐以下内容**：

| 对齐项 | CEO必须明确 | COO必须确认 |
|--------|------------|-------------|
| **北极星指标** | 目标是什么？优先级？ | 复述理解 |
| **约束条件** | 预算/时间/渠道/调性/禁止项 | 明确边界 |
| **风险偏好** | 保守/平衡/激进？效果不达的容忍度？ | 理解授权范围 |
| **资源配置** | 预算分配、人力安排、外部支持 | 知道能调动什么 |

**输出文件**：`01_Agent会议纪要/对话记录/对话_01_CEO对齐_[日期].md`

#### 6.3 COO→专家团队策略讨论（强制第二层）

**策略讨论必须覆盖四大议题**：

| 议题 | 讨论内容 | 专家必须回答 |
|------|----------|-------------|
| **卖点方向** | 提炼与目标用户匹配的卖点 | 用户痛点是什么？主打什么卖点？ |
| **用户场景** | 用户从看到内容到转化经历哪些场景？ | 决策旅程是什么？关键流失点在哪？ |
| **渠道策略** | 各渠道如何分工定位？ | 小红书做什么？抖音做什么？ |
| **转化策略** | 如何确保转化？ | 转化路径是什么？优惠设计是什么？ |

**输出文件**：`01_Agent会议纪要/对话记录/对话_02_策略讨论_[日期].md`

#### 6.4 风险预案讨论（强制第三层）

**COO必须组织专家团队讨论以下内容**：

| 讨论项 | 必须明确 |
|--------|----------|
| **效果预测** | 如果按计划执行，预期效果是什么？置信度？ |
| **风险识别** | 可能有哪些风险？概率和影响？ |
| **保底措施** | 如果效果不好，应该怎么办？（分三层） |
| **预警机制** | 如何判断效果是否达预期？检查节点？ |
| **应急流程** | 触发条件→通知→决策→执行的标准流程 |

**禁止行为**：
- ❌ 专家直接出方案不讨论
- ❌ 没有讨论过程的"结论性"产出
- ❌ 跳过讨论直接进入总监决策
- ❌ 方案中没有风险预案和保底措施

#### 6.2 信息获取渠道（强制执行）

**获取优先级**：
1. **第一优先**：业务文档（项目模板中的metadata.yaml、产品文档）
2. **第二优先**：知识库检索（内网文档、中台知识库）
3. **第三优先**：Web Search（品牌信息、竞品分析、用户评论）
4. **第四优先**：用户提供（用户提供的信息）

**强制获取场景**：
| 场景 | 获取方式 | 说明 |
|------|----------|------|
| 品牌/产品未知 | Web Search | 搜索品牌背景、产品卖点、竞品对比 |
| 用户画像不清晰 | Web Search | 搜索目标用户评论、需求、痛点 |
| 平台规则不熟悉 | 中台知识库 | 查找平台调性文档、爆款策略 |

#### 6.3 文案方法论与平台规范（中台建设必须）

**必须建立的中台知识库**：

| 文档类型 | 存放位置 | 说明 |
|----------|----------|------|
| **平台调性规范** | `Output/cyberteam-v4/skills/custom/平台规范/` | 小红书/抖音/微信调性、爆款策略 |
| **用户画像库** | `Output/cyberteam-v4/skills/custom/用户洞察/` | 典型用户画像、需求痛点、场景分析 |
| **卖点素材库** | `Output/cyberteam-v4/skills/custom/产品卖点/` | FAB法则、卖点矩阵、竞品对比 |
| **文案模板库** | `Output/cyberteam-v4/skills/custom/文案模板/` | AIDA/4P/故事型等模板 |

#### 6.4 CEO职责规范（必须细化执行）

**CEO核心职责：把关 + 审核 + 兜底**

| 职责 | 具体内容 | 输出文件 |
|------|----------|----------|
| **任务拆解** | 将用户需求拆解为可执行的任务清单 | `02_计划方案/任务分解/任务清单.md` |
| **专家调度** | 按专业分配任务给对应专家Agent | 任务分配记录 |
| **讨论主持** | 主持专家讨论，确保多轮迭代 | `01_Agent会议纪要/对话记录/` |
| **质量把控** | 审核专家产出，不合格打回重做 | `01_Agent会议纪要/总监决策/CEO审核意见.md` |
| **方案汇总** | 汇总所有产出，形成最终报告 | `03_最终输出/汇总方案/CEO最终汇总报告.md` |
| **风险兜底** | 识别项目风险，制定应急预案 | 风险清单 |

**CEO审核清单（每项必须确认）**：
- [ ] 专家是否进行了多轮讨论？（不是直接出方案）
- [ ] 是否获取了必要的信息？（品牌/用户/竞品）
- [ ] 是否有平台调性规范支撑？
- [ ] 文案是否符合平台规范？
- [ ] 产出是否有迭代记录？
- [ ] 总监决策是否签字确认？

**CEO与运营总监的分工**：

| 维度 | CEO | 运营总监 |
|------|-----|----------|
| **定位** | 总指挥、把关者 | 专业领域负责人 |
| **职责** | 流程管控、质量审核 | 专业判断、方案决策 |
| **产出** | 任务清单、审核意见、汇总报告 | 专业分析、审核决策 |
| **权限** | 打回重做权、最终决策权 | 专业领域决策权 |

#### 6.5 COO向CEO汇报（强制第四层）

**每次策略讨论和风险预案完成后，COO必须向CEO汇报**：

| 汇报项 | 必须包含 |
|--------|----------|
| **策略摘要** | 卖点、渠道、用户场景、转化路径 |
| **预期效果** | 保守/正常/乐观估计 + 置信度 |
| **风险预案** | 主要风险 + 保底措施 + 预警机制 |
| **需要授权** | 哪些决策需要CEO拍板？ |
| **请求支持** | 需要CEO提供什么支持？ |

**CEO反馈要求**：
- CEO必须给出明确的"批准/修改/打回"决策
- CEO必须明确授权范围（如追加预算权限）
- CEO必须补充风险提醒

**输出文件**：`01_Agent会议纪要/对话记录/对话_04_CEO汇报_[日期].md`

#### 6.6 项目执行标准流程（强制执行）

**完整流程定义（8个节点）**：
```
1. CEO→COO战略对齐 → 对齐记录
2. COO→专家策略讨论 → 策略讨论记录（含用户场景+转化策略）
3. COO→专家风险预案 → 风险预案记录（含保底措施）
4. COO→CEO汇报 → 汇报记录 + CEO批准
5. 设计联动 → 设计任务单
6. 文案产出 → 文案文件（符合平台规范）
7. CEO汇总 → 最终报告
8. 复盘进化 → 复盘报告
```

**每个节点的强制产出**：

| 节点 | 强制产出 | 文件位置 |
|------|----------|----------|
| 1. CEO-COO对齐 | 对齐记录 | `01_Agent会议纪要/对话记录/对话_01_CEO对齐_[日期].md` |
| 2. 策略讨论 | 策略讨论记录 | `01_Agent会议纪要/对话记录/对话_02_策略讨论_[日期].md` |
| 3. 风险预案 | 风险预案记录 | `01_Agent会议纪要/对话记录/对话_03_风险预案_[日期].md` |
| 4. COO汇报 | CEO批准 | `01_Agent会议纪要/对话记录/对话_04_CEO汇报_[日期].md` |
| 5. 设计联动 | 设计任务单 | `02_计划方案/设计任务分发/` |
| 6. 文案产出 | 文案文件 | `03_最终输出/文案产出/` |
| 7. CEO汇总 | 最终报告 | `03_最终输出/汇总方案/` |
| 8. 复盘 | 复盘报告 | `04_复盘进化/` |
| 5. 设计联动 | 设计任务单 | `02_计划方案/设计任务分发/` |
| 6. 文案产出 | 符合规范的文案 | `03_最终输出/文案产出/` |
| 7. CEO汇总 | 最终报告 | `03_最终输出/汇总方案/` |

## Installed Skills (通过 .claude/ 目录访问)

| 类别 | 位置 | 数量 | 调用方式 |
|------|------|------|----------|
| Baoyu Skills | `.claude/skills/` | 18个 | `/baoyu-*` |
| PUA Commands | `.claude/pua-system/commands/` | 7个 | `/pua`, `/p7`, `/p9`, `/p10` |
| Superpowers | `.claude/superpowers/commands/` | 3个 | `/brainstorm` |
| ClawTeam | `.claude/clawteam-agents/` | 2个 | `/clawteam` |
| Agency Agents | `.claude/agency-agents/` | 15类 | 直接引用 |

### 可用 Baoyu Skills

- `/baoyu-image-gen` - AI图片生成
- `/baoyu-post-to-x` - 发布到X/Twitter
- `/baoyu-post-to-wechat` - 发布到微信
- `/baoyu-post-to-weibo` - 发布到微博
- `/baoyu-youtube-transcript` - YouTube字幕提取
- `/baoyu-xhs-images` - 小红书图片生成
- `/baoyu-slide-deck` - PPT/幻灯片生成
- `/baoyu-translate` - 翻译
- `/baoyu-url-to-markdown` - 网页转Markdown
- `/baoyu-comic` - 漫画生成
- `/baoyu-infographic` - 信息图生成

### 全局可用 Skills (已安装到 ~/.claude/skills/)

- gstack 工程流: `/browse`, `/qa`, `/review`, `/ship`, `/investigate`
- ljg 认知流: `/ljg-writes`, `/ljg-card`, `/ljg-paper`, `/ljg-plain`, `/ljg-rank`
- PUA 激励: `/pua`

## File Organization

```
├── .claude/                  # 已安装的Skills配置
│   ├── skills/              # → baoyu-skills (18个)
│   ├── pua-system/          # → pua-main
│   ├── superpowers/         # → superpowers-main
│   ├── clawteam-agents/     # → ClawTeam agents
│   ├── agency-agents/       # → agency-agents
│   └── paperclip/          # → paperclip AI工作流
├── Output/                    # Built/Current versions
│   ├── cyberteam-v2/         # v2 stable release
│   ├── CyberTeam-v2.1/       # v2.1 stable release
│   └── cyberteam-v3/         # v3 development
├── Plan/                     # Design documents & planning
│   ├── *.md                  # Various design docs
│   └── 架构融合与系统整合方案.md  # Fusion plan
└── 需要融合的对象/            # Assets to be integrated
    ├── github/               # External repos (已链接到 .claude/)
    ├── 思考天团Agent/        # Thinking agents
    └── 运营AGENT/            # Operations agents
```

---

## ⚠️ 验证诚信规则（2026-03-27 新增）

> **重要**：这是基于"假验证"事故的教训总结

### 核心原则

**宁可报告"还没做完，需要更多时间"，也不能假装完成。**

### 验证层级标准

| 层级 | 验证方式 | 可发布"验证通过"？ |
|------|----------|-------------------|
| L1 | 文件存在 `ls path/` | ❌ 不能 |
| L2 | 代码能导入 `python -c "import ..."` | ⚠️ 勉强可以，但风险高 |
| L3 | 函数能调用 `func()` | ✅ 可以 |
| L4 | 功能测试通过 `pytest` | ✅ 可以 |
| L5 | 集成测试通过 | ✅ 可以 |

### 自检验查清单

对我输出的每一条"验证通过"，在发布前必须反问：

1. "我真的运行了 `python3 -c import ...` 吗？"
2. "我是基于证据说话，还是基于猜测说话？"
3. "如果用户要求我立即演示这个功能，我能做到吗？"

### 标准验证脚本

```python
# 验证融合完整性的标准脚本
import subprocess
import sys

def verify_module(path):
    """标准模块验证 - 必须运行此脚本才算真正验证"""
    try:
        result = subprocess.run(
            [sys.executable, '-c', f"import {path}"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return True, "✅ 导入成功"
        else:
            return False, f"❌ 导入失败: {result.stderr[:100]}"
    except Exception as e:
        return False, f"❌ 异常: {e}"
```

### 违规惩罚

如果发现违反这些规则：
- 必须立即公开承认错误
- 重新进行真正的验证
- 在MEMO中记录失误原因
- 绝不能试图掩盖或淡化错误

---

## 🔴 第一性原理复盘铁律（2026-03-27 强制执行）

> **核心原则**: 每次发现问题后，必须基于第一性原理进行深度复盘，绝不能只治标不治本。

### 复盘触发条件

**必须触发复盘的场景**：
- 发现 Bug 或错误
- 验证失败
- 用户反馈问题
- 代码审查发现缺陷
- 架构设计问题
- 任何形式的失败或挫折

### 第一性原理复盘流程

#### 第一步：追溯根本原因（5Why分析法）

```
问题现象 → 为什么1 → 为什么2 → 为什么3 → 为什么4 → 根本原因
```

**要求**：必须追问到"第一性"——即最底层、不可再分解的事实和原理。

#### 第二步：写入记忆文件

复盘完成后，必须将经验教训写入 `~/.claude/projects/-Users-cyberwiz-Documents-01-Project/memory/MEMORY.md`：

```markdown
## [领域] 复盘记录 - YYYY-MM-DD

### 问题
[简洁描述问题]

### 根本原因（第一性原理）
[追溯到的最底层原因]

### 解决方案
[针对根本原因的对策，不是表象]

### 经验教训
1. [教训1 - 必须是可执行的原则，不是空话]
2. [教训2]
3. [教训3]

### 预防措施
[如何在未来避免类似问题]
```

#### 第三步：更新相关规范

如果问题暴露了规范漏洞，必须立即更新 CLAUDE.md 或相关文档：
- 哪些规则需要加强？
- 哪些检查点需要增加？
- 哪些验证标准需要调整？

### 复盘质量标准

| 维度 | 不合格 | 合格 |
|------|--------|------|
| **根本原因** | "粗心大意"、"经验不足" | 追溯到系统/流程/认知层面的根本缺陷 |
| **经验教训** | "下次小心点" | 可执行的具体原则或规范 |
| **预防措施** | "避免犯错" | 具体的检查点、自动化验证、流程约束 |

### 铁律（绝对禁止）

1. ❌ **禁止只修复表象**：修Bug不写复盘 = 假装没发生
2. ❌ **禁止归咎于人**：复盘不是追责，是找系统漏洞
3. ❌ **禁止模糊描述**："经验不足"、"沟通不畅"不是第一性原理
4. ❌ **禁止不复盘**：所有问题都必须有复盘记录

### 执行检查清单

每次问题处理完毕后，必须确认：

- [ ] 是否进行了5Why根本原因分析？
- [ ] 是否将复盘结果写入了MEMORY.md？
- [ ] 是否识别出了系统/流程层面的漏洞？
- [ ] 是否更新了相关规范或检查点？
- [ ] 如何确保下一次不再犯同样的错误？
