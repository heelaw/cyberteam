# interfaces - 运营总监

## 输入 (Input)

| 来源 | 内容 |
|------|------|
| 增长总监 | 战略目标、季度KPI |
| CEO | 重大决策审批 |
| 数据部 | 数据分析报告 |

## 输出 (Output)

| 产出 | 接收方 |
|------|--------|
| 运营策略 | 各运营专家 |
| 运营报告 | 增长总监 |
| 资源需求 | 增长总监/CEO |

## 接口定义

### API Endpoint
```
POST /api/operations/director/task
GET  /api/operations/director/status
POST /api/operations/director/report
```

### 消息格式
```json
{
  "type": "task_assignment",
  "from": "operations_director",
  "to": "user_operations",
  "content": {
    "task": "用户留存优化",
    "KPI": "留存率提升10%",
    "deadline": "2026-03-31"
  }
}
```
