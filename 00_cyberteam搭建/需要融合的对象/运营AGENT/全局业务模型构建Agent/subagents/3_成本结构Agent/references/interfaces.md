# 成本结构Agent - 接口定义

## 输入接口

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| business_model_type | string | 是 | 商业模式类型 |
| cost_data | object | 是 | 成本数据 |

## 输出接口

| 字段 | 类型 | 说明 |
|------|------|------|
| cost_items | array | 成本项列表 |
| cost_proportion | object | 成本占比 |
| cost_optimization | array | 成本优化机会 |

## 调用方式

- 被 全局业务模型构建Agent 串行调用（Step 3）
