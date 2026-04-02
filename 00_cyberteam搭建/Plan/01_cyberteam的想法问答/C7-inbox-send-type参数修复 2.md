# C7 问题修复报告: cyberteam inbox send --type 参数问题

**问题编号**: C7
**问题描述**: Q67 spawn后inbox send使用--type参数存疑
**修复日期**: 2026-03-22
**修复人**: fix-inbox-cli

---

## 一、问题分析

### 1.1 问题根源

Q67 的 `TaskBridge.spawn_worker()` 方法中使用了下述命令格式：

```python
inbox_cmd = [
    "cyberteam", "inbox", "send",
    team_name,
    agent_name,
    inbox_msg,
    "--type", "task_assignment"  # <-- 错误用法
]
```

### 1.2 CLI 实际规格

通过 `cyberteam inbox send --help` 验证，实际 CLI 选项：

| 选项 | 功能 | 说明 |
|------|------|------|
| `--type TEXT` | Message type | 消息类型标签，默认 "message"，**不创建 TaskStore 条目** |
| `--task TEXT` | Also create TaskStore task | **同时创建 TaskStore 条目**，用于任务追踪 |

### 1.3 问题影响

- `--type task_assignment` 仅设置消息类型标签，**不会**在 TaskStore 中创建任务
- 导致 Worker Agent 无法通过 TaskStore 追踪任务状态
- 违背了 Q67 "spawn后 Agent 通过 inbox 接收任务指令" 的设计意图

---

## 二、修复方案

### 2.1 代码修复

**位置**: Q67-ClawTeam集成适配器设计.md, 第 490 行

**修改前**:
```python
inbox_cmd = [
    "cyberteam", "inbox", "send",
    team_name,
    agent_name,
    inbox_msg,
    "--type", "task_assignment"  # 错误：只设置标签，不创建任务
]
```

**修改后**:
```python
inbox_cmd = [
    "cyberteam", "inbox", "send",
    team_name,
    agent_name,
    inbox_msg,
    "--task", task_subject  # 正确：创建 TaskStore 条目
]
```

### 2.2 文档修复

**位置**: Q67 第 1337 行 (执行流程说明)

**修改前**:
```
├─► cyberteam inbox send <team> <agent> <task JSON> --type task_assignment
```

**修改后**:
```
├─► cyberteam inbox send <team> <agent> <task JSON> --task <subject>
```

---

## 三、验证方法

### 3.1 CLI 命令验证

```bash
# 验证 --task 选项存在
cyberteam inbox send --help | grep -A1 "\-\-task"

# 验证命令格式
cyberteam inbox send <team> <to> <content> --task <subject>
```

### 3.2 代码逻辑验证

修复后的 `spawn_worker` 流程：

1. `spawn tmux claude --team <team> --agent-name <name> --agent-type <type>` - 创建 Agent 进程
2. `inbox send <team> <agent> <json> --task <subject>` - 发送任务**并创建 TaskStore 条目**
3. Worker Agent 可通过 TaskStore 查询任务状态

---

## 四、修正记录

| 日期 | 修正内容 | 状态 |
|------|----------|------|
| 2026-03-22 | 将 `--type task_assignment` 改为 `--task task_subject` | ✅ 已修复 |
| 2026-03-22 | 更新第1337行 CLI 命令示例 | ✅ 已修复 |

---

## 五、影响评估

| 方面 | 影响 |
|------|------|
| TaskStore 集成 | ✅ 现在能正确创建任务条目 |
| Worker 追踪 | ✅ Worker 现在可通过 TaskStore 查询状态 |
| 消息传递 | ⚠️ 消息体不变，仅增加 TaskStore 同步 |
| 向后兼容 | ✅ 不影响现有消息格式 |
