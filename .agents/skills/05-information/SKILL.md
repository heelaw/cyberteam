---
name: information-department
description: 信息部 - 采用 CODE 信息管理体系，负责信息采集、整理、分析与评估
version: 1.0.0
author: CyberWiz
tags: [information, collection, organization, analysis]
---

# Information Department - 信息部

## 部门概述

信息部采用 **CODE 信息管理体系**，负责为决策提供信息支持。

## CODE 体系

| 阶段 | 说明 | Skills |
|------|------|--------|
| **C**ollect | 信息采集 | web-collector, rss-collector, sanjieke |
| **O**rganize | 信息整理 | organizer, course-reviewer |
| **D**istill | 信息提炼 | analyzer |
| **E**pply | 信息应用 | all |

## 核心 Skills

| Skill | 功能 | 状态 |
|-------|------|------|
| web-collector | 网页采集 | ✅ 可用 |
| rss-collector | RSS采集 | ✅ 可用 |
| sanjieke | 课程采集 | ✅ 可用 |
| course-reviewer | 课程内容校对 | ✅ 可用 |
| organizer | 信息整理 | ✅ 可用 |
| analyzer | 信息分析 | ✅ 可用 |

## 使用示例

### 采集信息
```
skill: web-collector
action: search
query: "Codex 新功能"
```

### 整理信息
```
skill: organizer
action: organize
source: web
```

### 分析信息
```
skill: analyzer
action: evaluate
item_id: "xxx"
```

### 生成报告
```
skill: analyzer
action: report
type: daily
```

## 信息流转

```
采集 → 整理 → 提炼 → 应用
  ↓      ↓      ↓     ↓
web/    分类/   摘要/ 报告/
rss     标签    评估  查询
         索引    趋势
```

## 数据存储

```
~/Documents/CyberWiz-Information/
├── sources/           # 原始数据
│   ├── web/
│   ├── rss/
│   └── sanjieke/
├── processed/         # 处理后数据
│   ├── summaries/
│   ├── tags/
│   └── index/
└── reports/          # 报告输出
    ├── daily/
    ├── weekly/
    └── monthly/
```
