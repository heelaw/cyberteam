# 思考天团 Agent 目录蓝图

## 总体结构

```text
思考天团/
├── SKILL.md
├── AGENT.md
├── workflow/
├── core/
├── agents/
├── models/
└── references/
```

## 分层说明

### 1. SKILL 层

职责：触发、识别意图、选择分析模式、调用主持人。

### 2. 主持人 Agent 层

职责：标准化输入、选择专家、控制并行/辩论/链式流程、整合输出。

### 3. 核心 Agent 层

建议保留的目录：

```text
agents/
├── kahneman/
├── problem-reformulation/
├── fivewhy/
├── first-principle/
├── swot-tows/
├── systems-thinking/
├── probabilistic/
├── grow/
├── wbs/
├── kiss/
├── manager-leap/
└── ai-board/
```

### 4. 模型库层

```text
models/
├── bias/
├── heuristics/
├── strategy/
├── psychology/
├── structure/
├── uncertainty/
├── execution/
└── org-growth/
```

## 路由建议

- 决策类 → `kahneman`
- 诊断类 → `fivewhy` / `problem-reformulation`
- 创新类 → `first-principle`
- 战略类 → `swot-tows`
- 复杂系统类 → `systems-thinking`
- 不确定性类 → `probabilistic`
- 目标落地类 → `grow` + `wbs`
- 复盘类 → `kiss`
- 管理类 → `manager-leap`
- 重大决策 → `ai-board` + `kahneman`

## 最终原则

- 能独立输出的，才保留为 Agent。
- 只有同类能力的，不要重复造 Agent。
- 其余全部沉到模型库，供主持人按需调用。
