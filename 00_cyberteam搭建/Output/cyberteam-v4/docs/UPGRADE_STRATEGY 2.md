# CyberTeam V4 升级同步策略

> 版本: v1.0
> 日期: 2026-03-26
> 目标: 确保 CyberTeam V4 能快速跟随 ClawTeam 升级

---

## 一、设计原则

### 1.1 核心原则

```
ClawTeam (上游)  ──────────────────────────────────────▶  CyberTeam V4 (下游)
     │                                                              │
     │  底层模块同步更新                                             │  企业级扩展保持独立
     │  spawn/team/workspace/board/                                 │  transport/ (MessageRouter, HandoffProtocol)
     │                                                              │  engine/ (CEO, Department, Strategy)
     ▼                                                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    适配层 (Adapter Layer)                    │
│  integration/cyberteam_adapter.py                            │
│  cyberteam/adaptors/clawteam_compat.py                      │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 模块分类

| 分类 | 模块 | 同步策略 | 说明 |
|------|------|----------|------|
| **底层同步** | spawn/, team/, workspace/, board/ | 与 ClawTeam 完全同步 | 保持一致 |
| **企业扩展** | transport/ (扩展部分) | 独立发展 | CyberTeam 独有 |
| **大脑引擎** | engine/ | 独立发展 | 业务逻辑层 |
| **适配层** | integration/, cyberteam/adaptors/ | 随 ClawTeam 升级更新 | 隔离层 |

---

## 二、ClawTeam 升级流程

### 2.1 升级检查清单

当 ClawTeam 发布新版本时，按以下顺序检查：

```
[ ] 1. 检查 ClawTeam 新版本变化
[ ] 2. 识别受影响的模块
[ ] 3. 执行兼容性测试
[ ] 4. 更新适配层 (如果需要)
[ ] 5. 验证所有模块导入
[ ] 6. 运行完整测试套件
```

### 2.2 模块升级影响评估

| ClawTeam 变更模块 | CyberTeam 受影响组件 | 评估方法 |
|-------------------|---------------------|----------|
| spawn/ | SwarmOrchestrator | `python3 -c "from swarm_orchestrator import SwarmOrchestrator"` |
| team/ | 所有使用 TeamManager 的模块 | `python3 -c "from cyberteam.team import TeamManager"` |
| workspace/ | WorkspaceManager | `python3 -c "from cyberteam.workspace import WorkspaceManager"` |
| transport/ | 消息传递层 | `python3 -c "from cyberteam.transport import get_transport"` |
| board/ | Dashboard | `python3 -c "from cyberteam.board import BoardCollector"` |
| config.py | 配置管理 | `python3 -c "from cyberteam.config import load_config"` |

### 2.3 快速升级脚本

```bash
#!/bin/bash
# upgrade_check.sh - ClawTeam 升级检查脚本

set -e

echo "=== CyberTeam V4 升级检查 ==="

# 1. 检查 ClawTeam 版本
CLAWTEAM_VERSION=$(clawteam --version 2>/dev/null || echo "unknown")
echo "ClawTeam 版本: $CLAWTEAM_VERSION"

# 2. 核心模块导入测试
echo ""
echo "模块导入测试:"

python3 -c "from cyberteam.team import TeamManager" && echo "  ✅ team/" || echo "  ❌ team/"
python3 -c "from cyberteam.spawn import get_backend" && echo "  ✅ spawn/" || echo "  ❌ spawn/"
python3 -c "from cyberteam.workspace import WorkspaceManager" && echo "  ✅ workspace/" || echo "  ❌ workspace/"
python3 -c "from cyberteam.transport import get_transport" && echo "  ✅ transport/" || echo "  ❌ transport/"
python3 -c "from cyberteam.board import BoardCollector" && echo "  ✅ board/" || echo "  ❌ board/"
python3 -c "from swarm_orchestrator import SwarmOrchestrator" && echo "  ✅ swarm_orchestrator" || echo "  ❌ swarm_orchestrator/"
python3 -c "from integration.cyberteam_adapter import CyberTeamAdapter" && echo "  ✅ integration/" || echo "  ❌ integration/"
python3 -c "from engine.ceo import CEORouter" && echo "  ✅ engine/ceo" || echo "  ❌ engine/ceo"

# 3. 适配器健康检查
echo ""
echo "适配器健康检查:"
python3 -c "
from integration.cyberteam_adapter import CyberTeamAdapter
adapter = CyberTeamAdapter()
health = adapter.health_check()
print(f'  cyberteam_available: {health[\"cyberteam_available\"]}')
print(f'  backend: {health[\"backend\"]}')
"

echo ""
echo "=== 检查完成 ==="
```

---

## 三、CyberTeam 定制化扩展

### 3.1 CyberTeam 独有模块

| 模块 | 位置 | 功能 | 升级影响 |
|------|------|------|----------|
| **Transport 扩展** | `cyberteam/transport/` | MessageRouter, HandoffProtocol, InboxManager | 无（独立发展） |
| **Engine** | `engine/` | CEO, Department, Strategy, Debate | 无（独立发展） |
| **Adaptors** | `cyberteam/adaptors/` | ClawTeam 兼容层 | 当 ClawTeam 升级时更新 |
| **Agent 定义** | `agents/` | Agent 角色定义 | 无（独立发展） |
| **Skills** | `skills/` | 技能定义 | 无（独立发展） |
| **Thinking Models** | `thinking_models/` | 105 个思维专家 | 无（独立发展） |

### 3.2 扩展点清单

```
CyberTeam V4 扩展点
│
├── transport/transport.py      ← TransportLayer (企业级通信)
├── transport/message_router.py  ← MessageRouter (智能路由)
├── transport/handoff_protocol.py ← HandoffProtocol (任务交接)
├── engine/swarm/               ← 独立 Swarm 实现
├── agents/                     ← Agent 角色定义
└── skills/                    ← 技能定义
```

---

## 四、接口契约

### 4.1 engine层 → cyberteam底层 接口

所有 engine 层对 cyberteam 底层的调用必须通过 `integration/cyberteam_adapter.py`：

```python
# ❌ 禁止直接导入
from cyberteam.team import TeamManager  # 在 engine 层禁止

# ✅ 正确方式：通过适配器
from integration.cyberteam_adapter import CyberTeamAdapter
adapter = CyberTeamAdapter()
adapter.create_team(...)
```

### 4.2 适配器接口清单

```python
class CyberTeamAdapter:
    # 团队管理
    def create_team(self, team_name: str, description: str = "") -> dict
    def delete_team(self, team_name: str) -> bool
    def list_teams(self) -> list[str]

    # Agent 管理
    def spawn_agent(self, team_name: str, agent_name: str, role: str,
                    task: str = None, backend: str = None) -> AgentInfo
    def stop_agent(self, agent_name: str) -> bool
    def is_agent_alive(self, agent_name: str) -> bool

    # 任务管理
    def create_task(self, team_name: str, subject: str, ...) -> TaskItem
    def assign_task(self, team_name: str, agent_name: str, task_id: str) -> bool
    def complete_task(self, team_name: str, task_id: str, result: str) -> bool

    # 消息传递
    def send_message(self, team_name: str, from_agent: str,
                    to_agent: str, content: str) -> bool
    def get_messages(self, team_name: str, agent_name: str) -> list[dict]
```

---

## 五、测试验证

### 5.1 完整测试命令

```bash
# 1. 模块导入测试
python3 << 'EOF'
import sys
sys.path.insert(0, '.')

# 核心模块
from cyberteam.team import TeamManager, TaskStore, MailboxManager
from cyberteam.spawn import get_backend, SpawnRegistryManager
from cyberteam.workspace import WorkspaceManager, WorkspaceInfo
from cyberteam.transport import get_transport, FileTransport, P2PTransport
from cyberteam.board import BoardCollector, BoardRenderer
from cyberteam.adaptors import ClawTeamCompat, ConfigUnifier

# Swarm
from swarm_orchestrator import SwarmOrchestrator, SwarmStatus

# Engine
from engine.ceo import CEORouter
from engine.department import DepartmentExecutor

# Adapter
from integration.cyberteam_adapter import CyberTeamAdapter

# Adapter 健康检查
adapter = CyberTeamAdapter()
health = adapter.health_check()
assert health['cyberteam_available'] == True

print("✅ 所有模块导入成功")
EOF

# 2. CLI 测试
cyberteam --version
cyberteam --help

# 3. Swarm 创建测试 (可选，需要 tmux)
python3 << 'EOF'
from swarm_orchestrator import SwarmOrchestrator, SwarmStatus

swarm = SwarmOrchestrator("test-upgrade", "测试升级")
print(f"✅ Swarm 创建成功: {swarm.team_name}")
EOF
```

---

## 六、版本兼容性矩阵

| CyberTeam V4 | ClawTeam 版本 | 兼容性 | 备注 |
|--------------|---------------|--------|------|
| v4.0.0 | v0.2.0+ | ✅ 兼容 | 当前版本 |
| v4.0.0 | v0.1.x | ⚠️ 未测试 | 可能需要适配 |
| v4.0.0 | v0.3.0+ | 🔄 待验证 | 需运行升级检查 |

---

## 七、升级后检查清单

当 ClawTeam 升级后，执行以下检查：

```
[ ] 1. 运行 upgrade_check.sh
[ ] 2. 验证所有模块导入成功
[ ] 3. 检查 cyberteam_adapter.py 接口兼容性
[ ] 4. 运行 SwarmOrchestrator 基本功能测试
[ ] 5. 验证 CEO 路由引擎正常工作
[ ] 6. 检查 ConfigUnifier 配置迁移
[ ] 7. 测试 CLI 命令完整性
[ ] 8. 更新本文档版本记录
```

---

## 八、联系与支持

如遇到升级问题，请检查：

1. **模块导入问题**: 检查 `__init__.py` 导出是否完整
2. **适配器问题**: 检查 `integration/cyberteam_adapter.py` 接口
3. **Swarm 问题**: 检查 `swarm_orchestrator.py` 导入语句
4. **配置问题**: 使用 `ConfigUnifier` 验证配置

---

*文档版本: v1.0 | 更新日期: 2026-03-26*
