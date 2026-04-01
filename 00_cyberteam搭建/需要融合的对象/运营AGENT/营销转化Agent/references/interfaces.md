# 营销转化Agent - 接口协议

## 输入接口

### 用户输入

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| product_info | string | 是 | 产品信息 |
| target_user | string | 是 | 目标用户描述 |
| marketing_goal | string | 是 | 营销目标 |

### 来自其他Agent的输入

| 来源Agent | 传递内容 | 触发条件 |
|-----------|----------|----------|
| 用户运营Agent | 用户画像和分层 | 用户分析完成后 |
| 增长Agent | 增长目标和约束 | 增长项目启动时 |

## 输出接口

### 直接输出

| 字段 | 类型 | 说明 |
|------|------|------|
| user_profile | object | 目标用户画像 |
| conversion_funnel | object | 转化链路设计 |
| action_recommendations | array | 优化建议 |

### 传递给其他Agent

| 目标Agent | 传递内容 | 传递条件 |
|-----------|----------|----------|
| 内容运营Agent | 转化文案需求 | 需要文案时 |
| 数据驱动Agent | 转化数据 | 需要数据追踪时 |
