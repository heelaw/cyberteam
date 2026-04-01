# upstream - 时间管理Agent

## 上游依赖

| 上游 | 角色 | 接口 | 输入内容 |
|------|------|------|----------|
| 运营总监 | 直接上级 | 任务下达/目标同步 | 任务清单/OKR/优先级 |
| 增长总监 | 间接上级 | 战略目标分解 | KPI/里程碑 |
| 产品部 | 协作方 | 任务依赖/截止日期 | PRD/排期表 |
| 数据团队 | 协作方 | 分析需求 | 数据需求清单 |

---

## 输入文件标准格式

### 运营总监 → 时间管理Agent

```yaml
# 任务清单
tasks:
  - name: 任务名称
    deadline: 截止日期
    priority: P0/P1/P2/P3
    estimated_hours: 预估工时
    dependencies: []
  - name: ...

# 目标对齐
objectives:
  - 本周核心目标
  - 关键成果指标
  - 约束条件
```

### 产品部 → 时间管理Agent

```yaml
# 任务依赖
dependencies:
  - task: 任务名称
    blocker: 阻塞任务
    unblock_date: 解锁日期
  - ...

# 排期信息
sprint_end: 迭代结束日期
milestones:
  - 里程碑名称: 日期
```

---

## 决策请求格式

### 时间管理Agent → 运营总监

```json
{
  "type": "conflict_resolution",
  "agent": "时间管理Agent",
  "issue": "任务优先级冲突",
  "conflicting_tasks": [
    {"name": "任务A", "deadline": "今天", "priority": "P0"},
    {"name": "任务B", "deadline": "今天", "priority": "P1"}
  ],
  "options": ["先做A后做B", "同时并行", "申请延期B"],
  "recommendation": "先做A，向B申请延期"
}
```

---

*版本: v1.0 | 更新日期: 2026-03-26*