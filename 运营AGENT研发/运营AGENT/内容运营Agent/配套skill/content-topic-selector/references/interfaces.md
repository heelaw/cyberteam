# content-topic-selector - 接口定义

## 输入接口

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| positioning | object | 是 | 内容定位（来自content-positioning-analyzer） |
| current_trends | array | 是 | 当前热点 |
| historical_performance | object | 否 | 历史选题表现 |

## 输出接口

| 字段 | 类型 | 说明 |
|------|------|------|
| topic_directions | array | 选题方向列表 |
| topic_plan | array | 选题计划 |

## 调用方式

- 被 content-positioning-analyzer 调用
- 被 新媒体进阶Agent 调用
