# interfaces - 运营总监

## 输入 (Input)

| 来源 | 内容 | 频率 |
|------|------|------|
| 增长总监 | 战略目标、季度KPI、预算 | 季度/月度 |
| CEO | 重大决策审批、资源调配 | 按需 |
| 数据团队 | 数据分析报告、指标看板 | 周报/实时 |
| 营销总监 | 渠道效果反馈、用户画像 | 双周 |

## 输出 (Output)

| 产出 | 接收方 | 频率 |
|------|--------|------|
| 运营策略 | 各运营专家 | 周/双周 |
| 运营报告 | 增长总监 | 周报 |
| 资源需求 | 增长总监/CEO | 按需 |
| 增长建议 | 营销总监 | 双周 |

## 接力区接口（与营销总监）

### 交接点：用户完成首次关键行为

**营销→运营 的交接信号**：
```json
{
  "type": "user_handoff",
  "trigger": "first_key_action_completed",
  "user_id": "xxx",
  "action": "first_purchase",
  "timestamp": "2026-03-25T10:00:00Z",
  "user_profile": {
    "acquisition_channel": "douyin",
    "first_session_duration": 120,
    "features_used": ["search", "cart"]
  }
}
```

**运营→营销 的反馈信号**：
```json
{
  "type": "channel_feedback",
  "channel": "douyin",
  "metrics": {
    "activation_rate": 0.45,
    "d7_retention": 0.22,
    "LTV_estimate": 158.0
  },
  "recommendation": "加大渠道B投放，减少渠道A"
}
```

## 协作循环接口

### 反馈闭环（运营→营销）
```json
{
  "type": "channel_optimization_feedback",
  "content": {
    "channel_a": {"CAC": 25, "LTV": 18, " verdict": "LTV < CAC，停止投放" },
    "channel_b": {"CAC": 30, "LTV": 120, "verdict": "优质渠道，加大投放" }
  }
}
```

### 需求闭环（营销→运营）
```json
{
  "type": "campaign_support_request",
  "content": {
    "campaign": "618大促",
    "expected_users": 1000000,
    "start_date": "2026-06-01",
    "request": "新手引导系统扩容、客服准备、召回策略"
  }
}
```

## API Endpoints

```
POST /api/operations/director/task          # 下达任务
GET  /api/operations/director/status         # 状态查询
POST /api/operations/director/report        # 提交报告
POST /api/operations/director/escalate     # 问题升级
GET  /api/operations/director/dashboard     # 数据看板
POST /api/operations/director/handoff      # 用户交接
```

## 协作节奏

| 协作方 | 节奏 | 形式 |
|--------|------|------|
| 增长总监 | 周报 + 月度战略会 | 1:1 + 团队会 |
| 各运营专家 | 每日站会 + 周复盘 | 团队会 |
| 营销总监 | 双周协作会 | 同步会 |
| 产品部 | 按需 | 评审会 |
| 数据团队 | 周数据评审 | 数据会 |

---

*版本: v2.0 | 更新日期: 2026-03-25*
