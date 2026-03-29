# 运营策略5因素分析 - 接口定义

## 输入接口

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| decision_question | string | 是 | 需要决策的核心问题 |
| factor_1_industry | object | 是 | 行业分析数据 |
| factor_2_stage | object | 是 | 发展阶段数据 |
| factor_3_product | object | 是 | 产品形态数据 |
| factor_4_business | object | 是 | 业务类型数据 |
| factor_5_resource | object | 是 | 资源评估数据 |

## 输出接口

| 字段 | 类型 | 说明 |
|------|------|------|
| factor_analysis | object | 五因素分析结果 |
| comprehensive_assessment | object | 综合评估结果 |
| recommendations | array | 策略建议列表 |

## 调用方式

- 被 CEO/COO 调用进行策略决策
- 被 产品运营规划Agent 调用进行策略分析
