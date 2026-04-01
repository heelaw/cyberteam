# 产品运营规划Agent - 接口协议

## 输入接口

### 用户输入格式

```json
{
  "type": "object",
  "properties": {
    "user_goal": {
      "type": "string",
      "description": "用户的产品运营规划目标",
      "examples": [
        "产品处于成长期怎么运营",
        "季度规划怎么做",
        "如何找到增长点"
      ]
    },
    "product_info": {
      "type": "object",
      "properties": {
        "product_type": { "type": "string" },
        "product_stage": { "type": "string" },
        "target_users": { "type": "string" },
        "business_model": { "type": "string" }
      }
    }
  },
  "required": ["user_goal"]
}
```

## 输出接口

### Agent输出格式

```json
{
  "type": "object",
  "properties": {
    "skill_used": {
      "type": "string",
      "enum": ["产品生命周期策略矩阵", "运营策略5因素分析", "中长期运营规划制定", "业务形态破局点识别"]
    },
    "stage_assessment": { "type": "string" },
    "strategy_recommendations": {
      "type": "array",
      "items": { "type": "string" }
    },
    "action_plan": {
      "type": "array",
      "items": { "type": "string" }
    }
  }
}
```

## Skill调用协议

| 场景 | 调用Skill | 触发关键词 |
|------|----------|-----------|
| 阶段策略 | 产品生命周期策略矩阵 | "xx阶段怎么运营"、"探索期/成长期/成熟期/衰退期" |
| 运营方向 | 运营策略5因素分析 | "运营重点是什么"、"如何确定运营方向" |
| 规划制定 | 中长期运营规划制定 | "季度规划怎么做"、"年度规划怎么写" |
| 增长突破 | 业务形态破局点识别 | "增长点在哪里"、"如何突破" |
