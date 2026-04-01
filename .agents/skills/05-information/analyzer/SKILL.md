---
name: information-analyzer
description: 信息分析评估工具，价值评估、摘要生成、趋势分析、报告生成
version: 1.0.0
author: CyberWiz Information Department
tags: [information, analyzer, analysis, report, summary]
dependencies: []
---

# Information Analyzer - 信息分析评估

## 功能概述

对整理后的信息进行深度分析，包括价值评估、自动摘要、趋势分析、报告生成。

## 核心功能

### 1. 价值评估
评估信息的价值分数和可信度

### 2. 摘要生成
自动生成内容摘要

### 3. 趋势分析
分析信息趋势和模式

### 4. 报告生成
生成结构化报告

## 使用示例

### 评估信息价值
```
skill: information-analyzer
action: evaluate
item_id: "xxx"
dimensions:
  - relevance
  - credibility
  - timeliness
```

### 生成摘要
```
skill: information-analyzer
action: summarize
item_id: "xxx"
length: medium
```

### 趋势分析
```
skill: information-analyzer
action: trend
topic: AI
period: 30d
```

### 生成报告
```
skill: information-analyzer
action: report
type: daily
scope: all
```

## 评估维度

| 维度 | 说明 | 权重 |
|------|------|------|
| 相关性 | 与目标的相关程度 | 0.3 |
| 可信度 | 来源可靠性 | 0.25 |
| 时效性 | 信息的时效性 | 0.2 |
| 深度 | 内容的深度 | 0.15 |
| 原创性 | 原创程度 | 0.1 |

## 报告类型

| 类型 | 频率 | 内容 |
|------|------|------|
| 快速摘要 | 实时 | 单条信息简报 |
| 日报 | 每日 | 当日采集汇总 |
| 周报 | 每周 | 趋势分析、重点内容 |
| 月报 | 每月 | 深度分析、建议 |

## 输出位置

```
~/Documents/CyberWiz-Information/reports/
├── daily/
│   └── 2026-02-28.json
├── weekly/
│   └── 2026-W09.md
├── monthly/
│   └── 2026-02.md
└── analysis/
    └── trend_ai_30d.json
```

## 配置选项

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| summary_length | string | medium | 摘要长度(short/medium/long) |
| analysis_depth | string | basic | 分析深度(basic/deep) |
| auto_report | boolean | false | 自动报告开关 |
