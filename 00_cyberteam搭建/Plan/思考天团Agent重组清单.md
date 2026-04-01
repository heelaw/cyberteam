# 思考天团 Agent 重组清单

## 处理原则

- 保留：输出契约清晰、边界独立、用户高频使用的能力。
- 合并：同族近义、职责重叠、触发场景高度相似的模型。
- 降级：低频、过细、更多像标签而不是独立人格的模型。

## 保留为独立 Agent

| ID | 角色 | 说明 |
|---|---|---|
| kahneman | 决策与偏差 | 决策场景高频，输出稳定 |
| fivewhy | 根因诊断 | 与其他模型边界清晰 |
| problem-reformulation | 问题重构 | 独立入口能力 |
| first-principle | 第一性原理 | 创新与重构核心能力 |
| swot-tows | 战略分析 | 竞争与规划场景稳定 |
| systems-thinking | 系统思维 | 复杂系统整合能力 |
| probabilistic / bayesian | 概率思维 | 不确定性决策必需 |
| grow | 目标实现 | 从目标到路径 |
| wbs | 执行拆解 | 从路径到任务 |
| kiss | 复盘简化 | 回顾与提炼 |
| manager-leap | 管理跃迁 | 管理成长场景独立 |
| ai-board | 多角色决策 | 重大决策评审 |

## 合并成能力组

| 能力组 | 合并来源 |
|---|---|
| 结构化思维组 | mckinsey, critical-thinking, falsification-principle |
| 逆向推理组 | reverse-thinking, inversion, counterfactual |
| 多视角组 | six-hats, dialectical |
| 资源权衡组 | opportunity-cost, sunk-cost, pareto |
| 偏差识别组 | confirmation-bias, availability-heuristic, representativeness-heuristic |
| 简化克制组 | occams-razor, hanlons-razor, maslows-hammer |
| 复杂性韧性组 | anti-fragile, second-order, systems-thinker |
| 增长网络组 | compound-effect, flywheel, network-effects, metcalfe-law |

## 降级为模型库

| 类别 | 处理方式 |
|---|---|
| 行为偏差 | 作为检查清单和提示标签 |
| 战略理论 | 作为参考模块被调用 |
| 管理法则 | 作为组织成长提示卡 |
| 心理学理论 | 作为风险提示与约束 |
| 认知启发式 | 作为路由辅助规则 |

## 命名修正

| 现状 | 建议 |
|---|---|
| `goldlin` 内容是复盘，命名却像问题定义 | 纠正映射，避免继续错位 |
| `kiss` 内容像吉德林法则 | 重新归位为复盘模块 |
| `reverse-thinking` / `inversion` / `counterfactual` | 统一到逆向推理组 |
| `systems-thinking` / `systems-thinker` | 统一 canonical 名称 |
| `probabilistic` / `bayesian` | 统一到概率推理组 |

## 推荐执行顺序

1. 先修正命名与 canonical mapping。
2. 再抽出 8-12 个核心 Agent。
3. 然后把剩余模型转成能力卡。
4. 最后重写 Skill 的路由与输出模板。
