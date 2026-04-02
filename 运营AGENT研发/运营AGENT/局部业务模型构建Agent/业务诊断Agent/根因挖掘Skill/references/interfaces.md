# 根因挖掘Skill - 接口协议

## 输入接口

| 接口名称 | 类型 | 描述 | 必需 |
|----------|------|------|------|
| problem_statement | Object | 问题描述 | 是 |
| evidence | Array | 相关证据 | 否 |

## 输出接口

| 接口名称 | 类型 | 描述 |
|----------|------|------|
| root_cause | Object | 根本原因 |
| cause_chain | Array | 原因链 |
| evidence_summary | Object | 证据摘要 |
