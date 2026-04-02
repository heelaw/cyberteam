# goal-driven-main 运行契约

## 最终目标

把 CyberTeam Desktop 做成一个可持续迭代的本地优先系统：Electron 负责运行时，Next.js 负责渲染层，SQLite 负责单一事实源，所有协作、审核、路线图和质量门控都能写回运行时数据。

## 伪代码

```text
goal = "把 CyberTeam Desktop 做成可用、可验证、可扩展的本地 AI 协作系统"
done = false
iteration = 0

while not done and iteration < MAX_ITERATIONS:
    iteration += 1

    observe_repo_state()
    read_current_plan_and_runtime_contract()
    load_pua_pressure()

    tasks = decompose_goal_into_atomic_tasks(goal)
    assign_tasks_to_experts(tasks, roles=[
        "总指挥",
        "路由/架构",
        "数据/DB",
        "渲染/UI",
        "IPC/桥接",
        "路由/页面",
        "质量检查"
    ])

    run_tasks_in_parallel(tasks)

    quality_report = quality_gate(
        checks=["typecheck", "build", "runtime_consistency", "hidden_edge_cases"]
    )

    if quality_report.failed:
        fix_root_causes(quality_report.findings)
        continue

    if product_has_new_gap():
        add_gap_to_backlog()
        continue

    done = all_core_flows_work() and quality_report.passed and no_known_blockers()

return final_report(goal, iteration, quality_report)
```

## 角色分工

- `总指挥`：统一目标、拆解任务、收敛冲突、决定是否进入下一轮。
- `路由/架构`：保持数据模型、运行态、页面入口、IPC 约束一致。
- `数据/DB`：维护 SQLite schema、seed、snapshot、insert/update 逻辑。
- `渲染/UI`：维护页面、实时刷新、表单交互、展示一致性。
- `IPC/桥接`：维护 preload、handler、channel 名称、payload 类型。
- `路由/页面`：维护 app route、静态导出、seed 复用、入口一致性。
- `质量检查`：专门扫描遗漏问题、隐藏 bug、测试缺口、回归风险。

## 质量门

1. `typecheck` 必须通过。
2. `build` 必须通过。
3. 运行时数据必须能从 SQLite 读回并刷新 UI。
4. 新增能力必须有对应的 schema 或 bridge，不允许只改 UI。
5. 每一轮必须检查同类问题，不只修单点。

## 失败处理

- 如果同一类问题重复出现，切换方案，不在原地微调。
- 如果发现事实不一致，先查源码和运行态，不猜。
- 如果出现隐藏断点，补齐最小验证，再继续推进。
- 如果需要人工介入，先冻结当前进度并记录恢复点。

## 完成条件

- 核心产品流完整：Dashboard / Chat / Organization / Playground / Market / Settings。
- 路由、IPC、DB、UI 形成闭环。
- `check` 和 `build` 通过。
- 质量检查没有新的 P0 / P1 问题。
- 路线图和运行态都可编辑、可持久化、可刷新。

