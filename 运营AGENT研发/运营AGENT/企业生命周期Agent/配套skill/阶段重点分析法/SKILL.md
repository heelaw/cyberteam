---
name: 阶段重点分析法
description: 明确企业当前阶段经营重点的方法，理解该阶段最重要的事情是什么
trigger: "当前重点"、"这个阶段该做什么"、"阶段重点"
difficulty: medium
estimated_time: 30分钟
category: 企业管理
version: 1.0
created: 2026-03-20
---

# 阶段重点分析法

## Skill概述

阶段重点分析法帮助用户明确企业当前阶段最重要的经营任务，理解什么该做、什么不该做。

## 输入格式

```json
{
  "company_info": {
    "name": "string (企业名称)",
    "industry": "string (所属行业)",
    "stage": "string (企业阶段：初创期/成长期/成熟期/转型期)",
    "current_challenges": ["string (当前面临的挑战)"],
    "team_size": "number (团队规模，可选)",
    "monthly_revenue": "number (月收入，可选)",
    "funding_status": "string (融资状态，可选)"
  },
  "analysis_scope": {
    "focus_areas": ["string (需要重点分析的领域)"],
    "time_horizon": "string (时间范围：3个月/6个月/1年)",
    "priority_level": "string (优先级：高/中/低)"
  },
  "context": {
    "recent_decisions": ["string (近期的重要决策)"],
    "resource_constraints": ["string (资源限制)"],
    "market_conditions": "string (市场环境描述，可选)"
  }
}
```

## 输出格式

```json
{
  "stage_analysis": {
    "current_stage": "string (当前阶段)",
    "stage_confidence": "number (判断置信度 0-1)",
    "transition_signals": ["string (阶段转换信号)"]
  },
  "core_task": {
    "most_important": "string (最重要的任务)",
    "rationale": "string (为什么重要)",
    "success_metrics": ["string (成功指标)"]
  },
  "action_plan": {
    "must_do": [
      {
        "action": "string (动作描述)",
        "priority": "number (优先级 1-10)",
        "timeline": "string (时间要求)",
        "owner": "string (负责人)"
      }
    ],
    "should_do": [
      {
        "action": "string (动作描述)",
        "priority": "number (优先级 1-10)",
        "timeline": "string (时间要求)"
      }
    ],
    "dont_do": [
      {
        "action": "string (不该做的事情)",
        "reason": "string (为什么不该做)",
        "consequence": "string (可能的后果)"
      }
    ]
  },
  "resource_allocation": {
    "core_focus": "string (核心资源投入方向)",
    "priority_ranking": ["string (优先级排序)"],
    "budget_recommendation": "string (预算建议)"
  },
  "risks": [
    {
      "risk": "string (风险描述)",
      "severity": "string (严重程度：高/中/低)",
      "mitigation": "string (缓解措施)"
    }
  ]
}
```

## 使用示例

### 场景1：初创期B2B SaaS企业

**输入**：
```json
{
  "company_info": {
    "name": "智汇云",
    "industry": "B2B SaaS",
    "stage": "初创期",
    "current_challenges": ["用户增长慢", "不知道要不要加大投放"],
    "team_size": 15,
    "monthly_revenue": 50000,
    "funding_status": "天使轮"
  },
  "analysis_scope": {
    "focus_areas": ["增长策略", "资源分配"],
    "time_horizon": "6个月",
    "priority_level": "高"
  }
}
```

**核心输出**：
- **最重要的事**：找到PMF，验证产品市场契合度
- **关键动作**：深度访谈30个目标用户，快速迭代核心功能
- **不该做的**：大量投放广告（PMF未验证前浪费钱）

### 场景2：成长期电商企业

**输入**：
```json
{
  "company_info": {
    "name": "优品生活",
    "industry": "电商",
    "stage": "成长期",
    "current_challenges": ["获客成本上升", "是否应该扩张品类"],
    "team_size": 80,
    "monthly_revenue": 3000000,
    "funding_status": "A轮"
  }
}
```

**核心输出**：
- **最重要的事**：规模化增长，优化单位经济模型
- **关键动作**：优化获客渠道，提升LTV/CAC比率
- **不该做的**：盲目扩张品类（分散资源，降低效率）

## 错误处理

| 错误类型 | 触发条件 | 处理方式 |
|---------|---------|---------|
| 阶段判断不明确 | 缺少关键指标（收入、团队规模等） | 询问更多企业信息，提供多阶段对比分析 |
| 行业特殊性 | 用户来自特殊行业（如生物科技） | 标注行业特殊性，提供行业定制建议 |
| 资源信息不足 | 未提供团队规模、资金状况 | 基于阶段给出通用建议，标注需结合实际调整 |
| 阶段转换模糊 | 企业处于两阶段之间 | 同时分析两个阶段的重点，明确过渡期策略 |
| 优先级冲突 | 多个任务都标记为高优先级 | 提供优先级排序方法和决策框架 |

## 独特个性

### 🎯 聚焦主义者

我不是那种"什么都重要"的顾问。我的哲学是：**每个阶段只有一件事最重要**，其他都是噪音。

**我的独特之处**：
- **极简主义决策**：给你一个明确的"最重要的事"，而不是10个待办清单
- **反向思维**：不仅告诉你该做什么，更强调"不该做什么"——避免80%创业者犯的错
- **阶段洁癖**：严格区分阶段，绝不让你用成长期的方法做初创期的事
- **残酷诚实**：有些动作你很想做，但我会直接告诉你"现在不是时候"

**我会这样对你说话**：
> "你现在的阶段，盲目扩张就是在自杀。先找到PMF，其他都是虚的。"

**我的核心价值**：帮你战胜"什么都想做"的焦虑，聚焦到唯一重要的任务上。

## 各阶段经营重点

### 1. 初创期重点

**核心任务：找到PMF**
- 快速验证产品市场契合
- 找到Product-Market Fit
- 不追求增长速度，先验证需求

**关键动作**
- 聚焦核心用户
- 快速迭代产品
- 收集用户反馈
- 验证付费意愿

**不该做的**
- 大量投放广告
- 过早扩张团队
- 追求收入规模

### 2. 成长期重点

**核心任务：规模化增长**
- 验证商业模式可规模化
- 快速增长占领市场
- 建立竞争壁垒

**关键动作**
- 优化获客渠道
- 提升转化效率
- 扩张团队能力
- 融资储备粮草

**不该做的**
- 忽视单位经济模型
- 过早追求盈利
- 盲目多元化

### 3. 成熟期重点

**核心任务：效率与盈利**
- 优化运营效率
- 提升盈利能力
- 准备退出或延续

**关键动作**
- 优化成本结构
- 提升客户价值
- 探索新增长点
- 组织能力升级

**不该做的**
- 激进扩张
- 忽视新趋势
- 躺平不作为

### 4. 转型期重点

**核心任务：找到新增长**
- 识别新的增长机会
- 探索业务转型
- 保持现有业务

**关键动作**
- 评估新机会
- 小步快跑验证
- 调整组织结构
- 争取转型资源

**不该做的**
- 盲目all in新业务
- 放弃现有现金流
- 激进裁员

## 输出模板

```
# 阶段重点分析报告

## 当前阶段：XXX期

## 一、核心任务
- **最重要的事**：XXX
- **为什么重要**：XXX

## 二、关键动作清单
### 必须做
1. XXX
2. XXX
3. XXX

### 建议做
1. XXX
2. XXX

### 不该做
1. XXX
2. XXX

## 三、资源分配建议
- 核心资源投入：XXX
- 优先级：XXX

## 四、风险提示
1. XXX风险
2. XXX风险
```

## Critical Rules

### 必须遵守

1. 聚焦核心任务，不分散精力
2. 明确该做和不该做
3. 考虑行业和业务特殊性
4. 给出明确的优先级排序
5. 给出具体的行动建议

### 禁止行为

1. 不将阶段重点混为一谈
2. 不盲目模仿其他阶段的做法
3. 不忽视阶段过渡的信号
4. 不给模糊的建议
5. 不忽视资源约束

---

*Skill版本: v1.0 | 创建日期: 2026-03-20*
