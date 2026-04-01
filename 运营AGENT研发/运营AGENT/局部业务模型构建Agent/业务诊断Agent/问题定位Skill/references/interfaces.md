# 问题定位Skill - 接口协议

## 输入接口

| 接口名称 | 类型 | 描述 | 必需 |
|----------|------|------|------|
| problem_description | string | 问题描述 | 是 |
| symptoms | Array | 问题现象 | 否 |

## 输出接口

| 接口名称 | 类型 | 描述 |
|----------|------|------|
| core_problem | Object | 核心问题 |
| problem_structure | Object | 问题结构 |
| priority_assessment | Array | 优先级评估 |
