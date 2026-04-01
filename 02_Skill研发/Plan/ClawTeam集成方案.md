# ClawTeam 集成方案

## 一、背景概述

ClawTeam 是一个框架无关的多代理协作 CLI 工具，由 HKUDS 开发维护。其核心理念是让 AI Agent 能够自主组建团队、分工协作、共享发现、收敛到最优方案。当前项目版本为 0.1.2，支持 Python 3.10+。

### 1.1 核心能力

| 能力模块 | 功能描述 |
|---------|---------|
| **团队管理** | 创建团队、成员加入审批、团队状态查询 |
| **任务管理** | 任务创建/更新/查询、依赖链、状态自动流转 |
| **消息通信** | 点对点消息、广播、消息队列管理 |
| **代理生成** | 支持 tmux/subprocess 后端、Git Worktree 隔离 |
| **看板监控** | 实时任务进度、tmux 窗口 tiled 视图 |

### 1.2 适用场景

- **自主 ML 研究**: 多 GPU 实验群体，8 Agent × 8 H100 自主优化
- **Agent 软件工程**: 并行软件开发，自动拆分为 API、后端、前端、测试
- **多分析师信号融合**: 7 个分析师 Agent + 风控经理收敛投资决策
- **自定义群体**: TOML 模板定义任意团队原型

---

## 二、集成目标

本方案旨在将 ClawTeam 无缝集成到 Cyberwiz 企业级 AI 协作系统中，实现以下目标：

1. **统一入口**: 通过 Cyberwiz CLI 直接调用 ClawTeam 功能
2. **Skill 化**: 将 ClawTeam 封装为可复用的 Skill
3. **模板化**: 预置常用团队模板，开箱即用
4. **工作流整合**: 与 Cyberwiz 现有工作流深度融合

---

## 三、集成架构

### 3.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Cyberwiz CLI 入口                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ Skill层     │  │ Team层      │  │ Agent层             │ │
│  │ (clawteam)  │  │ (team ops)  │  │ (spawn/monitoring)  │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    ClawTeam Core                            │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ │
│  │ Team Mgr  │ │ Task Mgr  │ │ Inbox     │ │ Workspace │ │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    Transport Layer                           │
│              File-based / ZeroMQ P2P                        │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 模块映射

| Cyberwiz 模块 | ClawTeam 模块 | 集成方式 |
|---------------|---------------|---------|
| Skill 引擎 | clawteam skill | 直接调用 CLI |
| Team 协调 | team commands | 封装为 API |
| Agent 管理 | spawn/monitoring | 进程托管 |
| 任务追踪 | task commands | 数据对接 |

---

## 四、集成实现

### 4.1 CLI 命令封装

**方案 A: 符号链接方式**

```bash
# 在 Cyberwiz 命令路径中创建符号链接
ln -s /path/to/cyberteam ~/.local/bin/cyberteam

# 验证
cyberteam --help
```

**方案 B: 包装脚本方式**

```python
# cyberwiz_team.py
import subprocess
import sys

def run_cyberteam(args):
    cmd = ["cyberteam"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    return result.returncode

if __name__ == "__main__":
    run_cyberteam(sys.argv[1:])
```

### 4.2 Skill 定义

根据现有 `.agents/skills/clawteam/SKILL.md`，集成时需确保：

```yaml
# Skill 触发条件
triggers:
  - "create a team"
  - "spawn agents"
  - "assign tasks"
  - "coordinate multiple agents"
  - "cyberteam"
  - "multi-agent coordination"
```

### 4.3 环境变量配置

```bash
# 基础配置
export CLAWTEAM_HOME=~/.cyberteam
export CLAWTEAM_TRANSPORT=file  # 或 p2p

# 身份配置（Leader 模式）
export CLAWTEAM_AGENT_ID="leader-001"
export CLAWTEAM_AGENT_NAME="leader"
export CLAWTEAM_AGENT_TYPE="leader"
export CLAWTEAM_TEAM_NAME="my-team"
```

### 4.4 模板集成

预置模板路径：`clawteam/templates/`

| 模板名称 | 适用场景 |
|---------|---------|
| `software-dev.toml` | 软件开发团队 |
| `research-paper.toml` | 学术研究团队 |
| `hedge-fund.toml` | 投资分析团队 |
| `code-review.toml` | 代码审查团队 |
| `strategy-room.toml` | 战略决策团队 |

---

## 五、使用流程

### 5.1 快速启动

```bash
# 1. 设置 Leader 身份
export CLAWTEAM_AGENT_ID="leader-001"
export CLAWTEAM_AGENT_NAME="leader"
export CLAWTEAM_AGENT_TYPE="leader"

# 2. 创建团队
cyberteam team spawn-team my-team -d "Project team" -n leader

# 3. 创建任务
cyberteam task create my-team "Design system" -o leader
cyberteam task create my-team "Implement feature" -o worker1

# 4. 查看看板
cyberteam board show my-team
```

### 5.2 代理协作

```bash
# 生成 Worker 代理
cyberteam spawn --team my-team --agent-name worker1 \
  --task "Implement the auth module"

# 发送指令
cyberteam inbox send my-team worker1 "Start implementing"

# 监控任务
cyberteam task wait my-team --timeout 600
```

---

## 六、测试验证

### 6.1 端到端测试

使用 `clawteam-dev` skill 进行完整生命周期测试：

```bash
# 清理 → 创建团队 → 创建任务 → 生成代理 → 等待完成 → 验证 → 清理
```

### 6.2 测试矩阵

| 测试项 | 验证内容 | 预期结果 |
|--------|---------|---------|
| Team Creation | 团队创建 | `OK Team 'e2e-test' created` |
| Task Dependencies | 任务依赖链 | blocked 状态正确设置 |
| Agent Spawn | 代理生成 | tmux 窗口 + worktree 创建 |
| Message Passing | 消息通信 | inbox 消息正确传递 |
| Task Wait | 任务等待 | 超时/完成正确返回 |
| Cleanup | 资源清理 | worktree/tmux 全部清除 |

---

## 七、注意事项

1. **依赖要求**: Python 3.10+, tmux, git
2. **工作目录**: 需要在 git 仓库中运行（用于 worktree 隔离）
3. **权限设置**: 生产环境需配置 `skip_permissions=false`
4. **传输层**: 默认使用文件传输，P2P 模式需安装 `pyzmq`
5. **数据存储**: 默认存储在 `~/.cyberteam/`

---

## 八、实施计划

| 阶段 | 任务 | 预计时间 |
|------|------|---------|
| Phase 1 | 环境搭建与 CLI 验证 | 1 天 |
| Phase 2 | Skill 集成与触发配置 | 1 天 |
| Phase 3 | 模板定制与工作流封装 | 2 天 |
| Phase 4 | 测试验证与文档输出 | 1 天 |

---

## 九、附录

### A. 命令速查

```bash
# 团队操作
cyberteam team spawn-team <name> -d <desc> -n <leader>
cyberteam team status <team>
cyberteam team discover

# 任务操作
cyberteam task create <team> <subject> -o <owner> --blocked-by <id>
cyberteam task update <team> <id> --status <status>
cyberteam task list <team> --status <status>
cyberteam task wait <team> --timeout <sec>

# 消息操作
cyberteam inbox send <team> <recipient> <message>
cyberteam inbox receive <team>

# 看板操作
cyberteam board show <team>
cyberteam board live <team> --interval <sec>
cyberteam board attach <team>

# 代理生成
cyberteam spawn --team <team> --agent-name <name> --task <task>
```

### B. 数据结构

```
~/.cyberteam/
├── config.json          # 全局配置
├── teams/              # 团队数据
│   └── {team_name}/
│       └── team.json
├── tasks/              # 任务数据
│   └── {team_name}/
│       └── tasks.json
├── inboxes/            # 消息队列
│   └── {agent_id}/
│       └── messages/
├── workspaces/         # 工作空间
│   └── {team_name}/
│       └── {agent_name}/
└── events/             # 事件日志
```

---

*文档版本: 1.0*
*创建日期: 2026-03-23*
*作者: ClawTeam专家*
