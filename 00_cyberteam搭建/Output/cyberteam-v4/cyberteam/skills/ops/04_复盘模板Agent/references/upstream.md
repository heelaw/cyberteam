# upstream - 复盘模板Agent

## 上游依赖

| 上游 | 角色 | 接口 | 输入内容 |
|------|------|------|----------|
| 运营总监 | 直接上级 | 复盘任务下达 | 复盘范围/参与人员/时间 |
| 增长总监 | 间接上级 | 战略复盘需求 | 战略目标达成分析 |
| 产品部 | 协作方 | 产品数据提供 | 功能使用数据/反馈 |
| 数据团队 | 协作方 | 数据分析支持 | KPI数据/漏斗分析 |

---

## 输入文件标准格式

### 运营总监 → 复盘模板Agent

```yaml
# 复盘任务
retro_task:
  type: 项目复盘/活动复盘/周复盘/月复盘
  scope: 复盘范围
  participants: 参与人员
  date: 复盘日期

# 项目背景
project:
  name: 项目名称
  original_goals:
    - 目标1
    - 目标2
  key_milestones:
    - 里程碑1
    - 里程碑2
  kpis:
    - 指标1: 目标值
    - 指标2: 目标值
```

### 数据团队 → 复盘模板Agent

```yaml
# 数据支持
actual_results:
  kpis:
    - 指标1: 实际值 vs 目标值
    - 指标2: 实际值 vs 目标值

findings:
  - 发现1: 描述
  - 发现2: 描述

user_feedback:
  - 正面反馈
  - 负面反馈
```

---

## 决策请求格式

### 复盘模板Agent → 运营总监

```json
{
  "type": "retro_summary",
  "agent": "复盘模板Agent",
  "retro_type": "项目复盘",
  "key_findings": {
    "successes": ["成功因素1", "成功因素2"],
    "failures": ["失败因素1", "失败因素2"],
    "action_items": ["改进行动1", "改进行动2"]
  },
  "recommendation": "建议沉淀的方法论"
}
```

---

*版本: v1.0 | 更新日期: 2026-03-26*