# interfaces - 通信协作中台

## 输入接口

| 接口 | 类型 | 说明 |
|------|------|------|
| `message` | Message | 发送的消息对象 |
| `handoff` | Handoff | 任务交接请求（可选） |
| `collaboration` | Collaboration | 协作编排请求（可选） |

## 输出接口

| 接口 | 类型 | 说明 |
|------|------|------|
| `delivery_status` | DeliveryStatus | 消息送达状态 |
| `handoff_status` | HandoffStatus | Handoff状态 |
| `exception_info` | ExceptionInfo | 异常信息（如果有） |

## Message 结构

```yaml
Message:
  id: string              # 消息唯一ID (UUID)
  type: enum               # REQUEST/RESPONSE/NOTIFICATION/ALERT/ACKNOWLEDGE/REDIRECT/NEGOTIATE/CANCEL
  sender: string           # 发送者Agent ID
  recipients: string[]     # 接收者Agent ID列表
  subject: string          # 消息主题
  content: object          # 消息内容
  metadata:
    timestamp: datetime    # 时间戳
    priority: enum         # CRITICAL/HIGH/NORMAL/LOW/BACKGROUND
    correlation_id: string  # 关联ID
    reply_to: string       # 回复地址
  attachments: string[]    # 附件列表
  routing:
    path: string[]        # 消息路径
    hops: int             # 跳数
    ttl: int              # 生存时间
```

## HandoffStatus 结构

```yaml
HandoffStatus:
  handoff_id: string      # Handoff唯一ID
  status: enum            # IDLE/PENDING/ACTIVE/COMPLETED/FAILED/CANCELLED
  from_agent: string      # 移交方
  to_agent: string        # 接收方
  task: Task             # 交接的任务
  timestamp: datetime     # 状态变更时间
```

## 消息类型

| 类型 | 代码 | 说明 | 典型场景 |
|------|------|------|----------|
| 请求 | REQUEST | 请求某个Agent执行操作 | 任务分发 |
| 响应 | RESPONSE | 对请求的响应 | 结果返回 |
| 通知 | NOTIFICATION | 事件通知 | 状态变更 |
| 告警 | ALERT | 异常告警 | 问题通知 |
| 确认 | ACKNOWLEDGE | 确认收到 | 收据确认 |
| 重定向 | REDIRECT | 转发到其他Agent | 任务转交 |
| 协商 | NEGOTIATE | 协作协商 | 资源协调 |
| 取消 | CANCEL | 取消操作 | 任务中止 |

## 优先级定义

| 优先级 | 代码 | SLA |
|--------|------|-----|
| 紧急 | CRITICAL | ≤10s |
| 高 | HIGH | ≤30s |
| 普通 | NORMAL | ≤5min |
| 低 | LOW | ≤30min |
| 后台 | BACKGROUND | 无限制 |

## 调用示例

```python
from agents.middle-tier.communication import CommunicationHub

comm = CommunicationHub()

# 发送消息
result = comm.send_message(message={
    "type": "REQUEST",
    "sender": "ceo",
    "recipients": ["growth-bg"],
    "subject": "执行内容运营任务",
    "content": {"task_id": "tsk-123", "description": "发布小红书文案"},
    "metadata": {"priority": "HIGH"}
})

# Handoff
handoff = comm.initiate_handoff(
    from_agent="product-bg",
    to_agent="tech-bg",
    task={"task_id": "tsk-124", "description": "开发积分功能"}
)

# 返回示例
{
    "handoff_id": "hd-20260325-001",
    "status": "PENDING",
    "from_agent": "product-bg",
    "to_agent": "tech-bg",
    "task": {"task_id": "tsk-124", "description": "开发积分功能"}
}
```
