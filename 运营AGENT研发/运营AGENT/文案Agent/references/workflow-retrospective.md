# 文案Agent 全流程复盘与总接手文档

## 这份文档的用途

这是一份给新窗口直接接手的总说明。它回答四件事：

1. 这个包是什么。
2. 现在做到哪里了。
3. 还缺什么。
4. 下一位接手者先看什么、先做什么、先验证什么。

它不是背景介绍，也不是工作日志。它是后续批量化扩散的操作底稿。

## 包的边界

- 当前工作区是 `/Users/cyberwiz/Documents/01_Project/运营AGENT研发/运营AGENT/文案Agent`。
- 这个包已经是可上岗的数字员工包，不再用旧的培训语境组织表达。
- 所有对外可读内容都要围绕岗位、SOP、判断、边界、QA 展开。
- 根层只保留路由、门禁、复盘和最小导航，不塞长文。

## 目录路径图

| 位置 | 作用 | 说明 |
|---|---|---|
| [`SKILL.md`](/Users/cyberwiz/Documents/01_Project/运营AGENT研发/运营AGENT/文案Agent/SKILL.md) | 根调度入口 | 只负责岗位定义、调度原则、路由表和交接说明 |
| [`SOUL.md`](/Users/cyberwiz/Documents/01_Project/运营AGENT研发/运营AGENT/文案Agent/SOUL.md) | 岗位人格和边界 | 说明如何判断、何时回退、什么不能做 |
| [`references/route-map.md`](/Users/cyberwiz/Documents/01_Project/运营AGENT研发/运营AGENT/文案Agent/references/route-map.md) | 流程主路由 | 定义从需求到交付的主链路 |
| [`references/platform-presets.md`](/Users/cyberwiz/Documents/01_Project/运营AGENT研发/运营AGENT/文案Agent/references/platform-presets.md) | 平台预设 | 把短/中/长触点映射到具体平台 |
| [`references/method-matrix.md`](/Users/cyberwiz/Documents/01_Project/运营AGENT研发/运营AGENT/文案Agent/references/method-matrix.md) | 不变量矩阵 | 只保留跨 Skill 的统一判断 |
| [`references/assessment.md`](/Users/cyberwiz/Documents/01_Project/运营AGENT研发/运营AGENT/文案Agent/references/assessment.md) | 根层验收 | 定义包级别的 pass / fail 门禁 |
| [`references/workflow-retrospective.md`](/Users/cyberwiz/Documents/01_Project/运营AGENT研发/运营AGENT/文案Agent/references/workflow-retrospective.md) | 总接手文档 | 当前进度、质量要求、QA、扩散模板 |
| [`skills/*/SKILL.md`](/Users/cyberwiz/Documents/01_Project/运营AGENT研发/运营AGENT/文案Agent/skills) | 最小 SOP 单元 | 每个文件只做一个可执行单元 |
| [`skills/*/references/reference.md`](/Users/cyberwiz/Documents/01_Project/运营AGENT研发/运营AGENT/文案Agent/skills) | 该单元的详细 SOP | 讲清楚看什么、怎么采、怎么判、什么是好、什么不能做 |
| [`skills/*/assessments/assessment.md`](/Users/cyberwiz/Documents/01_Project/运营AGENT研发/运营AGENT/文案Agent/skills) | 该单元考核 | 明确 pass / fail 条件和测试样例 |
| [`skills/*/scripts/run.py`](/Users/cyberwiz/Documents/01_Project/运营AGENT研发/运营AGENT/文案Agent/skills) | 该单元入口 | 统一包装器，输出结构化诊断 |
| [`scripts/copywriting_skill_runner.py`](/Users/cyberwiz/Documents/01_Project/运营AGENT研发/运营AGENT/文案Agent/scripts/copywriting_skill_runner.py) | 共享诊断逻辑 | 统一处理输入、校验、红线和下一步 |
| [`scripts/validate_agent_package.py`](/Users/cyberwiz/Documents/01_Project/运营AGENT研发/运营AGENT/文案Agent/scripts/validate_agent_package.py) | 包级校验 | 检查禁词、链接、噪音文件和技能目录完整性 |

## 当前进度

### 已完成

- 根层 `SKILL.md` 已切到调度型数字员工定位。
- `SOUL.md` 已写清岗位边界、工作姿态、兜底规则。
- `references/route-map.md` 已建立主链路和回退规则。
- `references/platform-presets.md` 已把短 / 中 / 长映射到平台。
- `references/method-matrix.md` 已写出跨 Skill 不变量。
- `references/assessment.md` 已定义根层门禁。
- `skills/*/SKILL.md` 已拆成 9 个最小单元。
- `skills/*/references/reference.md` 已初步落地细分 SOP。
- `skills/*/assessments/assessment.md` 已初步落地验收门禁。
- `skills/*/scripts/run.py` 已全部落地统一入口。
- `scripts/copywriting_skill_runner.py` 已能输出结构化诊断。
- `scripts/validate_agent_package.py` 已能做包级检查。

### 仍需补强

- `research-sellpoint-forward` 还可以继续加厚证据采样和边界示例。
- `research-sellpoint-backward` 还可以继续加厚反推链路的断点判断。
- 未来扩散到其他章节时，需要统一模板，不允许每章重新发明格式。
- 后续新增 Skill 时，必须先回到这份总接手文档，再进入具体章节。

### 当前规模

- Skill 总数：9 个。
- 根层参考文件：5 个。
- 根层脚本：2 个。
- 统一 Skill 入口脚本：9 个。
- 当前最需要继续加厚的内容：正向卖点、反向卖点、后续章节复制模板。

## 新窗口接手顺序

新对话只要按这个顺序看，就能恢复上下文：

1. [`SKILL.md`](/Users/cyberwiz/Documents/01_Project/运营AGENT研发/运营AGENT/文案Agent/SKILL.md)
2. [`SOUL.md`](/Users/cyberwiz/Documents/01_Project/运营AGENT研发/运营AGENT/文案Agent/SOUL.md)
3. [`references/route-map.md`](/Users/cyberwiz/Documents/01_Project/运营AGENT研发/运营AGENT/文案Agent/references/route-map.md)
4. [`references/platform-presets.md`](/Users/cyberwiz/Documents/01_Project/运营AGENT研发/运营AGENT/文案Agent/references/platform-presets.md)
5. [`references/method-matrix.md`](/Users/cyberwiz/Documents/01_Project/运营AGENT研发/运营AGENT/文案Agent/references/method-matrix.md)
6. [`references/assessment.md`](/Users/cyberwiz/Documents/01_Project/运营AGENT研发/运营AGENT/文案Agent/references/assessment.md)
7. [`references/workflow-retrospective.md`](/Users/cyberwiz/Documents/01_Project/运营AGENT研发/运营AGENT/文案Agent/references/workflow-retrospective.md)
8. 具体要改的 `skills/<skill>/SKILL.md`
9. 对应的 `skills/<skill>/references/reference.md`
10. 对应的 `skills/<skill>/assessments/assessment.md`
11. 对应的 `skills/<skill>/scripts/run.py`

## 输出文件规范

- 所有 Skill 必须保留三件套：`SKILL.md`、`references/reference.md`、`assessments/assessment.md`。
- 所有 Skill 必须补齐 `scripts/run.py`。
- 根层文件只写导航和门禁，不写章节内细节。
- 细节全部下沉到对应 Skill，不许堆在根层。
- 新增文件优先放在对应 Skill 目录下，不要散落到总目录。

## Input / Output 规范

### Input 在哪里

- 用户原话、行为、搜索、反馈、对话、对比、数据，都属于输入证据。
- 输入证据可以来自聊天记录、访谈、埋点、工单、竞品、内容表现、转化表现。
- 输入不足时，先补证据，不许直接写终稿。

### Output 在哪里

- 需求判断输出：`detect-need-type`
- 用户分层输出：`segment-users`
- 卖点输出：`research-sellpoint-forward` 或 `research-sellpoint-backward`
- 场景输出：`judge-scenario`
- 结构输出：`select-structure`
- 初稿输出：`draft-copy`
- 改写输出：`edit-copy`
- 终检输出：`self-check-copy`
- 包级输出：`references/workflow-retrospective.md` 和 `scripts/validate_agent_package.py`

## 质量要求

### 1. 输出必须是可执行判断，不是摘要

- 要写“怎么做”，不是只写“是什么”。
- 要写“为什么这么判”，不是只给标签。
- 要写“下一步回到哪一步”，不是一句“继续优化”。

### 2. 每个环节必须有 QA

- 必须能通过 pass / fail 判定。
- 必须能指出缺口。
- 必须能处理反例和边界。

### 3. 必须遵循渐进式披露

- 根层只保留总规则。
- 具体方法放到 `references/reference.md`。
- 把完整案例、失败案例、红线、边界放到各自 Skill 的 reference 和 assessment 里。

### 4. 必须能让新人照着做

- 新人拿到文件后，应能知道先看什么。
- 新人应能知道缺什么要补什么。
- 新人应能知道什么情况下绝对不能硬做。

## QA 总表

| 环节 | QA 重点 | 通过标准 |
|---|---|---|
| 需求识别 | 证据够不够、冲突处理对不对 | 能判断明确 / 模糊 / 潜在，并写出缺口 |
| 用户分层 | 决策链清不清、主次清不清 | 能明确主写对象、辅助对象和不该写的人群 |
| 卖点提炼 | 证据足不足、方向全不全 | 能找到主卖点并保留证据缺口 |
| 场景判断 | 平台和时长是否匹配 | 能输出平台预设、触点和 CTA 强度 |
| 结构选择 | 用户状态和结构是否匹配 | 能给主结构和备用结构，并说明排除理由 |
| 初稿 | 主张、理由、证据、动作是否闭环 | 能写出第一版可读内容 |
| 删改 | 是否改事实、改卖点、改主线 | 只改表达，不改事实 |
| 自检 | 七问是否全部通过 | 7/7 才能通过 |
| 包级校验 | 禁词、链接、噪音、入口是否完整 | 能通过 `validate_agent_package.py` |

## 具体操作方法

### 资料研读

先做目录级扫描，再做逐章摘录。摘录时按这五列记：来源、知识点、SOP、案例、红线。

### 拆分方法

先问四个问题：输入是什么、输出是什么、判断点是什么、能不能独立交付。只要混了两个以上目标，就继续拆。

### 编写方法

每个 Skill 先写“适用场景”，再写“执行步骤”，再写“交付骨架”，再写“绝对不能”，最后补“案例”和“QA 门禁”。

### 复核方法

用“新人测试”验证：新人能不能做、会不会回退、知不知道好坏、知不知道什么不能做。

## 这次暴露的问题

### 问题 1：结构还不够厚

原因：只把主线写出来了，边界、反例、失败路径还不够密。

修正：每个判断点都补“看什么、怎么采、怎么判、怎么错、怎么回退”。

### 问题 2：脚本层曾经是空壳

原因：有入口意识，但没把入口写成可运行包装器。

修正：每个 Skill 都要有 `scripts/run.py`，输出结构化诊断。

### 问题 3：包级结构容易散

原因：文件多，但入口和索引不够清晰。

修正：根层只留总图，细节全部下沉到 Skill 目录。

### 问题 4：扩散时容易不齐

原因：每一章都从头想，导致粒度不一致。

修正：后续必须统一模板，复制后再补章节差异。

## 后续扩散模板

每个新章节先补齐这 8 项：

1. 最小单元是什么。
2. 输入是什么。
3. 输出是什么。
4. 判断阈值是什么。
5. 红线是什么。
6. 失败案例是什么。
7. QA 怎么做。
8. 失败后回到哪里。

## goal-driven-main 伪代码

```text
goal = "把文案Agent扩散成可直接上岗的数字员工包，并确保每个Skill都足够厚、可执行、可QA"
criteria = [
  "根层无禁词，无散乱入口",
  "每个Skill都有SKILL.md、reference.md、assessment.md、run.py",
  "每个Skill都能输出明确判断、缺口、回退和下一步",
  "自检通过率为7/7，包级校验通过",
  "新窗口只读总接手文档就能恢复上下文"
]

while not all(criteria):
    read latest skill docs
    identify thinnest node
    thicken SOP, cases, red lines, and QA
    add or repair run.py
    update retrospective memory
    re-run package validation

if all(criteria):
    stop and publish the handoff state
```

## 本轮经验教训

- 结构只写主线会显得薄，必须补齐看什么、怎么采、怎么判、怎么错、怎么回退。
- 每个 Skill 至少要同时具备：判定标准、反例、边界、输出骨架、QA、回退路径。
- 文档越厚，不是越啰嗦，而是越能让新人直接执行、让旧窗口无缝接手。
- 以后扩散新章节时，先复制这套密度，再做章节差异，不要重新发明格式。
- 新窗口接手最关键的不是“看过很多”，而是“能直接开始改，且知道先改哪里”。

## 本轮已加厚的节点

- `judge-scenario`
- `select-structure`
- `draft-copy`
- `edit-copy`
- `self-check-copy`

## 当前建议

- 继续优先加厚最薄的 Skill，不要平均铺开。
- 先把 `run.py` 补齐，再做二轮内容加厚。
- 每完成一轮，就把经验回写到这份总接手文档。
- 后续新章节必须先读这份文档，再开始改文件。

## 新窗口开工清单

新对话如果要无损接手，按这个顺序读完就够：

1. [`SKILL.md`](/Users/cyberwiz/Documents/01_Project/运营AGENT研发/运营AGENT/文案Agent/SKILL.md)
2. [`SOUL.md`](/Users/cyberwiz/Documents/01_Project/运营AGENT研发/运营AGENT/文案Agent/SOUL.md)
3. [`references/route-map.md`](/Users/cyberwiz/Documents/01_Project/运营AGENT研发/运营AGENT/文案Agent/references/route-map.md)
4. [`references/platform-presets.md`](/Users/cyberwiz/Documents/01_Project/运营AGENT研发/运营AGENT/文案Agent/references/platform-presets.md)
5. [`references/method-matrix.md`](/Users/cyberwiz/Documents/01_Project/运营AGENT研发/运营AGENT/文案Agent/references/method-matrix.md)
6. [`references/assessment.md`](/Users/cyberwiz/Documents/01_Project/运营AGENT研发/运营AGENT/文案Agent/references/assessment.md)
7. [`references/workflow-retrospective.md`](/Users/cyberwiz/Documents/01_Project/运营AGENT研发/运营AGENT/文案Agent/references/workflow-retrospective.md)
8. 目标 Skill 的 `SKILL.md`
9. 目标 Skill 的 `references/reference.md`
10. 目标 Skill 的 `assessments/assessment.md`
11. 目标 Skill 的 `scripts/run.py`

## 现在该怎么看质量

把每个 Skill 当成一个新人岗前 SOP 来看，检查四件事：

1. 能不能独立启动，不依赖上下文猜题。
2. 能不能做出判断，不只是复述知识。
3. 能不能说清楚什么是好、什么是坏、什么绝对不能做。
4. 能不能在失败时知道回到哪里补证据。

## 这次工作真正修正了什么

- 以前的问题不是“有没有知识”，而是“知识有没有变成可执行判断”。
- 以前的问题不是“有没有 Skill”，而是“Skill 有没有厚到新人能照着做”。
- 以前的问题不是“有没有流程”，而是“流程有没有带 QA、回退和边界”。
- 以前的问题不是“有没有输出”，而是“输出能不能直接喂给下一跳”。

## 后续扩散规则

- 每新增一个章节，先把它拆成最小单元，再写三件套。
- 每个最小单元都必须有输入、判断、输出、边界、失败案例、QA。
- 如果一个文件里同时出现多个目标，就继续拆，不要硬合并。
- 如果一个 Skill 的 reference 还不能让新人做事，就继续补例子和反例，直到能做。

## 批量化作业顺序

1. 找最薄的单元。
2. 补 SOP。
3. 补案例。
4. 补反例。
5. 补红线。
6. 补 QA。
7. 补回退路径。
8. 跑校验脚本。
9. 记录到复盘文档。

## 质量底线

- 不是“写得像”，而是“能干活”。
- 不是“看着完整”，而是“遇到分叉时知道怎么判”。
- 不是“有例子”，而是“例子能覆盖边界和失败”。
- 不是“能过一遍”，而是“新窗口也能接着干”。
