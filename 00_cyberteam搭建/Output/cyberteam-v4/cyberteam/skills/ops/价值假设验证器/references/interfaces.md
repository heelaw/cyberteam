# 价值假设验证器 - 接口定义

## 输入接口

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| hypothesis | string | 是 | 待验证的假设 |
| constraints | object | 是 | 资源/时间约束 |
| context | object | 否 | 业务背景信息 |

## 输出接口

| 字段 | 类型 | 说明 |
|------|------|------|
| verification | object | 验证方案和结果 |
| decision | object | 决策建议 |
| next_steps | array | 下一步行动 |

## 调用方式

- 被 CEO/COO 调用进行假设验证
- 被 探索型项目破局器 调用进行风险评估
