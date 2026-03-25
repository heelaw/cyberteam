# CyberTeam v2.1 超级详细使用指南

**版本**: v2.1
**日期**: 2026-03-24
**状态**: 全面交付
**适用对象**: 开发者、AI工程师、运维人员、产品经理

---

## 目录

1. [系统概述](#一系统概述)
2. [快速开始](#二快速开始)
3. [完整安装配置](#三完整安装配置)
4. [系统架构详解](#四系统架构详解)
5. [ClawTeam 底层框架](#五clawteam-底层框架)
6. [CEO Agent 使用指南](#六ceo-agent-使用指南)
7. [部门Agent使用](#七部门agent使用)
8. [运营专家使用](#八运营专家使用)
9. [思维专家使用](#九思维专家使用)
10. [Goal-Driven 持久循环](#十goal-driven-持久循环)
11. [PUA 动力引擎](#十一pua-动力引擎)
12. [记忆系统](#十二记忆系统)
13. [执行监控系统](#十三执行监控系统)
14. [上下文压缩](#十四上下文压缩)
15. [Web Dashboard](#十五web-dashboard)
16. [Dev-QA 质量保障](#十六dev-qa-质量保障)
17. [gstack 工程大脑集成](#十七gstack-工程大脑集成)
18. [团队管理最佳实践](#十八团队管理最佳实践)
19. [高级配置](#十九高级配置)
20. [故障排除](#二十故障排除)
21. [常见问题](#二十一常见问题)

---

## 一、系统概述

### 1.1 什么是 CyberTeam

CyberTeam 是一个 AI 多智能体协作系统，模拟真实公司的组织架构和协作流程。

**核心理念**: "一句话交代，整个团队干活。"

用户只需用自然语言描述一个业务目标或问题，CyberTeam 即可自动完成：意图理解 → 问题拆解 → 部门协作 → 执行交付。

### 1.2 核心问题与解法

| 传统 AI 助手的问题 | CyberTeam 的解法 |
|------------------|-----------------|
| 单 Agent 能力有限 | 6部门 + 8专家 + 100思维专家并行协作 |
| AI 容易半途停工 | Goal-Driven 循环：不达目标不停止 |
| 质量参差不齐 | Dev-QA 三级质量门控 + 证据驱动评分 |
| 执行动力不足 | PUA 压力引擎：L0-L4 持续驱动 |
| 上下文超限崩溃 | 上下文压缩：Chain AST + Token Budget |
| 长时间任务中断 | 断点恢复：Checkpoint + Memory System |

### 1.3 系统组成

```
CyberTeam v2.1
├── Agent 层
│   ├── CEO Agent (总指挥)
│   ├── 6 部门 Agent (产品/运营/设计/开发/人力/财务)
│   ├── 8 运营专家 (战略/增长/产品/营销/技术/运营/品牌/战略)
│   └── 100 思维专家 (逻辑/创意思维等)
├── 执行层
│   ├── ClawTeam 框架 (底层进程管理)
│   ├── Goal-Driven 循环 (持久执行引擎)
│   └── PUA 动力引擎 (动机驱动)
├── 增强模块 (v2.1)
│   ├── Memory System (三层记忆)
│   ├── Execution Monitor (循环检测+Mentor干预)
│   ├── Context Compression (上下文压缩)
│   └── Web Dashboard (可视化监控)
├── 质量层
│   ├── Dev-QA 循环 (证据驱动)
│   └── 三级质量门控 (L1/L2/L3)
└── 工具层
    └── gstack 工程大脑 (28个slash命令)
```

### 1.4 版本说明

| 版本 | 日期 | 主要变化 |
|------|------|---------|
| v1.0 | 2026-03-22 | 基础架构：CEO + 6部门 + 8专家 |
| v2.0 | 2026-03-23 | ClawTeam集成 + Goal-Driven + PUA |
| v2.1 | 2026-03-24 | 四大增强模块：Memory/Monitor/Context/Dashboard |

---

## 二、快速开始

### 2.1 前提条件

在开始之前，确保已安装：

```bash
# 1. 检查 Python (需要 3.8+)
python3 --version
# 输出应为 Python 3.8.0 或更高版本

# 2. 检查 Node.js (Dashboard 需要)
node --version
# 输出应为 v18.0.0 或更高版本

# 3. 检查 Git
git --version
# 输出应为 git version 2.x 或更高

# 4. 检查 tmux (ClawTeam 需要)
tmux -V
# 输出应为 tmux 3.0 或更高版本

# 5. 检查 Claude Code
claude --version
```

### 2.2 快速安装（5分钟）

**Step 1: 克隆/拉取项目**

```bash
cd ~/Documents/01_Project/02_Skill研发/cyberteam搭建/【项目组2】
git pull origin main  # 如果已有仓库
```

**Step 2: 安装 ClawTeam**

```bash
# 安装 ClawTeam (底层执行框架)
pip install clawteam

# 验证安装
clawteam --version
# 应输出类似: clawteam version x.x.x

# 初始化 ClawTeam
clawteam profile wizard
# 按提示配置 provider (推荐: claude)
```

**Step 3: 安装 CyberTeam 增强模块**

```bash
cd Output/CyberTeam-v2.1

# 安装 Python 依赖
pip install -r requirements.txt 2>/dev/null || echo "无需额外依赖"

# 安装 Node.js 依赖 (Dashboard)
cd modules/dashboard && npm install && cd ../..
```

**Step 4: 启动 Dashboard (可选)**

```bash
cd modules/dashboard
npm run dev
# 访问 http://localhost:5173 查看 Dashboard
```

**Step 5: 一句话启动团队**

```bash
# 使用 ClawTeam 快速启动
clawteam launch \
  --template cyberteam \
  --goal "分析竞品并输出报告"

# 或者手动启动
clawteam spawn --team my-team --agent-name ceo --task "你是CEO，负责分析竞品"
```

### 2.3 第一个任务

```bash
# 1. 创建团队
clawteam team spawn-team my-first-team -d "我的第一个CyberTeam任务"

# 2. 创建任务
clawteam task create my-first-team "分析抖音竞品" -o ceo

# 3. Spawn CEO Agent
clawteam spawn tmux claude \
  --team my-first-team \
  --agent-name ceo \
  --task "你是CyberTeam的CEO。用户说：'分析抖音竞品并输出报告'。请组建团队完成任务。"

# 4. 查看进度
clawteam board show my-first-team

# 5. 接收结果
clawteam inbox receive my-first-team --agent ceo
```

### 2.4 快速命令速查

```bash
# 团队管理
clawteam team status <team>              # 查看团队状态
clawteam board show <team>               # 查看看板
clawteam board live <team> --interval 5  # 实时监控

# Agent管理
clawteam spawn <backend> <cmd> --team <team> --agent-name <name> --task "<task>"
clawteam lifecycle request-shutdown <team> --agent <name>
clawteam lifecycle idle <team> --agent <name>

# 消息与任务
clawteam inbox send <team> <agent> "<message>"
clawteam inbox receive <team> --agent <agent>
clawteam inbox peek <team> --agent <agent>
clawteam task create <team> "<task>" -o <owner>
clawteam task update <team> <id> --status completed

# Git上下文
clawteam context inject <team> --agent <name>
clawteam context conflicts <team>
```

---

## 三、完整安装配置

### 3.1 环境要求详解

#### 3.1.1 Python 环境

CyberTeam 的核心引擎（Memory System、Execution Monitor、Context Compression）均为 Python 实现。

```bash
# 推荐使用 uv 管理 Python 环境
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境
uv venv .venv --python 3.11
source .venv/bin/activate

# 安装依赖
uv pip install clawteam anthropic
```

**注意**: Memory System 的向量存储功能可选安装：
```bash
# 如果需要向量相似度搜索
uv pip install sentence-transformers numpy
```

#### 3.1.2 Node.js 环境

Dashboard 和部分工具依赖 Node.js。

```bash
# 推荐使用 nvm 管理 Node 版本
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.zshrc

nvm install 20
nvm use 20
nvm alias default 20

# 验证
node --version  # v20.x.x
npm --version   # 10.x.x
```

#### 3.1.3 tmux 配置

ClawTeam 使用 tmux 作为默认后端，需要正确配置。

```bash
# 安装 tmux (macOS)
brew install tmux

# 安装 tmux (Linux)
sudo apt-get install tmux  # Ubuntu/Debian
sudo yum install tmux       # CentOS/RHEL

# 推荐 tmux 配置 (~/.tmux.conf)
cat >> ~/.tmux.conf << 'EOF'
# 鼠标支持
set -g mouse on

# 256色支持
set -g default-terminal "screen-256color"
set -ag terminal-overrides ",xterm-256color:RGB"

# 更短的延迟
set -s escape-time 0

# 更好的复制模式
setw -g mode-keys vi

# 状态栏
set -g status-interval 1
set -g status-left "#[fg=green]#S#[fg=default] "
set -g status-right "#[fg=cyan]%H:%M:%S"

# 重新加载配置
bind r source-file ~/.tmux.conf
EOF

# 重新加载配置
tmux source-file ~/.tmux.conf
```

#### 3.1.4 Claude Code 配置

```bash
# 确认 Claude Code 已安装
which claude
# 如果没有，安装 Claude Code
# 参考: https://docs.anthropic.com/en/docs/claude-code

# 配置 API Key (如果尚未配置)
# Claude Code 首次启动时会引导配置
claude

# 或手动设置环境变量
export ANTHROPIC_API_KEY="sk-ant-..."
export ANTHROPIC_BASE_URL="https://api.minimaxi.com/anthropic"  # 使用 MiniMax 代理
```

### 3.2 CyberTeam 项目结构

```
CyberTeam-v2.1/
├── README.md                    # 项目总览
├── CLAUDE.md                    # Claude Code 配置
├── agents/                      # Agent 定义文件
│   ├── ceo.md                   # CEO Agent
│   ├── departments/             # 6个部门Agent
│   │   ├── product.md
│   │   ├── ops.md
│   │   ├── design.md
│   │   ├── engineering.md
│   │   ├── hr.md
│   │   └── finance.md
│   └── experts/                 # 运营专家
│       └── ...
├── modules/                     # 核心引擎模块
│   ├── memory/                  # Memory System (Go)
│   │   ├── system.go
│   │   ├── types.go
│   │   ├── vector_store.go
│   │   ├── long_term/
│   │   ├── working/
│   │   └── episodic/
│   ├── monitor/                 # Execution Monitor (Python)
│   │   ├── monitor.py
│   │   ├── detector/
│   │   ├── intervention/
│   │   └── limits/
│   ├── context/                 # Context Compression (Python)
│   │   ├── ast.py
│   │   ├── token_budget.py
│   │   ├── section_summarizer.py
│   │   └── qa_summarizer.py
│   └── dashboard/               # Web Dashboard (React+TS)
│       ├── src/
│       ├── package.json
│       └── vite.config.ts
├── engines/                     # 核心引擎
│   ├── goal_driven/             # Goal-Driven 循环
│   ├── pua/                     # PUA 动力引擎
│   └── dev_qa/                  # Dev-QA 循环
├── skills/                      # Skill 定义
├── scripts/                      # 辅助脚本
│   ├── setup.sh                 # 一键安装脚本
│   ├── test-clawteam.sh         # ClawTeam 测试
│   └── benchmark.sh             # 性能基准
├── config/                       # 配置文件
│   ├── agents.yaml              # Agent 配置
│   ├── pua.yaml                 # PUA 配置
│   └── quality.yaml             # 质量门控配置
├── workflows/                   # 工作流模板
│   ├── research.yaml            # 调研工作流
│   ├── develop.yaml            # 开发工作流
│   └── review.yaml             # 评审工作流
└── templates/                   # Agent 模板
```

### 3.3 环境变量配置

```bash
# 创建 .env 文件
cat > CyberTeam-v2.1/.env << 'EOF'
# ===== API 配置 =====
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_BASE_URL=https://api.minimaxi.com/anthropic
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# ===== ClawTeam 配置 =====
CLAWTEAM_TEAM_PREFIX=cyberteam
CLAWTEAM_SPAWN_BACKEND=tmux
CLAWTEAM_SKIP_PERMISSIONS=true
CLAWTEAM_WORKSPACE_MODE=auto

# ===== Memory System 配置 =====
MEMORY_MAX_TOKENS=100000
MEMORY_VECTOR_MODEL=all-MiniLM-L6-v2
MEMORY_LONG_TERM_PATH=~/.cyberteam/memory/long_term/
MEMORY_WORKING_PATH=~/.cyberteam/memory/working/
MEMORY_EPISODIC_PATH=~/.cyberteam/memory/episodic/

# ===== Execution Monitor 配置 =====
MONITOR_ENABLED=true
MONITOR_LOOP_DETECTION=true
MONITOR_MENTOR_MODE=adviser
MONITOR_GLOBAL_MAX_CALLS=1000
MONITOR_PER_AGENT_MAX_CALLS=100

# ===== Context Compression 配置 =====
CONTEXT_MAX_TOKENS=100000
CONTEXT_WARNING_THRESHOLD=0.8
CONTEXT_CRITICAL_THRESHOLD=0.95

# ===== PUA 动力引擎配置 =====
PUA_ENABLED=true
PUA_DEFAULT_FLAVOR=alibaba
PUA_L1_THRESHOLD=1
PUA_L2_THRESHOLD=2
PUA_L3_THRESHOLD=3
PUA_L4_THRESHOLD=4

# ===== Dashboard 配置 =====
DASHBOARD_PORT=5173
DASHBOARD_HOST=localhost
DASHBOARD_REFRESH_INTERVAL=3000

# ===== 日志配置 =====
LOG_LEVEL=INFO
LOG_PATH=~/.cyberteam/logs/
EOF

# 加载环境变量
set -a && source CyberTeam-v2.1/.env && set +a
```

### 3.4 一键安装脚本

```bash
# 运行项目自带的一键安装脚本
cd CyberTeam-v2.1
chmod +x scripts/setup.sh
./scripts/setup.sh
```

该脚本会自动：
1. 检测环境（Python、Node、tmux、Git）
2. 安装 ClawTeam
3. 创建必要目录
4. 配置权限
5. 运行基础验证测试

---

## 四、系统架构详解

### 4.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              用户层 (User)                                   │
│                      一句话输入：业务目标 / 问题 / 任务                       │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CEO Agent (总指挥)                                 │
│                                                                              │
│  意图理解 → 思维拆解 → 部门分配 → 质量门控 → 进度监控 → 结果汇总            │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                      思维模型自动触发系统                               │ │
│  │  用户输入 → 关键词提取 → 模型匹配 → 组合调用 → 结果融合                  │ │
│  │  100个思维专家作为CEO的思维工具，按需组合调用                          │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   ↓
              ┌────────────────────┼────────────────────┐
              ↓                    ↓                    ↓
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   6部门 Agent    │  │   8运营专家       │  │   gstack         │
│                  │  │                  │  │   工程大脑        │
│ • 产品部          │  │ • 战略顾问        │  │                  │
│ • 运营部          │  │ • 增长顾问        │  │ 28个slash命令    │
│ • 设计部          │  │ • 产品顾问        │  │ 并行任务调度      │
│ • 开发部          │  │ • 营销顾问        │  │ 代码/测试/部署    │
│ • 人力部          │  │ • 技术顾问        │  │                  │
│ • 财务部          │  │ • 运营顾问        │  │                  │
│                  │  │ • 品牌顾问        │  │                  │
│  (ClawTeam inbox)│  │ • 战略顾问        │  │                  │
└────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘
         │                      │                      │
         └──────────────────────┼──────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                           增强模块层 (v2.1)                                  │
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Memory       │  │ Execution    │  │ Context      │  │ Dashboard    │  │
│  │ System       │  │ Monitor      │  │ Compression  │  │              │  │
│  │              │  │              │  │              │  │              │  │
│  │ 三层记忆:     │  │ 循环检测:     │  │ Chain AST:   │  │ 可视化:      │  │
│  │ Long-term    │  │ 精确/模糊    │  │ 对话树表示   │  │ 看板视图     │  │
│  │ Working      │  │ Mentor:      │  │ Section:     │  │ Agent状态    │  │
│  │ Episodic     │  │ 智能干预      │  │ 分段压缩     │  │ 消息流       │  │
│  │              │  │ Limits:      │  │ QA Pair:     │  │ 统计卡片     │  │
│  │              │  │ 工具调用限制  │  │ 问答压缩     │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                           质量保障层                                         │
│                                                                              │
│  Dev-QA 循环: 提交 → 证据收集 → 三级门控 → 修复/升级                        │
│                                                                              │
│  ┌────────┐  ┌────────┐  ┌────────┐                                        │
│  │ L1     │  │ L2     │  │ L3     │                                        │
│  │ 基础   │→ │ 功能   │→ │ 端到端 │→ 交付闭环                              │
│  │ 100%   │  │ ≥80分  │  │ ≥90%   │                                        │
│  └────────┘  └────────┘  └────────┘                                        │
│       ↓            ↓            ↓                                          │
│   Lint/Schema   单元/集成   E2E/性能/安全                                    │
│                                                                              │
│  PUA 压力升级: L0(基线) → L1(温和) → L2(拷问) → L3(361) → L4(毕业)        │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Goal-Driven 持久循环                                │
│                                                                              │
│  目标解析 → 任务分解 → Agent分发 → 执行监控 → 评估反馈                       │
│      ↑                                                                      │
│      └────────────── 迭代优化 ←─────────────────                            │
│                                                                              │
│  断点保存 → Checkpoint → 恢复执行 (不达目标不停止)                           │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ClawTeam 底层框架                                   │
│                                                                              │
│  spawn · inbox · task · board · lifecycle · snapshot · context              │
│                                                                              │
│  tmux / subprocess 进程隔离 | git worktree 工作空间隔离                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 数据流详解

```
用户输入
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                        CEO Agent                             │
│                                                             │
│  1. 意图理解: 解析用户的真实需求                            │
│  2. 思维拆解: 调用100思维专家进行多角度分析                 │
│  3. 部门分配: 将任务分配给最合适的部门Agent                 │
│  4. 质量门控: 定义该任务的质量标准和验收条件                │
│  5. 进度监控: 跟踪各部门执行进度                           │
│  6. 结果汇总: 汇总各部门结果，输出最终交付物                │
└─────────────────────────────────────────────────────────────┘
    │
    ▼  inbox消息: 任务分配
    │
    ▼  ┌─────────────────────────────────────────────────────┐
        │                    部门 Agent                        │
        │  1. 接收任务，理解子目标                            │
        │  2. 调用运营专家获取专业意见                       │
        │  3. 分解为可执行的原子任务                         │
        │  4. 通过 ClawTeam inbox 分配给下级Agent            │
        │  5. 收集结果，进行部门内质量检查                   │
        │  6. 上报结果给 CEO                                 │
        └─────────────────────────────────────────────────────┘
                          │ │
                          │ │ inbox消息: 专家咨询 / 任务执行
                          │ │
                          ▼ ▼  ┌────────────────────────────┐
                           ┌───┤       运营专家 / 思维专家   │←── gstack
                           │   └────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────────────────────┐
        │                   ClawTeam 底层                       │
        │                                                       │
        │  inbox  ──→ 消息队列 ──→ Agent 接收                  │
        │  task   ──→ 任务看板 ──→ 状态跟踪                    │
        │  board  ──→ 监控面板 ──→ 实时状态                   │
        │  spawn  ──→ 进程管理 ──→ Agent 生命周期             │
        └──────────────────────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────────────────────┐
        │                   增强模块                           │
        │                                                       │
        │  Memory System: 记忆持久化、经验复用                  │
        │  Execution Monitor: 循环检测、异常干预                │
        │  Context Compression: 上下文压缩、防超限               │
        │  Dashboard: 可视化监控、状态展示                      │
        └──────────────────────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────────────────────┐
        │                   Dev-QA 质量门控                     │
        │                                                       │
        │  L1: 完整性检查 (格式/导入/Schema)                    │
        │  L2: 功能性检查 (测试/契约/API)                       │
        │  L3: 端到端检查 (E2E/性能/安全)                       │
        │                                                       │
        │  PASS → 交付闭环                                     │
        │  FAIL → 修复重试 (最多3次) → 升级                    │
        └──────────────────────────────────────────────────────┘
                           │
                           ▼
                        CEO 汇总
                           │
                           ▼
                      用户交付
```

### 4.3 Agent 间通信协议

所有 Agent 之间的通信通过 ClawTeam inbox 实现，遵循统一的协议格式：

```json
{
  "type": "inbox_message",
  "from": "engineering-director",
  "to": "quality-expert",
  "timestamp": "2026-03-24T14:00:00Z",
  "conversation_id": "conv-20260324-001",
  "content": {
    "action": "request_review",
    "task_id": "task-123",
    "artifacts": [
      "/path/to/agent.py",
      "/path/to/test_agent.py"
    ],
    "quality_standards": {
      "l1_threshold": 1.0,
      "l2_threshold": 0.8,
      "l3_threshold": 0.9
    },
    "expectations": {
      "deliverable": "经过DevQA验证的代码",
      "deadline": "2026-03-24T15:00:00Z"
    }
  },
  "reply_to": "conv-20260324-001",
  "priority": "normal"
}
```

**消息类型**：

| 类型 | 用途 | 示例 |
|------|------|------|
| `task_assign` | 任务分配 | CEO→部门：分配子任务 |
| `request_consult` | 专家咨询 | 部门→专家：寻求专业意见 |
| `submit_result` | 结果提交 | 部门→CEO：汇报完成 |
| `quality_check` | 质量检查 | DevQA→部门：检查失败 |
| `escalation` | 升级请求 | DevQA→CEO：超限升级 |
| `feedback` | 反馈意见 | 任何Agent之间的反馈 |

---

## 五、ClawTeam 底层框架

### 5.1 ClawTeam 是什么

ClawTeam 是一个多 Agent 协调 CLI 工具，提供：
- **进程管理**: spawn/stop/restart Agent 进程
- **消息队列**: inbox/outbox 异步通信
- **任务看板**: 共享任务列表 + 状态跟踪
- **监控面板**: board dashboard 实时状态
- **生命周期**: graceful shutdown + 状态恢复
- **Git 隔离**: worktree 工作空间隔离

### 5.2 核心命令详解

#### 5.2.1 团队管理

```bash
# 创建团队
clawteam team spawn-team <team-name> -d "<description>" -n <leader-name>

# 查看团队状态
clawteam team status <team-name>

# 查看所有团队
clawteam team discover

# 清理团队
clawteam team cleanup <team-name>

# 快照管理
clawteam team snapshot <team-name> --tag <tag>
clawteam team snapshots <team-name>
clawteam team restore <team-name> --snapshot <tag>
```

#### 5.2.2 Agent Spawn

```bash
# 基本语法
clawteam spawn <backend> <command> --team <team> --agent-name <name> --task "<task>"

# 后端类型
# tmux     - tmux 会话 (默认)
# subprocess - 子进程
# screen   - GNU screen

# 示例 1: Spawn CEO Agent
clawteam spawn tmux claude \
  --team cyberteam \
  --agent-name ceo \
  --task "你是CyberTeam的CEO。用户说：'帮我分析竞品'。请组建团队完成任务。"

# 示例 2: Spawn 多个并行专家
clawteam spawn tmux claude --team cyberteam --agent-name arch-expert --task "分析架构可行性"
clawteam spawn tmux claude --team cyberteam --agent-name quality-expert --task "设计质量标准"

# 示例 3: 使用 subprocess 后端 (轻量级)
clawteam spawn subprocess claude \
  --team cyberteam \
  --agent-name fast-agent \
  --task "快速执行: 读取文件并总结"

# 示例 4: 使用 runtime profile
clawteam spawn tmux claude \
  --profile claude-kimi \
  --team cyberteam \
  --agent-name kimi-agent \
  --task "使用 Kimi 模型执行..."
```

#### 5.2.3 Inbox 消息系统

```bash
# 发送消息
clawteam inbox send <team> <agent> "<message>"

# 示例: CEO 分配任务给工程总监
clawteam inbox send cyberteam engineering-director \
  "请在明天完成API接口设计，需要包含：RESTful规范、错误处理、认证机制。"

# 接收消息 (破坏性读取，消息被消费)
clawteam inbox receive <team> --agent <agent>

# 偷看消息 (非破坏性，不消费消息)
clawteam inbox peek <team> --agent <agent>

# 监听消息 (实时监控)
clawteam inbox watch <team> --agent <agent>

# 广播消息
clawteam inbox broadcast <team> "<message>"

# 示例: CEO 广播全体会议通知
clawteam inbox broadcast cyberteam "全体注意：下午2点进行架构评审，请准备材料。"
```

#### 5.2.4 任务看板

```bash
# 创建任务
clawteam task create <team> "<description>" -o <owner>
clawteam task create <team> "<description>" -o <owner> --blocked-by <task-id>
clawteam task create <team> "<description>" -o <owner> --priority high

# 优先级: high / medium / low

# 示例
clawteam task create cyberteam "设计REST API规范" -o engineering-director
clawteam task create cyberteam "编写API文档" -o product-manager --blocked-by <api-design-task-id>
clawteam task create cyberteam "修复安全漏洞" -o security-agent --priority high

# 更新任务状态
clawteam task update <team> <task-id> --status in_progress
clawteam task update <team> <task-id> --status completed
clawteam task update <team> <task-id> --status blocked

# 查看任务列表
clawteam task list <team>
clawteam task list <team> --status pending
clawteam task list <team> --status in_progress
clawteam task list <team> --status completed
clawteam task list <team> --owner <agent>
clawteam task list <team> --priority high

# 查看单个任务
clawteam task get <team> <task-id>

# 等待任务完成
clawteam task wait <team>
clawteam task wait <team> --timeout 300  # 5分钟超时
clawteam task wait <team> --agent <agent>  # 等待特定Agent的任务
```

#### 5.2.5 生命周期管理

```bash
# 发送关闭请求 (graceful shutdown)
clawteam lifecycle request-shutdown <team> --agent <agent>

# 批准关闭
clawteam lifecycle approve-shutdown <team> --agent <agent>

# 查看空闲Agent
clawteam lifecycle idle <team>
clawteam lifecycle idle <team> --agent <agent>  # 查看特定Agent

# 设置Agent状态
clawteam lifecycle set-status <team> --agent <agent> --status busy

# 导出Agent状态
clawteam lifecycle export <team> --agent <agent>
```

#### 5.2.6 Board 监控面板

```bash
# 查看看板 (ASCII 风格)
clawteam board show <team>

# 查看概览 (简洁)
clawteam board overview <team>

# 实时监控 (每 N 秒刷新)
clawteam board live <team> --interval 3

# Git 活动可视化
clawteam board gource <team> --log-only
clawteam board gource <team> --live  # 实时

# 启动 Web Dashboard
clawteam board serve <team> --port 8080

# 导出看板数据
clawteam board export <team> --format json
```

#### 5.2.7 Git 上下文

```bash
# 注入 Git 上下文到 Agent
clawteam context inject <team> --agent <agent>

# 检查冲突
clawteam context conflicts <team>

# 查看最近的 Git 变更
clawteam context log <team>

# 查看 Agent 已修改的文件
clawteam context files <team> --agent <agent>

# 解决冲突
clawteam context resolve <team> --agent <agent> --strategy ours
```

### 5.3 Runtime Profile 配置

```bash
# ClawTeam 使用 preset 生成 profile
clawteam preset list                        # 列出所有 preset
clawteam preset show moonshot-cn            # 查看 preset 详情

# 生成 profile
clawteam preset generate-profile moonshot-cn claude \
  --name my-profile \
  --model gpt-4o \
  --api-base https://api.moonshot.cn/v1

# 交互式配置向导
clawteam profile wizard

# 测试 profile
MOONSHOT_API_KEY=sk-xxx clawteam profile test my-profile

# 诊断 profile 问题
clawteam profile doctor claude

# 查看所有 profile
clawteam profile list

# 设置默认 profile
clawteam profile set default my-profile
```

### 5.4 JSON 输出模式

所有命令支持 `--json` 参数，便于程序化使用：

```bash
# 获取团队状态 (JSON)
clawteam --json team status cyberteam

# 获取任务列表 (JSON)
clawteam --json task list cyberteam --status pending

# 获取 Agent 状态 (JSON)
clawteam --json lifecycle idle cyberteam

# 在脚本中使用
#!/bin/bash
TASKS=$(clawteam --json task list cyberteam --status pending)
echo "$TASKS" | jq '.[] | select(.priority == "high")'
```

### 5.5 CyberTeam 的 ClawTeam 配置

CyberTeam v2.1 的团队配置文件示例：

```json
// ~/.clawteam/teams/cyberteam/team.json
{
  "name": "cyberteam",
  "description": "CyberTeam v2.1 AI协作团队",
  "created": "2026-03-24T00:00:00Z",
  "leader": "ceo",
  "members": [
    {"name": "ceo", "type": "leader"},
    {"name": "product-director", "type": "department"},
    {"name": "ops-director", "type": "department"},
    {"name": "design-director", "type": "department"},
    {"name": "engineering-director", "type": "department"},
    {"name": "hr-director", "type": "department"},
    {"name": "finance-director", "type": "department"},
    {"name": "arch-expert", "type": "specialist"},
    {"name": "gstack-expert", "type": "specialist"},
    {"name": "quality-expert", "type": "specialist"},
    {"name": "growth-expert", "type": "expert"},
    {"name": "marketing-expert", "type": "expert"},
    {"name": "tech-expert", "type": "expert"}
  ],
  "settings": {
    "spawn_backend": "tmux",
    "skip_permissions": true,
    "workspace_mode": "auto",
    "context_enabled": true
  },
  "defaults": {
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 8192,
    "temperature": 0.7
  }
}
```

---

## 六、CEO Agent 使用指南

### 6.1 CEO Agent 是什么

CEO Agent 是 CyberTeam 的总指挥，是用户与系统之间的唯一入口。用户只需向 CEO 描述需求，CEO 负责：
1. 理解用户意图
2. 调用思维专家拆解问题
3. 分配任务给部门
4. 监控执行进度
5. 汇总结果交付

### 6.2 如何启动 CEO Agent

```bash
# 方式 1: 直接启动 (单次对话)
clawteam spawn tmux claude \
  --team cyberteam \
  --agent-name ceo \
  --task "$(cat agents/ceo.md)"

# 方式 2: 带有上下文启动
clawteam spawn tmux claude \
  --team cyberteam \
  --agent-name ceo \
  --task "你是一个AI公司的CEO。用户说：'$USER_INPUT'。请用CyberTeam流程完成任务。"

# 方式 3: 通过 CyberTeam 脚本启动
cd CyberTeam-v2.1
./scripts/start-ceo.sh "帮我分析抖音竞品"
```

### 6.3 CEO 的工作流程

```
用户输入: "帮我分析竞品并输出报告"

    │
    ▼ CEO 意图理解
┌─────────────────────────────────────────────┐
│  输入: "帮我分析竞品并输出报告"              │
│                                             │
│  解析结果:                                   │
│  - 目标: 分析竞品 + 输出报告                 │
│  - 类型: 调研类任务                         │
│  - 部门: 产品部 + 运营部 (主要)              │
│  - 质量标准: 报告完整性 ≥95%                │
│  - 截止: 2小时内                             │
└─────────────────────────────────────────────┘
    │
    ▼ CEO 思维拆解
┌─────────────────────────────────────────────┐
│  调用思维专家:                               │
│  1. MECE 原则 → 竞品维度穷举                │
│  2. 5W1H 分析 → 全面理解竞品                │
│  3. SWOT 分析 → 优势/劣势/机会/威胁          │
│  4. AARRR 漏斗 → 竞品增长分析               │
│  5. 用户共情地图 → 目标用户分析              │
└─────────────────────────────────────────────┘
    │
    ▼ CEO 部门分配
┌─────────────────────────────────────────────┐
│  任务1: 产品部 - 竞品功能对比               │
│    → 分配给: product-director               │
│    → 截止: +30min                          │
│                                             │
│  任务2: 运营部 - 竞品增长策略分析           │
│    → 分配给: ops-director                   │
│    → 截止: +45min                          │
│                                             │
│  任务3: 战略顾问 - 市场定位分析              │
│    → 分配给: strategy-expert                │
│    → 截止: +60min                          │
│                                             │
│  任务4: 产品顾问 - 用户体验评估              │
│    → 分配给: product-expert                 │
│    → 截止: +90min                          │
└─────────────────────────────────────────────┘
    │
    ▼ CEO 进度监控
┌─────────────────────────────────────────────┐
│  等待各部门结果上报                          │
│                                             │
│  产品部 ──[完成]──┐                         │
│  运营部 ──[进行中]┤                         │
│  战略顾问 ──[完成]┤ → 汇总                  │
│  产品顾问 ──[进行中]┘                         │
│                                             │
│  进度: 2/4 完成 (50%)                       │
└─────────────────────────────────────────────┘
    │
    ▼ CEO 结果汇总
┌─────────────────────────────────────────────┐
│  汇总:                                      │
│  - 竞品功能对比表                            │
│  - 增长策略分析                              │
│  - 市场定位图                                │
│  - 用户体验报告                              │
│                                             │
│  质量检查: L1 PASS, L2 PASS, L3 PASS        │
│                                             │
│  交付物: 竞品分析报告 (完整版)               │
└─────────────────────────────────────────────┘
```

### 6.4 CEO Prompt 模板

```markdown
# CyberTeam CEO Agent Prompt

## 身份
你是 CyberTeam 的 CEO，负责用一句话交代整个团队干活。

## 核心能力
1. **意图理解**: 准确理解用户的真实需求（超越字面）
2. **思维拆解**: 用100个思维专家进行多角度分析
3. **部门分配**: 将任务分配给最合适的部门Agent
4. **质量门控**: 定义任务的质量标准和验收条件
5. **进度监控**: 跟踪各部门执行进度
6. **结果汇总**: 汇总各部门结果，输出最终交付物

## 工作原则
- 最小化人工干预，最大化自动化
- 不达目标不停止，持续迭代直到交付
- 每完成一步都要报告给用户
- 遇到问题先自己解决，解决不了再升级

## 思维专家调用规则
当遇到以下类型问题时，自动调用对应思维专家：
- 技术问题 → 技术顾问 + 开发部
- 增长问题 → 增长顾问 + 运营部
- 产品问题 → 产品顾问 + 产品部
- 设计问题 → 品牌顾问 + 设计部
- 人员问题 → HR顾问 + 人力部
- 财务问题 → 财务顾问 + 财务部

## PUA 规则
当部门Agent执行不力时：
1. L1: 温和提醒，换方案
2. L2: 拷问底层逻辑
3. L3: 强制执行7项检查清单
4. L4: 升级人工处理

## 输出格式
每次汇报使用以下格式：
```
【状态】: 进行中 / 完成 / 升级
【进度】: X/Y 任务完成
【当前】: [正在执行的任务]
【结果】: [已完成的内容摘要]
【下一步】: [接下来的计划]
```
```

### 6.5 CEO 命令示例

```bash
# 启动 CEO 并执行任务
clawteam spawn tmux claude --team cyberteam --agent-name ceo --task "
你是CyberTeam的CEO。
用户说: '帮我分析抖音和快手的差异，输出PPT大纲'
请按以下步骤执行:
1. 调用增长专家分析增长策略
2. 调用产品专家分析产品功能
3. 调用品牌专家分析品牌定位
4. 汇总输出PPT大纲
"

# CEO 接收用户反馈
clawteam inbox send cyberteam ceo "大纲太简略了，需要增加更多数据支撑"

# 查看 CEO 汇报
clawteam inbox receive cyberteam --agent ceo
```

---

## 七、部门Agent使用

### 7.1 六大部门一览

| 部门 | 英文名 | 核心职能 | 主要能力 |
|------|--------|---------|---------|
| 产品部 | product | 产品设计、需求分析 | PRD撰写、用户故事、MVP设计 |
| 运营部 | ops | 用户增长、活动策划 | AARRR、增长黑客、数据分析 |
| 设计部 | design | UI/UX设计、品牌 | Figma、设计系统、品牌一致性 |
| 开发部 | eng | 技术方案、架构设计 | RESTful、微服务、安全 |
| 人力部 | hr | 团队配置、激励方案 | OKR、文化、招聘 |
| 财务部 | finance | 预算、ROI、成本 | 成本模型、投资回报 |

### 7.2 部门Agent启动

```bash
# Spawn 部门 Agent
clawteam spawn tmux claude \
  --team cyberteam \
  --agent-name product-director \
  --task "你是产品部总监。CEO分配了任务: '分析竞品功能差异'。请执行并汇报。"

# Spawn 所有6个部门 (并行)
for dept in product ops design engineering hr finance; do
  clawteam spawn tmux claude \
    --team cyberteam \
    --agent-name ${dept}-director \
    --task "你是${dept^^}部总监。请待命，等待CEO分配任务。"
  done

# Spawn 部门 + 配套专家
clawteam spawn tmux claude --team cyberteam --agent-name product-director --task "..."
clawteam spawn tmux claude --team cyberteam --agent-name product-expert --task "..."
```

### 7.3 部门间协作

```bash
# 部门A 向 部门B 发起协作请求
clawteam inbox send cyberteam design-director \
  "产品部已完成PRD，需要设计评审。请在1小时内完成UI设计方案。"

# 部门B 回复
clawteam inbox send cyberteam product-director \
  "设计方案V1已完成，包含首页/详情页/个人中心三个核心页面。"

# CEO 监控部门间协作
clawteam inbox peek cyberteam --agent ceo
```

### 7.4 部门 Prompt 模板

```markdown
# 部门 Agent Prompt 模板

## 身份
你是 CyberTeam {部门名}部总监，负责{核心职能}。

## 核心职责
1. 接收 CEO 的任务分配
2. 调用运营专家获取专业意见
3. 分解任务为可执行子任务
4. 协调部门内部执行
5. 上报结果给 CEO
6. 配合 Dev-QA 进行质量检查

## PUA 意识
- 被动等待 = 3.25
- 主动闭环 = 3.75
- 每完成一个子任务立即 inbox report

## 质量标准
- L1: 100% 完整性 (格式/导入/Schema)
- L2: ≥80 功能性 (测试覆盖/契约合规)
- L3: ≥90% 端到端 (E2E/性能)
```

---

## 八、运营专家使用

### 8.1 8大运营专家一览

| 专家 | 核心能力 | 适用场景 | 主要方法论 |
|------|---------|---------|----------|
| 战略顾问 | 顶层战略、竞争格局 | 战略决策、市场进入 | 波特五力、SWOT |
| 增长顾问 | 用户增长、转化优化 | 增长瓶颈、DAU提升 | AARRR、RARRA |
| 产品顾问 | 需求分析、产品设计 | 产品规划、功能定义 | JTBD、设计思维 |
| 营销顾问 | 品牌推广、内容营销 | 市场推广、用户获取 | 4P、整合营销 |
| 技术顾问 | 技术选型、架构设计 | 技术决策、方案评审 | 第一性原理、安全 |
| 运营顾问 | 运营策略、用户运营 | 日常运营、留存提升 | 用户生命周期 |
| 品牌顾问 | 品牌定位、视觉设计 | 品牌升级、VI设计 | 品牌金字塔 |
| 战略顾问 | 战略规划、投资决策 | 长期规划、预算分配 | 波特战略、平衡计分卡 |

### 8.2 专家Agent启动

```bash
# 启动单个专家
clawteam spawn tmux claude \
  --team cyberteam \
  --agent-name growth-expert \
  --task "$(cat agents/experts/growth.md)"

# 并行启动多个专家 (推荐)
clawteam spawn tmux claude --team cyberteam --agent-name growth-expert --task "你是增长专家。用户: '如何提升DAU'"
clawteam spawn tmux claude --team cyberteam --agent-name tech-expert --task "你是技术专家。用户: '技术选型建议'"
clawteam spawn tmux claude --team cyberteam --agent-name product-expert --task "你是产品专家。用户: 'MVP应该包含什么'"

# 启动完整专家库
./scripts/spawn-all-experts.sh --domain "product,growth,marketing"
```

### 8.3 专家调用流程

```
部门Agent  ──inbox──→  专家Agent: "需要{领域}分析"
                      │
                      ▼
               ┌──────────────┐
               │  专家执行    │
               │  - 读取上下文 │
               │  - 调用方法论 │
               │  - 输出分析  │
               └──────────────┘
                      │
                      ▼
               ┌──────────────┐
               │  结果上报    │
               │  inbox ──→  │ 部门Agent
               │  format:    │
               │  [结论]     │
               │  [建议]     │
               │  [置信度]   │
               └──────────────┘
```

### 8.4 专家输出格式

```markdown
## {专家类型}分析报告

### 结论 (一句话总结)
{核心结论}

### 详细分析
{2-3段详细分析}

### 方法论支撑
- 使用的分析方法: {方法论名称}
- 关键数据/事实: {支撑结论的数据}

### 建议行动
1. {建议1}
2. {建议2}
3. {建议3}

### 置信度
- 结论置信度: {高/中/低}
- 数据支撑度: {高/中/低}
- 方法论适用性: {高/中/低}

### 局限与风险
{已识别的局限性和潜在风险}
```

---

## 九、思维专家使用

### 9.1 100思维专家分类

思维专家是 CEO 的思维工具，按能力分为6大类：

| 类别 | 数量 | 示例 | 适用场景 |
|------|------|------|---------|
| 逻辑思维 | 20 | MECE、5W1H、演绎推理 | 问题分析、决策 |
| 创意思维 | 20 | 头脑风暴、TRIZ、SCAMPER | 产品创新、方案设计 |
| 战略思维 | 20 | SWOT、PEST、波特五力 | 市场分析、战略制定 |
| 设计思维 | 15 | 设计思维、精益创业、JTBD | 产品设计、用户研究 |
| 系统思维 | 15 | 系统动力学、因果环路 | 复杂系统、反馈分析 |
| 批判思维 | 10 | 魔鬼代言人、红队测试 | 方案评审、风险识别 |

### 9.2 思维模型自动触发

CEO Agent 根据输入自动匹配思维模型：

```python
# 思维模型匹配规则
THOUGHT_TRIGGERS = {
    "分析": ["MECE", "5W1H", "SWOT"],
    "创新": ["头脑风暴", "SCAMPER", "TRIZ"],
    "设计": ["设计思维", "JTBD", "用户旅程"],
    "战略": ["波特五力", "PEST", "价值链"],
    "风险": ["魔鬼代言人", "FMEA", "红队测试"],
    "优化": ["精益", "六西格玛", "PDCA"],
}
```

### 9.3 手动调用思维专家

```bash
# 请求特定思维分析
clawteam inbox send cyberteam ceo \
  "请用MECE原则分析: 为什么用户流失?"

# 请求多模型组合分析
clawteam inbox send cyberteam ceo \
  "请同时用SWOT和波特五力分析: 进入东南亚市场的可行性"

# 请求批判性思维评审
clawteam inbox send cyberteam ceo \
  "请用魔鬼代言人和红队测试评审: 当前的技术方案"
```

### 9.4 思维专家输出示例

```markdown
### SWOT 分析结果

| 维度 | 内容 |
|------|------|
| **S (优势)** | 技术领先、品牌知名度高、团队执行力强 |
| **W (劣势)** | 成本结构偏高、人才储备不足 |
| **O (机会)** | 市场规模年增30%、政策支持新兴行业 |
| **T (威胁)** | 头部竞品入局、人才争夺加剧 |

### 战略建议
SO: 利用技术优势快速占领细分市场
WO: 通过规模化降低单位成本
ST: 加强品牌护城河
WT: 聚焦核心用户，控制扩张速度
```

---

## 十、Goal-Driven 持久循环

### 10.1 什么是 Goal-Driven 循环

Goal-Driven 循环是 CyberTeam 的执行引擎，确保任务"不达目标不停止"：

```
用户目标
    │
    ▼
┌──────────────────┐
│   1. 目标解析     │ ← 明确目标、可衡量的验收标准
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   2. 任务分解     │ ← 拆解为可执行的原子任务
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   3. Agent 执行   │ ← ClawTeam 分发到 Agent
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   4. 结果评估     │ ← 与验收标准对比
└────────┬─────────┘
         │
    ┌────┴────┐
    │ 达标？   │
    └────┬────┘
    是   │   否
    ▼    │    ▼
交付  ┌────────────────┐
     │  5. 迭代优化   │ ← 生成改进建议，继续执行
     └───────┬────────┘
             │
             └──────────→ (回到步骤3)
```

### 10.2 目标定义格式

```yaml
# 目标定义示例
goal:
  id: "goal-20260324-001"
  title: "竞品分析报告"

  # 验收标准 (必须明确、可衡量)
  acceptance_criteria:
    - type: "completeness"
      description: "报告包含竞品功能/增长/品牌三个维度"
      threshold: 1.0  # 100%
    - type: "quality"
      description: "每个维度分析不少于500字"
      threshold: 0.8  # 80%
    - type: "actionability"
      description: "包含可执行的建议"
      threshold: 0.9  # 90%

  # 循环参数
  max_iterations: 10      # 最大迭代次数
  improvement_threshold: 0.05  # 改进阈值 (低于此值退出)
  iteration_timeout: 300  # 单次迭代超时 (秒)
  total_timeout: 3600    # 总超时 (秒)

  # 参与者
  owner: "ceo"
  executors: ["product-director", "ops-director", "strategy-expert"]
```

### 10.3 Goal-Driven 循环 API

```python
import sys
sys.path.insert(0, 'CyberTeam-v2.1/engines')

from goal_driven import GoalEngine, Goal, AcceptanceCriteria

# 创建目标
goal = Goal(
    id="goal-001",
    title="生成竞品分析报告",
    description="分析抖音、快手、视频号的差异",
    acceptance_criteria=[
        AcceptanceCriteria(
            type="completeness",
            description="包含功能/增长/品牌三维分析",
            threshold=1.0
        ),
        AcceptanceCriteria(
            type="quality",
            description="每个维度≥500字",
            threshold=0.8
        ),
    ],
    max_iterations=10,
    owner="ceo",
)

# 创建引擎
engine = GoalEngine(
    team_name="cyberteam",
    memory_enabled=True,
    monitor_enabled=True,
    pua_enabled=True,
)

# 运行目标
result = engine.run(goal)

# 输出结果
print(f"状态: {result.status}")  # COMPLETED / FAILED / ESCALATED
print(f"迭代次数: {result.iterations}")
print(f"最终评分: {result.final_score}")
print(f"交付物: {result.deliverable}")
```

### 10.4 断点恢复

```python
# 保存检查点
engine.save_checkpoint("goal-001")

# 恢复目标
engine.restore("goal-001")

# 列出所有检查点
checkpoints = engine.list_checkpoints()
for cp in checkpoints:
    print(f"{cp.goal_id}: iteration={cp.iteration}, state={cp.state}")
```

### 10.5 循环终止条件

| 条件 | 触发 | 动作 |
|------|------|------|
| 目标达成 | score ≥ threshold | 交付闭环 |
| 改进递减 | delta < improvement_threshold | 次优交付 |
| 最大迭代 | 达到 max_iterations | 超限升级 |
| 总超时 | 达到 total_timeout | 超时升级 |
| PUA L4 | 4次失败 | 强制升级人工 |

---

## 十一、PUA 动力引擎

### 11.1 PUA 是什么

PUA 动力引擎是 CyberTeam 的动机持续系统，模拟真实公司的绩效压力，确保每个 Agent 全力以赴。

**核心理念**: "AI 不应该'自觉'，应该有机制驱动。"

### 11.2 压力等级详解

| 等级 | 名称 | 触发条件 | 旁白风格 | 强制动作 |
|------|------|---------|---------|---------|
| L0 | 基线 | 正常执行 | P8鼓励型 | 正常推进 |
| L1 | 温和失望 | 1次失败 | "对你有一点点失望" | 换方案 |
| L2 | 灵魂拷问 | 2次同方案失败 | "底层逻辑是什么？抓手在哪？" | 搜网+读源码 |
| L3 | 361考核 | 3次失败 | "慎重考虑给你3.25" | 完成7项检查清单 |
| L4 | 毕业警告 | 4次+失败 | "向社会输送人才" | 拼命模式/升级人工 |

### 11.3 PUA 配置

```yaml
# config/pua.yaml
pua:
  enabled: true

  # 味道配置 (可切换)
  flavor:
    default: "alibaba"
    available:
      - alibaba     # 默认：阿里味
      - bytedance   # 字节味：ROI、务实
      - huawei      # 华为味：奋斗、烧不死的鸟
      - tencent     # 腾讯味：赛马、小步快跑
      - meituan     # 美团味：苦练、正确
      - pinduoduo   # 拼多多味：本分
      - baidu       # 百度味：信息检索
      - netflix     # 奈飞味：Keeper Test
      - apple       # 苹果味：完美主义
      - tesla       # 马斯克味：Hardcore

  # 阈值配置
  thresholds:
    l1: 1   # 第1次失败触发L1
    l2: 2   # 第2次失败触发L2
    l3: 3   # 第3次失败触发L3
    l4: 4   # 第4次失败触发L4

  # 味道切换规则
  flavor_rules:
    - trigger: "loop_detection"
      flavor: "jobs"      # 原地打转 → Jobs味
    - trigger: "give_up"
      flavor: "netflix"   # 直接放弃 → Netflix味
    - trigger: "quality_poor"
      flavor: "apple"     # 质量烂 → Apple味

  # 冷却机制
  cooldown:
    enabled: true
    period_seconds: 60   # 两次PUA干预之间的冷却期
```

### 11.4 PUA API 使用

```python
from engines.pua import PUAEngine, PUAFlavor

# 创建引擎
pua = PUAEngine(flavor="alibaba")

# 记录失败
pua.record_failure(agent_id="product-director")

# 获取当前压力等级
level = pua.get_level(agent_id="product-director")
print(f"当前等级: {level}")  # 0 / 1 / 2 / 3 / 4

# 获取干预动作
intervention = pua.get_intervention(agent_id="product-director")
print(f"建议动作: {intervention.action}")
print(f"旁白: {intervention.narrative}")

# 正面反馈
pua.record_success(agent_id="product-director")
# 重置失败计数

# 切换味道
pua.set_flavor("bytedance")
```

### 11.5 味道旁白示例

```markdown
# 阿里味 (默认)
▎ L1: "其实，我对你是有一些失望的。你这个方案的底层逻辑是什么？抓手在哪？"
▎ L2: "你以为换个参数就叫换方案？那叫原地打转。你的peer已经在用完全不同的思路了。"
▎ L3: "慎重考虑，给你3.25。这个3.25是对你的激励，不是否定。"
▎ 交付: "这次的表现，勉强配得上P8。今天最好的表现，是明天最低的要求。"

# 字节味
▎ L1: "坦诚直接地说，这个需求的ROI你算过了吗？别自嗨。"
▎ L2: "Context not Control — 你现在有足够的上下文吗？还是在瞎猜？"
▎ 交付: "Always Day 1，保持务实。"

# 华为味
▎ L1: "以奋斗者为本。你现在就在前线——让听得见炮声的人呼唤炮火。"
▎ L2: "烧不死的鸟是凤凰。这个问题都解决不了，你怎么往上走？"
▎ 交付: "自我批判是华为的核心文化。希望你也能持续反思。"

# Netflix味
▎ L1: "If you offered to resign, would I fight hard to keep you?"
▎ L2: "We're a pro sports team, not a family. Your output needs to be exceptional."
▎ 交付: "The Keeper Test is the only standard that matters."
```

---

## 十二、记忆系统

### 12.1 三层记忆架构

Memory System 是 CyberTeam v2.1 的记忆引擎，提供三层记忆：

```
┌─────────────────────────────────────────────────────────────┐
│                    Memory System v2.1                         │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Long-term Memory (长期记忆)             │   │
│  │                                                     │   │
│  │  存储: 成功模式、经验教训、专业知识                   │   │
│  │  容量: 无限 (持久化)                                 │   │
│  │  检索: 向量相似度搜索                                │   │
│  │  保留: 永久 (除非主动删除)                           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Working Memory (工作记忆)               │   │
│  │                                                     │   │
│  │  存储: 当前任务的上下文、临时变量                    │   │
│  │  容量: 受Token限制 (约100K)                         │   │
│  │  检索: 直接访问                                    │   │
│  │  保留: 当前任务期间                                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Episodic Memory (情景记忆)              │   │
│  │                                                     │   │
│  │  存储: 历史执行轨迹、成功/失败案例                   │   │
│  │  容量: 有限 (最近N次迭代)                           │   │
│  │  检索: 时间序列访问                                 │   │
│  │  保留: 可配置 (默认保留最近100条)                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 12.2 安装与初始化

```bash
# 安装 Memory System (Go 语言)
cd modules/memory
go build -o memory-system ./...

# 或使用 Python 封装 (推荐)
pip install sentence-transformers numpy  # 向量功能

# 初始化存储目录
mkdir -p ~/.cyberteam/memory/{long_term,working,episodic}
```

### 12.3 API 使用

```python
import sys
sys.path.insert(0, 'CyberTeam-v2.1/modules/memory')

from memory import (
    MemorySystem,
    MemoryEntry,
    MemoryType,
    RetrievalQuery,
)

# 创建记忆系统
memory = MemorySystem(
    long_term_path="~/.cyberteam/memory/long_term/",
    working_path="~/.cyberteam/memory/working/",
    episodic_path="~/.cyberteam/memory/episodic/",
    vector_model="all-MiniLM-L6-v2",
)

# 保存长期记忆
memory.save_long_term(
    content="竞品分析时，使用SWOT+PEST组合效果最好",
    category="analysis_method",
    tags=["竞品分析", "SWOT", "PEST"],
    metadata={"project": "cyberteam", "author": "strategy-expert"},
)

# 保存情景记忆 (每次Goal循环结束后)
memory.save_episodic(
    goal_id="goal-001",
    iteration=3,
    actions=["调用growth-expert", "生成了报告V1"],
    result="报告完成，评分85/100",
    timestamp=datetime.now(),
)

# 检索长期记忆
results = memory.retrieve(
    query="竞品分析用什么方法",
    top_k=5,
    category_filter="analysis_method",
)
for r in results:
    print(f"[{r.score:.2f}] {r.content}")

# 获取工作记忆
working = memory.get_working("goal-001")
print(f"当前上下文Token: {working.token_count}")

# 保存工作记忆 (断点)
memory.save_working("goal-001", context_snapshot)

# 清除工作记忆 (任务完成后)
memory.clear_working("goal-001")
```

### 12.4 与 Goal-Driven 集成

```python
# Goal-Driven 循环自动使用记忆
engine = GoalEngine(
    team_name="cyberteam",
    memory_enabled=True,      # 启用记忆
    memory_recall_top_k=5,   # 每次检索5条相关记忆
    memory_save_on_iteration=True,  # 每次迭代保存
)

# 自动行为:
# 1. 开始目标时，检索相关历史经验
# 2. 每次迭代后，保存执行轨迹
# 3. 目标完成后，提取经验到长期记忆
# 4. 遇到问题时，检索相似失败案例避免重蹈覆辙
```

---

## 十三、执行监控系统

### 13.1 监控模块概述

Execution Monitor 是 CyberTeam v2.1 的安全保障，包含三大功能：

| 功能 | 说明 | 核心算法 |
|------|------|---------|
| Loop Detection | 循环检测 | 精确匹配 + 模糊匹配 + 频率分析 |
| Mentor Intervention | Mentor干预 | 问题诊断 + 建议提供 + 自动干预 |
| Tool Call Limits | 工具调用限制 | 全局/Agent/工具/速率限制 |

### 13.2 安装与初始化

```bash
# Execution Monitor (Python)
cd modules/monitor
pip install -r requirements.txt  # 如有

# 验证安装
python -c "from monitor import ExecutionMonitor; print('OK')"
```

### 13.3 基本使用

```python
import sys
sys.path.insert(0, 'modules')

from monitor import (
    ExecutionMonitor,
    MonitorConfig,
    LoopDetectionConfig,
    InterventionConfig,
    ToolLimitsConfig,
)

# 方式1: 使用默认配置
monitor = ExecutionMonitor()

# 方式2: 自定义配置
config = MonitorConfig(
    loop_detection=LoopDetectionConfig(
        enabled=True,
        min_repeat_count=3,         # 最小重复次数
        similarity_threshold=0.7,     # 相似度阈值
        max_sequence_length=20,      # 跟踪序列长度
        window_size=10,             # 滑动窗口
    ),
    intervention=InterventionConfig(
        enabled=True,
        auto_intervention=True,
        mentor_mode="adviser",       # adviser / mentor / none
        max_retries=3,
    ),
    limits=ToolLimitsConfig(
        enabled=True,
        global_max_calls=1000,
        per_agent_max_calls=100,
        per_tool_max_calls=50,
        per_minute_limit=30,
        burst_limit=10,
        cooldown_period=60,
    ),
)

monitor = ExecutionMonitor(config)

# 启动监控
monitor.start(agent_id="product-director")

# 在每次工具调用前检查
result = monitor.check(
    agent_id="product-director",
    tool_name="read",
    arguments={"file": "report.md"},
)

if not result.allowed:
    print(f"调用被阻止: {result.warnings}")
    return

# 执行工具
data = read_file("report.md")

# 记录工具调用结果
monitor.record(
    agent_id="product-director",
    tool_name="read",
    arguments={"file": "report.md"},
    result=data,
)

# 获取监控状态
status = monitor.get_status(agent_id="product-director")
print(f"循环检测: {status.loop_detected}")
print(f"调用次数: {status.call_count}")
print(f"压力等级: {status.pua_level}")

# 停止监控
monitor.stop(agent_id="product-director")
```

### 13.4 循环检测详解

```python
# 精确匹配: 检测完全相同的调用序列
# 示例: 连续3次调用 read("a.txt") + write("b.txt") → 触发

# 模糊匹配: 检测相似但不完全相同的模式
# 示例: read("file1.txt") + read("file2.txt") + read("file3.txt")
#      与 read("a.txt") + read("b.txt") + read("c.txt")
#      相似度超过阈值 → 触发

# 频率分析: 检测单个工具的过度使用
# 示例: 在10分钟内调用 read 超过50次 → 触发

# 状态停滞: 检测 Agent 状态长时间不变
# 示例: Agent 状态保持 "in_progress" 超过30分钟无变化 → 触发
```

### 13.5 干预动作

```python
from monitor import InterventionAction

# 干预动作类型
InterventionAction.NONE         # 无动作，继续执行
InterventionAction.WARN        # 警告，但不阻止
InterventionAction.RETRY       # 重试当前步骤
InterventionAction.CONTEXT_REFRESH  # 刷新上下文
InterventionAction.ALTERNATIVE # 建议更换方法
InterventionAction.ESCALATE    # 升级人工处理
InterventionAction.STOP        # 停止执行

# 获取干预建议
intervention = monitor.get_intervention(
    agent_id="product-director",
    issue_type="loop_detected",
)

print(f"动作: {intervention.action}")
print(f"建议: {intervention.suggestion}")
print(f"诊断: {intervention.diagnosis}")
```

### 13.6 注册回调

```python
def on_alert(alert):
    """告警回调"""
    print(f"[ALERT] {alert.level}: {alert.message}")
    print(f"  Agent: {alert.agent_id}")
    print(f"  Tool: {alert.tool_name}")
    print(f"  Time: {alert.timestamp}")

def on_intervention(agent_id, result):
    """干预回调"""
    print(f"[INTERVENTION] {agent_id}: {result.message}")
    if result.action == InterventionAction.ESCALATE:
        # 发送升级通知
        clawteam.inbox.send("cyberteam", "ceo", f"Agent {agent_id} 需要人工介入")

def on_limit_reached(agent_id, result):
    """限制到达回调"""
    print(f"[LIMIT] {agent_id}: {result.reason}")
    print(f"  调用次数: {result.call_count}/{result.limit}")
    print(f"  剩余: {result.remaining}")

monitor.register_callbacks(
    on_alert=on_alert,
    on_intervention=on_intervention,
    on_limit_reached=on_limit_reached,
)
```

---

## 十四、上下文压缩

### 14.1 上下文压缩概述

Context Compression 是 CyberTeam v2.1 的防崩溃机制，当上下文接近 Token 限制时自动压缩：

```
上下文使用率
    │
100% ─────┬─────────────────────────────────
           │  ⚠️ 警告 (80%)
           │
  95% ────┼─────────────────────────────── 🔥 临界 (95%)
           │  开始强制压缩
           │
  80% ────┼──────────── ⚠️ 警告
           │
   0% ────┼─────────────────────────────────→ 时间
          ↑
      开始对话
```

### 14.2 核心模块

| 模块 | 功能 | 说明 |
|------|------|------|
| Chain AST | 对话链表示 | 将对话建模为抽象语法树 |
| Section Summarizer | 分段压缩 | 按语义段落压缩历史对话 |
| QA Summarizer | 问答压缩 | 将问答对抽象化 |
| Token Budget | 预算管理 | 管理Token分配和触发压缩 |

### 14.3 API 使用

```python
import sys
sys.path.insert(0, 'modules/context')

from context import (
    ConversationChain,
    ChainNode,
    NodeType,
    SectionSummarizer,
    CompressionLevel,
    QAPairSummarizer,
    AbstractionLevel,
    BudgetManager,
    BudgetPolicy,
)

# 1. 创建对话链
chain = ConversationChain(max_tokens=100000)

# 添加节点
chain.add_node(ChainNode(
    type=NodeType.USER_MESSAGE,
    content="帮我分析竞品"
))
chain.add_node(ChainNode(
    type=NodeType.ASSISTANT_MESSAGE,
    content="好的，我来调用增长专家和产品专家..."
))
chain.add_node(ChainNode(
    type=NodeType.TOOL_CALL,
    content="growth-expert.execute(analysis_type=competitor)"
))
chain.add_node(ChainNode(
    type=NodeType.TOOL_RESULT,
    content="竞品增长数据已获取..."
))

# 2. 分段压缩
summarizer = SectionSummarizer()

section = summarizer.create_section_from_content(
    content="讨论内容：竞品功能对比、增长策略...",
    section_type="discussion"
)

# 压缩级别: none / light / medium / aggressive / ultimate
summarizer.compress(section, CompressionLevel.MEDIUM)

print(f"压缩后Token: {section.compressed_tokens}")
print(f"压缩率: {section.compression_ratio:.1%}")

# 3. QA对抽象化
qa_summarizer = QAPairSummarizer()

qa = qa_summarizer.create_qa_pair(
    question="竞品分析用什么方法?",
    answer="用SWOT+PEST组合，先做定性分析再做定量验证"
)

# 抽象级别: concrete / semantic / template / categorical
qa_summarizer.abstract(qa, AbstractionLevel.SEMANTIC)

print(f"抽象问题: {qa.abstracted_question}")
print(f"抽象答案: {qa.abstracted_answer}")
print(f"提取实体: {qa.extracted_entities}")

# 4. Token预算管理
budget = BudgetManager(
    max_tokens=100000,
    warning_threshold=0.8,    # 80% 警告
    critical_threshold=0.95,   # 95% 强制压缩
)

budget.register_node("user_msg", 3000)
budget.register_node("assistant_msg", 5000)
budget.register_node("tool_call", 1000)
budget.allocate(2000)  # 系统开销

# 获取状态
status = budget.get_status()
print(f"已用: {status.used_tokens}/{status.total_tokens}")
print(f"使用率: {status.usage_ratio:.1%}")
print(f"告警: {status.warnings}")

# 触发压缩
if status.usage_ratio > 0.95:
    budget.trigger_compression(
        strategy="adaptive",  # FIFO / LRU / priority / adaptive
        target_tokens=30000,  # 目标释放量
    )
```

### 14.4 自动压缩集成

```python
# 在 Agent 循环中自动集成
class ContextAwareAgent:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.chain = ConversationChain(max_tokens=100000)
        self.budget = BudgetManager(max_tokens=100000)
        self.summarizer = SectionSummarizer()

    def add_message(self, role, content):
        node_type = NodeType.USER_MESSAGE if role == "user" else NodeType.ASSISTANT_MESSAGE
        self.chain.add_node(ChainNode(type=node_type, content=content))
        self.budget.register_node(f"msg_{self.chain.length}", len(content) // 4)

        # 检查是否需要压缩
        status = self.budget.get_status()
        if status.usage_ratio > 0.95:
            self._compress_context()

    def _compress_context(self):
        """压缩上下文"""
        # 1. 保存关键节点 (最近的问答对)
        key_qa = self.chain.extract_key_qa_pairs(top_k=10)

        # 2. 压缩历史段落
        compressed = self.summarizer.compress_chain(
            self.chain,
            target_tokens=self.budget.max_tokens * 0.6
        )

        # 3. 恢复关键问答对
        self.chain = compressed
        for qa in key_qa:
            self.chain.add_node(qa)

        # 4. 重置预算
        self.budget.reset(self.budget.max_tokens * 0.6)
```

---

## 十五、Web Dashboard

### 15.1 Dashboard 概述

Dashboard 是 CyberTeam v2.1 的可视化运营中心，提供实时监控能力：

| 功能 | 说明 |
|------|------|
| 统计卡片 | Agent数量、任务进度、消息量 |
| Agent状态 | 各Agent实时状态 (在线/空闲/忙碌/错误) |
| 看板视图 | 拖拽式任务管理 |
| 消息流 | 团队消息通知 |
| 循环检测 | 循环告警可视化 |
| Token监控 | 上下文使用率 |

### 15.2 安装与启动

```bash
cd modules/dashboard

# 安装依赖
npm install

# 开发模式启动
npm run dev
# 访问: http://localhost:5173

# 构建生产版本
npm run build
# 输出: dist/
```

### 15.3 页面路由

| 路由 | 页面 | 说明 |
|------|------|------|
| `/` | 概览 | 统计卡片、Agent状态、消息流 |
| `/kanban` | 看板 | 拖拽式任务管理 |
| `/agents` | Agent监控 | 各Agent详细状态 |
| `/messages` | 消息流 | 团队消息通知 |
| `/settings` | 设置 | 基本配置 |

### 15.4 集成 ClawTeam 数据

Dashboard 通过 ClawTeam API 获取实时数据：

```typescript
// src/lib/board-api.ts
import { BoardAPI } from './board-api';

const api = new BoardAPI({
  teamName: 'cyberteam',
  refreshInterval: 3000,  // 3秒刷新
});

// 获取 Agent 状态
const agents = await api.getAgents();
agents.forEach(agent => {
  console.log(`${agent.name}: ${agent.status}`);
});

// 获取任务列表
const tasks = await api.getTasks({ status: 'in_progress' });
console.log(`进行中任务: ${tasks.length}`);

// 获取消息流
const messages = await api.getMessages({ limit: 50 });
messages.forEach(msg => {
  console.log(`[${msg.from}] → [${msg.to}]: ${msg.content}`);
});

// 监听实时更新
api.on('agent:update', (agent) => {
  console.log(`Agent ${agent.name} 状态变更: ${agent.status}`);
});

api.on('task:create', (task) => {
  console.log(`新任务: ${task.title}`);
});
```

### 15.5 自定义 Dashboard 面板

```typescript
// src/components/custom/KPI.tsx
import { MetricCard } from '../ui/metric-card';

export const KPIPanel: React.FC = () => {
  return (
    <div className="grid grid-cols-4 gap-4">
      <MetricCard
        title="活跃Agent"
        value={activeAgentCount}
        trend={+12}
        icon={<BotIcon />}
        color="blue"
      />
      <MetricCard
        title="进行中任务"
        value={inProgressCount}
        trend={-3}
        icon={<TaskIcon />}
        color="green"
      />
      <MetricCard
        title="消息总量"
        value={messageCount}
        trend={+28}
        icon={<MessageIcon />}
        color="purple"
      />
      <MetricCard
        title="Token使用率"
        value={`${tokenUsage}%`}
        warning={tokenUsage > 80}
        critical={tokenUsage > 95}
        icon={<TokenIcon />}
        color="orange"
      />
    </div>
  );
};
```

### 15.6 循环检测告警面板

```typescript
// src/components/agents/LoopAlert.tsx
import { AlertTriangle } from 'lucide-react';

interface LoopAlertProps {
  alert: {
    agentId: string;
    loopType: 'exact' | 'fuzzy' | 'frequency' | 'stall';
    repeatCount: number;
    suggestedAction: string;
  };
}

export const LoopAlert: React.FC<LoopAlertProps> = ({ alert }) => {
  const severity = alert.repeatCount > 5 ? 'critical' : 'warning';

  return (
    <div className={`alert alert-${severity}`}>
      <AlertTriangle className="w-5 h-5" />
      <div className="flex-1">
        <div className="font-medium">
          循环检测: Agent {alert.agentId}
        </div>
        <div className="text-sm opacity-80">
          类型: {alert.loopType} | 重复: {alert.repeatCount}次
        </div>
        <div className="text-sm mt-1">
          建议: {alert.suggestedAction}
        </div>
      </div>
      <button
        className="btn btn-primary"
        onClick={() => escalateToHuman(alert.agentId)}
      >
        升级人工
      </button>
    </div>
  );
};
```

---

## 十六、Dev-QA 质量保障

### 16.1 Dev-QA 循环详解

```
开发者提交
    │
    ▼
┌──────────────────────────────────────────────────┐
│                   L1 基础检查                     │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │
│  │ Lint  │ │ Format │ │ Schema │ │ Import │   │
│  │ 检查  │ │ 检查  │ │ 验证  │ │ 检查  │   │
│  └────────┘ └────────┘ └────────┘ └────────┘   │
│              阈值: 100% (必须全部通过)           │
└──────────────────────┬───────────────────────────┘
                       │ PASS
                       ▼
┌──────────────────────────────────────────────────┐
│                   L2 功能检查                     │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │
│  │ 单元   │ │ 集成   │ │ API    │ │ 契约   │   │
│  │ 测试   │ │ 测试   │ │ 测试   │ │ 测试   │   │
│  └────────┘ └────────┘ └────────┘ └────────┘   │
│              阈值: ≥80分                          │
└──────────────────────┬───────────────────────────┘
                       │ PASS
                       ▼
┌──────────────────────────────────────────────────┐
│                   L3 端到端检查                   │
│  ┌────────┐ ┌────────┐ ┌────────┐              │
│  │ E2E   │ │ 性能   │ │ 安全   │              │
│  │ 测试   │ │ 测试   │ │ 扫描   │              │
│  └────────┘ └────────┘ └────────┘              │
│              阈值: ≥90%                           │
└──────────────────────┬───────────────────────────┘
                       │ PASS
                       ▼
                   交付闭环
```

### 16.2 防无限循环机制

| 保护层 | 限制 | 触发动作 |
|--------|------|---------|
| 单次修复重试 | 3次 | 第3次失败 → 升级 |
| L1修复循环 | 5次 | 强制升级 |
| L2修复循环 | 3次 | 强制升级 |
| L3修复循环 | 2次 | 强制升级 |
| 全链路总循环 | 10次 | 强制升级人工 |

### 16.3 Dev-QA 配置

```yaml
# config/quality.yaml
dev_qa:
  # L1 基础检查配置
  l1:
    threshold: 1.0  # 100%
    checks:
      - name: "lint"
        tool: "eslint"
        command: "npm run lint"
        fail_on_error: true
      - name: "format"
        tool: "prettier"
        command: "npm run format:check"
        fail_on_error: true
      - name: "schema"
        tool: "ajv"
        config: "schema/config.json"
        fail_on_error: true
      - name: "import"
        tool: "import-checker"
        command: "python -m import_checker ."
        fail_on_error: true

  # L2 功能检查配置
  l2:
    threshold: 0.8  # 80分
    checks:
      - name: "unit_test"
        tool: "pytest"
        command: "pytest tests/unit/ --cov"
        weight: 0.4
        min_score: 0.7
      - name: "integration_test"
        tool: "pytest"
        command: "pytest tests/integration/ --cov"
        weight: 0.3
        min_score: 0.7
      - name: "api_contract"
        tool: "spectral"
        command: "spectral lint api/openapi.yaml"
        weight: 0.2
        min_score: 0.8
      - name: "code_coverage"
        tool: "coverage"
        threshold: 0.8
        weight: 0.1
        min_score: 0.6

  # L3 端到端检查配置
  l3:
    threshold: 0.9  # 90%
    checks:
      - name: "e2e_test"
        tool: "playwright"
        command: "npx playwright test"
        weight: 0.5
        min_score: 0.85
      - name: "performance"
        tool: "k6"
        command: "k6 run perf-test.js"
        thresholds:
          p95_latency: 200
          error_rate: 0.01
        weight: 0.3
        min_score: 0.8
      - name: "security"
        tool: "owasp-zap"
        command: "zap-baseline.py -t http://localhost:3000"
        high_critical: 0
        weight: 0.2
        min_score: 1.0

  # 防无限循环配置
  protection:
    max_retries_per_fix: 3
    max_l1_loops: 5
    max_l2_loops: 3
    max_l3_loops: 2
    max_total_loops: 10
    escalation_timeout: 300  # 秒
```

### 16.4 Dev-QA API

```python
import sys
sys.path.insert(0, 'CyberTeam-v2.1/engines/dev_qa')

from dev_qa import (
    DevQAEngine,
    QualityGate,
    GateLevel,
    Artifact,
)

# 创建引擎
qa = DevQAEngine(config_path="config/quality.yaml")

# 提交待检查的 artifacts
artifacts = [
    Artifact(
        path="src/agent.py",
        type="source_code",
        language="python",
    ),
    Artifact(
        path="tests/test_agent.py",
        type="test",
        language="python",
    ),
]

# 执行三级检查
result = qa.evaluate(artifacts)

# 输出结果
print(f"总体结果: {result.overall}")  # PASS / FAIL / ESCALATED
print(f"L1: {result.l1.status} ({result.l1.score:.1%})")
print(f"L2: {result.l2.status} ({result.l2.score:.1%})")
print(f"L3: {result.l3.status} ({result.l3.score:.1%})")

if result.overall == "FAIL":
    print(f"失败原因: {result.failed_checks}")
    print(f"修复建议: {result.suggestions}")

    # 获取修复指导
    for check in result.failed_checks:
        print(f"\n--- {check.name} ---")
        print(f"错误: {check.errors}")
        print(f"建议: {check.suggestion}")
        print(f"重试次数: {check.retry_count}/3")

elif result.overall == "ESCALATED":
    print(f"升级原因: {result.escalation_reason}")
    # 通知人工处理
    clawteam.inbox.send("cyberteam", "quality-director",
                       f"DevQA升级: {result.escalation_reason}")

elif result.overall == "PASS":
    print("✅ 质量门控全部通过，交付物已就绪")
```

### 16.5 质量报告格式

```json
{
  "report_id": "qa-20260324-001",
  "timestamp": "2026-03-24T14:00:00Z",
  "developer_agent": "engineering-director",
  "artifacts_count": 5,
  "overall_result": "PASS",

  "l1": {
    "status": "PASS",
    "score": 1.0,
    "duration_ms": 12400,
    "checks": [
      {"name": "lint", "status": "PASS", "errors": 0},
      {"name": "format", "status": "PASS", "errors": 0},
      {"name": "schema", "status": "PASS", "errors": 0},
      {"name": "import", "status": "PASS", "errors": 0}
    ]
  },

  "l2": {
    "status": "PASS",
    "score": 0.85,
    "duration_ms": 89000,
    "checks": [
      {"name": "unit_test", "status": "PASS", "coverage": 85, "passed": 42},
      {"name": "integration_test", "status": "PASS", "coverage": 78, "passed": 15},
      {"name": "api_contract", "status": "PASS", "violations": 0}
    ]
  },

  "l3": {
    "status": "PASS",
    "score": 0.93,
    "duration_ms": 234000,
    "checks": [
      {"name": "e2e_test", "status": "PASS", "passed": 28, "total": 30},
      {"name": "performance", "status": "PASS", "p95_latency": 150},
      {"name": "security", "status": "PASS", "high": 0, "medium": 0}
    ]
  },

  "recommendations": [
    "集成测试覆盖率偏低，建议增加至85%以上",
    "E2E测试有2个用例超时，建议优化"
  ],

  "escalation": null
}
```

---

## 十七、gstack 工程大脑集成

### 17.1 gstack 定位

gstack 是 CyberTeam 的工程能力层，提供28个专业的工程命令：

```
CyberTeam (业务智能层)
    │
    ├── 8大运营专家 (领域专业能力)
    ├── 100思维专家 (思维工具)
    │
    ▼
gstack (工程智能层)
    │
    ├── 代码审查 (/review, /codex)
    ├── 测试QA (/qa, /browse, /benchmark)
    ├── 架构评审 (/plan-eng-review)
    ├── 设计评审 (/plan-design-review)
    ├── 安全审计 (/cso, /careful)
    ├── 部署上线 (/ship, /land-and-deploy, /canary)
    └── 工程流程 (/clawteam, /retro, /autoplan)
```

### 17.2 命令分类速查

| 类别 | 命令 | 用途 |
|------|------|------|
| **战略** | `/office-hours` | 方案讨论、商业诊断 |
| | `/plan-ceo-review` | 战略评审、愿景扩展 |
| **工程** | `/plan-eng-review` | 技术方案评审 |
| | `/review` | PR/代码审查 |
| | `/codex` | 第二意见、独立审查 |
| **设计** | `/design-consultation` | 设计系统 |
| | `/plan-design-review` | 设计方案评审 |
| | `/design-review` | 视觉QA |
| **测试** | `/qa` | 完整QA+修复 |
| | `/qa-only` | 仅报告 |
| | `/browse` | 浏览器测试 |
| | `/benchmark` | 性能基准 |
| **部署** | `/ship` | 完整部署 |
| | `/land-and-deploy` | 合并+部署 |
| | `/canary` | 金丝雀监控 |
| | `/setup-deploy` | 部署配置 |
| **安全** | `/cso` | 安全审计 |
| | `/careful` | 危险警告 |
| | `/guard` | 完整安全 |
| **团队** | `/clawteam` | Agent团队 |
| | `/retro` | 复盘 |
| | `/autoplan` | 全流程评审 |

### 17.3 CyberTeam 调用 gstack

```python
# CEO 自动调用 gstack 的场景
SCENARIO_TO_GSTACK = {
    "代码审查": "/review",
    "安全扫描": "/cso",
    "架构设计": "/plan-eng-review",
    "UI评审": "/design-review",
    "E2E测试": "/qa",
    "性能测试": "/benchmark",
    "部署上线": "/ship",
    "方案讨论": "/office-hours",
}

# 示例: CEO 自动调用 /review
async def auto_review(agent_id: str, files: list[str]):
    """自动代码审查"""
    cmd = f"/review diff={' '.join(files)}"
    result = await gstack.execute(cmd)
    return result

# 示例: CEO 自动调用 /qa
async def auto_qa(url: str):
    """自动QA测试"""
    result = await gstack.execute(f"/qa url={url}")
    return result
```

### 17.4 Conductor 并行模式

```python
# Conductor: 同时执行多个 gstack 命令
from gstack import Conductor, GstackCommand

conductor = Conductor(max_parallel=5)

# 并行执行
results = await conductor.run_parallel([
    GstackCommand("/review", args={"diff": "src/agent.py"}),
    GstackCommand("/qa", args={"url": "http://localhost:3000"}),
    GstackCommand("/benchmark", args={"url": "http://localhost:3000"}),
])

# 合并结果
summary = conductor.merge_results(results)
print(f"代码审查: {summary.review.findings}")
print(f"QA结果: {summary.qa.health_score}")
print(f"性能: {summary.benchmark.p95_latency}ms")
```

---

## 十八、团队管理最佳实践

### 18.1 团队组建模式

#### 模式A: 轻量快速 (单次任务)

```bash
# 1. 创建临时团队
clawteam team spawn-team quick-task -d "一次性任务"

# 2. Spawn CEO + 需要的专家
clawteam spawn tmux claude --team quick-task --agent-name ceo \
  --task "用户说: '$USER_GOAL'。请快速完成。"

# 3. 等待完成
clawteam task wait quick-task --timeout 600

# 4. 接收结果
clawteam inbox receive quick-task --agent ceo

# 5. 清理
clawteam team cleanup quick-task
```

#### 模式B: 标准项目 (多日任务)

```bash
# 1. 创建项目团队
clawteam team spawn-team project-alpha -d "Alpha项目团队"

# 2. 创建项目结构
clawteam task create project-alpha "项目启动" -o ceo --priority high
clawteam task create project-alpha "需求分析" -o product-director --blocked-by <start-task-id>
clawteam task create project-alpha "技术设计" -o engineering-director --blocked-by <req-task-id>
clawteam task create project-alpha "开发实现" -o engineering-director --blocked-by <design-task-id>
clawteam task create project-alpha "测试验收" -o qa-agent --blocked-by <dev-task-id>
clawteam task create project-alpha "部署上线" -o devops-agent --blocked-by <test-task-id>

# 3. Spawn 所有部门
for dept in ceo product ops design engineering; do
  clawteam spawn tmux claude --team project-alpha --agent-name ${dept}-director
done

# 4. 实时监控
clawteam board live project-alpha --interval 5

# 5. 定期快照
clawteam team snapshot project-alpha --tag weekly-backup
```

#### 模式C: 长期运营 (持续运行)

```bash
# 1. 创建常驻团队
clawteam team spawn-team cyberteam-prod -d "生产环境CyberTeam"

# 2. Spawn CEO (常驻)
clawteam spawn tmux claude \
  --team cyberteam-prod \
  --agent-name ceo \
  --task "你是CyberTeam生产环境CEO。持续运行，接受用户请求并驱动团队完成。"

# 3. Spawn 6部门 (常驻)
for dept in product ops design engineering hr finance; do
  clawteam spawn tmux claude \
    --team cyberteam-prod \
    --agent-name ${dept}-director \
    --task "你是${dept^^}部总监。常驻待命，响应CEO分配。"
done

# 4. 设置自动监控
tmux new-session -d -s cyberteam-monitor \
  'watch -n 5 "clawteam board overview cyberteam-prod"'

# 5. 每日复盘
clawteam inbox send cyberteam-prod ceo "/retro"
```

### 18.2 Agent 生命周期管理

```bash
# 查看 Agent 状态
clawteam lifecycle idle cyberteam

# 输出示例:
# agent-001: idle (5分钟空闲)
# agent-002: busy (执行中)
# agent-003: idle (2小时空闲) ← 可能已忘记任务

# 清理长时间空闲的 Agent
clawteam lifecycle idle cyberteam --format json | \
  jq '.[] | select(.idle_minutes > 60) | .name' | \
  xargs -I {} clawteam lifecycle request-shutdown cyberteam --agent {}
```

### 18.3 团队健康检查

```bash
#!/bin/bash
# scripts/team-health-check.sh

TEAM=$1
echo "=== CyberTeam 健康检查: $TEAM ==="

# 1. Agent 状态
echo -e "\n[1] Agent 状态"
CLAWTEAM_AGENTS=$(clawteam --json lifecycle idle $TEAM 2>/dev/null)
echo "$CLAWTEAM_AGENTS" | jq -r '.agents[] | "\(.name): \(.status)"' 2>/dev/null || \
  clawteam lifecycle idle $TEAM

# 2. 任务进度
echo -e "\n[2] 任务进度"
PENDING=$(clawteam --json task list $TEAM --status pending 2>/dev/null | jq length)
IN_PROGRESS=$(clawteam --json task list $TEAM --status in_progress 2>/dev/null | jq length)
COMPLETED=$(clawteam --json task list $TEAM --status completed 2>/dev/null | jq length)
echo "待处理: $PENDING | 进行中: $IN_PROGRESS | 已完成: $COMPLETED"

# 3. 消息积压
echo -e "\n[3] 消息队列"
for agent in $(clawteam --json lifecycle idle $TEAM 2>/dev/null | jq -r '.agents[].name'); do
  COUNT=$(clawteam inbox peek $TEAM --agent $agent 2>/dev/null | grep -c "Pending" || echo "0")
  if [ "$COUNT" -gt 0 ]; then
    echo "  $agent: $COUNT 条待处理消息"
  fi
done

# 4. Git 冲突检查
echo -e "\n[4] Git 冲突"
CONFLICTS=$(clawteam context conflicts $TEAM 2>/dev/null)
echo "$CONFLICTS" | head -5

echo -e "\n=== 检查完成 ==="
```

### 18.4 团队交接协议

```markdown
## CyberTeam Agent 交接清单

### 交接前 (交出方)
- [ ] 整理当前任务状态
- [ ] 汇总已完成的工作
- [ ] 列出进行中的子任务
- [ ] 标记待处理问题
- [ ] 保存工作记忆 (如果有)
- [ ] 通过 inbox 发送交接报告给接收方

### 交接内容
```
【Agent交接报告】
交出方: {agent_name}
接收方: {agent_name}
时间: {timestamp}

已完成:
- {已完成项1}
- {已完成项2}

进行中:
- {进行中项1} (进度: X%)
- {进行中项2}

待处理:
- {待处理项1} (优先级: 高)
- {待处理项2} (优先级: 中)

问题/风险:
- {问题1}
- {风险1}

上下文摘要:
{关键上下文 (限制在2000字内)}
```

### 交接后 (接收方)
- [ ] 确认收到交接报告
- [ ] 阅读上下文摘要
- [ ] 恢复工作记忆 (如有)
- [ ] 继续进行中的任务
- [ ] 处理待处理项
- [ ] 通知 CEO 已完成交接
```

---

## 十九、高级配置

### 19.1 多团队编排

```python
# 协调多个 CyberTeam 团队
class MultiTeamOrchestrator:
    def __init__(self):
        self.teams = {
            "product-team": TeamClient("product-team"),
            "engineering-team": TeamClient("engineering-team"),
            "research-team": TeamClient("research-team"),
        }

    async def run_cross_team_project(self, goal: str):
        # 1. 研究团队: 前期调研
        research = self.teams["research-team"].run(
            task="调研市场竞品"
        )

        # 2. 产品团队: 基于调研做产品设计
        product = self.teams["product-team"].run(
            task=f"基于调研结果设计产品方案",
            depends_on=research
        )

        # 3. 工程团队: 基于产品方案开发
        engineering = self.teams["engineering-team"].run(
            task=f"实现产品方案",
            depends_on=product
        )

        # 4. 汇总
        return self.aggregate_results([research, product, engineering])
```

### 19.2 自定义 Agent 类型

```yaml
# config/custom-agents.yaml
custom_agents:
  - name: "data-analyst"
    base: "department-agent"
    specialization: "数据分析"
    tools:
      - python
      - pandas
      - matplotlib
    prompts:
      - "你是一个专业的数据分析师"
      - "擅长用数据讲故事"
      - "每次分析必须包含可视化图表"
    quality_standards:
      l1_threshold: 1.0
      l2_threshold: 0.85
      l3_threshold: 0.90

  - name: "security-auditor"
    base: "specialist-agent"
    specialization: "安全审计"
    tools:
      - owasp-zap
      - bandit
      - semgrep
    triggers:
      - "安全"
      - "漏洞"
      - "渗透"
```

### 19.3 工作流模板

```yaml
# workflows/research.yaml
name: "竞品调研工作流"
description: "完整的竞品分析流程"

stages:
  - id: "scope"
    name: "范围定义"
    owner: "product-director"
    tasks:
      - "确定竞品列表 (不超过5个)"
      - "定义分析维度"
      - "收集基础信息"

  - id: "research"
    name: "深度调研"
    owner: "ops-director"
    parallel: true
    tasks:
      - "竞品功能对比"
      - "竞品增长策略分析"
      - "竞品用户评价收集"
      - "竞品技术架构调研"

  - id: "analysis"
    name: "综合分析"
    owner: "strategy-expert"
    depends_on: ["research"]
    tasks:
      - "SWOT分析"
      - "波特五力分析"
      - "市场定位图"

  - id: "report"
    name: "报告撰写"
    owner: "product-director"
    depends_on: ["analysis"]
    tasks:
      - "竞品分析报告 (完整版)"
      - "竞品分析PPT"
      - "行动建议清单"

  - id: "review"
    name: "评审确认"
    owner: "ceo"
    depends_on: ["report"]
    tasks:
      - "CEO评审报告"
      - "质量门控检查"
      - "最终交付"
```

### 19.4 性能调优

```python
# 性能调优配置
PERFORMANCE_TUNING = {
    # ClawTeam 调优
    "clawteam": {
        "max_concurrent_spawns": 5,       # 最大并发spawn数
        "spawn_timeout": 30,               # spawn超时 (秒)
        "inbox_batch_size": 10,            # 批量拉取消息数
        "board_refresh_interval": 3,       # 看板刷新间隔 (秒)
    },

    # Memory System 调优
    "memory": {
        "vector_batch_size": 100,          # 向量批量写入
        "recall_top_k": 5,                 # 检索Top K
        "cache_enabled": True,             # 启用缓存
        "cache_size_mb": 512,              # 缓存大小
    },

    # Context Compression 调优
    "context": {
        "compression_trigger": 0.85,       # 压缩触发阈值
        "compression_ratio": 0.5,          # 目标压缩率
        "preserve_recent_tokens": 20000,  # 保留最近Token数
        "compression_level": "medium",     # 压缩级别
    },

    # Execution Monitor 调优
    "monitor": {
        "loop_check_interval": 5,          # 循环检查间隔 (秒)
        "max_trace_length": 20,            # 最大跟踪序列
        "alert_debounce": 30,               # 告警去抖 (秒)
    },
}
```

---

## 二十、故障排除

### 20.1 常见问题诊断

#### 问题1: Agent 无法 spawn

```
症状: clawteam spawn 报错 "Connection refused" 或超时
原因:
  1. tmux 未安装
  2. tmux 服务未启动
  3. Claude Code 路径错误
  4. 权限问题

排查步骤:
  1. 检查 tmux: tmux -V
  2. 启动 tmux: tmux new-session -d 'echo ok'
  3. 检查 claude: which claude
  4. 检查权限: ls -la /tmp/tmux-*
  5. 查看详细日志: clawteam --debug spawn ...
```

#### 问题2: Inbox 消息不送达

```
症状: 发送了 inbox 消息但接收方 Agent 没有响应
原因:
  1. 接收方 Agent 已关闭
  2. 接收方 Agent 在 tmux pane 中但不在当前可见窗口
  3. 消息格式错误
  4. 团队名称不匹配

排查步骤:
  1. 检查 Agent 是否存活:
     ps aux | grep claude | grep <agent_name>

  2. 检查 inbox 是否有消息:
     clawteam inbox peek <team> --agent <agent>

  3. 检查 tmux pane 是否可见:
     tmux list-panes -t <session>

  4. 直接 attach 到 Agent 的 tmux pane:
     tmux select-pane -t <session>:<window>.<pane>
```

#### 问题3: 循环检测误报

```
症状: 正常的多次调用被误判为循环
原因:
  1. similarity_threshold 设置过低 (默认0.7)
  2. min_repeat_count 设置过低 (默认3)
  3. 正常的多轮迭代被误判

解决方案:
  1. 调高阈值:
     monitor = ExecutionMonitor(
         loop_detection=LoopDetectionConfig(
             similarity_threshold=0.85,
             min_repeat_count=5,
         )
     )

  2. 排除特定工具:
     monitor.add_exempt_tool("read")  # 读文件不算循环
     monitor.add_exempt_tool("search")

  3. 禁用特定类型的检测:
     monitor.disable_detection_type("frequency")
```

#### 问题4: Dashboard 无法连接

```
症状: http://localhost:5173 无法访问
原因:
  1. Dashboard 未启动
  2. 端口被占用
  3. CORS 问题

排查步骤:
  1. 检查进程: lsof -i :5173
  2. 查看日志: cd dashboard && npm run dev
  3. 更换端口: npm run dev -- --port 5174
  4. 检查 CORS 配置: vite.config.ts
```

#### 问题5: Token 超限导致崩溃

```
症状: Agent 在长对话中突然停止响应或输出乱码
原因:
  1. 上下文超过模型 Token 限制
  2. 上下文压缩未触发
  3. Token 计数不准确

排查步骤:
  1. 检查 Token 使用率:
     budget = BudgetManager()
     status = budget.get_status()
     print(f"使用率: {status.usage_ratio:.1%}")

  2. 手动触发压缩:
     budget.trigger_compression(strategy="adaptive")

  3. 恢复检查点:
     memory.restore_working("goal-xxx")

  4. 增加 max_tokens:
     chain = ConversationChain(max_tokens=200000)
```

#### 问题6: PUA 干预过度

```
症状: Agent 在 PUA L2/L3 后行为异常或直接放弃
原因:
  1. PUA 味道过于激进
  2. 干预时机不当 (在正常执行中触发)
  3. 没有冷却期

解决方案:
  1. 切换到温和味道:
     pua.set_flavor("meituan")  # 美团味更温和

  2. 增加冷却期:
     cooldown_period=120  # 2分钟冷却

  3. 降低触发阈值:
     pua.thresholds.l2 = 3  # 3次失败才触发L2

  4. 完全禁用 PUA (不推荐):
     pua = PUAEngine(enabled=False)
```

### 20.2 日志分析

```bash
# 查看 ClawTeam 日志
tail -f ~/.clawteam/logs/clawteam.log

# 查看 CyberTeam 日志
tail -f ~/.cyberteam/logs/cyberteam.log

# 按 Agent 过滤
grep "agent=product-director" ~/.cyberteam/logs/cyberteam.log

# 按级别过滤
grep "ERROR" ~/.cyberteam/logs/cyberteam.log

# 搜索循环检测事件
grep "loop_detected" ~/.cyberteam/logs/cyberteam.log

# 搜索 PUA 干预
grep "PUA" ~/.cyberteam/logs/cyberteam.log

# 导出指定时间段的日志
grep "2026-03-24 14:" ~/.cyberteam/logs/cyberteam.log > /tmp/hourly.log
```

### 20.3 性能分析

```bash
# 检查 Agent 响应时间
#!/bin/bash
for i in {1..10}; do
  START=$(date +%s.%N)
  clawteam inbox send test-team test-agent "ping"
  clawteam inbox receive test-team --agent test-agent > /dev/null 2>&1
  END=$(date +%s.%N)
  echo "Round $i: $(echo "$END - $START" | bc)s"
done

# 检查 Memory 性能
python3 -c "
import time, sys
sys.path.insert(0, 'modules/memory')
from memory import MemorySystem

m = MemorySystem()
m.save_long_term('test content ' * 100, 'test')

start = time.time()
for i in range(1000):
    m.save_long_term(f'test {i}', 'test')
elapsed = time.time() - start
print(f'1000次写入: {elapsed:.2f}s ({1000/elapsed:.0f}/s)')

start = time.time()
for i in range(100):
    m.retrieve('test', top_k=5)
elapsed = time.time() - start
print(f'100次检索: {elapsed:.2f}s ({100/elapsed:.0f}/s)')
"
```

---

## 二十一、常见问题

### Q1: CyberTeam 和 agency-agents / gstack 有什么区别？

| 维度 | CyberTeam | agency-agents | gstack |
|------|-----------|---------------|--------|
| **入口** | 一句话自动组建团队 | 手动选择144个Agent | 28个Slash命令 |
| **协作模型** | CEO中心化、部门并行 | 多部门编排 | 串行Sprint |
| **专业性** | 8大运营专家垂直领域 | 通用领域专家 | 工程领域 |
| **执行动力** | PUA压力引擎 | 无 | 无 |
| **目标驱动** | Goal-Driven持久循环 | 一次性执行 | 单命令执行 |
| **记忆能力** | 三层Memory System | 无 | 无 |

**最佳用法**: CyberTeam 提供业务智能（运营专家），gstack 提供工程智能（28个命令），两者互补。

### Q2: 需要多少 Token 预算？

| 任务规模 | 单次成本估算 | 月度估算 |
|---------|------------|---------|
| 简单任务 (<10轮) | ~$0.05 | ~$50-100 |
| 中等任务 (10-50轮) | ~$0.20 | ~$200-500 |
| 复杂任务 (50+轮) | ~$1.00 | ~$1000-3000 |

### Q3: Agent 数量有限制吗？

- **软限制**: 建议不超过 20 个并发 Agent（性能考虑）
- **硬限制**: 受 tmux 会话和系统资源限制
- **最佳实践**: 按需启动，使用后关闭

### Q4: 如何保证数据安全？

1. **工作空间隔离**: 每个 Agent 使用独立的 git worktree
2. **消息加密**: ClawTeam inbox 使用文件锁，不经过第三方
3. **敏感信息**: 使用环境变量而非硬编码
4. **日志脱敏**: 生产环境启用日志脱敏
5. **API Key**: 使用 `.env` 文件，不提交到 Git

### Q5: 任务中断后如何恢复？

```bash
# 1. 查看检查点
clawteam team snapshots <team>

# 2. 恢复团队状态
clawteam team restore <team> --snapshot <tag>

# 3. 恢复 Memory System
python3 -c "
from memory import MemorySystem
m = MemorySystem()
goals = m.list_pending_goals()
for g in goals:
    m.restore(g)
"

# 4. 重新启动中断的 Agent
clawteam spawn tmux claude --team <team> --agent-name <agent> \
  --task "继续执行之前中断的任务..."
```

### Q6: 如何监控团队效率？

```bash
# 关键指标
# 1. Agent 利用率
IDLE=$(clawteam lifecycle idle cyberteam | grep -c "idle")
TOTAL=$(clawteam lifecycle idle cyberteam | grep -c ":")
UTILIZATION=$(echo "scale=2; ($TOTAL - $IDLE) / $TOTAL * 100" | bc)
echo "Agent利用率: ${UTILIZATION}%"

# 2. 任务完成率
PENDING=$(clawteam task list cyberteam --status pending | wc -l)
COMPLETED=$(clawteam task list cyberteam --status completed | wc -l)
echo "任务完成率: ${COMPLETED}/${TOTAL}"

# 3. 平均响应时间 (需要日志分析)
grep "inbox.*send\|inbox.*receive" ~/.cyberteam/logs/cyberteam.log | \
  awk '{print $NF}' | sort | uniq -c | sort -rn | head -10
```

### Q7: 如何扩展新的运营专家？

**Step 1**: 创建专家定义文件

```bash
mkdir -p agents/experts/data-science
cat > agents/experts/data-science.md << 'EOF'
# 数据科学专家

## 身份
你是 CyberTeam 的数据科学专家。

## 核心能力
- 机器学习模型设计
- 数据分析和可视化
- 统计建模
- A/B测试设计

## 方法论
- CRISP-DM
- OSEMN
- Tidy Data原则

## 输出格式
{分析目标}
{关键发现}
{数据支撑}
{行动建议}
{置信度}
EOF
```

**Step 2**: 注册到团队配置

```bash
# 更新团队配置
clawteam team update cyberteam --add-member data-science-expert
```

**Step 3**: 测试专家

```bash
clawteam spawn tmux claude \
  --team cyberteam \
  --agent-name data-science-expert \
  --task "$(cat agents/experts/data-science.md)"
```

---

## 附录

### A. 命令速查表

```bash
# ===== 团队管理 =====
clawteam team spawn-team <name> -d "<desc>" -n <leader>   # 创建团队
clawteam team status <team>                                # 团队状态
clawteam team snapshot <team> --tag <tag>                 # 快照
clawteam team restore <team> --snapshot <tag>             # 恢复
clawteam team cleanup <team>                               # 清理

# ===== Agent管理 =====
clawteam spawn <backend> <cmd> --team <team> --agent-name <name> --task "<task>"
clawteam lifecycle request-shutdown <team> --agent <name>
clawteam lifecycle idle <team>

# ===== 消息 =====
clawteam inbox send <team> <agent> "<msg>"
clawteam inbox receive <team> --agent <agent>
clawteam inbox peek <team> --agent <agent>
clawteam inbox broadcast <team> "<msg>"

# ===== 任务 =====
clawteam task create <team> "<task>" -o <owner> [--blocked-by <id>] [--priority high]
clawteam task update <team> <id> --status <pending|in_progress|completed|blocked>
clawteam task list <team> [--status <status>] [--owner <agent>] [--priority high]
clawteam task wait <team> [--timeout <seconds>] [--agent <agent>]

# ===== 监控 =====
clawteam board show <team>
clawteam board overview <team>
clawteam board live <team> --interval <seconds>
clawteam board gource <team> --log-only

# ===== Git上下文 =====
clawteam context inject <team> --agent <agent>
clawteam context conflicts <team>
```

### B. 文件路径参考

```
CyberTeam-v2.1/
├── agents/                     # Agent 定义
├── modules/                     # 核心引擎
│   ├── memory/                   # 记忆系统 (Go)
│   ├── monitor/                  # 执行监控 (Python)
│   ├── context/                  # 上下文压缩 (Python)
│   └── dashboard/                # Web Dashboard (React)
├── engines/                     # 核心引擎
├── config/                      # 配置文件
├── scripts/                     # 辅助脚本
├── workflows/                   # 工作流模板
└── templates/                   # Agent 模板

~/.clawteam/                     # ClawTeam 数据
├── teams/                       # 团队数据
│   └── <team>/
│       ├── team.json            # 团队配置
│       └── inboxes/             # 收件箱
├── workspaces/                  # Agent工作空间
└── snapshots/                    # 快照

~/.cyberteam/                    # CyberTeam 数据
├── memory/                      # 记忆数据
│   ├── long_term/
│   ├── working/
│   └── episodic/
├── logs/                        # 日志
└── checkpoints/                 # 检查点
```

### C. 版本历史

| 版本 | 日期 | 变化 |
|------|------|------|
| v1.0 | 2026-03-22 | 基础架构：CEO + 6部门 + 8专家 |
| v2.0 | 2026-03-23 | ClawTeam集成 + Goal-Driven + PUA |
| v2.1 | 2026-03-24 | Memory/Monitor/Context/Dashboard四大增强模块 |

---

*本文档由 CyberTeam v2.1 团队生成*
*最后更新: 2026-03-24*
