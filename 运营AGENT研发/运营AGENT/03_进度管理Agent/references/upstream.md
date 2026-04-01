# upstream - 进度管理Agent

## 上游依赖

| 上游 | 角色 | 接口 | 输入内容 |
|------|------|------|----------|
| 运营总监 | 直接上级 | 项目授权/资源协调 | 项目范围/预算/团队 |
| 增长总监 | 间接上级 | 战略目标/里程碑 | KPI/验收标准 |
| 产品部 | 协作方 | 需求变更/功能验收 | PRD/验收标准 |
| 技术部 | 协作方 | 技术方案/实现进度 | 技术方案/排期 |

---

## 输入文件标准格式

### 运营总监 → 进度管理Agent

```yaml
# 项目信息
project:
  name: 项目名称
  start_date: 开始日期
  end_date: 截止日期
  budget: 预算

# 里程碑
milestones:
  - name: 里程碑1
    date: 日期
    criteria: 验收标准
  - name: ...

# 资源
resources:
  team: 团队成员
  budget: 预算余额
```

### 产品部 → 进度管理Agent

```yaml
# 需求变更
changes:
  - id: 变更ID
    description: 变更描述
    impact: 影响分析
    priority: 优先级

# 验收进度
acceptance:
  - feature: 功能名称
    status: 待验收/通过/拒绝
    date: 日期
```

---

## 决策请求格式

### 进度管理Agent → 运营总监

```json
{
  "type": "risk_escalation",
  "agent": "进度管理Agent",
  "project": "项目名称",
  "risk": {
    "description": "关键路径任务延期",
    "probability": "高",
    "impact": "导致整体延期10天",
    "mitigation": "增加资源/压缩非关键路径"
  },
  "decision_needed": "批准风险应对方案"
}
```

---

*版本: v1.0 | 更新日期: 2026-03-26*