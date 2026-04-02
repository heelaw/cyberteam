---
description: RSS 订阅抓取器 - 从 RSS 源抓取文章并保存到 Obsidian
---

# rss-fetcher

RSS 订阅抓取器 - 从 RSS 源抓取文章并保存到 03_Resource/

## 触发词

- "抓取 RSS"
- "更新订阅"
- "获取资讯"

## 功能

### fetch_rss

从配置的 RSS 源抓取最新文章

```yaml
输入:
  sources: "config/rss_sources.yaml"
  days: 1  # 抓取最近几天的内容

输出:
  - Markdown 文件保存到 03_Resource/
  - 添加 YAML frontmatter
  - 生成抓取报告
```

## 配置文件

`02_Area/02_CODE 管理体系/config/rss_sources.yaml`:

```yaml
sources:
  - name: "阮一峰的网络日志"
    url: "https://www.ruanyifeng.com/blog/atom.xml"
    category: "技术博客"
    output_dir: "03_Resource/技术博客/阮一峰/"

  - name: "少数派"
    url: "https://sspai.com/feed"
    category: "效率工具"
    output_dir: "03_Resource/效率工具/少数派/"

  - name: "AI Daily"
    url: "https://way2agi.com/feed"
    category: "AI 资讯"
    output_dir: "03_Resource/way2agi/"
```

## MCP 工具

- `obsidian:write_note` - 写入笔记
- `filesystem:create_directory` - 创建目录
- `web:fetch` - 获取网页内容

## 输出模板

```markdown
---
title: "{{文章标题}}"
source: "{{来源名称}}"
url: "{{原始链接}}"
published: "{{发布日期}}"
tags: [{{标签列表}}]
category: "{{类别}}"
fetched: 2026-03-12
---

# {{文章标题}}

> 来源: [{{来源名称}}]({{原始链接}})
> 发布时间: {{发布日期}}

## 内容摘要

{{摘要}}

## 正文

{{文章内容}}
```

## 依赖

- `feedparser` - RSS 解析
- `requests` - HTTP 请求
- `python-dateutil` - 日期解析
