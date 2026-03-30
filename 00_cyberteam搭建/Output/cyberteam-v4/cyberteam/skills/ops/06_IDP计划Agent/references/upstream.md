# upstream - IDP计划Agent

## 上游依赖

| 上游 | 角色 | 接口 | 输入内容 |
|------|------|------|----------|
| 直属上级 | 直接上级 | 目标对齐/审批 | 岗位职责/发展期望 |
| HR | 政策指导 | IDP政策/资源 | 模板/预算/培训资源 |
| 运营总监 | 间接上级 | 团队发展 | 团队规划/人才梯队 |

---

## 输入文件标准格式

### 直属上级 → IDP计划Agent

```yaml
# 员工信息
employee:
  name: 员工姓名
  current_role: 当前岗位
  tenure: 司龄

# 岗位要求
role_requirements:
  - 能力1: 必备
  - 能力2: 加分
  - 能力3: 发展后具备

# 发展期望
development_expectations:
  short_term: 短期（1年内）目标
  medium_term: 中期（1-3年）目标
  long_term: 长期（3年+）目标
```

### HR → IDP计划Agent

```yaml
# IDP政策
policy:
  template: IDP模板版本
  review_frequency: 回顾频率（季度/半年）
  budget: 培训预算

# 资源清单
resources:
  training_courses:
    - 课程1
    - 课程2
  mentors:
    - 导师1: 专业领域
    - 导师2: 专业领域
```

---

## 决策请求格式

### IDP计划Agent → 直属上级

```json
{
  "type": "idp_approval",
  "agent": "IDP计划Agent",
  "employee": "员工姓名",
  "proposed_idp": {
    "short_term_goals": ["目标1", "目标2"],
    "learning_plan": "70-20-10分配",
    "resources_needed": ["导师A", "课程B"]
  },
  "approval_needed": "目标方向和资源确认"
}
```

---

*版本: v1.0 | 更新日期: 2026-03-26*