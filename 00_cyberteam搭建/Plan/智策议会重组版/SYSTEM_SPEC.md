# 策源议会 重组版系统规格

## 1. 目标

把原先分散、重叠、错位的思维模型整理成一个可落地、可判断价值、可做取舍的协作系统。

这个版本不是“100 个 Agent 的大拼盘”，而是一个分层明确、职责收敛、先判断值不值得用的系统：

- 入口用 Skill。
- 调度用主持人 Agent。
- 高价值能力保留少量核心 Agent。
- 长尾思维模型沉到模型库。

## 2. 最终形态

```text
用户问题
  ↓
智策议会 Skill
  ↓
主持人 Agent
  ├── 决策与偏差组
  ├── 问题定义与诊断组
  ├── 战略与竞争组
  ├── 系统与复杂性组
  ├── 概率与不确定性组
  ├── 执行与迭代组
  └── 组织与成长组
  ↓
模型库 / 能力卡 / 检查清单
  ↓
最终报告
```

## 3. 核心原则

1. 一个能力只保留一个 canonical slot。
2. 只有输出契约不同，才保留独立 Agent。
3. 同族近义模型统一合并。
4. 路由只看任务，不看模型收藏。
5. 每个核心 Agent 必须有明确边界。

## 4. 保留的核心 Agent

| ID | 角色 | 用途 |
|---|---|---|
| kahneman | 决策与偏差 | 选择、风险、判断 |
| problem-reformulation | 问题重构 | 重新定义问题 |
| fivewhy | 根因诊断 | 连续追问根因 |
| first-principle | 第一性原理 | 从本质重建方案 |
| swot-tows | 战略分析 | 竞争、布局、规划 |
| systems-thinking | 系统思维 | 关联、反馈、涌现 |
| probabilistic | 概率思维 | 不确定性与期望值 |
| grow | 目标实现 | 目标到路径 |
| wbs | 执行拆解 | 任务分解 |
| kiss | 复盘简化 | 回顾、提炼、停改启 |
| manager-leap | 管理跃迁 | 组织与角色成长 |
| ai-board | 多角色决策 | 董事会式评审 |

## 5. 归并后的能力组

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

## 6. 入口规则

### 6.1 问题分类

- 决策类 → kahneman
- 诊断类 → fivewhy / problem-reformulation
- 创新类 → first-principle
- 战略类 → swot-tows
- 复杂系统类 → systems-thinking
- 不确定性类 → probabilistic
- 目标落地类 → grow + wbs
- 复盘类 → kiss
- 管理类 → manager-leap
- 重大决策 → ai-board + kahneman

### 6.2 模式选择

- 并行分析：多角度判断。
- 交叉辩论：重大决策。
- 链式分析：诊断和执行路径。

## 7. 输出规范

每次分析必须输出：

- 问题理解
- 值不值得用议会
- with / without 差异
- 专家观点
- 共识与分歧
- 综合结论
- 行动建议

约束：

- 每位专家不超过 3 条核心洞察。
- 不允许堆砌专家。
- 不允许无结论输出。
- 不允许不判断价值就直接开分析。

## 8. 迁移建议

1. 先修正命名错位。
2. 再把 V1 的 14 个核心专家作为第一批骨架。
3. 从 V2 里挑出真正独立的能力，补充到核心层。
4. 剩余长尾模型全部进入模型库。

## 9. 结论

这个系统的正确方向不是“更大”，而是“更清楚、更值、更能帮用户省事”。

入口要轻，路由要准，专家要少而强，长尾要沉到库里。
