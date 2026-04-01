# 阶段重点分析法 - 接口定义

## 输入接口

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| company_info | object | 是 | 企业信息 |
| analysis_scope | object | 是 | 分析范围 |
| context | object | 否 | 背景信息 |

## 输出接口

| 字段 | 类型 | 说明 |
|------|------|------|
| stage_analysis | object | 阶段分析结果 |
| core_task | object | 核心任务 |
| action_plan | object | 行动计划 |
| resource_allocation | object | 资源配置 |
| risks | array | 风险列表 |

## 调用方式

- 被 企业生命周期Agent 主Agent 调用
