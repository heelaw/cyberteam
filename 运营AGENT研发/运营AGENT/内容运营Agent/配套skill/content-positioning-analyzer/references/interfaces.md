# content-positioning-analyzer - 接口定义

## 输入接口

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| product_info | string | 是 | 产品/账号信息 |
| target_users | string | 是 | 目标用户 |
| competitor_analysis | array | 否 | 竞品分析 |

## 输出接口

| 字段 | 类型 | 说明 |
|------|------|------|
| positioning | object | 定位结果 |
| content_guidelines | object | 内容规范 |
| implementation | object | 实施计划 |

## 调用方式

- 被 新媒体进阶Agent 调用
- 被 内容运营Agent 主Agent 调用
