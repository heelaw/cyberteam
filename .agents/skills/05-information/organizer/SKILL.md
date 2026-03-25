---
name: information-organizer
description: 信息整理归档工具，自动分类、标签生成、索引构建
version: 1.0.0
author: CyberWiz Information Department
tags: [information, organizer, classification, indexing]
dependencies:
  - obsidian-mcp-server
---

# Information Organizer - 信息整理归档

## 功能概述

将采集到的信息进行结构化整理，包括自动分类、标签生成、索引构建。

## 核心功能

### 1. 自动分类
根据内容类型自动分类到对应目录

### 2. 标签生成
自动提取关键词生成标签

### 3. 索引构建
构建全文索引便于检索

## 使用示例

### 整理单条信息
```
skill: information-organizer
action: organize
source: web
item_id: "xxx"
```

### 批量整理
```
skill: information-organizer
action: batch_organize
source: rss
date: today
```

### 重建索引
```
skill: information-organizer
action: reindex
scope: all
```

### 手动分类
```
skill: information-organizer
action: classify
item_id: "xxx"
category: AI
tags: [LLM, Codex]
```

## 分类规则

| 分类 | 关键词 |
|------|--------|
| AI | ai, llm, gpt, Codex, model |
| 产品 | product, feature, launch |
| 编程 | code, developer, programming |
| 商业 | business, startup, funding |
| 趋势 | trend, future, prediction |

## 输出结构

```
~/Documents/CyberWiz-Information/processed/
├── by_category/
│   ├── ai/
│   ├── product/
│   └── ...
├── by_tag/
│   ├── llm/
│   └── ...
├── index.json
└── embeddings/    # 向量索引（可选）
```

## 配置选项

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| auto_classify | boolean | true | 自动分类开关 |
| auto_tag | boolean | true | 自动标签开关 |
| embedding | boolean | false | 向量索引开关 |
