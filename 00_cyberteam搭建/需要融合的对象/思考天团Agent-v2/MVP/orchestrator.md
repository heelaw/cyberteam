# 意图分类器（简化版MVP）

## 功能

根据用户问题，判断应该调用哪些专家。

## 分类逻辑

```json
{
  "intent_router": {
    "decision_tree": [
      {
        "condition": "包含'转化'、'增长'、'用户行为'关键词",
        "route": ["kahneman", "first_principle", "six_hats"]
      },
      {
        "condition": "包含'根本原因'、'创新'、'突破'关键词",
        "route": ["first_principle", "six_hats"]
      },
      {
        "condition": "包含'决策'、'评估'、'风险'关键词",
        "route": ["six_hats", "kahneman"]
      },
      {
        "condition": "默认（通用问题）",
        "route": ["kahneman", "first_principle", "six_hats"]
      }
    ]
  }
}
```

## 路由规则

1. **关键词匹配优先**: 先检查问题中是否包含专家触发关键词
2. **多专家覆盖**: 默认选择3位专家并行分析
3. **维度互补**: 确保覆盖认知偏差(kahneman)、本质还原(first_principle)、全面视角(six_hats)
