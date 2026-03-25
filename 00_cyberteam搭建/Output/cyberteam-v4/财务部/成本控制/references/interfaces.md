# 成本控制 接口协议

## 输入接口

### 来自CFO
| 消息类型 | 内容 | 触发条件 |
|---------|------|----------|
| 分析任务 | 成本结构分析任务 | 定期/按需 |
| 降本需求 | 降本增效任务下达 | 战略要求 |
| ROI评估 | 投资项目成本评估 | 按需 |

### 来自各BG
| 消息类型 | 内容 | 触发条件 |
|---------|------|----------|
| 成本咨询 | 产品/项目成本核算 | 日常 |
| 采购评估 | 新采购成本效益评估 | 采购前 |
| 降本提案 | 降本增效建议提交 | 日常 |

## 输出接口

### 流向CFO
| 消息类型 | 内容 | 频率 |
|---------|------|------|
| 分析报告 | 成本结构分析报告 | 季度 |
| 降本建议 | 降本增效方案 | 按需 |
| ROI评估 | 投资回报评估报告 | 按需 |
| 预警通知 | 异常成本预警 | 实时 |

### 流向各BG
| 消息类型 | 内容 | 频率 |
|---------|------|------|
| 成本反馈 | 产品/项目成本核算结果 | 按需 |
| 优化建议 | 成本优化建议 | 日常 |
| 预警提醒 | 成本异常预警 | 实时 |

### 流向预算管理
```json
{
  "data_type": "成本核算数据",
  "period": "2026-Q1",
  "department": "产品BG",
  "product": "核心产品A",
  "cost_breakdown": {
    "直接材料": 5000000,
    "直接人工": 3000000,
    "制造费用": 2000000,
    "分摊管理费用": 1000000
  },
  "total_cost": 11000000,
  "unit_cost": 110,
  "suggestions": ["建议优化制造费用结构"]
}
```

## 数据格式

### 成本核算报告
```json
{
  "report_type": "产品成本核算",
  "product_name": "产品A",
  "period": "2026-Q1",
  "cost_structure": {
    "direct_material": 5000000,
    "direct_labor": 3000000,
    "manufacturing_overhead": 2000000,
    "allocated_expense": 1000000
  },
  "total_cost": 11000000,
  "unit_cost": 110,
  "cost_per_unit_trend": "环比-3.2%"
}
```

### ROI评估报告
```json
{
  "project_name": "智能化升级项目",
  "investment_amount": 2000000,
  "annual_benefits": {
    "cost_saving": 500000,
    "efficiency_gain": 300000,
    "quality_improvement": 200000
  },
  "total_annual_benefit": 1000000,
  "roi": 50,
  "payback_period": 2.0,
  "npv": 1500000,
  "recommendation": "批准"
}
```

### 降本增效建议
```json
{
  "opportunity_id": "COST-001",
  "department": "技术BG",
  "current_cost": 5000000,
  "proposed_solution": "采用云原生架构",
  "expected_saving": 1500000,
  "saving_rate": 30,
  "implementation_cost": 200000,
  "net_saving": 1300000,
  "timeline": "6个月",
  "risk_level": "中",
  "recommendation": "建议推进"
}
```

### 成本预警
```json
{
  "alert_type": "cost_overrun",
  "severity": "warning",
  "department": "增长BG",
  "cost_item": "市场费用",
  "budget": 1000000,
  "actual": 1250000,
  "variance": 25,
  "variance_amount": 250000,
  "root_cause": "活动规模扩大",
  "recommended_action": "评估效果，确认是否追加预算"
}
```
