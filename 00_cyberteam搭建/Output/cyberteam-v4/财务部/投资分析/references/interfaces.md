# 投资分析 接口协议

## 输入接口

### 来自CFO/CEO
| 消息类型 | 内容 | 触发条件 |
|---------|------|----------|
| 评估任务 | 投资项目评估任务 | 按需 |
| 尽调任务 | 尽职调查任务 | 按需 |
| 投后任务 | 投后管理跟踪 | 按需 |

### 来自战略部
| 消息类型 | 内容 | 触发条件 |
|---------|------|----------|
| 战略优先级 | 战略方向和优先级 | 年度战略 |
| 标的推荐 | 潜在投资标的 | 按需 |
| 协同评估 | 业务协同价值评估 | 按需 |

### 来自业务BG
| 消息类型 | 内容 | 触发条件 |
|---------|------|----------|
| 投资提案 | 自业务部门提交的投资想法 | 按需 |
| 立项支持 | 投资项目立项申请 | 按需 |

## 输出接口

### 流向CFO
| 消息类型 | 内容 | 频率 |
|---------|------|------|
| 评估报告 | 投资项目评估报告 | 按需 |
| 尽调报告 | 尽职调查报告 | 按需 |
| 投后报告 | 投后管理跟踪报告 | 季度 |
| 风险预警 | 投资风险预警 | 实时 |

### 流向战略部
| 消息类型 | 内容 | 频率 |
|---------|------|------|
| 财务意见 | 投资标的财务评估 | 按需 |
| 协同分析 | 业务协同价值量化 | 按需 |

### 流向各BG
| 消息类型 | 内容 | 频率 |
|---------|------|------|
| 评估反馈 | 投资项目财务意见 | 按需 |
| ROI建议 | 投资回报优化建议 | 按需 |

### 流向预算管理
```json
{
  "data_type": "资本性支出预算",
  "period": "2026",
  "investment_projects": [
    {
      "project_name": "XX项目",
      "investment_type": "股权投资",
      "amount": 5000000,
      "timeline": "2026-Q2",
      "expected_roi": 25,
      "expected_irr": 20
    }
  ],
  "total_capex": 15000000
}
```

## 数据格式

### 投资评估报告
```json
{
  "report_type": "投资项目评估",
  "project_name": "XX公司股权收购",
  "investment_amount": 50000000,
  "shareholding": 30,
  "valuation_method": "DCF + Comparable",
  "valuation_range": {
    "optimistic": 60000000,
    "base": 50000000,
    "pessimistic": 40000000
  },
  "financial_projections": {
    "year1_revenue": 20000000,
    "year2_revenue": 35000000,
    "year3_revenue": 50000000,
    "year5_revenue": 80000000
  },
  "returns_analysis": {
    "irr": 22.5,
    "npv": 15000000,
    "roi": 35,
    "payback_period": 3.5
  },
  "risk_factors": [
    "市场风险：行业增速放缓",
    "运营风险：团队稳定性",
    "整合风险：文化融合挑战"
  ],
  "sensitivity_analysis": {
    "key_variable": "收入增速",
    "irr_range": "18-28%"
  },
  "recommendation": "建议批准",
  "conditions": ["设置对赌条款", "分阶段投资"]
}
```

### 尽职调查报告
```json
{
  "report_type": "财务尽职调查",
  "target_company": "XX公司",
  "diligence_scope": ["财务报表", "税务合规", "资产负债"],
  "key_findings": {
    "revenue_quality": "中等",
    "profitability": "良好",
    "cash_flow": "一般",
    "debt_level": "可控"
  },
  "adjustments": [
    {
      "item": "收入确认调整",
      "impact": -5000000,
      "description": "提前确认收入需调减"
    }
  ],
  "adjusted_ebitda": 15000000,
  "recommended_valuation": 45000000,
  "main_risks": [
    "客户集中度高（TOP3占比60%）",
    "应收账款周转天数较长"
  ],
  "due_diligence_conclusion": "风险可控，建议推进"
}
```

### 投后跟踪报告
```json
{
  "report_type": "投后管理跟踪",
  "investment_name": "XX公司股权",
  "report_date": "2026-03-25",
  "period": "2026-Q1",
  "performance": {
    "revenue_actual": 5200000,
    "revenue_target": 5000000,
    "revenue_achievement": 104,
    "profit_actual": 800000,
    "profit_target": 1000000,
    "profit_achievement": 80
  },
  "milestones": [
    {"milestone": "产品上线", "status": "已完成", "date": "2026-01"},
    {"milestone": "客户导入", "status": "进行中", "date": "2026-Q2"}
  ],
  "risk_alerts": ["毛利率低于预期"],
  "recommendation": "继续持有，加强运营管控"
}
```

### 投资风险预警
```json
{
  "alert_type": "investment_risk",
  "severity": "high",
  "investment_name": "XX公司股权",
  "risk_indicator": "财务指标恶化",
  "description": "Q1收入仅完成目标的70%，现金消耗速度快于预期",
  "actual_vs_budget": {
    "revenue": {"actual": 3500000, "budget": 5000000, "variance": -30},
    "cash_burn": {"actual": 2000000, "budget": 1500000, "variance": 33}
  },
  "recommended_action": "启动投后干预，要求管理层出具整改计划"
}
```
