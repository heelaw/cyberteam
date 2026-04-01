# 收入结构Agent - 接口定义

## 输入接口

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| business_model_type | string | 是 | 商业模式类型（来自模式识别） |
| revenue_data | object | 是 | 收入数据 |

## 输出接口

| 字段 | 类型 | 说明 |
|------|------|------|
| revenue_sources | array | 收入来源列表 |
| revenue_proportion | object | 收入占比 |
| revenue_formula | string | 收入公式 |

## 调用方式

- 被 全局业务模型构建Agent 串行调用（Step 2）
