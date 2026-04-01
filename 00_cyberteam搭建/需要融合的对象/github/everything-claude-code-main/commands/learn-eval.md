# /learn-eval - 提取、评估，然后保存

在编写任何技能文件之前，通过质量门、保存位置决策和知识放置意识来扩展“/learn”。

## 提取什么

寻找：

1. **错误解决模式** — 根本原因+修复+可重用性
2. **调试技术**——非显而易见的步骤、工具组合
3. **解决方法** — 库怪癖、API 限制、特定于版本的修复
4. **项目特定模式** — 约定、架构决策、集成模式

## 流程

1. 检查会话中可提取的模式
2. 确定最有价值/可重用的见解

3. **确定保存位置：**
   - 问：“这个模式在不同的项目中有用吗？”
   - **全局**（`~/.claude/skills/learned/`）：可跨 2 个以上项目使用的通用模式（bash 兼容性、LLM API 行为、调试技术等）
   - **项目**（当前项目中的`.claude/skills/learned/`）：特定于项目的知识（特定配置文件的怪癖、特定于项目的架构决策等）
   - 如有疑问，请选择“全球”（移动“全球”→“项目”比相反更容易）

4. 使用以下格式起草技能文件：```markdown
---
name: pattern-name
description: "Under 130 characters"
user-invocable: false
origin: auto-extracted
---

# [Descriptive Pattern Name]

**Extracted:** [Date]
**Context:** [Brief description of when this applies]

## Problem
[What problem this solves - be specific]

## Solution
[The pattern/technique/workaround - with code examples]

## When to Use
[Trigger conditions]
```5. **质量门 - 检查表 + 整体结论**

   ### 5a。所需清单（通过实际读取文件进行验证）

   在评估草稿之前执行以下**所有**操作：

   - [ ] 按关键字 Grep `~/.claude/skills/` 和相关项目 `.claude/skills/` 文件以检查内容重叠
   - [ ] 检查 MEMORY.md（项目和全局）是否重叠
   - [ ] 考虑附加到现有技能是否足够
   - [ ] 确认这是一个可重复使用的模式，而不是一次性修复

   ### 5b。整体判断

   综合清单结果和草稿质量，然后选择以下**之一**：

   |判决 |意义|下一步行动|
   |---------|---------|-------------|
   | **保存** |独特、具体、范围广泛 |继续执行步骤 6 |
   | **改进然后保存** |有价值但需要完善|列出改进→修改→重新评估（一次）|
   | **吸收到[X]** |应附加到现有技能 |显示目标技能和附加内容 → 步骤 6 |
   | **掉落** |琐碎、多余或过于抽象 |解释推理并停止 |

   **指导维度**（告知判决，不计分）：

   - **特异性和可操作性**：包含可立即使用的代码示例或命令
   - **范围适合**：名称、触发条件和内容对齐并集中于单一模式
   - **独特性**：提供现有技能未涵盖的价值（由清单结果告知）
   - **可重用性**：未来会话中存在真实的触发场景

6. **特定判决确认流程**

   - **改进然后保存**：在一次重新评估后提出所需的改进+修订草案+更新的清单/结论；如果修改后的判决是**保存**，则用户确认后保存，否则按照新判决
   - **保存**：当前保存路径+清单结果+1行判决理由+完整草稿→用户确认后保存
   - **吸收到[X]**：当前目标路径+添加（差异格式）+清单结果+判决理由→用户确认后追加
   - **删除**：仅显示清单结果+推理（无需确认）

7.保存/吸收到指定位置

## 步骤 5 的输出格式```
### Checklist
- [x] skills/ grep: no overlap (or: overlap found → details)
- [x] MEMORY.md: no overlap (or: overlap found → details)
- [x] Existing skill append: new file appropriate (or: should append to [X])
- [x] Reusability: confirmed (or: one-off → Drop)

### Verdict: Save / Improve then Save / Absorb into [X] / Drop

**Rationale:** (1-2 sentences explaining the verdict)
```## 设计原理

该版本用基于清单的整体判定系统取代了之前的 5 维数字评分标准（特异性、可操作性、范围适合性、非冗余性、覆盖率 1-5）。现代前沿模型（Opus 4.6+）具有很强的上下文判断能力——将丰富的定性信号强行转化为数字分数会失去细微差别，并可能产生误导性的总数。整体方法让模型自然权衡所有因素，产生更准确的保存/删除决策，同时明确的检查表确保不会跳过任何关键检查。

## 注释

- 不要提取琐碎的修复（拼写错误、简单的语法错误）
- 不要提取一次性问题（特定 API 中断等）
- 关注可以在未来会议中节省时间的模式
- 保持技能集中——每项技能一个模式
- 当判决为“吸收”时，追加到现有技能而不是创建新文件