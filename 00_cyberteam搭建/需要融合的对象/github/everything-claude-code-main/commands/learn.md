# /learn - 提取可重用模式

分析当前会话并提取任何值得保存为技能的模式。

## 触发器

当您解决了一个重要的问题时，可以在会话期间的任何时刻运行“/learn”。

## 提取什么

寻找：

1. **错误解决模式**
   - 发生了什么错误？
   - 根本原因是什么？
   - 是什么解决了它？
   - 对于类似的错误，它可以重复使用吗？

2. **调试技巧**
   - 不明显的调试步骤
   - 有效的工具组合
   - 诊断模式

3. **解决方法**
   - 图书馆怪癖
   - API 限制
   - 特定于版本的修复

4. **特定于项目的模式**
   - 发现代码库约定
   - 做出的架构决策
   - 整合模式

## 输出格式

在 `~/.claude/skills/learned/[pattern-name].md` 创建技能文件：```markdown
# [Descriptive Pattern Name]

**Extracted:** [Date]
**Context:** [Brief description of when this applies]

## Problem
[What problem this solves - be specific]

## Solution
[The pattern/technique/workaround]

## Example
[Code example if applicable]

## When to Use
[Trigger conditions - what should activate this skill]
```## 流程

1. 检查会话中可提取的模式
2. 确定最有价值/可重用的见解
3. 起草技能档案
4. 保存前要求用户确认
5.保存到`~/.claude/skills/learned/`

## 注释

- 不要提取琐碎的修复（拼写错误、简单的语法错误）
- 不要提取一次性问题（特定 API 中断等）
- 关注可以在未来会议中节省时间的模式
- 集中技能 - 每项技能一个模式