# 模型整合Agent - 接口定义

## 输入接口

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| business_model_type | string | 是 | 商业模式类型 |
| revenue_structure | object | 是 | 收入结构 |
| cost_structure | object | 是 | 成本结构 |
| process_analysis | object | 否 | 流程分析 |
| metrics | object | 否 | 指标体系 |

## 输出接口

| 字段 | 类型 | 说明 |
|------|------|------|
| integrated_model | object | 完整业务模型 |
| model_visualization | string | 模型可视化 |
| logical_relationships | object | 逻辑关系 |

## 调用方式

- 被 全局业务模型构建Agent 串行调用（Step 6）
