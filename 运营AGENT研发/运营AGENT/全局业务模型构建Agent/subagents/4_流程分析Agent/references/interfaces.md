# 流程分析Agent - 接口定义

## 输入接口

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| business_model | object | 是 | 业务模型 |
| process_data | object | 否 | 流程数据 |

## 输出接口

| 字段 | 类型 | 说明 |
|------|------|------|
| core_processes | array | 核心流程列表 |
| conversion_points | array | 关键转化环节 |
| bottlenecks | array | 瓶颈识别 |
| optimization_opportunities | array | 优化机会 |

## 调用方式

- 被 全局业务模型构建Agent 并行调用（Step 4）
