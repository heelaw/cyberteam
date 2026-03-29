# Q1: GitHub 仓库研究 - Agent 和 Skill 设计模式

**问题**: 这个项目文件夹里是我收集到的一些 GitHub 仓库。我现在需要去研究并了解这些仓库：1. 他们是怎么做 Agent 的 2. 以及他们怎么做 Skill 的

**研究范围**: 8个代表性仓库（agent-skills, gstack, claude-skills, oh-my-openagent-dev, awesome-claude-skills, OpenViking, agency-agents, claude-code-templates）

---

## 一、Agent 架构模式

### 1.1 分层架构（主流）

```
┌─────────────────────────────────────────┐
│           Planning Layer（规划层）         │
│   Prometheus | Metis | Momus            │
├─────────────────────────────────────────┤
│           Execution Layer（执行层）       │
│   Atlas（编排器）                         │
├─────────────────────────────────────────┤
│           Worker Layer（工作者层）        │
│   Sisyphus-Junior | Oracle | Explore    │
└─────────────────────────────────────────┘
```
**代表仓库**: oh-my-openagent-dev

### 1.2 核心组件模式

| 组件 | 模式 | 代表 |
|------|------|------|
| **AgentLoop** | 消息驱动循环 | OpenViking |
| **ContextBuilder** | 渐进式上下文构建 | gstack, claude-skills |
| **MemoryStore** | 双层记忆（长期+历史）| OpenViking |
| **ToolRegistry** | 动态工具注册 | OpenViking, gstack |
| **SkillLoader** | 4层加载优先级 | oh-my-openagent-dev |

### 1.3 Agent 定义格式（通用）

```yaml
---
name: agent-name
description: 角色描述...
color: blue        # 可选
emoji: 🏗️          # 可选
vibe: 设计理念...   # 可选
---

# Agent Personality
## 🧠 Identity & Memory
## 🎯 Core Mission
## 🚨 Critical Rules
## 📋 Deliverable Template
## 🔄 Workflow Process
```

### 1.4 协作机制

| 模式 | 实现 | 代表 |
|------|------|------|
| **Handoff** | 通过标签传递上下文 | agency-agents |
| **Pipeline** | PM→Architect→Dev→QA | agency-agents |
| **Intent Gate** | 先理解真实意图再路由 | oh-my-openagent-dev |
| **Category委托** | 语义分类→模型映射 | oh-my-openagent-dev |

---

## 二、Skill 定义格式

### 2.1 通用结构（YAML frontmatter + Markdown）

```yaml
---
name: skill-name
description: Use when [触发条件]. [能力描述]
license: MIT
metadata:
  author: https://github.com/xxx
  version: "1.0.0"
  domain: frontend|backend|workflow
  triggers: keyword1, keyword2
  role: specialist|expert
  scope: implementation|review|design
---
```

### 2.2 标准目录结构

```
skill-name/
├── SKILL.md              # 核心定义（~80-100行）
├── assess/               # 评估清单
├── evals/                # 测试案例
├── references/           # 参考文档（按需加载）
│   ├── templates.md
│   └── examples.md
├── scripts/              # 可执行脚本
└── assets/               # 模板/资源文件
```

### 2.3 SKILL.md 正文结构

```markdown
# Skill Name

## Role Definition        # 2-3句话定义专家角色

## When to Use This Skill  # 触发场景列表

## Core Workflow           # 5步以内，每步有输入/输出/成功标准

## Reference Guide         # 路由表 | Topic | Reference | Load When |

## Constraints
### MUST DO (≥3条)
### MUST NOT DO (≥5条)

## Output Templates        # 输出格式定义
```

### 2.4 渐进式加载机制（多个仓库采用）

| 层级 | 内容 | Token | 触发 |
|------|------|-------|------|
| **L0** | name + description | ~100 | 始终 |
| **L1** | SKILL.md body | <5k | skill 激活 |
| **L2** | scripts/references | 按需 | 按需 |

---

## 三、关键设计模式汇总

### 3.1 可直接借鉴的模式

| 模式 | 来源 | 价值 |
|------|------|------|
| **MUST DO / MUST NOT DO** 约束 | claude-skills | 增强 Skill 规范性 |
| **Description Trap** | claude-skills | 描述只写能力+触发，不写流程 |
| **Reference Guide 路由表** | claude-skills | 按需加载避免 token 膨胀 |
| **Progressive Disclosure** | awesome-claude-skills | 三层加载节省 token |
| **Critical Rules 结构** | agency-agents | 增强禁止行为描述 |
| **Deliverable Template** | agency-agents | 统一 Skill 输出格式 |
| **Fix-First Review** | gstack | 自动化修复 + 人工判断分离 |
| **三层测试验证** | gstack | 静态→E2E→LLM-as-judge |
| **Intent Gate** | oh-my-openagent-dev | 先理解意图再路由 |
| **Category + Skill 委托** | oh-my-openagent-dev | 语义分类解耦模型选择 |
| **多级 Skill 优先级** | oh-my-openagent-dev | 项目覆盖全局 |

### 3.2 自动化工具

| 工具 | 来源 | 功能 |
|------|------|------|
| `generate_agents.py` | agent-skills | 自动生成 AGENTS.md |
| `gen-skill-docs.ts` | gstack | 模板→SKILL.md 生成 |
| `validate-skills.py` | claude-skills | YAML 格式验证 |
| `convert.sh` | agency-agents | Agent 格式转换（多工具）|
| `init_skill.py` | awesome-claude-skills | 初始化 Skill 目录 |

---

## 四、与当前项目的对比

### 当前项目结构（MEMORY.md v3）
```
Output/{skill-name}/
├── SKILL.md
├── assess/评估清单.json
├── evals/evals.json
└── references/
    ├── templates.md
    └── examples.md
```

### 可补充的方向

| 方向 | 建议 | 来源 |
|------|------|------|
| **scripts/ 目录** | 添加可执行脚本支持 | claude-code-templates |
| **多层 .md 文档** | 如 forms.md, reference.md | claude-code-templates |
| **MUST DO/NOT 规范** | 每 skill ≥3+5 条约束 | claude-skills |
| **渐进式加载** | references/ 按需路由 | claude-skills |
| **组件审查流程** | 建立 component-reviewer | claude-code-templates |
| **版本自动管理** | 基于 conventional commits | agent-skills |

---

## 五、核心发现

1. **Agent 和 Skill 本质相同**：都是 YAML frontmatter + Markdown 结构
2. **分层加载是共识**：L0元数据 → L1正文 → L2资源，按需加载节省 token
3. **约束规范是质量关键**：MUST DO / MUST NOT DO 模式被多个仓库采用
4. **渐进式披露是最佳实践**：避免上下文膨胀
5. **自动化工具提升效率**：生成器、验证器、转换器

---

**研究日期**: 2026-03-20
**来源仓库**: agent-skills, gstack, claude-skills, oh-my-openagent-dev, awesome-claude-skills, OpenViking, agency-agents, claude-code-templates
