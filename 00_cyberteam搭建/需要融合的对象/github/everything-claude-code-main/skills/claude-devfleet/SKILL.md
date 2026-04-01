# Claude DevFleet 多代理编排

## 何时使用

当您需要派遣多个 Claude Code 代理并行执行编码任务时，请使用此技能。每个代理都在一个独立的 git 工作树中运行，并具有完整的工具。

需要通过 MCP 连接正在运行的 Claude DevFleet 实例：```bash
claude mcp add devfleet --transport http http://localhost:18801/mcp
```## 它是如何工作的```
User → "Build a REST API with auth and tests"
  ↓
plan_project(prompt) → project_id + mission DAG
  ↓
Show plan to user → get approval
  ↓
dispatch_mission(M1) → Agent 1 spawns in worktree
  ↓
M1 completes → auto-merge → auto-dispatch M2 (depends_on M1)
  ↓
M2 completes → auto-merge
  ↓
get_report(M2) → files_changed, what_done, errors, next_steps
  ↓
Report back to user
```### 工具

|工具|目的|
|------|---------|
| `计划项目（提示）` |人工智能将描述分解为具有连锁任务的项目 |
| `create_project(名称、路径？、描述？)` |手动创建项目，返回 `project_id` |
| `create_mission（project_id，标题，提示，depends_on？，auto_dispatch？）` |添加任务。 `depends_on` 是任务 ID 字符串列表（例如，`["abc-123"]`）。设置“auto_dispatch=true”以在满足 deps 时自动启动。 |
| `dispatch_mission(mission_id, model?, max_turns?)` |启动特工执行任务|
| `cancel_mission(mission_id)` |停止正在运行的代理 |
| `wait_for_mission(mission_id, timeout_seconds?)` |阻止直到任务完成（参见下面的注释）|
| `get_mission_status(mission_id)` |不阻塞查看任务进度 |
| `get_report(mission_id)` |阅读结构化报告（文件更改、测试、错误、后续步骤）|
| `get_dashboard()` |系统概述：正在运行的代理、统计数据、最近的活动 |
| `list_projects()` |浏览所有项目 |
| `list_missions(project_id, status?)` |列出项目中的任务 |

> **关于“wait_for_mission”的注意事项：** 这会阻止对话长达“timeout_seconds”（默认 600）。对于长时间运行的任务，最好每 30-60 秒使用“get_mission_status”进行轮询，以便用户看到进度更新。

### 工作流程：计划→调度→监控→报告

1. **计划**：调用 `plan_project(prompt="...")` → 返回 `project_id` + 具有 `depends_on` 链和 `auto_dispatch=true` 的任务列表。
2. **显示计划**：向用户呈现任务标题、类型和依赖链。
3. **Dispatch**：在根任务上调用 `dispatch_mission(mission_id=<first_mission_id>)` （空 `depends_on`）。剩余任务会在其依赖项完成时自动调度（因为“plan_project”在其上设置了“auto_dispatch=true”）。
4. **监控**：调用`get_mission_status(mission_id=...)`或`get_dashboard()`来检查进度。
5. **报告**：任务完成时调用 `get_report(mission_id=...)`。与用户分享亮点。

### 并发

DevFleet 默认运行最多 3 个并发代理（可通过“DEVFLEET_MAX_AGENTS”进行配置）。当所有插槽已满时，带有“auto_dispatch=true”的任务会在任务观察器中排队，并在插槽空闲时自动调度。检查“get_dashboard()”当前插槽的使用情况。

## 示例

### 全自动：计划和启动

1. `plan_project(prompt="...")` → 显示包含任务和依赖项的计划。
2. 调度第一个任务（带有空 `depends_on` 的任务）。
3. 剩余任务会随着依赖关系的解析而自动调度（它们具有 `auto_dispatch=true`）。
4. 报告项目 ID 和任务计数，以便用户知道启动了什么。
5. 定期使用“get_mission_status”或“get_dashboard()”进行轮询，直到所有任务达到最终状态（“已完成”、“失败”或“已取消”）。
6. 每个终端任务的“get_report(mission_id=...)”——总结成功并指出失败、错误和后续步骤。

### 手动：逐步控制

1. `create_project(name="My Project")` → 返回 `project_id`。
2. 第一个（根）任务的`create_mission(project_id=project_id, title="...",prompt="...", auto_dispatch=true)` → 捕获`root_mission_id`。
   每个后续任务的`create_mission(project_id=project_id, title="...",prompt="...", auto_dispatch=true,depends_on=["<root_mission_id>"])`。
3. `dispatch_mission(mission_id=...)` 在第一个任务上启动链。
4. 完成后`get_report(mission_id=...)`。

### 顺序审查

1. `create_project(name="...")` → 获取`project_id`。
2.`create_mission(project_id=project_id, title="实现功能",prompt="...")`→获取`impl_mission_id`。
3.`dispatch_mission(mission_id=impl_mission_id)`，然后使用`get_mission_status`轮询直到完成。
4. `get_report(mission_id=impl_mission_id)` 查看结果。
5. `create_mission(project_id=project_id, title="Review",prompt="...", dependent_on=[impl_mission_id], auto_dispatch=true)` — 由于已经满足依赖关系而自动启动。

## 指南

- 发货前务必与用户确认计划，除非他们同意。
- 报告状态时包括任务标题和 ID。
- 如果任务失败，请在重试之前阅读其报告。
- 在批量调度之前检查“get_dashboard()”以了解代理插槽的可用性。
- 任务依赖关系形成 DAG——不创建循环依赖关系。
- 每个代理都在独立的 git 工作树中运行，并在完成后自动合并。如果发生合并冲突，更改将保留在代理的工作树分支上以供手动解决。
- 手动创建任务时，如果您希望任务在依赖关系完成时自动触发，请始终设置“auto_dispatch=true”。如果没有此标志，任务将保持“草稿”状态。