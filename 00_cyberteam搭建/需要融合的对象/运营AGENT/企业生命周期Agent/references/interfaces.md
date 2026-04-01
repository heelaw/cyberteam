# 企业生命周期Agent - 接口协议

## 输入接口

### 用户输入格式

```json
{
  "type": "object",
  "properties": {
    "company_status": {
      "type": "object",
      "properties": {
        "funding_stage": { "type": "string" },
        "team_size": { "type": "number" },
        "business_maturity": { "type": "string" },
        "revenue_status": { "type": "string" }
      }
    },
    "question_type": {
      "type": "string",
      "enum": ["阶段判断", "阶段特征", "阶段重点", "阶段策略"]
    }
  },
  "required": ["company_status"]
}
```

## 输出接口

### Agent输出格式

```json
{
  "type": "object",
  "properties": {
    "lifecycle_stage": {
      "type": "string",
      "enum": ["初创期", "成长期", "成熟期", "转型期/衰退期"]
    },
    "stage_characteristics": {
      "type": "array",
      "items": { "type": "string" }
    },
    "key_focus": {
      "type": "array",
      "items": { "type": "string" }
    },
    "strategy_recommendations": {
      "type": "array",
      "items": { "type": "string" }
    }
  }
}
```

## Skill调用协议

| Skill | 触发关键词 | 输出 |
|-------|----------|------|
| 生命周期判断法 | "发展阶段"、"企业阶段"、"生命周期" | 阶段判断结果 |
| 阶段特征分析法 | "阶段特征"、"成熟期"、"成长期" | 特征分析报告 |
| 阶段重点分析法 | "当前重点"、"这个阶段该做什么" | 重点任务清单 |
| 阶段策略匹配法 | "阶段策略"、"A轮"、"B轮" | 策略建议 |
