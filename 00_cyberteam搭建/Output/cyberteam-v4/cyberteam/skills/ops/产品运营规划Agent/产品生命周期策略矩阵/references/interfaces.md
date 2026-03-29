# 产品生命周期策略矩阵 - 接口定义

## 输入接口

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| product_info | object | 是 | 产品基本信息 |
| metrics | object | 是 | 产品指标数据 |
| current_strategy | string | 否 | 当前运营策略 |

## 输出接口

| 字段 | 类型 | 说明 |
|------|------|------|
| stage_judgment | object | 阶段判断结果 |
| recommended_strategies | array | 推荐策略列表 |
| key_metrics | array | 关键指标 |
| transition_signals | object | 阶段转换信号 |

## 调用方式

- 被 `运营策略5因素分析` 调用
- 被 `全局业务模型构建Agent` 调用
