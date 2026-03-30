# CyberTeam v3 Agent 通信协议规范 (CCP)

> **版本**: v1.0
> **创建日期**: 2026-03-24
> **协议名称**: CyberTeam Communication Protocol (CCP)
> **状态**: 最终规范

---

## 一、协议概述

### 1.1 协议目标

1. **统一通信**: 定义 Agent 间统一的消息格式
2. **可靠传输**: 确保消息可靠传递和确认
3. **错误处理**: 定义重试和降级机制
4. **可扩展性**: 支持协议版本升级

### 1.2 协议架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    CCP 协议架构                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  应用层                                                          │
│  ├─── 消息类型: request/response/notification/heartbeat        │
│  ├─── 消息动作: execute_task/report_result/notify_status       │
│  └─── 消息参数: task_id/params/context                         │
│                                                                  │
│  表示层                                                          │
│  ├─── 消息格式: JSON                                            │
│  ├─── 字符编码: UTF-8                                           │
│  └─── 压缩: 可选 (Gzip)                                         │
│                                                                  │
│  传输层                                                          │
│  ├─── 传输方式: 文件系统                                        │
│  ├─── 路由方式: CEO 集中路由                                    │
│  └─── 确认机制: ACK/NACK                                        │
│                                                                  │
│  基础设施层                                                      │
│  ├─── 存储位置: ~/.cyberteam/messages/                         │
│  ├─── 目录结构: in/out/draft/archive                           │
│  └─── 文件命名: {message_id}.json                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、消息格式定义

### 2.1 消息结构

```json
{
  "message_protocol": "CyberTeam-v3",
  "version": "1.0",
  "header": {
    "id": "MSG-20260324-001",
    "from": "PM",
    "to": "数据分析部",
    "timestamp": "2026-03-24T15:10:00Z",
    "type": "request",
    "priority": "normal",
    "correlation_id": "TASK-20260324-001"
  },
  "body": {
    "action": "execute_task",
    "params": {
      "task_id": "TASK-20260324-001",
      "title": "提升下月GMV 15%",
      "description": "通过优化转化率提升下月GMV",
      "skills": ["/growth-analysis"],
      "deadline": "2026-03-25T18:00:00Z"
    },
    "context": {
      "parent_task": null,
      "expert_opinions": [],
      "user_request": "帮我增长下月营业指标"
    }
  },
  "footer": {
    "checksum": "abc123def456",
    "signature": null
  }
}
```

### 2.2 消息类型

| 类型 | 用途 | 方向 | 示例 |
|------|------|------|------|
| **request** | 请求执行任务 | L2 → L3 | PM → 部门: 执行任务 |
| **response** | 返回执行结果 | L3 → L2 | 部门 → PM: 任务完成 |
| **notification** | 通知状态变化 | 任意 → 任意 | 部门 → PM: 任务进度更新 |
| **heartbeat** | 心跳保活 | L3 → L2 | 部门 → PM: 我还活着 |

### 2.3 消息动作

| 动作 | 适用类型 | 说明 |
|------|----------|------|
| **execute_task** | request | 执行一个任务 |
| **report_result** | response | 报告执行结果 |
| **notify_status** | notification | 通知状态变化 |
| **heartbeat** | heartbeat | 心跳保活 |
| **query_status** | request | 查询状态 |
| **cancel_task** | request | 取消任务 |

### 2.4 消息优先级

| 优先级 | 值 | 用途 | 处理策略 |
|--------|-----|------|----------|
| **urgent** | 1 | 紧急任务 | 立即处理 |
| **high** | 2 | 高优先级 | 优先处理 |
| **normal** | 3 | 普通优先级 | 正常处理 |
| **low** | 4 | 低优先级 | 空闲时处理 |

---

## 三、消息传输

### 3.1 传输架构

```
发送者 (A)
    ↓
1. 生成消息
2. 序列化为 JSON
3. 计算校验和
4. 写入 ~/.cyberteam/messages/out/{msg_id}.json
5. 通知 CEO
    ↓
CEO (路由器)
    ↓
1. 读取消息
2. 验证格式
3. 查询路由表
4. 转发消息 (写入 in 目录)
5. 通知接收者
    ↓
接收者 (B)
    ↓
1. 读取消息
2. 验证校验和
3. 反序列化
4. 处理消息
5. 生成响应
    ↓
响应流程 (反向)
```

### 3.2 目录结构

```yaml
~/.cyberteam/messages/
  in/                    # 接收箱
    {message_id}.json    # 待处理的消息
    _processing/         # 处理中的消息
    _done/               # 已处理的消息

  out/                   # 发送箱
    {message_id}.json    # 待发送的消息
    _sent/               # 已发送的消息
    _failed/             # 发送失败的消息

  draft/                 # 草稿箱
    {message_id}.json    # 草稿消息

  archive/               # 归档
    {date}/              # 按日期归档
      {message_id}.json
```

### 3.3 消息命名规则

```yaml
格式: {prefix}-{timestamp}-{random}.json

示例:
  MSG-20260324-151000-abc123.json
  RES-20260324-151030-def456.json
  NOT-20260324-151100-ghi789.json

前缀:
  MSG: 通用消息
  REQ: 请求
  RES: 响应
  NOT: 通知
  HBT: 心跳
```

---

## 四、消息确认机制

### 4.1 ACK/NACK 机制

```yaml
ACK (确认):
  触发: 接收者成功接收并解析消息
  格式:
    {
      "message_protocol": "CyberTeam-v3",
      "type": "ACK",
      "original_message_id": "MSG-20260324-001",
      "received_at": "2026-03-24T15:10:05Z",
      "status": "received"
    }
  发送: 接收者 → 发送者

NACK (拒绝):
  触发: 接收者无法接收或解析消息
  格式:
    {
      "message_protocol": "CyberTeam-v3",
      "type": "NACK",
      "original_message_id": "MSG-20260324-001",
      "received_at": "2026-03-24T15:10:05Z",
      "reason": "格式错误/校验和错误/不支持的消息类型"
    }
  发送: 接收者 → 发送者
```

### 4.2 超时与重试

```yaml
超时配置:
  ACK 超时: 30 秒
  响应超时: 根据任务类型而定
  心跳超时: 60 秒

重试策略:
  最大重试次数: 3 次
  重试间隔: 指数退避 (5s, 10s, 20s)
  重试后仍失败: 标记为失败，通知 CEO

重试流程:
  1. 发送消息
  2. 等待 ACK
  3. 超时 → 重试1 (5秒后)
  4. 超时 → 重试2 (10秒后)
  5. 超时 → 重试3 (20秒后)
  6. 仍失败 → 标记失败
```

### 4.3 心跳机制

```yaml
心跳配置:
  心跳间隔: 30 秒
  心跳超时: 60 秒
  心跳格式:
    {
      "message_protocol": "CyberTeam-v3",
      "type": "heartbeat",
      "from": "数据分析部",
      "timestamp": "2026-03-24T15:10:00Z",
      "status": "idle/busy/error",
      "current_task": "TASK-001" (如果有)
    }

心跳处理:
  PM 接收心跳:
    - 更新部门状态
    - 检查心跳间隔
    - 超时 → 标记部门为离线

  部门发送心跳:
    - 每 30 秒发送一次
    - 状态变化时立即发送
```

---

## 五、错误处理

### 5.1 错误类型

| 错误类型 | 说明 | 处理方式 |
|---------|------|----------|
| **格式错误** | 消息格式不正确 | NACK + 不重试 |
| **校验错误** | 校验和验证失败 | NACK + 重试 |
| **路由错误** | 找不到目标 | 通知 CEO + 不重试 |
| **处理错误** | 任务执行失败 | 返回错误响应 + 不重试 |
| **超时错误** | 响应超时 | 重试 3 次 |

### 5.2 错误响应格式

```json
{
  "message_protocol": "CyberTeam-v3",
  "type": "error",
  "original_message_id": "MSG-20260324-001",
  "error": {
    "code": "PROCESSING_ERROR",
    "message": "任务执行失败",
    "details": "具体错误信息",
    "timestamp": "2026-03-24T15:15:00Z"
  }
}
```

### 5.3 错误码定义

```yaml
错误码列表:
  FORMAT_ERROR: 消息格式错误
  CHECKSUM_ERROR: 校验和错误
  ROUTE_ERROR: 路由错误
  TIMEOUT_ERROR: 超时错误
  PROCESSING_ERROR: 处理错误
  RESOURCE_ERROR: 资源错误
  PERMISSION_ERROR: 权限错误
  UNKNOWN_ERROR: 未知错误
```

---

## 六、安全机制

### 6.1 数据完整性

```yaml
校验和:
  算法: SHA-256
  计算: hash(header + body)
  存储: footer.checksum
  验证: 接收者验证校验和

签名 (可选):
  算法: HMAC-SHA256
  密钥: 环境变量 CCP_SIGNATURE_KEY
  计算: hmac_sha256(message, key)
  存储: footer.signature
  验证: 接收者验证签名
```

### 6.2 访问控制

```yaml
权限矩阵:
  发送权限:
    - L1 (CEO): 可以发送给任何人
    - L2 (PM/Strategy): 可以发送给 L3
    - L3 (部门): 只能发送给 L2

  接收权限:
    - L1 (CEO): 可以接收来自任何人
    - L2 (PM/Strategy): 可以接收来自 L1/L3
    - L3 (部门): 只能接收来自 L2

权限检查:
  1. 检查发送者是否有发送权限
  2. 检查接收者是否有接收权限
  3. 如果权限不足，返回 PERMISSION_ERROR
```

### 6.3 数据加密 (可选)

```yaml
加密:
  算法: AES-256-GCM
  密钥: 环境变量 CCP_ENCRYPTION_KEY
  加密范围: body 字段
  触发条件: 敏感信息 (密码、密钥等)
```

---

## 七、协议版本

### 7.1 版本号

```yaml
当前版本: 1.0
版本格式: {major}.{minor}
  - major: 重大变更，不兼容旧版本
  - minor: 小改进，向后兼容

版本协商:
  1. 发送者发送消息时携带版本号
  2. 接收者检查版本号
  3. 如果版本不兼容，返回错误
```

### 7.2 升级策略

```yaml
升级路径:
  1.0 → 1.1: 向后兼容，平滑升级
  1.1 → 2.0: 不兼容，需要双轨运行

升级流程:
  1. 新旧版本双轨运行
  2. 逐步迁移到新版本
  3. 完全切换到新版本
  4. 停止旧版本
```

---

## 八、性能考虑

### 8.1 消息大小限制

```yaml
最大消息大小: 1 MB
超过限制:
  - 压缩消息
  - 或使用文件引用
```

### 8.2 批量传输

```yaml
批量消息:
  适用场景: 多个独立任务
  格式:
    {
      "message_protocol": "CyberTeam-v3",
      "type": "batch",
      "messages": [msg1, msg2, msg3]
    }

处理:
  - 接收者逐个处理
  - 或并行处理
```

### 8.3 消息压缩

```yaml
压缩:
  算法: Gzip
  触发: 消息大小 > 100 KB
  格式:
    {
      "message_protocol": "CyberTeam-v3",
      "compressed": true,
      "encoding": "gzip",
      "payload": "base64_encoded_compressed_data"
    }
```

---

## 九、监控与日志

### 9.1 消息日志

```yaml
日志位置: ~/.cyberteam/logs/messages/

日志内容:
  - 消息 ID
  - 发送者
  - 接收者
  - 时间戳
  - 消息类型
  - 处理状态
  - 错误信息 (如果有)

日志格式: JSON Lines
```

### 9.2 性能监控

```yaml
监控指标:
  - 消息发送成功率
  - 消息接收成功率
  - 平均响应时间
  - 消息队列长度
  - 重试次数
  - 错误率

监控方式:
  - 定期收集指标
  - 写入 ~/.cyberteam/metrics/
  - 生成监控报告
```

---

## 十、附录

### 10.1 完整消息示例

#### 示例1: PM → 部门 (请求执行任务)

```json
{
  "message_protocol": "CyberTeam-v3",
  "version": "1.0",
  "header": {
    "id": "MSG-20260324-001",
    "from": "PM",
    "to": "数据分析部",
    "timestamp": "2026-03-24T15:10:00Z",
    "type": "request",
    "priority": "normal",
    "correlation_id": "TASK-20260324-001"
  },
  "body": {
    "action": "execute_task",
    "params": {
      "task_id": "TASK-20260324-001",
      "title": "提升下月GMV 15%",
      "description": "通过优化转化率提升下月GMV",
      "skills": ["/growth-analysis", "/leverage-analysis"],
      "deadline": "2026-03-25T18:00:00Z"
    },
    "context": {
      "parent_task": null,
      "expert_opinions": [
        {
          "expert": "增长黑客专家",
          "opinion": "转化率优化ROI最高",
          "confidence": 0.85
        }
      ],
      "user_request": "帮我增长下月营业指标"
    }
  },
  "footer": {
    "checksum": "abc123def456",
    "signature": null
  }
}
```

#### 示例2: 部门 → PM (返回执行结果)

```json
{
  "message_protocol": "CyberTeam-v3",
  "version": "1.0",
  "header": {
    "id": "RES-20260324-001",
    "from": "数据分析部",
    "to": "PM",
    "timestamp": "2026-03-24T15:30:00Z",
    "type": "response",
    "priority": "normal",
    "correlation_id": "TASK-20260324-001"
  },
  "body": {
    "action": "report_result",
    "params": {
      "task_id": "TASK-20260324-001",
      "status": "success",
      "result": {
        "output": "增长诊断报告已完成",
        "artifacts": ["growth_diagnosis_report.md"],
        "recommendations": [
          "优化落地页转化率",
          "增加复购激励",
          "提升客单价"
        ]
      },
      "metrics": {
        "duration": 1200,
        "token_usage": 15000
      }
    },
    "context": {
      "completion_time": "2026-03-24T15:30:00Z",
      "next_steps": null
    }
  },
  "footer": {
    "checksum": "def456ghi789",
    "signature": null
  }
}
```

#### 示例3: 部门 → PM (心跳)

```json
{
  "message_protocol": "CyberTeam-v3",
  "version": "1.0",
  "header": {
    "id": "HBT-20260324-001",
    "from": "数据分析部",
    "to": "PM",
    "timestamp": "2026-03-24T15:15:00Z",
    "type": "heartbeat",
    "priority": "low",
    "correlation_id": null
  },
  "body": {
    "action": "heartbeat",
    "params": {
      "status": "busy",
      "current_task": "TASK-20260324-001",
      "progress": 0.6
    },
    "context": {}
  },
  "footer": {
    "checksum": "ghi789jkl012",
    "signature": null
  }
}
```

### 10.2 校验和计算示例

```python
import hashlib
import json

def calculate_checksum(header, body):
    """计算消息校验和"""
    # 序列化
    header_str = json.dumps(header, sort_keys=True)
    body_str = json.dumps(body, sort_keys=True)

    # 拼接
    message = header_str + body_str

    # 计算 SHA-256
    checksum = hashlib.sha256(message.encode('utf-8')).hexdigest()

    return checksum

# 示例
header = {"id": "MSG-001", "from": "PM", "to": "数据分析部"}
body = {"action": "execute_task", "params": {...}}

checksum = calculate_checksum(header, body)
# 输出: "abc123def456..."
```

---

## 十一、实施指南

### 11.1 实施步骤

```yaml
Step 1: 创建目录结构
  mkdir -p ~/.cyberteam/messages/{in,out,draft,archive}
  mkdir -p ~/.cyberteam/messages/in/{_processing,_done}
  mkdir -p ~/.cyberteam/messages/out/{_sent,_failed}

Step 2: 实现消息发送
  - 定义消息格式
  - 序列化为 JSON
  - 计算校验和
  - 写入文件
  - 通知接收者

Step 3: 实现消息接收
  - 读取文件
  - 验证校验和
  - 反序列化
  - 处理消息
  - 发送 ACK

Step 4: 实现 CEO 路由
  - 读取消息
  - 查询路由表
  - 转发消息
  - 等待 ACK

Step 5: 测试验证
  - 发送测试消息
  - 验证消息格式
  - 验证传输流程
  - 验证错误处理
```

### 11.2 验证清单

- [ ] 消息格式正确
- [ ] 校验和计算正确
- [ ] 消息传输成功
- [ ] ACK/NACK 机制正常
- [ ] 超时重试机制正常
- [ ] 心跳机制正常
- [ ] 错误处理正常
- [ ] 性能满足要求

---

**协议版本**: v1.0
**创建日期**: 2026-03-24
**作者**: 架构专家 + 集成专家
**状态**: 最终规范

---

*本文档定义了 CyberTeam v3 的 Agent 通信协议 (CCP)，包括消息格式、传输机制、确认机制、错误处理、安全机制等，确保 Agent 间可靠通信。*
