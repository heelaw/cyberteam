# user-growth-promoter

## 简介

推动用户增长，通过数据分析、机制设计实现用户规模的扩大。

## 触发关键词

```
用户增长、增长策略、裂变增长、数据驱动增长、增长黑客
```

## 触发场景描述

```
当需要实现用户增长目标时触发：
- 需要制定增长策略
- 需要设计裂变机制
- 需要优化获客成本
- 需要找到增长杠杆点
```

## 输入

### 必需输入

| 字段 | 类型 | 说明 |
|------|------|------|
| growth_target | string | 增长目标 |
| current_user_base | number | 当前用户基础 |

### 可选输入

| 字段 | 类型 | 说明 |
|------|------|------|
| budget | string | 增长预算 |
| channel_data | object | 渠道数据 |

## 输出

```json
{
  "growth_analysis": {
    "current_status": "现状分析",
    "growth_rate": "增长率",
    "bottlenecks": ["增长瓶颈"]
  },
  "growth_strategy": {
    "primary_lever": "主要杠杆",
    "secondary_levers": ["辅助杠杆"],
    "implementation_sequence": ["实施顺序"]
  },
  "specific_plans": [
    {
      "initiative": "增长举措",
      "expected_output": "预期产出",
      "resource_requirement": "资源需求",
      "timeline": "时间线"
    }
  ]
}
```

## 方法论：增长策略框架

### AARRR模型

- **Acquisition**：获客
- **Activation**：激活
- **Retention**：留存
- **Referral**：推荐
- **Revenue**：变现

### 增长杠杆分析

1. 分析当前增长瓶颈
2. 找到最高杠杆点
3. 制定优先级
4. 快速实验迭代

### 禁止行为

1. 禁止只关注获客忽视留存和变现
2. 禁止盲目烧钱增长不计算ROI
3. 禁止增长策略损害用户体验
4. 禁止用单一增长手段
5. 禁止增长目标不切实际

## 参考文献

- `references/aarrr-growth-model.md`
