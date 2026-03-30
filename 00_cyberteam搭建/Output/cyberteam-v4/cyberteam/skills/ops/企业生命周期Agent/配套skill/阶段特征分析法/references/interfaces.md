# 阶段特征分析法 - 接口定义

## 输入接口

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| company_snapshot | object | 是 | 企业快照数据 |
| analysis_dimensions | object | 是 | 分析维度设置 |
| comparison_benchmark | object | 否 | 对比基准 |
| context | object | 否 | 背景信息 |

## 输出接口

| 字段 | 类型 | 说明 |
|------|------|------|
| stage_diagnosis | object | 阶段诊断结果 |
| business_profile | object | 业务特征 |
| team_profile | object | 团队特征 |
| financial_profile | object | 财务特征 |
| competitive_profile | object | 竞争特征 |

## 调用方式

- 被 企业生命周期Agent 主Agent 调用
