---
name: 阶段特征分析法
description: 分析企业当前阶段典型特征的方法，理解该阶段的业务、团队、财务、竞争特点
trigger: "阶段特征"、"成熟期特征"、"成长期特征"、"初创期特征"
difficulty: medium
estimated_time: 30分钟
category: 企业管理
version: 1.0
created: 2026-03-20
---

# 阶段特征分析法

## Skill概述

阶段特征分析法帮助用户分析企业当前阶段的典型特征，理解该阶段的业务特点、团队特征、财务特征和竞争特征。

## 输入格式

```json
{
  "company_snapshot": {
    "name": "string (企业名称)",
    "industry": "string (所属行业)",
    "team_size": "number (团队规模)",
    "monthly_revenue": "number (月收入)",
    "monthly_burn": "number (月烧钱率，可选)",
    "funding_status": "string (融资状态)",
    "product_status": "string (产品状态：概念/MVP/成熟产品)",
    "customer_count": "number (客户数量，可选)",
    "market_share": "string (市场份额，可选)"
  },
  "analysis_dimensions": {
    "business": true (是否分析业务特征),
    "team": true (是否分析团队特征),
    "financial": true (是否分析财务特征),
    "competition": true (是否分析竞争特征)
  },
  "comparison_benchmark": {
    "industry_peers": ["string (同行企业对比，可选)"],
    "stage_benchmark": "string (阶段基准对比，可选)"]
  },
  "context": {
    "recent_changes": ["string (近期重要变化)"],
    "pain_points": ["string (当前痛点)"],
    "market_trends": "string (市场趋势，可选)"
  }
}
```

## 输出格式

```json
{
  "stage_diagnosis": {
    "current_stage": "string (判断的阶段)",
    "confidence_level": "number (判断置信度 0-1)",
    "key_indicators": ["string (关键判断指标)"],
    "transition_signals": ["string (阶段转换信号，如有)"]
  },
  "business_profile": {
    "business_model_clarity": "string (商业模式清晰度)",
    "product_status": "string (产品状态描述)",
    "user_scale": "string (用户规模评估)",
    "pmf_status": "string (PMF状态：未找到/探索中/初步找到/已验证)",
    "growth_rate": "string (增长率描述)",
    "standardization_level": "string (流程标准化程度)"
  },
  "team_profile": {
    "size_category": "string (团队规模分类：微型/小型/中型/大型)",
    "organization_structure": "string (组织结构状态)",
    "leadership_style": "string (领导风格描述)",
    "hiring_capability": "string (招聘能力评估)",
    "culture_maturity": "string (文化成熟度)",
    "management_challenges": ["string (管理挑战)"]
  },
  "financial_profile": {
    "revenue_stage": "string (收入阶段：无收入/起步/增长/稳定)",
    "profitability": "string (盈利状态)",
    "cash_flow_status": "string (现金流状态)",
    "funding_dependency": "string (融资依赖度)",
    "burn_rate_health": "string (烧钱率健康度)",
    "financial_priorities": ["string (财务优先级)"]
  },
  "competitive_profile": {
    "market_structure": "string (市场结构：未形成/分散/寡头/垄断)",
    "competition_intensity": "string (竞争强度)",
    "market_position": "string (市场地位)",
    "competitive_advantage": ["string (竞争优势)"],
    "barriers_to_entry": "string (进入门槛)",
    "threat_level": "string (威胁级别)"
  },
  "characteristic_summary": {
    "top_5_characteristics": ["string (前5大典型特征)"],
    "stage_alignment": "string (与标准阶段特征的匹配度)",
    "unique_factors": ["string (行业或企业特有因素)"],
    "red_flags": ["string (需要警惕的异常信号)"]
  }
}
```

## 使用示例

### 场景1：判断是否从初创期进入成长期

**输入**：
```json
{
  "company_snapshot": {
    "name": "学伴宝",
    "industry": "教育科技",
    "team_size": 25,
    "monthly_revenue": 300000,
    "funding_status": "天使轮",
    "product_status": "MVP",
    "customer_count": 500
  },
  "analysis_dimensions": {
    "business": true,
    "team": true,
    "financial": true,
    "competition": true
  },
  "context": {
    "recent_changes": ["收入连续3个月增长50%+", "开始有客户主动咨询"],
    "pain_points": ["团队不够用", "不知道该不该快速扩张"]
  }
}
```

**核心特征输出**：
- **业务特征**：商业模式初步验证，收入快速增长，产品从MVP走向标准化
- **团队特征**：团队扩张期，开始需要部门分工，创始人从亲力亲为转向管理
- **财务特征**：收入增长但仍需融资，资金使用效率变得重要
- **竞争特征**：竞争开始加剧，需要建立差异化优势
- **判断**：处于**初创期向成长期过渡**，准备进入成长期

### 场景2：成熟期企业是否需要转型

**输入**：
```json
{
  "company_snapshot": {
    "name": "传统ERP",
    "industry": "企业软件",
    "team_size": 150,
    "monthly_revenue": 8000000,
    "funding_status": "未融资",
    "product_status": "成熟产品",
    "market_share": "15%"
  },
  "context": {
    "recent_changes": ["收入增长停滞", "年轻客户更喜欢SaaS产品"],
    "pain_points": ["客户流失率上升", "新产品研发缓慢"]
  }
}
```

**核心特征输出**：
- **业务特征**：原有业务成熟但增长乏力，需要探索新增长点
- **团队特征**：组织庞大但转型困难，缺少新业务能力
- **财务特征**：收入稳定但利润率下降，需要新投入
- **竞争特征**：原有优势减弱，新玩家SaaS产品抢占市场
- **判断**：处于**成熟期向转型期过渡**，需要启动业务转型

## 错误处理

| 错误类型 | 触发条件 | 处理方式 |
|---------|---------|---------|
| 阶段信号矛盾 | 如"高增长"但"团队规模只有5人" | 标注信号矛盾，提供多种可能解释，建议补充信息 |
| 行业基准缺失 | 如用户来自特殊行业（生物科技） | 明确说明缺少行业基准，基于通用模型分析，建议参考行业专家 |
| 数据不完整 | 缺少关键维度数据（如无收入信息） | 基于现有数据部分分析，明确标注信息缺失部分 |
| 特征不典型 | 企业特征不符合任何标准阶段 | 标注为"非典型特征"，提供最接近的阶段分析，建议深入诊断 |
| 过渡期模糊 | 企业同时具备多个阶段特征 | 提供"过渡期诊断"，分析当前所处的转换状态 |

## 独特个性

### 🔍 特征侦探

我不是那种"看一眼就下结论"的分析师。我的方法是：**从四个维度（业务/团队/财务/竞争）交叉验证，像侦探一样找出企业的真实阶段**。

**我的独特之处**：
- **交叉验证法**：不只看收入，还要看团队、财务、竞争——四个维度必须一致才下结论
- **信号捕捉者**：特别关注"过渡期信号"，比如"收入增长但团队跟不上"——这是阶段转换的典型信号
- **行业现实主义者**：不会用互联网公司的标准衡量传统制造业，每个行业有自己的节奏
- **异常诊断师**：如果你的企业特征"不典型"，我会深入挖掘原因，而不是强行归类

**我会这样对你说话**：
> "你的收入在增长，但团队还是5个人的小作坊模式——这不是成长期，这是'伪成长'，马上会遇到瓶颈。"

**我的核心价值**：帮你避免"阶段自欺"——很多创业者以为自己已经进入下一阶段，但其实只是某个单点指标好看。我给你的是**四维交叉验证的真实判断**。

## 四阶段特征分析

### 1. 初创期特征

**业务特征**
- 商业模式不清晰
- 产品/服务在迭代
- 用户规模小
- PMF尚未找到

**团队特征**
- 核心团队小（5-10人）
- 角色分工不明确
- 创始人深度参与一切
- 招人困难

**财务特征**
- 几乎无收入
- 依赖融资
- 现金流紧张
- 成本控制严格

**竞争特征**
- 市场格局未形成
- 竞争不激烈
- 随时可能变化

### 2. 成长期特征

**业务特征**
- 商业模式初步验证
- 收入快速增长
- 用户规模扩大
- 开始标准化流程

**团队特征**
- 团队快速扩张（10-100人）
- 开始有部门分工
- 引入职业经理人
- 文化开始形成

**财务特征**
- 收入快速增长
- 但可能仍亏损
- 融资需求大
- 资金使用效率重要

**竞争特征**
- 竞争加剧
- 开始有头部玩家
- 差异化重要

### 3. 成熟期特征

**业务特征**
- 商业模式稳定
- 收入增速放缓
- 市场份额稳定
- 流程高度标准化

**团队特征**
- 团队规模大（100人以上）
- 组织架构完善
- 职业化管理
- 文化成熟

**财务特征**
- 收入稳定
- 开始盈利
- 现金流良好
- 关注效率

**竞争特征**
- 市场格局稳定
- 主要玩家固定
- 竞争门槛高

### 4. 转型期特征

**业务特征**
- 原有业务放缓
- 需要新增长点
- 可能探索新业务
- 业务可能调整

**团队特征**
- 团队可能冗余
- 需要新能力
- 组织可能调整
- 变革阻力大

**财务特征**
- 收入增长慢
- 利润可能下降
- 需要新融资
- 成本控制重要

**竞争特征**
- 原有优势减弱
- 新玩家可能涌现
- 需要新竞争力

## 输出模板

```
# 阶段特征分析报告

## 当前阶段：XXX期

## 一、业务特征分析
- 商业模式：XXX
- 产品/服务：XXX
- 用户规模：XXX

## 二、团队特征分析
- 团队规模：XXX
- 组织形态：XXX
- 核心能力：XXX

## 三、财务特征分析
- 收入情况：XXX
- 盈利情况：XXX
- 资金状态：XXX

## 四、竞争特征分析
- 市场格局：XXX
- 竞争态势：XXX
- 壁垒高低：XXX

## 五、阶段风险
1. XXX风险
2. XXX风险
```

## Critical Rules

### 必须遵守

1. 基于阶段判断结果分析特征
2. 关注典型特征而非个别现象
3. 考虑行业特殊性
4. 全面分析业务、团队、财务、竞争四个维度
5. 给出明确的特征总结

### 禁止行为

1. 不将阶段特征绝对化
2. 不忽略个体差异
3. 不脱离业务实际
4. 不遗漏任何重要维度
5. 不为简化而忽略细节

---

*Skill版本: v1.0 | 创建日期: 2026-03-20*
