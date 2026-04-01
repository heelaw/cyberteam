# 业务操盘手咨询Agent - 接口协议

## 输入接口

### 用户输入格式

```json
{
  "type": "object",
  "properties": {
    "user_question": {
      "type": "string",
      "description": "用户的商业问题描述",
      "examples": [
        "我的业务赚不赚钱？",
        "公司值多少钱？",
        "要不要做这个新业务？"
      ]
    },
    "context": {
      "type": "object",
      "properties": {
        "business_type": { "type": "string" },
        "company_stage": { "type": "string" },
        "additional_data": { "type": "object" }
      }
    }
  },
  "required": ["user_question"]
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
      "enum": ["财务拆解器", "业务拆解器", "价值评估器", "生命周期判断器", "决策分析器", "高管响应器"]
    },
    "problem_type": { "type": "string" },
    "analysis_result": {
      "type": "object",
      "description": "各Skill的具体输出"
    },
    "recommendations": {
      "type": "array",
      "items": { "type": "string" }
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    }
  }
}
```

## Skill调用协议

### 问题关键词匹配规则

| 问题关键词 | 调用Skill | 优先级 | 触发条件 |
|-----------|----------|--------|----------|
| 赚不赚钱/利润/成本/亏损/盈亏 | 财务拆解器 | P0 | 包含任一关键词 |
| 业务问题/从哪入手/怎么分析/拆解 | 业务拆解器 | P0 | 包含任一关键词 |
| 值多少钱/估值/融资/公司价值 | 价值评估器 | P1 | 包含任一关键词 |
| 现在该做什么/阶段/发展/生命周期 | 生命周期判断器 | P1 | 包含任一关键词 |
| 对不对/能不能做/风险/决策 | 决策分析器 | P1 | 包含任一关键词 |
| 老板/高管/汇报/沟通/同频 | 高管响应器 | P2 | 包含任一关键词 |

## 错误处理

| 错误类型 | 处理方式 | Fallback |
|---------|---------|----------|
| 关键词无法匹配 | 返回无法回答 | 引导用户明确问题 |
| Skill调用失败 | 重试1次 | 返回通用建议 |
| 数据不足 | 提示补充信息 | 基于假设给出方向性建议 |
