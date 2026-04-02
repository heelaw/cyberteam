# 上下文预算优化器

分析您的 Claude Code 设置的上下文窗口消耗并生成可操作的建议以减少令牌开销。

＃＃ 用法```
/context-budget [--verbose]
```- 默认：带有热门推荐的摘要
- `--verbose`：每个组件的完整细分

$参数

## 做什么

使用以下输入运行 **context-budget** 技能 (`skills/context-budget/SKILL.md`)：

1. 如果“$ARGUMENTS”中存在“--verbose”标志，则传递“--verbose”标志
2. 假设上下文窗口为 200K（Claude Sonnet 默认值），除非用户另有指定
3. 遵循技能的四个阶段：清点 → 分类 → 检测问题 → 报告
4. 向用户输出格式化的Context Budget Report

该技能处理所有扫描逻辑、令牌估计、问题检测和报告格式。