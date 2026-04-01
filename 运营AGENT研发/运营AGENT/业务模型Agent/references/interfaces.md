# 业务模型Agent - 接口协议

## 输入接口

### 用户输入格式

```json
{
  "type": "object",
  "properties": {
    "user_goal": {
      "type": "string",
      "description": "用户的业务模型相关目标",
      "examples": [
        "理解业务模型概念",
        "梳理现有业务模型",
        "从0搭建新业务模型"
      ]
    },
    "business_context": {
      "type": "object",
      "properties": {
        "business_type": { "type": "string" },
        "business_stage": { "type": "string" },
        "specific_issue": { "type": "string" }
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
    "skill_sequence": {
      "type": "array",
      "items": { "type": "string" },
      "description": "建议使用的Skill顺序"
    },
    "model_result": {
      "type": "object",
      "properties": {
        "model_type": { "type": "string" },
        "components": { "type": "array" },
        "key_metrics": { "type": "array" }
      }
    },
    "recommendations": {
      "type": "array",
      "items": { "type": "string" }
    }
  }
}
```

## Skill调用协议

| 场景 | 调用Skill | 触发关键词 |
|------|----------|-----------|
| 概念理解 | 业务模型概念与构成 | "什么是业务模型"、"业务模型构成" |
| 整体梳理 | 整体业务模型梳理 | "怎么梳理业务模型"、"整体模型" |
| 局部分析 | 局部业务模型形成 | "局部模型"、"局部业务" |
| 新业务 | 从0搭建业务模型 | "从0到1"、"新业务搭建" |
| 创新启发 | 跨界模型借鉴 | "跨界借鉴"、"业务创新" |
