# 模型库

模型库不是废案收容所，而是思维能力的底座。这里放的是长尾模型、偏差标签、检查清单和提示片段。

## 设计原则

- 长尾模型服务于核心专家，不抢主流程。
- 同类模型尽量合并为一个 bucket。
- 路由时优先看任务，不先看模型收藏。
- 模型库负责补强、校验和提醒，不负责单独主导结论。

## 子目录

- 主入口：`decision`、`structure`、`psychology`、`uncertainty`、`execution`、`org-growth`、`strategy`。
- 支持桶：`bias`、`heuristics`。
- `decision` - 决策取舍、止损、继续与否、价值判断。
- `bias` - 认知偏差与判断失真。
- `heuristics` - 启发式、简化规则、快速筛选。
- `strategy` - 战略、竞争、商业布局。
- `psychology` - 动机、情绪、行为偏差。
- `structure` - 结构化表达、框架转换、论证组织。
- `uncertainty` - 概率、不确定性、证据更新。
- `execution` - 目标拆解、行动推进、迭代节奏。
- `org-growth` - 组织、管理、增长与演化。

## 使用方式

- 需要提醒偏差时，先查 `bias`。
- 需要压缩和简化时，先查 `heuristics`。
- 需要竞争判断时，先查 `strategy`。
- 需要解释人和行为时，先查 `psychology`。
- 需要把表达变清楚时，先查 `structure`。
- 需要估计风险和信念更新时，先查 `uncertainty`。
- 需要把目标变成行动时，先查 `execution`。
- 需要处理管理与组织升级时，先查 `org-growth`。

## 补缺原则

这次从 100 个模型提示词里补进来的高频模型，优先落在 7 个主入口里；`bias`、`heuristics` 作为支持桶补位。不是每个模型都要单独保留，但只要它能稳定帮助判断、拆解、止损或执行，就值得入库。

模型解释是否值得保留，统一按 `references/model-evaluation-rubric.md` 里的标准判断：能不能改变判断、能不能拆解问题、能不能指出边界、能不能推动下一步。

完整的主归属总表见 `references/model-coverage-map.md`。

优先级最高的判断入口是：

- 该不该做、要不要停、值不值得继续 → `decision`
- 框架不清、表达散乱、需要换角度 → `structure`
- 人为什么这么想、这么做、这么偏 → `psychology`
- 结果不确定、要算概率、要预演失败 → `uncertainty`
- 怎么做得更省力、更稳、更快 → `execution`
- 系统怎么保持活力、怎么长期演化 → `org-growth`
- 竞争、布局、护城河、窗口期 → `strategy`
