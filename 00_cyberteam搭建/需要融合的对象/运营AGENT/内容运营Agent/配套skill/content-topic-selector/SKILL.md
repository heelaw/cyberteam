---
name: content-topic-selector
description: 策划内容选题，找到能吸引用户的8个常见选题方向
trigger: "选题策划、内容选题、选题方向、热点选题、选题规划"
difficulty: medium
estimated_time: 15-20分钟
version: v1.0
author: Cyberwiz
tags: [内容运营, 选题策划]
success_metrics:
  - metric: 选题命中率
    target: "≥80%"
    measurement: 内容表现反馈
---

# content-topic-selector

## 简介

策划内容选题，找到能吸引用户的8个常见选题方向。

## 触发关键词

```
选题策划、内容选题、选题方向、热点选题、选题规划
```

## 触发场景描述

```
当需要策划选题时触发：
- 不知道该写什么内容
- 需要规划月度选题
- 需要追热点但不知道角度
- 需要找到用户感兴趣的点
```

## 输入

### 必需输入

| 字段 | 类型 | 说明 |
|------|------|------|
| positioning | object | 内容定位（来自content-positioning-analyzer） |
| current_trends | array | 当前热点 |

### 可选输入

| 字段 | type | 说明 |
|------|------|------|
| historical_performance | object | 历史选题表现 |

## 输出

```json
{
  "topic_directions": [
    {
      "direction_id": 1,
      "name": "选题方向名称",
      "description": "方向描述",
      "examples": ["选题案例"],
      "applicable_heat_level": "高/中/低"
    }
  ],
  "topic_plan": [
    {
      "topic": "具体选题",
      "direction": "所属方向",
      "timing": "发布时间",
      "angle": "切入角度"
    }
  ]
}
```

## 方法论：8个常见选题方向

### 方向1：对知名对象的吐槽

- 引发好奇心
- 争议性强

### 方向2：深度分析解读

- 专业深度
- 正面严肃

### 方向3：颠覆式认知

- 反常识观点
- 引发讨论

### 方向4：热点差异化解读

- 速度快
- 角度独特

### 方向5：数据盘点预言

- 年度盘点
- 趋势预测

### 方向6：共鸣性问题解读

- 触及用户痛点
- 疑问式切入

### 方向7：娱乐性话题关联

- 大众喜闻乐见
- 轻松有趣

### 方向8：精彩故事段子

- 情节反转
- 不可思议

### 禁止行为

1. 禁止偏离账号定位的选题
2. 禁止盲目追热点不考虑关联性
3. 禁止选题过于单一缺乏广度
4. 禁止不考虑时效性硬追热点
5. 禁止选题只顾流量不顾价值

## 参考文献

- `references/S8.06-8个选题方向.md`
