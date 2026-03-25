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
