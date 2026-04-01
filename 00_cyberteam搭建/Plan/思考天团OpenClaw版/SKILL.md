---
name: think-team-openclaw
description: 多思维模型协作入口，适配 OpenClaw 的问题路由、专家调度和结论整合。
---

# 思考天团 OpenClaw 版

## 定位

这是思考天团重组版给 OpenClaw 的适配入口。核心逻辑仍以 `../思考天团重组版/` 为准，这里只保留 OpenClaw 需要的技能包装。

## 读取顺序

1. 先读 `../思考天团重组版/SYSTEM_SPEC.md`。
2. 再读 `../思考天团重组版/SKILL.md`。
3. 再读 `../思考天团重组版/AGENT.md` 和 `../思考天团重组版/WORKFLOW.md`。
4. 路由映射以 `../思考天团重组版/MAPPING.md` 为准。
5. 专家与模型边界分别参考 `../思考天团重组版/agents/README.md` 和 `../思考天团重组版/models/README.md`。

## 工作原则

- 一个问题只保留一个主问题。
- 先选主专家，再补辅助专家。
- 默认只用 2-5 个核心专家。
- 通过并行、辩论或链式方式组织分析。
- 最终必须收敛到明确结论和行动建议。

## 路由规则

- 决策选择 → `kahneman`
- 原因诊断 → `fivewhy` + `problem-reformulation`
- 目标实现 → `grow` + `wbs`
- 战略规划 → `swot-tows`
- 创新突破 → `first-principle`
- 多角度分析 → `systems-thinking` + `ai-board`
- 复盘总结 → `kiss`
- 方法提炼 → `problem-reformulation` + `systems-thinking`
- 管理跃迁 → `manager-leap`
- 不确定性判断 → `probabilistic`

## 标准输出

- 问题理解
- 专家选择理由
- 专家观点摘要
- 共识与分歧
- 综合结论
- 行动建议

## 交付要求

- 每位专家最多保留 3 条核心洞察。
- 长尾模型只做补强，不抢主流程。
- 不允许只有分析，没有判断。
- 不允许把所有模型都拉出来。
