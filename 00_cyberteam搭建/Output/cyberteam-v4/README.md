# CyberTeam V4

> 基于 [ClawTeam](https://github.com/HKUDS/ClawTeam) 开发的垂直行业 AI Agent 群体智能系统

**Solo 🤖 → Swarm 🦞🤖🤖🤖** — 让 AI Agent 组建蜂群、协同思考、共同交付

---

## 核心特性

### 🔬 Swarm Intelligence (群体智能)

| 功能 | 说明 |
|------|------|
| **Leader Agent 创建子 Agent** | 每个子 Agent 拥有独立的 Git Worktree 和 tmux 会话 |
| **任务分配 + 依赖链** | 支持 DAG 任务图，完成时自动解除下游阻塞 |
| **Agent 间消息传递** | 定向消息 + 广播，支持复杂协作流程 |
| **监控进度** | 实时看板，监控每个 Agent 的状态和进度 |
| **动态调整** | 终止低效 Agent，用新方向重新分配 |
| **结果汇聚** | 收敛到最优方案，人类只需提供初始目标 |

### 📦 模块结构

| 模块 | 说明 | 继承自 |
|------|------|--------|
| `cyberteam.team` | 团队管理、任务、消息 | ClawTeam/team |
| `cyberteam.spawn` | Agent 生成、tmux 后端 | ClawTeam/spawn |
| `cyberteam.workspace` | Git Worktree 管理 | ClawTeam/workspace |
| `cyberteam.transport` | 消息传递层 | ClawTeam/transport |
| `cyberteam.board` | 仪表盘和可视化 | ClawTeam/board |

## 安装

### 前置要求

| 依赖 | 版本 | 说明 |
|------|------|------|
| Python | 3.10+ | 运行时 |
| Node.js | 22+ | CDP Proxy 必需 |
| Chrome/Chromium | 最新 | 浏览器自动化 |

### 基本安装

```bash
pip install -e .
```

### CDP 浏览器配置 (可选但推荐)

web-access skill 提供完整浏览器自动化能力，支持登录态访问、动态页面抓取。

#### 1. 验证 web-access skill 已集成

web-access skill 已通过符号链接集成在 `SKILLS/third-party/web-access`：

```bash
ls -la SKILLS/third-party/web-access  # 确认符号链接有效
```

如符号链接失效（断链），重新创建：
```bash
ln -s ~/.claude/skills/web-access SKILLS/third-party/web-access
```

#### 2. Chrome 开启远程调试

1. Chrome 地址栏打开 `chrome://inspect/#remote-debugging`
2. 勾选 **Allow remote debugging for this browser instance**
3. 重启 Chrome（如需要）

#### 3. 验证依赖

```bash
bash SKILLS/third-party/web-access/scripts/check-deps.sh
```

预期输出：
```
node: ok (v22.x.x)
chrome: ok (port 9222)
proxy: ready
```

#### 4. 启动 CDP Proxy (如未自动启动)

```bash
node ~/.claude/skills/web-access/scripts/cdp-proxy.mjs &
```

#### 可用工具

| 工具 | 功能 |
|------|------|
| `cdp_check_deps` | 检查依赖状态 |
| `cdp_list_targets` | 列出打开的标签页 |
| `cdp_new_tab` | 创建新标签页 |
| `cdp_eval` | 执行 JavaScript |
| `cdp_click` | 点击元素 |
| `cdp_scroll` | 滚动页面 |
| `cdp_screenshot` | 页面截图 |
| `cdp_navigate` | 导航 |
| `cdp_close_tab` | 关闭标签页 |

详细文档：[docs/web-access-integration.md](./docs/web-access-integration.md)

## 快速开始

### CLI

```bash
# 创建团队
cyberteam launch --template swarm --goal "完成项目X"

# Spawn Agent
cyberteam spawn tmux claude --team my-team --agent-name researcher --task "搜索资料"

# 查看状态
cyberteam team status my-team
```

### Python API

```python
from integration.cyberteam_adapter import CyberTeamAdapter

adapter = CyberTeamAdapter()
swarm = adapter.create_swarm("my-team", "目标", "swarm")
task = adapter.assign_task("my-team", "researcher", "搜索AI进展")
adapter.complete_task("my-team", task.task_id, "结果")
```

## 项目结构

```
cyberteam-v4/
├── cyberteam/           # 核心包 (基于 ClawTeam)
│   ├── team/           # 团队管理
│   ├── spawn/          # Agent 生成
│   ├── workspace/      # 工作区
│   ├── transport/      # 消息传递
│   └── board/          # 仪表盘
├── engine/             # 行业引擎
│   ├── ceo.py         # CEO 路由
│   └── ...
└── integration/        # 外部集成
```

## CLI 命令

| 命令 | 功能 |
|------|------|
| `cyberteam launch` | 从模板启动团队 |
| `cyberteam spawn` | Spawn Agent |
| `cyberteam team` | 团队管理 |
| `cyberteam task` | 任务管理 |
| `cyberteam inbox` | 消息收件箱 |
| `cyberteam board` | 仪表盘 |

---

*基于 ClawTeam 开发，MIT License*
