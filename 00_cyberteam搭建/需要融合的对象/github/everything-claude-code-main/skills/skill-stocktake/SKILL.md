# 技能盘点

Slash 命令（`/skill-stocktake`）使用质量检查表 + AI 整体判断来审核所有 Claude 技能和命令。支持两种模式：快速扫描最近更改的技能，以及全面盘点以进行完整审查。

## 范围

该命令针对以下路径**相对于调用它的目录**：

|路径|描述 |
|------|-------------|
| `~/.claude/skills/` |全球技能（所有项目）|
| `{cwd}/.claude/skills/` |项目级技能（如果目录存在）|

**在第 1 阶段开始时，该命令明确列出已找到并扫描的路径。**

### 针对特定项目

要包含项目级技能，请从该项目的根目录运行：```bash
cd ~/path/to/my-project
/skill-stocktake
```如果项目没有“.claude/skills/”目录，则仅评估全局技能和命令。

## 模式

|模式|触发|持续时间 |
|------|---------|---------|
|快速扫描 | `results.json` 存在（默认）| 5–10 分钟 |
|全面盘点| `results.json` 缺失，或 `/skill-stocktake full` | 20–30 分钟 |

**结果缓存：** `~/.claude/skills/skill-stocktake/results.json`

## 快速扫描流程

仅重新评估自上次运行（5-10 分钟）以来发生变化的技能。

1. 阅读 `~/.claude/skills/skill-stocktake/results.json`
2. 运行：`bash ~/.claude/skills/skill-stocktake/scripts/quick-diff.sh \
         〜/.claude/skills/skill-stocktake/results.json`
   （项目目录是从 `$PWD/.claude/skills` 自动检测到的；仅在需要时才显式传递它）
3. 如果输出为“[]”：报告“自上次运行以来没有更改”。并停止
4. 使用相同的第 2 阶段标准仅重新评估那些已更改的文件
5. 继承先前结果不变的技能
6. 只输出差异
7. 运行：`bash ~/.claude/skills/skill-stocktake/scripts/save-results.sh \
         ~/.claude/skills/skill-stocktake/results.json <<< "$EVAL_RESULTS"`

## 完整盘点流程

### 第 1 阶段 — 库存

运行：`bash ~/.claude/skills/skill-stocktake/scripts/scan.sh`

该脚本枚举技能文件、提取 frontmatter 并收集 UTC mtime。
项目目录是从 `$PWD/.claude/skills` 自动检测到的；仅在需要时才显式传递它。
显示脚本输出中的扫描摘要和清单表：```
Scanning:
  ✓ ~/.claude/skills/         (17 files)
  ✗ {cwd}/.claude/skills/    (not found — global skills only)
```|技能| 7d 使用 | 30 天使用 |描述 |
|--------|--------|---------|-------------|

### 第 2 阶段 — 质量评估

启动具有完整清单和清单的代理工具子代理（**通用代理**）：```text
Agent(
  subagent_type="general-purpose",
  prompt="
Evaluate the following skill inventory against the checklist.

[INVENTORY]

[CHECKLIST]

Return JSON for each skill:
{ \"verdict\": \"Keep\"|\"Improve\"|\"Update\"|\"Retire\"|\"Merge into [X]\", \"reason\": \"...\" }
"
)
```子代理读取每个技能、应用检查表并返回每个技能的 JSON：

`{ "verdict": "保留"|"改进"|"更新"|"退休"|"合并到 [X]", "reason": "..." }`

**块指导：** 每次子代理调用处理约 20 个技能，以保持上下文可管理。在每个块之后将中间结果保存到 `results.json` (`status: "in_progress"`)。

评估所有技能后：设置“状态：“已完成””，进入第 3 阶段。

**恢复检测：** 如果启动时发现 `status: "in_progress"`，则从第一个未评估的技能开始恢复。

每项技能都会根据此清单进行评估：```
- [ ] Content overlap with other skills checked
- [ ] Overlap with MEMORY.md / CLAUDE.md checked
- [ ] Freshness of technical references verified (use WebSearch if tool names / CLI flags / APIs are present)
- [ ] Usage frequency considered
```判定标准：

|判决 |意义|
|---------|---------|
|保留|有用且最新的 |
|改进|值得保留，但需要具体改进|
|更新 |引用的技术已过时（通过 WebSearch 验证）|
|退休 |低质量、陈旧或成本不对称 |
|合并到[X] |与另一项技能大量重叠；命名合并目标 |

评估是**全面的人工智能判断**——而不是数字标准。指导尺寸：
- **可操作性**：让您立即采取行动的代码示例、命令或步骤
- **范围适合**：名称、触发器和内容对齐；不太宽或太窄
- **唯一性**：无法被MEMORY.md / CLAUDE.md /其他技能替代的价值
- **货币**：技术参考在当前环境下有效

**原因质量要求** - “原因”字段必须是独立的且能够做出决策：
- 不要单独写“不变”——始终重申核心证据
- 对于**退休**：说明 (1) 发现了哪些具体缺陷，(2) 哪些内容涵盖了相同的需求
  - 坏：“被取代”
  - 好：“禁用模型调用：已经设置为 true；被持续学习 v2 取代，它涵盖了所有相同的模式以及置信度评分。没有保留任何独特的内容。”
- 对于**合并**：命名目标并描述要集成的内容
  - 不好：“与 X 重叠”
  - 好：“42 行薄内容；聊天日志到文章的第 4 步已经涵盖了相同的工作流程。将“文章角度”提示集成为该技能中的注释。”`
- 对于 **改进**：描述所需的具体更改（哪些部分、哪些操作、目标大小（如果相关））
  - 不好：“太长”
  - 好：“276 行；‘框架比较’部分（L80–140）重复 ai-era-architecture-principles；删除它以达到约 150 行。”`
- 对于**保留**（快速扫描中仅更改时间）：重述原始判决理由，不要写“未更改”
  - 不好：`“不变”`
  - 好：“mtime 已更新，但内容未更改。由规则/python/ 显式导入的独特 Python 参考；未发现重叠。”`

### 第 3 阶段 — 汇总表

|技能| 7d 使用 |判决 |原因 |
|--------|--------|---------|--------|

### 第 4 阶段 — 整合

1. **退役/合并**：在与用户确认之前提供每个文件的详细理由：
   - 发现了什么具体问题（重叠、过时、引用损坏等）
   - 什么替代方案涵盖相同的功能（对于退休：现有的技能/规则；对于合并：目标文件以及要集成的内容）
   - 删除的影响（任何相关技能、MEMORY.md 参考或受影响的工作流程）
2. **改进**：提出具体的改进建议并说明理由：
   - 改变什么以及为什么（例如，“修剪 430→200 行，因为 X/Y 部分重复 python 模式”）
   - 用户决定是否采取行动
3. **更新**：呈现已检查来源的更新内容
4.检查MEMORY.md行数；如果 >100 行，建议压缩

## 结果文件架构

`~/.claude/skills/skill-stocktake/results.json`:

**`evaluated_at`**：必须设置为评估完成的实际 UTC 时间。
通过 Bash 获取：`date -u +%Y-%m-%dT%H:%M:%SZ`。切勿使用仅日期近似值，例如“T00:00:00Z”。```json
{
  "evaluated_at": "2026-02-21T10:00:00Z",
  "mode": "full",
  "batch_progress": {
    "total": 80,
    "evaluated": 80,
    "status": "completed"
  },
  "skills": {
    "skill-name": {
      "path": "~/.claude/skills/skill-name/SKILL.md",
      "verdict": "Keep",
      "reason": "Concrete, actionable, unique value for X workflow",
      "mtime": "2026-01-15T08:30:00Z"
    }
  }
}
```## 注释

- 评估是盲目的：相同的清单适用于所有技能，无论其来源如何（ECC、自行创作、自动提取）
- 存档/删除操作始终需要明确的用户确认
- 没有按技能来源划分的判决