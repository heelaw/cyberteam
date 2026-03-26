# 生命周期判断法 - 接口定义

## 输入接口

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| company_name | string | 是 | 企业名称 |
| industry | string | 否 | 所属行业 |
| funding_stage | string | 否 | 融资阶段 |
| team_size | number | 否 | 团队规模 |
| revenue | string | 否 | 收入情况 |

## 输出接口

| 字段 | 类型 | 说明 |
|------|------|------|
| current_stage | string | 当前阶段判断 |
| confidence_score | number | 判断置信度 |
| dimension_scores | object | 各维度评分 |
| next_stage_prediction | string | 下阶段预测 |
| key_metrics_to_track | array | 关键追踪指标 |

## 调用方式

- 被 企业生命周期Agent 主Agent 调用
- 被 CEO/COO 调用进行阶段判断
