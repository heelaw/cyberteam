# upstream - 人力盘点Agent

## 上游依赖

| 上游 | 角色 | 接口 | 输入内容 |
|------|------|------|----------|
| HR总监 | 直接上级 | 盘点任务/政策指导 | 盘点范围/标准/时间 |
| 运营总监 | 间接上级 | 团队需求 | 人力需求/配置建议 |
| 财务团队 | 协作方 | 成本数据 | 人力成本/预算数据 |
| 数据团队 | 协作方 | 绩效数据 | 绩效系统数据 |

---

## 输入文件标准格式

### HR总监 → 人力盘点Agent

```yaml
# 盘点任务
inventory_task:
  scope: 全公司/部门/团队
  criteria: 评估标准
  timeline: 盘点时间表
  output_required: 九宫格/IDP/人效报告

# 评估标准
evaluation_criteria:
  performance_metrics:
    - 目标完成度
    - 工作质量
  potential_metrics:
    - 学习速度
    - 成长意愿
    - 适应能力
```

### 运营总监 → 人力盘点Agent

```yaml
# 团队信息
team:
  name: 团队名称
  headcount: 当前人数
  open_positions: 空缺职位
  planned_headcount: 规划人数

# 人力需求
requirements:
  - role: 岗位
    urgency: 紧急程度
    reason: 需求原因
```

---

## 决策请求格式

### 人力盘点Agent → HR总监

```json
{
  "type": "talent_inventory_report",
  "agent": "人力盘点Agent",
  "scope": "增长事业部",
  "nine_box_distribution": {
    "stars": 15,
    "core": 45,
    "underperformers": 10
  },
  "key_findings": ["高潜人才流失风险", "关键岗位备份不足"],
  "recommendations": ["制定继任计划", "调整激励方案"]
}
```

---

*版本: v1.0 | 更新日期: 2026-03-26*