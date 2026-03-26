# 模式识别Agent - 接口定义

## 输入接口

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| company_description | string | 是 | 企业主营业务描述 |
| product_type | string | 是 | 产品/服务类型 |
| target_users | string | 是 | 目标用户画像 |
| revenue_model | string | 是 | 变现方式 |

## 输出接口

| 字段 | 类型 | 说明 |
|------|------|------|
| business_model_type | string | 商业模式类型 |
| revenue_path | string | 商业价值路径 |
| conversion_chain | string | 收入转化链条 |

## 调用方式

- 被 全局业务模型构建Agent 串行调用（Step 1）
