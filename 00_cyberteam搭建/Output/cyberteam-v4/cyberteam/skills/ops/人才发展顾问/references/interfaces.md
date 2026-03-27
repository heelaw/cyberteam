# 人才发展顾问 - 接口定义

## 输入接口

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| team_info | object | 是 | 团队基本信息 |
| employee_info | array | 否 | 员工信息 |

## 输出接口

| 字段 | 类型 | 说明 |
|------|------|------|
| talent_assessment | object | 人才盘点结果 |
| idp | object | IDP个人发展计划 |
| one_on_one | object | 1on1沟通指导 |
| motivation | object | 激励方案 |

## 调用方式

- 被 CEO/COO 调用进行人才管理
- 被 团队管理Agent 调用进行人才发展
