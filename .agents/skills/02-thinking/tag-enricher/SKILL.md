---
description: 标签补充器 - 基于内容推荐标签并更新 frontmatter
---

# tag-enricher

标签补充器 - 基于内容推荐标签并更新 frontmatter

## 触发词

- "添加标签"
- "推荐标签"
- "补充元数据"

## 功能

### enrich_tags

分析文档内容，推荐合适的标签

```yaml
输入:
  document_path: "文档路径"

输出:
  {
    "tags": ["标签1", "标签2", "标签3"],
    "categories": ["主分类", "子分类"],
    "keywords": ["关键词1", "关键词2"]
  }
```

### update_frontmatter

更新文档的 YAML frontmatter

```yaml
输入:
  document_path: "文档路径"
  frontmatter: {
    "tags": [...],
    "category": "...",
    ...
  }

输出:
  - 更新后的文档
  - 变更摘要
```

## 标签体系

### 技术类
- AI/LLM: `AI`, `LLM`, `Codex`, `GPT`, `提示工程`
- 编程: `Python`, `JavaScript`, `Rust`, `Go`
- 框架: `React`, `Vue`, `Django`, `FastAPI`

### 方法类
- PARA: `PARA`, `项目管理`, `知识管理`
- CODE: `CODE`, `知识体系`, `第二大脑`
- 产品: `产品思维`, `用户研究`, `数据分析`

### 资源类
- 类型: `教程`, `文档`, `文章`, `视频`
- 来源: `GitHub`, `博客`, `公众号`, `书籍`

## MCP 工具

- `obsidian:read_note` - 读取笔记
- `obsidian:update_frontmatter` - 更新 frontmatter
- `memory:create_entities` - 创建知识图谱实体

## 输出示例

```yaml
---
title: "Codex 使用指南"
tags: [Codex, AI, 教程, 开发工具]
category: 技术教程
keywords: [Codex, AI 编程, 代码助手]
difficulty: 初级
estimated_time: "30 分钟"
---
```
