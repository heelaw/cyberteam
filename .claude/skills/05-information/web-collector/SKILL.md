---
name: web-collector
description: 网页信息采集工具，支持指定URL采集、关键词搜索采集、定时采集等多种模式
version: 1.0.0
author: CyberWiz Information Department
tags: [information, collector, web, scraping]
dependencies:
  - jina (MCP)
  - web-reader (MCP)
  - web-search-prime (MCP)
---

# Web Collector - 网页信息采集

## 功能概述

自动化采集网页内容，支持多种采集模式。

## 采集模式

### 1. URL 采集
直接采集指定 URL 的内容

```
skill: web-collector
action: collect_url
url: "https://example.com/article"
```

### 2. 关键词搜索采集
根据关键词搜索并采集相关内容

```
skill: web-collector
action: search
query: "Claude Code 新功能"
limit: 10
```

### 3. 定时采集
定时执行采集任务

```
skill: web-collector
action: schedule
cron: "0 9 * * *"
query: "AI 资讯"
```

## 所需 MCP 工具

| MCP 工具 | 用途 |
|---------|------|
| jina | 网页内容读取 |
| web-reader | 网页解析 |
| web-search-prime | 关键词搜索 |

## 输出格式

采集结果会自动保存到信息存储系统：

```
~/Documents/CyberWiz-Information/sources/web/
├── 2026-02-28/
│   ├── url_xxx.json
│   └── search_xxx.json
└── index.json
```

## 使用示例

### 采集单页
```
skill: web-collector
action: collect_url
url: "https://anthropic.com/news/claude-code"
```

### 批量搜索
```
skill: web-collector
action: search
query: "AI 编程工具"
sources:
  - google
  - twitter
  - github
```

### 采集并解析
```
skill: web-collector
action: collect_and_parse
url: "https://example.com"
parser: article
```

## 配置选项

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| timeout | number | 30000 | 超时时间(ms) |
| retry | number | 3 | 重试次数 |
| delay | number | 1000 | 请求间隔(ms) |
| headers | object | {} | 自定义请求头 |

## 注意事项

1. 遵守网站的 robots.txt 规则
2. 控制采集频率，避免对目标网站造成压力
3. 敏感信息需要加密存储
