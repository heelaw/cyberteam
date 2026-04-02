# 模型验证Agent - 接口定义

## 输入接口

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| integrated_model | object | 是 | 完整业务模型 |
| assumptions | array | 是 | 关键假设 |
| business_data | object | 否 | 实际业务数据 |

## 输出接口

| 字段 | 类型 | 说明 |
|------|------|------|
| validation_result | object | 验证结果 |
| logical_consistency | boolean | 逻辑一致性 |
| assumption_validation | array | 假设验证结果 |
| boundary_conditions | object | 边界条件 |
| optimization_suggestions | array | 优化建议 |

## 调用方式

- 被 全局业务模型构建Agent 串行调用（Step 7）
