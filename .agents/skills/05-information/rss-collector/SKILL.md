---
name: rss-collector
description: RSS 订阅采集工具，管理订阅源并自动抓取更新内容
version: 1.0.0
author: CyberWiz Information Department
tags: [information, collector, rss, feed]
dependencies: []
---

# RSS Collector - RSS 订阅采集

## 功能概述

自动化采集 RSS 订阅源内容，支持订阅管理、自动抓取、内容过滤。

## 核心功能

### 1. 订阅管理
添加、删除、列出 RSS 订阅源

### 2. 自动抓取
定时检查订阅源更新并采集

### 3. 内容过滤
根据关键词/标签过滤感兴趣的内容

## 使用示例

### 添加订阅
```
skill: rss-collector
action: add
feed_url: "https://example.com/feed.xml"
tags: [tech, ai]
```

### 列出订阅
```
skill: rss-collector
action: list
```

### 抓取更新
```
skill: rss-collector
action: fetch
source: all
```

### 抓取特定源
```
skill: rss-collector
action: fetch
source: tech_news
```

## 订阅配置

默认订阅源（可配置）：

| 源名称 | URL | 标签 |
|--------|-----|------|
| AI News | https://news.ycombinator.com/rss | tech, ai |
| OpenAI Blog | https://openai.com/blog/rss | ai |
| Anthropic Blog | https://anthropic.com/blog/rss | ai |

## 输出格式

```
~/Documents/CyberWiz-Information/sources/rss/
├── subscriptions.json    # 订阅列表
├── 2026-02-28/
│   ├── source1.json
│   └── source2.json
└── index.json
```

## 配置选项

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| check_interval | number | 3600000 | 检查间隔(ms) |
| max_items | number | 50 | 每次最大条目数 |
| auto_fetch | boolean | false | 自动抓取开关 |
