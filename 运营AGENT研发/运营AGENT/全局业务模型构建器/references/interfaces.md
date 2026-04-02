# 全局业务模型构建器 - 接口定义

## 输入接口

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| company_info | object | 是 | 公司基本信息 |
| product_info | object | 是 | 产品/服务描述 |
| target_users | object | 是 | 目标用户画像 |
| revenue_info | object | 是 | 收入来源 |
| current_process | object | 否 | 当前业务流程 |

## 输出接口

| 字段 | 类型 | 说明 |
|------|------|------|
| business_model | object | 完整业务模型 |
| revenue_formula | string | 收入公式 |
| key_assumptions | array | 关键假设 |
| risk_points | array | 风险点 |
| optimization_suggestions | array | 优化建议 |

## 调用方式

- 被 CEO/COO 调用进行业务梳理
- 被 业务操盘手咨询Agent 调用进行业务诊断
