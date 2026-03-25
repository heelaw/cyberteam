# CyberTeam V4 技术架构

> 基于 ClawTeam (https://github.com/HKUDS/ClawTeam) 开发的垂直行业产品

## 一、架构原则

1. **基于开源，扩展自研** - CyberTeam V4 以 ClawTeam 为基础，在其上扩展垂直行业功能
2. **模块化继承** - 复用 ClawTeam 的核心模块，扩展点进行子类化
3. **命名统一** - 所有 ClawTeam 命名改为 CyberTeam
4. **API 兼容** - 保持与 ClawTeam CLI 的兼容性

## 二、ClawTeam 源码结构 (基础层)

```
clawteam/                          # 来源: github.com/HKUDS/ClawTeam
├── team/
│   ├── models.py                  # TeamConfig, TeamMember, TaskItem
│   ├── manager.py                 # TeamManager - 团队生命周期
│   ├── tasks.py                   # TaskStore - 任务存储与依赖
│   ├── mailbox.py                 # MailboxManager - 消息传递
│   ├── costs.py                   # CostTracker - 成本追踪
│   ├── lifecycle.py               # LifecycleManager - 生命周期管理
│   ├── snapshot.py                # SnapshotManager - 状态快照
│   ├── watcher.py                 # Watcher - 状态监控
│   └── waiter.py                  # Waiter - 等待机制
├── spawn/
│   ├── registry.py                # SpawnRegistry - Agent 注册
│   ├── tmux_backend.py            # TmuxBackend - tmux 后端
│   ├── subprocess_backend.py      # SubprocessBackend - 子进程后端
│   ├── profiles.py                # ProfileManager - Agent 配置
│   ├── presets.py                 # TeamPresets - 团队模板
│   ├── sessions.py               # SessionManager - 会话持久化
│   └── adapters.py                # BackendAdapter - 后端适配器
├── workspace/
│   ├── git.py                    # Git 命令封装
│   ├── manager.py                # WorkspaceManager - 工作区管理
│   ├── models.py                 # WorkspaceInfo, ConflictInfo
│   ├── conflicts.py              # ConflictResolver - 冲突解决
│   └── context.py                # WorkspaceContext - 上下文
├── board/
│   ├── server.py                 # DashboardServer - Web 仪表盘
│   ├── renderer.py               # BoardRenderer - 看板渲染
│   ├── collector.py              # MetricsCollector - 指标收集
│   └── gource.py                 # GourceAnimator - 可视化动画
├── transport/
│   ├── base.py                   # TransportBase
│   ├── file.py                   # FileTransport - 文件传输
│   ├── p2p.py                    # P2PTransport - 点对点传输
│   └── claimed.py                # ClaimedTransport - 声明传输
├── cli/
│   └── commands.py               # CLI 命令实现
├── config.py                     # 全局配置
├── identity.py                   # 身份管理
└── timefmt.py                   # 时间格式化
```

## 三、CyberTeam V4 扩展结构

```
cyberteam/                         # V4 重命名 + 扩展
├── __init__.py                   # 包初始化
├── cli/
│   └── commands.py               # CyberTeam CLI 命令
│
├── team/                          # 扩展自 ClawTeam/team/
│   ├── models.py                 # 扩展 TeamConfig, TeamMember
│   ├── manager.py                # 扩展 TeamManager
│   ├── tasks.py                  # 扩展 TaskStore (增加 DAG 解析)
│   ├── mailbox.py                # 扩展 MailboxManager
│   └── costs.py                  # 扩展 CostTracker
│
├── swarm/                         # 🆕 Swarm Intelligence 核心
│   ├── orchestrator.py           # SwarmOrchestrator - 群体编排器
│   ├── brain/
│   │   ├── thinking_engine.py    # 思考引擎
│   │   └── decision_tree.py      # 决策树
│   └── intelligence/
│       ├── self_organizing.py    # 自组织机制
│       └── emergence.py          # 涌现算法
│
├── spawn/                         # 扩展自 ClawTeam/spawn/
│   ├── registry.py                # 扩展 SpawnRegistry
│   ├── tmux_backend.py           # 扩展 TmuxBackend
│   └── adapters.py                # 扩展 BackendAdapter
│
├── workspace/                     # 扩展自 ClawTeam/workspace/
│   ├── git.py                    # 扩展 Git
│   ├── manager.py                # 扩展 WorkspaceManager
│   └── models.py                 # 扩展 WorkspaceInfo
│
├── board/                         # 扩展自 ClawTeam/board/
│   ├── server.py                 # 扩展 DashboardServer
│   └── renderer.py               # 扩展 BoardRenderer
│
├── engine/                        # 🆕 垂直行业引擎
│   ├── ceo.py                    # CEO 路由引擎
│   ├── strategy.py               # 策略引擎
│   ├── department.py             # 部门引擎
│   ├── debate_engine.py          # 辩论引擎
│   └── launcher.py               # 启动器
│
├── integration/                   # 🆕 外部集成
│   ├── cyberteam_adapter.py      # CyberTeam 适配器
│   ├── gstack_adapter.py         # GStack 适配器
│   └── agency_adapter.py         # Agency 适配器
│
└── backend/                       # 🆕 FastAPI 后端
    └── app/
        ├── main.py
        ├── config.py
        └── api/
            ├── agents.py
            ├── tasks.py
            ├── experts.py
            ├── debate.py
            └── scoring.py
```

## 四、继承关系图

```
ClawTeam (基础层 - 开源)
│
├── team/models.py ──────────────► CyberTeam/team/models.py (扩展)
├── team/manager.py ─────────────► CyberTeam/team/manager.py (扩展)
├── team/tasks.py ───────────────► CyberTeam/swarm/orchestrator.py (组合+扩展)
├── team/mailbox.py ─────────────► CyberTeam/swarm/intelligence/self_organizing.py (扩展)
│
├── spawn/registry.py ───────────► CyberTeam/spawn/registry.py (扩展)
├── spawn/tmux_backend.py ───────► CyberTeam/spawn/tmux_backend.py (扩展)
│
├── workspace/git.py ─────────────► CyberTeam/workspace/git.py (扩展)
├── workspace/manager.py ────────► CyberTeam/workspace/manager.py (扩展)
│
└── board/server.py ─────────────► CyberTeam/board/server.py (扩展)
                                    │
                                    ▼
                          CyberTeam/engine/ (行业专用)
                          ├── ceo.py      - CEO 路由
                          ├── strategy.py - 策略
                          ├── department.py - 部门
                          └── debate_engine.py - 辩论
```

## 五、核心扩展点

### 5.1 Swarm Intelligence (群体智能)

```python
# CyberTeam/swarm/orchestrator.py
from clawteam.team.tasks import TaskStore as BaseTaskStore

class TaskStore(BaseTaskStore):
    """扩展任务存储，增加 DAG 解析"""

    def resolve_dependencies(self, task_ids: List[str]) -> List[List[str]]:
        """解析任务依赖，返回可并行执行的批次"""
        ...

class SwarmOrchestrator:
    """群体智能编排器 - 核心扩展"""

    def create_agent(self, name: str, role: str, workspace: bool = True):
        """创建子 Agent (独立 Worktree + tmux)"""

    def assign_task(self, agent: str, task: str, blocked_by: List[str] = None):
        """分配任务 (支持依赖链)"""

    def monitor_progress(self) -> SwarmStatus:
        """监控进度"""

    def terminate_and_respawn(self, agent: str, new_command: str):
        """终止低效 Agent，重新分配"""
```

### 5.2 CEO 路由引擎

```python
# CyberTeam/engine/ceo.py
class CEOThinkingEngine:
    """CEO 思维引擎 - 垂直行业核心"""

    def decompose(self, goal: str) -> Plan:
        """目标分解"""

    def route(self, complexity: str) -> RoutingDecision:
        """路由决策:
        - 简单咨询 → 直接回复
        - 低复杂度 → L3C executor
        - 高复杂度多领域 → SWARM
        """
```

### 5.3 辩论引擎

```python
# CyberTeam/engine/debate_engine.py
class DebateEngine:
    """多 Agent 辩论引擎"""

    def start_debate(self, topic: str, agents: List[str]) -> DebateResult:
        """启动辩论"""

    def vote(self, debate_id: str) -> VoteResult:
        """投票收敛"""
```

## 六、数据流

```
用户输入
    │
    ▼
CEO 路由引擎 (engine/ceo.py)
    │
    ├── 简单咨询 ──────────────────► 直接回复
    │
    ├── 低复杂度 ──────────────────► L3C Executor
    │
    └── 高复杂度多领域 ──────────────► SwarmOrchestrator
                                         │
                                         ├── 创建子 Agent (spawn/)
                                         │       ├── Git Worktree (workspace/)
                                         │       └── tmux Session (tmux_backend/)
                                         │
                                         ├── 分配任务 (team/tasks.py)
                                         │       └── 依赖链 + 自动阻塞/解除
                                         │
                                         ├── Agent 间通信 (team/mailbox.py)
                                         │
                                         ├── 监控进度 (board/)
                                         │
                                         └── 结果汇聚 ───────────► 最终方案
```

## 七、与 ClawTeam 的命令对照

| ClawTeam 命令 | CyberTeam V4 | 说明 |
|--------------|--------------|------|
| `clawteam launch` | `cyberteam launch` | 从模板启动团队 |
| `clawteam spawn` | `cyberteam spawn` | Spawn 单个 Agent |
| `clawteam team` | `cyberteam team` | 团队管理 |
| `clawteam task` | `cyberteam task` | 任务管理 |
| `clawteam inbox` | `cyberteam inbox` | 消息收件箱 |
| `clawteam board` | `cyberteam board` | 仪表盘 |
| `clawteam profile` | `cyberteam profile` | Agent 配置 |
| `clawteam session` | `cyberteam session` | 会话持久化 |
| `clawteam lifecycle` | `cyberteam lifecycle` | 生命周期管理 |
| `clawteam cost` | `cyberteam cost` | 成本追踪 |
| `clawteam workspace` | `cyberteam workspace` | Git Worktree |

## 八、文件映射清单

需要从 ClawTeam 复制并重命名的文件：

```bash
# 复制 + 重命名目录结构
clawteam/team/    ────► cyberteam/team/
clawteam/spawn/   ────► cyberteam/spawn/
clawteam/workspace/ ──► cyberteam/workspace/
clawteam/board/   ────► cyberteam/board/
clawteam/transport/ ───► cyberteam/transport/

# 重命名包和类
ClawTeam ──────────► CyberTeam
clawteam ──────────► cyberteam
TeamManager ────────► TeamManager (保留)
SpawnRegistry ──────► SpawnRegistry (保留)
```

## 九、依赖关系

```toml
# pyproject.toml
[project]
name = "cyberteam"
version = "4.0.0"
dependencies = [
    "clawteam @ file:///path/to/ClawTeam",  # 本地 ClawTeam 作为依赖
    "fastapi>=0.100.0",
    "uvicorn>=0.23.0",
    "typer>=0.9.0",
    "tmux>=0.23.0",
    "pyyaml>=6.0",
]

[project.scripts]
cyberteam = "cyberteam.cli.main:app"
```

## 十、后续开发计划

- [ ] **Phase 1**: 基础架构 - 复制 ClawTeam 并重命名为 CyberTeam
- [ ] **Phase 2**: Swarm 核心 - 实现 SwarmOrchestrator
- [ ] **Phase 3**: CEO 引擎 - 集成 CEO 路由
- [ ] **Phase 4**: 辩论引擎 - 实现多 Agent 辩论
- [ ] **Phase 5**: FastAPI 后端 - REST API
- [ ] **Phase 6**: CLI 工具 - cyberteam 命令
- [ ] **Phase 7**: Dashboard - Web UI

---

*最后更新: 2026-03-25*
*基于: ClawTeam v1.0 (https://github.com/HKUDS/ClawTeam)*
