# incentive-system-designer

## 简介

设计用户激励体系，通过机制设计引导用户行为，形成良性循环。

## 触发关键词

```
用户激励、激励体系、积分体系、等级体系、勋章系统
```

## 触发场景描述

```
当需要建立用户激励体系时触发：
- 需要提升用户活跃度
- 需要激励用户行为
- 现有激励效果下降
- 需要设计成长体系
```

## 输入

### 必需输入

| 字段 | 类型 | 说明 |
|------|------|------|
| target_behaviors | array | 目标行为 |
| user_segments | array | 用户分层（来自user-stratifier） |

### 可选输入

| 字段 | 类型 | 说明 |
|------|------|------|
| existing_system | object | 现有激励体系 |

## 输出

```json
{
  "incentive_system": {
    "core_loop": "核心激励循环",
    "elements": {
      "points": {
        "name": "积分名称",
        "rules": "积分规则",
        "usage": "积分用途"
      },
      "levels": {
        "name": "等级名称",
        "requirements": ["等级要求"],
        "benefits": ["等级权益"]
      },
      "badges": {
        "name": "勋章名称",
        "criteria": ["获取条件"]
      }
    }
  },
  "behavior_guidance": [
    {
      "target_behavior": "目标行为",
      "incentive": "激励方式",
      "expected_result": "预期结果"
    }
  ]
}
```

## 方法论：激励体系设计

### 核心要素

1. **积分系统**
   - 获取规则
   - 消耗用途
   - 价值感

2. **等级体系**
   - 成长路径
   - 等级权益
   - 升级门槛

3. **勋章徽章**
   - 成就认可
   - 特殊标识
   - 社交展示

### 激励设计原则

- 及时反馈
- 可感知的价值
- 合理的难度梯度
- 社交比较元素

### 禁止行为

1. 禁止激励体系过于复杂用户看不懂
2. 禁止积分通胀导致价值感丧失
3. 禁止只激励新用户忽视老用户
4. 禁止激励行为与业务目标背离
5. 禁止激励规则频繁变动

## 参考文献

- `references/incentive-design-method.md`
