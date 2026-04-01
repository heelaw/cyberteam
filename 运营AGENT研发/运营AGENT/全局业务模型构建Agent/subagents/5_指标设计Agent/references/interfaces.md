# 指标设计Agent - 接口定义

## 输入接口

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| business_model | object | 是 | 业务模型 |
| revenue_formula | string | 是 | 收入公式 |
| cost_structure | object | 否 | 成本结构 |

## 输出接口

| 字段 | 类型 | 说明 |
|------|------|------|
| key_metrics | array | 关键指标列表 |
| metric_priorities | array | 指标优先级 |
| data_collection_plan | object | 数据采集方案 |
| dashboard_design | object | 监控看板设计 |

## 调用方式

- 被 全局业务模型构建Agent 并行调用（Step 5）
