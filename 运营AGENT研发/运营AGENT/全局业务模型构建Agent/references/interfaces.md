# 全局业务模型构建Agent - 接口协议

## 输入接口

### 用户输入格式

```json
{
  "type": "object",
  "properties": {
    "business_description": {
      "type": "string",
      "description": "商业模式描述"
    },
    "analysis_focus": {
      "type": "array",
      "items": { "type": "string" },
      "description": "用户关注的分析维度"
    }
  },
  "required": ["business_description"]
}
```

## 输出接口

### Agent输出格式

```json
{
  "type": "object",
  "properties": {
    "business_model_type": { "type": "string" },
    "revenue_structure": {
      "type": "array",
      "items": { "type": "object" }
    },
    "cost_structure": {
      "type": "array",
      "items": { "type": "object" }
    },
    "key_processes": {
      "type": "array",
      "items": { "type": "string" }
    },
    "key_metrics": {
      "type": "array",
      "items": { "type": "string" }
    },
    "integrated_model": { "type": "object" }
  }
}
```

## SubAgent调用协议

| Stage | SubAgent | 输入 | 输出 |
|-------|----------|------|------|
| 1 | 模式识别Agent | 商业模式描述 | 商业模式识别报告 |
| 2 | 收入结构Agent | 识别报告 | 收入结构报告 |
| 3 | 成本结构Agent | 识别报告 | 成本结构报告 |
| 4 | 流程分析Agent | 收支报告 | 流程分析报告 |
| 5 | 指标设计Agent | 流程报告 | 指标设计报告 |
| 6 | 模型整合Agent | 各模块报告 | 完整业务模型 |
| 7 | 模型验证Agent | 完整模型 | 验证报告 |
