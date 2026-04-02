---
description: 自动分类器 - 分析文档内容并判断 PARA 类别
---

# auto-classifier

自动分类器 - 分析文档内容并判断 PARA 类别

## 触发词

- "分类这个文档"
- "判断 PARA 类别"
- "自动归类"

## 功能

### classify

分析文档内容，判断应该属于哪个 PARA 类别

```yaml
输入:
  document_path: "文档路径"
  content: "文档内容（可选）"

输出:
  {
    "category": "projects|areas|resources|archives",
    "confidence": 0.85,
    "reason": "分类理由",
    "suggested_path": "建议的存放路径"
  }
```

## 分类规则

### Projects（项目）
- 有明确的完成目标
- 有时间限制或截止日期
- 包含"完成"、"发布"、"上线"等关键词
- 示例：产品发布计划、学习路线

### Areas（领域）
- 长期维护的责任
- 需要持续关注
- 包含"管理"、"维护"、"优化"等关键词
- 示例：健康管理、财务管理、职业发展

### Resources（资源）
- 参考资料和教程
- 未来可能用得上
- 包含"教程"、"文档"、"收藏"等关键词
- 示例：技术文档、文章收藏

### Archives（归档）
- 已完成的项目
- 不再活跃的内容
- 包含"已完成"、"历史"、"旧版"等关键词
- 示例：已结束的项目、旧版本文档

## MCP 工具

- `obsidian:read_note` - 读取笔记
- `memory:create_entities` - 创建知识图谱实体

## 使用示例

```
用户: "这篇文章应该放在哪里？"
Agent: [分析内容]
      这是一篇关于 Python 异步编程的教程，
      建议归类到 Resources/技术教程/Python/
      理由：参考资料类内容，无明确行动目标
```
