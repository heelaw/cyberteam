# 技能创建命令

分析git历史生成Claude代码技巧：$ARGUMENTS

## 你的任务

1. **分析提交** - 从历史记录中识别模式
2. **提取模式** - 常见实践和约定
3. **生成SKILL.md** - 结构化技能文档
4. **创造本能** - 用于持续学习-v2

## 分析过程

### 第 1 步：收集提交数据```bash
# Recent commits
git log --oneline -100

# Commits by file type
git log --name-only --pretty=format: | sort | uniq -c | sort -rn

# Most changed files
git log --pretty=format: --name-only | sort | uniq -c | sort -rn | head -20
```### 第 2 步：识别模式

**提交消息模式**：
- 常见前缀（壮举、修复、重构）
- 命名约定
- 共同作者模式

**代码模式**：
- 文件结构约定
- 进口组织
- 错误处理方法

**审查模式**：
- 常见的评论反馈
- 重复修复类型
- 质量门

### 步骤3：生成SKILL.md```markdown
# [Skill Name]

## Overview
[What this skill teaches]

## Patterns

### Pattern 1: [Name]
- When to use
- Implementation
- Example

### Pattern 2: [Name]
- When to use
- Implementation
- Example

## Best Practices

1. [Practice 1]
2. [Practice 2]
3. [Practice 3]

## Common Mistakes

1. [Mistake 1] - How to avoid
2. [Mistake 2] - How to avoid

## Examples

### Good Example
```[语言]
// 代码示例```

### Anti-pattern
```[语言]
// 不该做什么```
```### 步骤 4：产生本能

对于持续学习 v2：```json
{
  "instincts": [
    {
      "trigger": "[situation]",
      "action": "[response]",
      "confidence": 0.8,
      "source": "git-history-analysis"
    }
  ]
}
```## 输出

创建：
- `skills/[name]/SKILL.md` - 技能文档
- `skills/[name]/instincts.json` - 本能集合

---

**提示**：运行“/skill-create --instincts”也可以生成持续学习的本能。