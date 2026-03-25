# downstream - 通信协作中台

## 直接下游

| 下游Agent | 关系 | 说明 |
|-----------|------|------|
| 目标Agent | 消息送达 | 消息路由到接收方 |
| 发送方Agent | 回执通知 | 消息状态回调 |
| 监控中台 | 告警转发 | 通信异常告警 |
| 记忆中台 | 日志存储 | 通信日志记录 |

## 输出物

| 输出物 | 下游使用方 | 用途 |
|--------|------------|------|
| 转发消息 | 目标Agent | 消息传递 |
| 送达回执 | 发送方Agent | 状态确认 |
| Handoff完成通知 | 移交方Agent | 交接确认 |
| 告警通知 | 监控中台 | 异常告警 |
| 通信日志 | 记忆中台 | 历史记录 |

## Handoff流程输出

### 发起Handoff输出

```yaml
Handoff发起:
  handoff_id: {UUID}
  from_agent: {移交方}
  to_agent: {接收方}
  task: {任务详情}
  status: PENDING
  timeout: 300s
```

### 接受Handoff输出

```yaml
Handoff接受:
  handoff_id: {UUID}
  status: ACTIVE
  accept_time: {时间}
  next_action: 开始执行任务
```

### 完成Handoff输出

```yaml
Handoff完成:
  handoff_id: {UUID}
  status: COMPLETED
  result: {执行结果}
  complete_time: {时间}
  callback_triggered: true/false
```

## 输出分类

### 消息传递输出

| 输出物 | 格式 | 下游使用 |
|--------|------|----------|
| 送达回执 | JSON | 发送方确认 |
| 响应消息 | Message | 请求方处理 |
| 转发通知 | Message | 目标Agent |

### 协作编排输出

| 输出物 | 格式 | 下游使用 |
|--------|------|----------|
| 协作状态 | JSON | 参与方了解 |
| 检查点报告 | JSON | 编排协调 |
| 终止通知 | JSON | 参与方结束 |

### 异常处理输出

| 输出物 | 格式 | 下游使用 |
|--------|------|----------|
| 重试通知 | JSON | 相关方重试 |
| 熔断触发 | JSON | 系统保护 |
| 升级告警 | JSON | 上级处理 |

## 下游数据流

```
通信中台
    ↓
    ├── 消息 → 目标Agent → 执行处理
    ├── 回执 → 发送方Agent → 状态更新
    ├── 完成通知 → 移交方Agent → 任务关闭
    ├── 异常告警 → 监控中台 → 告警处理
    └── 通信日志 → 记忆中台 → 历史存储
```
