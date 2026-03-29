# CyberTeam V4 融合方案 (ClawTeam 集成)

> 版本: v1.0
> 日期: 2026-03-26
> 状态: 执行中

---

## 一、融合目标

### 1.1 核心目标
将 CyberTeam V4 的自研 `cyberteam/` 底层模块与外部 ClawTeam v0.2.0 实现**无缝融合**，保持 CyberTeam 独有设计逻辑不变。

### 1.2 融合原则
| 原则 | 说明 |
|------|------|
| **逻辑独立** | `engine/` 层完全独立，不受融合影响 |
| **接口兼容** | CyberTeam CLI/SDK 与 ClawTeam CLI 接口兼容 |
| **数据统一** | 统一使用 `~/.cyberteam/` 存储数据 |
| **能力增强** | 保留 CyberTeam 独有功能，引入 ClawTeam 成熟功能 |

---

## 二、现状分析

### 2.1 目录结构对比

| 模块 | 外部 ClawTeam v0.2.0 | CyberTeam V4 | 差异 |
|------|---------------------|--------------|------|
| `spawn/` | ✅ 进程孵化 | ✅ 已有 | 接口兼容 |
| `team/` | ✅ 团队管理 | ✅ 已有 | 接口兼容 |
| `workspace/` | ✅ Worktree | ✅ 已有 | 分支前缀不同 |
| `transport/` | ✅ 文件/P2P | ✅ 文件/P2P | 95%兼容 |
| `board/` | ✅ 看板 | ✅ 已有 | 兼容 |
| `cli/` | ✅ 命令 | ✅ 自研 | 需要适配 |
| `agents/` | ❌ 无 | ✅ 独有 | **CyberTeam独有** |
| `skills/` | ❌ 无 | ✅ 独有 | **CyberTeam独有** |
| `mcp/` | ❌ 无 | ✅ 独有 | **CyberTeam独有** |
| `thinking_models/` | ❌ 无 | ✅ 独有 | **CyberTeam独有** |
| `memory/` | ❌ 无 | ✅ 独有 | **CyberTeam独有** |
| `monitoring/` | ❌ 无 | ✅ 独有 | **CyberTeam独有** |

### 2.2 关键差异点

| 差异项 | 外部 ClawTeam | CyberTeam V4 | 融合策略 |
|--------|---------------|--------------|----------|
| **数据目录** | `~/.clawteam/` | `~/.cyberteam/` | **统一为 `~/.cyberteam/`** |
| **Branch 前缀** | `clawteam/{team}/{agent}` | `cyberteam/{team}/{agent}` | **统一为 `cyberteam/{team}/{agent}`** |
| **CLI 命令** | `clawteam` | `cyberteam` | **保留 `cyberteam` 命令** |
| **Profile 配置** | `~/.clawteam/config.json` | `~/.cyberteam/config.json` | **统一配置文件** |
| **P2P Transport** | 完整实现 | 基础实现 | **补充 CyberTeam P2P** |

---

## 三、融合架构

### 3.1 分层架构

```
┌─────────────────────────────────────────────────────────────┐
│                      CyberTeam V4                           │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │                    engine/ (独有)                      │ │
│  │  ceo/ │ pm/ │ department/ │ thinking/ │ debate/       │ │
│  └───────────────────────────────────────────────────────┘ │
│                            │                                │
│                            ▼                                │
│  ┌───────────────────────────────────────────────────────┐ │
│  │              cyberteam/ (融合层)                       │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌───────────────┐ │ │
│  │  │ CyberTeam   │  │ ClawTeam    │  │ Adaptors/     │ │ │
│  │  │ 独有模块    │  │ 底层兼容    │  │ 适配层       │ │ │
│  │  │ agents/     │  │ spawn/      │  │ compat.py    │ │ │
│  │  │ skills/     │  │ team/       │  │ bridge.py    │ │ │
│  │  │ mcp/        │  │ workspace/  │  │              │ │ │
│  │  │ thinking/   │  │ transport/  │  │              │ │ │
│  │  └─────────────┘  └─────────────┘  └───────────────┘ │ │
│  └───────────────────────────────────────────────────────┘ │
│                            │                                │
│                            ▼                                │
│  ┌───────────────────────────────────────────────────────┐ │
│  │              外部 ClawTeam v0.2.0                     │ │
│  │  (可选使用，作为底层能力补充)                          │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 适配器架构

```
cyberteam/
├── adaptors/                    # 🆕 融合适配层
│   ├── __init__.py
│   ├── clawteam_compat.py      # ClawTeam 接口兼容层
│   ├── config_unifier.py        # 配置统一管理
│   └── transport_bridge.py      # 消息传递桥接
├── spawn/
│   └── registry.py              # Agent Profile 注册表
├── team/
│   └── manager.py               # 团队管理器
└── workspace/
    └── manager.py               # Worktree 管理器
```

---

## 四、执行计划

### 4.1 任务清单

| 序号 | 任务 | 优先级 | 状态 |
|------|------|--------|------|
| 1 | 创建融合适配层 `adaptors/` | P0 | ⏳ 执行中 |
| 2 | 统一配置管理 (`config_unifier.py`) | P0 | ⏳ 待执行 |
| 3 | 补充 P2P Transport 能力 | P1 | ⏳ 待执行 |
| 4 | 更新 workspace 分支前缀 | P1 | ⏳ 待执行 |
| 5 | 更新 CLI 命令适配 | P1 | ⏳ 待执行 |
| 6 | 验证融合后功能 | P0 | ⏳ 待执行 |

### 4.2 融合检查清单

- [ ] 创建 `cyberteam/adaptors/` 目录
- [ ] 实现 `clawteam_compat.py` 接口兼容层
- [ ] 实现 `config_unifier.py` 配置统一
- [ ] CyberTeam 独有模块正确导出
- [ ] ClawTeam 底层接口兼容
- [ ] CLI 命令 `cyberteam` 正常工作
- [ ] 数据目录统一到 `~/.cyberteam/`
- [ ] Branch 前缀统一为 `cyberteam/{team}/{agent}`

---

## 五、配置统一规范

### 5.1 数据目录结构

```
~/.cyberteam/                    # 统一数据目录
├── config.json                  # 主配置文件
├── teams/                       # 团队数据
│   └── {team_name}/
│       ├── members.json
│       └── tasks/
├── tasks/                       # 任务数据
│   └── {task_id}.json
├── workspaces/                  # Git Worktrees
│   └── {team}/
│       └── {agent}/
├── mailboxes/                   # 消息邮箱
│   └── {agent}/
│       └── inbox/
├── sessions/                    # 会话记录
└── costs/                       # 成本追踪
```

### 5.2 Branch 命名规范

```
# 统一格式
cyberteam/{team_name}/{agent_name}

# 示例
cyberteam/career-expert/ceo
cyberteam/career-expert/ops-agent
cyberteam/career-expert/marketing-agent
```

---

## 六、接口兼容层设计

### 6.1 ClawTeamCompat 类

```python
class ClawTeamCompat:
    """ClawTeam 接口兼容层"""

    # 进程孵化
    def spawn_agent(self, team: str, agent: str, task: str, profile: str):
        """兼容 clawteam spawn 命令"""
        pass

    # 团队管理
    def create_team(self, name: str):
        """兼容 clawteam team create 命令"""
        pass

    # 消息传递
    def send_message(self, to: str, message: str):
        """兼容 clawteam inbox send 命令"""
        pass

    # Worktree 管理
    def create_workspace(self, team: str, agent: str):
        """兼容 clawteam workspace create 命令"""
        pass
```

### 6.2 ConfigUnifier 类

```python
class ConfigUnifier:
    """配置统一管理器"""

    # 统一配置路径
    CONFIG_PATH = Path.home() / ".cyberteam" / "config.json"

    # 兼容 ClawTeam 环境变量
    COMPAT_ENV_VARS = {
        "CLAWTEAM_DATA_DIR": "CYBERTEAM_DATA_DIR",
        "CLAWTEAM_USER": "CYBERTEAM_USER",
        "CLAWTEAM_TEAM_NAME": "CYBERTEAM_TEAM_NAME",
    }

    def load_compat_config(self) -> CyberTeamConfig:
        """加载兼容配置（支持 ClawTeam 配置迁移）"""
        pass

    def save_compat_config(self, config: CyberTeamConfig):
        """保存配置（同时生成 ClawTeam 兼容软链接）"""
        pass
```

---

## 七、验证方案

### 7.1 功能验证

| 测试项 | 预期结果 | 验证方法 |
|--------|----------|----------|
| `cyberteam --help` | 显示帮助信息 | CLI 测试 |
| `cyberteam team list` | 显示团队列表 | CLI 测试 |
| `cyberteam spawn --help` | 显示 spawn 帮助 | CLI 测试 |
| 创建团队后自动创建 worktree | Branch 创建成功 | Git 命令验证 |
| 消息发送和接收 | 消息正确传递 | Inbox 测试 |

### 7.2 兼容性验证

| 测试项 | 预期结果 | 验证方法 |
|--------|----------|----------|
| ClawTeam 配置文件迁移 | `~/.clawteam/config.json` → `~/.cyberteam/config.json` | 文件验证 |
| 旧数据访问 | `~/.clawteam/teams/` 数据可访问 | 读取测试 |
| 环境变量兼容 | `CLAWTEAM_*` 环境变量生效 | ENV 测试 |

---

## 八、风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 配置冲突 | 用户现有 ClawTeam 配置丢失 | 先备份再迁移 |
| Branch 命名冲突 | Git worktree 冲突 | 统一前缀后重新创建 |
| 消息格式差异 | 历史消息无法读取 | 保留双格式支持 |

---

## 九、里程碑

| 阶段 | 完成标志 | 预期时间 |
|------|----------|----------|
| **Phase 1: 适配层** | `adaptors/` 模块完成 | 30 分钟 |
| **Phase 2: 配置统一** | 统一配置文件完成 | 15 分钟 |
| **Phase 3: CLI 适配** | `cyberteam` 命令正常工作 | 15 分钟 |
| **Phase 4: 验证测试** | 所有功能验证通过 | 30 分钟 |

---

*本文档为执行指南，请配合代码变更同步更新。*
