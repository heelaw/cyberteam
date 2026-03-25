# DevFleet — 多代理编排

通过 Claude DevFleet 协调并行 Claude Code 代理。每个代理都在一个独立的 git 工作树中运行，并具有完整的工具。

需要 DevFleet MCP 服务器：`claude mcp add devfleet --transport http http://localhost:18801/mcp`

## 流量```
User describes project
  → plan_project(prompt) → mission DAG with dependencies
  → Show plan, get approval
  → dispatch_mission(M1) → Agent spawns in worktree
  → M1 completes → auto-merge → M2 auto-dispatches (depends_on M1)
  → M2 completes → auto-merge
  → get_report(M2) → files_changed, what_done, errors, next_steps
  → Report summary to user
```## 工作流程

1. **根据用户的描述规划项目**：```
mcp__devfleet__plan_project(prompt="<user's description>")
```这将返回一个具有链式任务的项目。向用户显示：
- 项目名称和ID
- 每个任务：标题、类型、依赖性
- 依赖 DAG（哪些任务阻止哪些任务）

2. **等待用户批准**后再发货。清楚地展示计划。

3. **调度第一个任务**（带有空 `depends_on` 的任务）：```
mcp__devfleet__dispatch_mission(mission_id="<first_mission_id>")
```其余任务会在其依赖项完成时自动调度（因为“plan_project”使用“auto_dispatch=true”创建它们）。使用“create_mission”手动创建任务时，必须为此行为显式设置“auto_dispatch=true”。

4. **监控进度** — 检查正在运行的内容：```
mcp__devfleet__get_dashboard()
```或者检查特定任务：```
mcp__devfleet__get_mission_status(mission_id="<id>")
```对于长时间运行的任务，优先使用“get_mission_status”而不是“wait_for_mission”进行轮询，以便用户看到进度更新。

5. **阅读每个已完成任务的报告**：```
mcp__devfleet__get_report(mission_id="<mission_id>")
```对于每个达到最终状态的任务都调用此方法。报告包含：files_changed、what_done、what_open、what_tested、what_untested、next_steps、errors_encountered。

## 所有可用的工具

|工具|目的|
|------|---------|
| `计划项目（提示）` | AI 使用“auto_dispatch=true”将描述分解为链式任务 |
| `create_project(名称、路径？、描述？)` |手动创建项目，返回 `project_id` |
| `create_mission（project_id，标题，提示，depends_on？，auto_dispatch？）` |添加任务。 `depends_on` 是任务 ID 字符串列表。 |
| `dispatch_mission(mission_id, model?, max_turns?)` |启动代理|
| `cancel_mission(mission_id)` |停止正在运行的代理 |
| `wait_for_mission(mission_id, timeout_seconds?)` |阻塞直到完成（对于长任务更喜欢轮询）|
| `get_mission_status(mission_id)` |不阻塞地检查进度 |
| `get_report(mission_id)` |阅读结构化报告 |
| `get_dashboard()` |系统概述 |
| `list_projects()` |浏览项目 |
| `list_missions(project_id, status?)` |列出任务 |

## 指南

- 发货前务必确认计划，除非用户说“继续”
- 报告状态时包括任务标题和 ID
- 如果任务失败，请在重试之前阅读其报告以了解错误
- 代理并发数是可配置的（默认值：3）。多余的任务会排队并在空位空闲时自动调度。检查“get_dashboard()”以了解插槽可用性。
- 依赖关系形成 DAG——永远不会创建循环依赖关系
- 每个代理在完成后自动合并其工作树。如果发生合并冲突，更改将保留在工作树分支上以供手动解决。