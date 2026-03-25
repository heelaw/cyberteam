# ClawTeam 框架集成方案

**版本**: v1.0
**日期**: 2026-03-24
**作者**: architect-001 + tech-lead-001（P8闭环整理）
**团队**: cyberteam-discuss
**状态**: 已完成

---

## 一、集成策略概述

CyberTeam v2.0 采用 **ClawTeam 作为底层执行框架**，保留 CyberTeam 上层架构（CEO调度、部门Agent、运营专家）。ClawTeam 负责：
- 多Agent生命周期管理（spawn/stop/restart）
- 进程级隔离（tmux worktree）
- 消息队列（inbox/outbox）
- 任务看板（task board）
- 运行时监控（board dashboard）

```
┌──────────────────────────────────────────────────────────┐
│              CyberTeam 上层架构                          │
│  CEO Agent → 部门Agent → 运营专家 + 思维专家              │
│  (任务分发 · 结果聚合 · 决策生成)                         │
├──────────────────────────────────────────────────────────┤
│              ClawTeam 底层执行层                          │
│  spawn · inbox · task · board · lifecycle                │
├──────────────────────────────────────────────────────────┤
│              进程层（tmux/subprocess）                    │
│  Agent进程 · 工作空间隔离 · 环境变量注入                   │
└──────────────────────────────────────────────────────────┘
```

## 二、核心集成点

### 2.1 Agent Spawn 集成

CyberTeam 的每个 Agent（CEO、部门Agent、专家Agent）通过 ClawTeam spawn：

```bash
# CEO Agent spawn
clawteam spawn tmux claude \
  --team cyberteam \
  --agent-name ceo-agent \
  --task "你是CyberTeam CEO，负责调度整个团队..."

# 部门Agent spawn
clawteam spawn tmux claude \
  --team cyberteam \
  --agent-name engineering-director \
  --task "你是工程总监，负责..."

# 专家Agent spawn（并行）
clawteam spawn tmux claude --team cyberteam --agent-name arch-expert --task "..."
clawteam spawn tmux claude --team cyberteam --agent-name quality-expert --task "..."
```

### 2.2 Inbox 消息流

```
[CEO Agent]  ──inbox──→  [部门Agent]
[部门Agent]  ──inbox──→  [专家Agent]
[专家Agent]  ──inbox──→  [部门Agent]
[部门Agent]  ──inbox──→  [CEO Agent]
```

ClawTeam inbox 命令：
```bash
clawteam inbox send <team> <agent> <message>
clawteam inbox receive <team> --agent <agent>
clawteam inbox peek <team> --agent <agent>  # 非破坏性读取
```

### 2.3 任务看板集成

```bash
# 创建任务
clawteam task create cyberteam "实现Goal-Driven循环" -o engineering-director
clawteam task create cyberteam "设计DevQA门控" -o quality-expert --blocked-by <ceo-task>

# 更新状态
clawteam task update cyberteam <task-id> --status in_progress
clawteam task update cyberteam <task-id> --status completed

# 查看看板
clawteam board show cyberteam
clawteam board live cyberteam --interval 5
```

### 2.4 生命周期管理

```bash
# Agent 启动时自动注册
clawteam lifecycle on-exit --team cyberteam --agent <agent>

# 优雅退出
clawteam lifecycle request-shutdown cyberteam --agent <agent>

# 查看所有Agent状态
clawteam board overview cyberteam
```

## 三、ClawTeam 配置文件

CyberTeam 团队配置 (`~/.clawteam/teams/cyberteam/`):

```json
{
  "name": "cyberteam",
  "description": "CyberTeam v2.0 AI协作团队",
  "leader": "ceo-agent",
  "members": [
    {"name": "ceo-agent", "type": "leader"},
    {"name": "engineering-director", "type": "department"},
    {"name": "ops-director", "type": "department"},
    {"name": "quality-director", "type": "department"},
    {"name": "arch-expert", "type": "specialist"},
    {"name": "gstack-expert", "type": "specialist"},
    {"name": "quality-expert", "type": "specialist"}
  ],
  "settings": {
    "spawn_backend": "tmux",
    "skip_permissions": true,
    "workspace_mode": "auto"
  }
}
```

## 四、实施路线图

| 阶段 | 周次 | 内容 | 交付物 |
|------|------|------|--------|
| **Phase 0** | - | 环境准备：ClawTeam安装、配置、CLI验证 | 可用的clawteam命令 |
| **Phase 1** | Week1-2 | 基础循环框架：spawn→inbox→task→board 单Agent闭环 | 最小可运行团队 |
| **Phase 2** | Week3-4 | 断点恢复：lifecycle、snapshot、context注入 | 可恢复的团队状态 |
| **Phase 3** | Week5-6 | PUA集成：压力升级触发、inbox告警、多Agent协调 | PUA动机引擎 |
| **Phase 4** | Week7-8 | HUD与优化：board dashboard、监控面板、指标展示 | 可视化运营中心 |

## 五、风险评估

| 风险项 | 级别 | 缓解策略 |
|--------|------|----------|
| ClawTeam CLI稳定性 | 中 | Phase1先做PoC验证，隔离测试 |
| tmux会话管理冲突 | 低 | 使用--skip-permissions避免权限问题 |
| 消息队列积压 | 低 | inbox peek监控，定期清理 |
| Agent僵尸进程 | 中 | lifecycle on-exit自动清理 |
| 多Agent并发写入冲突 | 低 | git worktree隔离各Agent工作空间 |

**综合评估：ClawTeam集成 风险 中/低，实施可行。**

## 六、关键命令速查

```bash
# 团队管理
clawteam team status cyberteam
clawteam team snapshot cyberteam --tag v1.0
clawteam team restore cyberteam --snapshot v1.0

# Agent生命周期
clawteam spawn --team cyberteam --agent-name <name> --task "<task>"
clawteam lifecycle idle cyberteam --agent <name>
clawteam lifecycle request-shutdown cyberteam --agent <name>

# 消息与任务
clawteam inbox send cyberteam <agent> "<message>"
clawteam inbox peek cyberteam --agent <agent>
clawteam task list cyberteam --status pending
clawteam task create cyberteam "<task>" -o <owner>

# 监控
clawteam board show cyberteam
clawteam board live cyberteam --interval 3
clawteam board gource cyberteam --log-only

# Git上下文
clawteam context inject cyberteam --agent <name>
clawteam context conflicts cyberteam
```

## 七、与 CyberTeam 原架构的关系

| CyberTeam 原组件 | ClawTeam 映射 | 说明 |
|-----------------|---------------|------|
| Agent Supervisor | clawteam spawn/lifecycle | 进程管理 |
| 消息总线 | clawteam inbox | 异步消息队列 |
| 任务分发 | clawteam task | 共享任务看板 |
| 状态监控 | clawteam board | 实时监控面板 |
| 工作空间隔离 | git worktree | 各Agent独立工作目录 |
| 断点恢复 | clawteam snapshot | 团队状态快照 |

## 八、验证计划

```bash
# 1. CLI验证
clawteam --version
clawteam team status

# 2. 单Agent闭环
clawteam spawn --team test --agent-name test-1 --task "echo done"
clawteam inbox send test test-1 "report back"
clawteam inbox peek test --agent test-1
clawteam lifecycle request-shutdown test --agent test-1

# 3. 多Agent协作
clawteam spawn --team test --agent-name test-2
clawteam inbox send test test-2 "hello from test-1"
clawteam task create test "验证任务"
clawteam board show test

# 4. 集成测试
./scripts/test-clawteam-integration.sh
```
