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
