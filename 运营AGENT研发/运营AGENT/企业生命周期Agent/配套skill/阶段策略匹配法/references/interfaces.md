# 阶段策略匹配法 - 接口定义

## 输入接口

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| company_profile | object | 是 | 企业画像 |
| strategy_focus | object | 是 | 策略重点 |
| constraints | object | 否 | 约束条件 |

## 输出接口

| 字段 | 类型 | 说明 |
|------|------|------|
| strategy_match | object | 策略匹配结果 |
| funding_strategy | object | 融资策略 |
| organization_strategy | object | 组织策略 |
| growth_strategy | object | 增长策略 |
| exit_strategy | object | 退出策略 |

## 调用方式

- 被 企业生命周期Agent 主Agent 调用
