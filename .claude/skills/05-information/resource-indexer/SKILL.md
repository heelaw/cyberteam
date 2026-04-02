---
description: 为 03_Resource/ 中的文档创建索引和元数据
---

# resource-indexer

资源索引器 - 为 03_Resource/ 中的文档创建索引和元数据

## 触发词

- "索引资源"
- "更新索引"
- "扫描资源"
- "资源统计"

## 功能

### build_index

扫描指定目录，为每个文档添加 YAML frontmatter

```yaml
输入:
  directory: "03_Resource/"
  recursive: true

输出:
  - 创建/更新 _index.md 索引文件
  - 为每个文档添加 frontmatter
  - 生成统计报告
```

### search_resources

搜索资源

```yaml
输入:
  query: "搜索关键词"
  category: "github收藏/way2agi/etc"
  tags: ["AI", "Claude"]

输出:
  - 匹配的文档列表
  - 文档路径和摘要
```

## MCP 工具

- `obsidian:list_notes` - 列出笔记
- `obsidian:read_note` - 读取笔记
- `obsidian:write_note` - 写入笔记
- `obsidian:search_notes` - 搜索笔记
- `filesystem:list_directory` - 列出目录

## YAML Frontmatter 模板

```yaml
---
title: 文档标题
source: 来源 (github/way2agi/etc)
url: 原始链接（如有）
tags: [标签1, 标签2]
category: 资源类别
indexed: 2026-03-12
---
```

## 输出位置

- 索引文件: `03_Resource/_indices/_index.md`
- 统计报告: `02_Area/02_CODE 管理体系/output/reports/resource-index-report.md`
