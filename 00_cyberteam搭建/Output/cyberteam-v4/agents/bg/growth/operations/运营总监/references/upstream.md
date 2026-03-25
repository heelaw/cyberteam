# upstream - 运营总监

## 上游依赖

| 上游 | 角色 | 接口 | 输入文件 |
|------|------|------|----------|
| 增长总监 | 直接上级 | 战略目标/预算审批/方案决策 | `projects/{project_id}/context/business_context.md` |
| CEO | 最终上级 | 重大决策审批 | `projects/{project_id}/decisions/decision.md` |
| 产品BG | 协作方 | 产品需求对接/功能排期 | `projects/{project_id}/context/product_roadmap.md` |
| 数据团队 | 协作方 | 数据分析/指标定义 | `projects/{project_id}/context/data_*.md` |
| 营销总监 | 协作方 | 渠道效果/用户画像 | `projects/{project_id}/context/channel_*.md` |

---

## 输入文件标准格式

### 增长总监 → 运营总监

```yaml
# projects/{project_id}/context/business_context.md

## 项目信息
project_name: XXX业务运营诊断
project_type: 案例分析/策略制定/危机处理/常规运营

## 战略目标
objective: 在Q3实现流水1000万
success_metrics:
  - 指标1: 数值
  - 指标2: 数值

## 约束条件
constraints:
  budget: 100万
  timeline: Q3结束前
  headcount: 现有团队

## 业务数据
current_metrics:
  DAU: X
  MAU: X
  留存率(次日): X%
  转化率: X%
  LTV: X元
  CAC: X元
```

### 数据团队 → 运营总监

```yaml
# projects/{project_id}/context/data_analysis.md

## 分析结论
findings:
  - 发现1: 描述 + 数据支撑
  - 发现2: 描述 + 数据支撑

## 建议
recommendations:
  - 建议1: 描述
  - 建议2: 描述

## 原始数据
raw_data: 附件或链接
```

---

## 决策请求格式

### 增长总监 → 运营总监

```json
{
  "type": "decision_request",
  "project_id": "proj_20260325_001",
  "requestor": "增长总监",
  "decision_needed": "在下辉子账号变现方案选择",
  "options_count": 3,
  "decision_deadline": "2026-03-28T18:00:00Z",
  "materials": [
    "projects/proj_20260325_001/decisions/options.md"
  ]
}
```

### 运营总监 → 增长总监

```json
{
  "type": "decision_proposal",
  "project_id": "proj_20260325_001",
  "from": "运营总监",
  "proposal": "推荐方案B（直播带货+电商）",
  "options": [
    {"id": "A", "name": "广告为主", "pros": "...", "cons": "..."},
    {"id": "B", "name": "直播带货+电商", "pros": "...", "cons": "..."},
    {"id": "C", "name": "线下活动+周边", "pros": "...", "cons": "..."}
  ],
  "recommendation": "B",
  "confidence": "80%",
  "risk": "用户画像偏男粉，转化率可能低于预期"
}
```

---

## 重大升级条件

| 情况 | 触发条件 | 升级内容 |
|------|----------|----------|
| 战略目标偏离 | 核心指标偏差>30% | 重新对齐战略 |
| 资源严重不足 | 无法支撑核心任务 | 资源申请或目标调整 |
| 跨部门无法协调 | 阻塞>3天无解 | 增长总监介入 |

---

*版本: v2.0 | 更新日期: 2026-03-25*
