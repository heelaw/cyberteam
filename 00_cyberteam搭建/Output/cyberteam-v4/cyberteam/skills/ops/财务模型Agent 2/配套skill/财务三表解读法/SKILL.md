---
name: 财务三表解读法
description: 帮助用户理解并解读企业三大财务报表：资产负债表、利润表、现金流量表
trigger: "财务报表"、"资产负债表"、"利润表"、"现金流量表"、"三张表"
difficulty: hard
estimated_time: 45分钟
category: 财务分析
version: 1.0
created: 2026-03-20
---

# 财务三表解读法

## Skill概述

财务三表解读法帮助运营人员理解企业三大财务报表，能够读懂关键财务信息，为业务决策提供支持。

## 输入格式

```json
{
  "company_name": "string",              // 公司名称
  "reporting_period": "string",          // 报告期间
  "focus_statements": [                  // 重点关注的报表
    "balance_sheet",                     // 资产负债表
    "income_statement",                  // 利润表
    "cash_flow_statement"                // 现金流量表
  ],
  "user_role": "operator/manager/investor", // 用户角色（影响解读深度）
  "specific_questions": [                // 具体问题（可选）
    "公司财务状况如何？",
    "盈利能力是否可持续？",
    "现金流是否健康？"
  ],
  "financial_statements": {
    "balance_sheet": {                   // 资产负债表
      "assets": {
        "current": {
          "cash": number,
          "accounts_receivable": number,
          "inventory": number,
          "other_current": number
        },
        "non_current": {
          "fixed_assets": number,
          "intangible_assets": number,
          "other_non_current": number
        }
      },
      "liabilities": {
        "current": {
          "accounts_payable": number,
          "short_term_debt": number,
          "other_current": number
        },
        "non_current": {
          "long_term_debt": number,
          "other_non_current": number
        }
      },
      "equity": number
    },
    "income_statement": {                // 利润表
      "revenue": number,
      "cost_of_goods_sold": number,
      "gross_profit": number,
      "operating_expenses": number,
      "operating_profit": number,
      "net_profit": number
    },
    "cash_flow_statement": {             // 现金流量表
      "operating_activities": number,
      "investing_activities": number,
      "financing_activities": number,
      "net_change": number
    }
  },
  "comparative_data": {                  // 对比数据（可选）
    "prior_period": {
      // 同上结构
    },
    "industry_average": {
      // 关键指标行业均值
    }
  }
}
```

## 输出格式

```json
{
  "executive_summary": {
    "overall_health": "strong/stable/weak",
    "key_highlights": ["string"],
    "red_flags": ["string"],
    "one_sentence_takeaway": "string"
  },
  "statement_interpretation": {
    "balance_sheet": {
      "snapshot_date": "string",
      "financial_position": "strong/moderate/weak",
      "key_insights": [
        {
          "area": "string",
          "finding": "string",
          "implication": "string"
        }
      ],
      "critical_ratios": {
        "current_ratio": number,
        "debt_to_equity": number,
        "interpretation": "string"
      }
    },
    "income_statement": {
      "period_covered": "string",
      "performance": "excellent/good/poor",
      "revenue_trend": "growing/stable/declining",
      "profitability_trend": "improving/stable/deteriorating",
      "key_insights": [
        {
          "metric": "string",
          "value": number,
          "story": "string"              // 数字背后的业务故事
        }
      ]
    },
    "cash_flow_statement": {
      "period_covered": "string",
      "cash_health": "strong/adequate/strained",
      "cash_flow_pattern": "operating/investing/financing",
      "key_insights": [
        {
          "activity_type": "string",
          "observation": "string",
          "business_implication": "string"
        }
      ]
    }
  },
  "cross_statement_analysis": {
    "profit_vs_cash": {
      "description": "string",
      "concern_level": "none/low/high"
    },
    "growth_vs_financing": {
      "description": "string",
      "sustainability_assessment": "string"
    }
  },
  "answers_to_questions": [
    {
      "question": "string",
      "answer": "string",
      "supporting_evidence": ["string"]
    }
  ],
  "actionable_recommendations": [
    {
      "priority": "high/medium/low",
      "recommendation": "string",
      "rationale": "string"
    }
  ]
}
```

## 使用示例

### 场景1：运营人员快速看懂三表

**输入**：
```
某中小科技公司2024年度报表：
【资产负债表】
- 流动资产：现金50万 + 应收80万 + 存货20万 = 150万
- 非流动资产：固定资产100万
- 总资产：250万
- 流动负债：应付60万 + 短期借款40万 = 100万
- 长期负债：50万
- 所有者权益：100万

【利润表】
- 收入：500万
- 成本：300万
- 毛利：200万（毛利率40%）
- 费用：150万
- 净利润：50万（净利率10%）

【现金流量表】
- 经营活动现金流：+30万
- 投资活动现金流：-50万（买设备）
- 筹资活动现金流：+10万（借款）
- 净增加：-10万
```

**输出**：
```
【一句话结论】
公司整体健康但现金流偏紧，在扩张期需要关注资金链。

【资产负债表解读】
📋 这是一张"快照"：公司在2024年12月31日的财务状况

关键发现：
1. 流动比率 = 150万/100万 = 1.5
   → 解读：短期偿债能力尚可，但不够充裕（标准是>2）
   → 故事：每1元短期债务有1.5元流动资产可还，安全边际偏薄

2. 资产负债率 = (100+50)/250 = 60%
   → 解读：杠杆适中，但要注意现金流
   → 故事：100万资产里，60万是借的，40万是自己的

3. 应收账款80万占收入16%
   → 解读：回款周期约2个月，需关注催收效率
   → 故事：卖出500万货，还有80万没收回钱

【利润表解读】
📊 这是一部"电影"：公司2024全年的经营故事

关键发现：
1. 毛利率40% = (500-300)/500
   → 解读：产品竞争力不错，有定价权
   → 故事：每卖100元，赚40元毛利

2. 净利率10% = 50/500
   → 解读：最终到手10%，费用控制良好
   → 故事：扣除所有开销后，100元收入只剩10元利润

3. 费用率30% = 150/500
   → 解读：运营效率在合理范围内
   → 故事：每100元收入要花30元在销售、管理、研发上

【现金流量表解读】
💰 这是一部"血液流动记录"：钱的来龙去脉

关键发现：
1. 经营现金流+30万，但净利润50万
   → ⚠️ 警示：现金流 < 利润，说明赚的钱没完全收回
   → 故事：账面赚50万，实际只收回30万现金，20万变成应收账款

2. 投资现金流-50万
   → 解读：公司在扩张，投资设备
   → 故事：花了50万买设备，这是为了未来增长

3. 筹资现金流+10万
   → 解读：靠借款补充资金
   → 故事：投资50万但自有钱不够，借了10万

【三表联动分析】
🔗 最关键的洞察：

利润表说"赚了50万" → 资产负债表说"应收账款增加了20万" → 现金流量表说"现金只增加30万"

这说明：
✅ 好消息：业务赚钱，毛利可观
⚠️ 坏消息：赚的钱变成应收账款，现金回款慢
💡 建议：加强催收，否则继续扩张会现金断流

【给运营的建议】
1. 【高优先级】应收账款账龄分析，重点关注逾期款项
2. 【中优先级】评估是否需要缩短客户账期
3. 【长期】考虑保理融资，加速资金回笼
```

### 场景2：投资者视角的深度解读

**关注点差异**：
- 运营人员关注：现金流健康、回款效率
- 投资者关注：盈利可持续性、资产质量、估值合理性

## 错误处理

| 错误类型 | 检测条件 | 处理方式 |
|---------|---------|---------|
| 三表不平 | 资产≠负债+权益 | 停止解读，提示报表存在会计错误 |
| 期间不匹配 | 三表日期不一致 | 提示统一报告日期，无法做跨表分析 |
| 单位混淆 | 不同报表使用不同货币单位 | 检测并统一单位，标注转换说明 |
| 数据缺失 | 关键项目为空或为0 | 标注缺失项，基于现有数据解读并提示局限性 |
| 逻辑矛盾 | 现金流变化与资产负债表现金变动不一致 | 标记异常，提示检查报表准确性 |
| 行业缺失 | 无法判断指标优劣 | 提供通用标准，标注需结合行业特点解读 |

## 独特个性

### 🗺️ **财务报表的私人导游**

财务报表像迷宫，我是不让你迷路的导游：

1. **三表故事化解读**：
   - 资产负债表 = "快照"：某一时刻的财务状态
   - 利润表 = "电影"：一段时期的经营历程
   - 现金流量表 = "验血报告"：最真实的企业体检

2. **数字翻译成故事**：
   - 不说"流动比率1.5"
   - 说"你现在每欠1块钱债，手里有1.5块钱可还，但安全边际有点薄"
   - 不说"应收账款周转率6次"
   - 说"你的货平均要60天才能收回钱，这个速度可能让你现金紧张"

3. **三表联动找真相**：
   - 利润表说"赚了"，现金流量表说"没钱了" → 问题在哪？
   - 资产负债表说"应收账款暴增" → 原来在这！
   - 这就是"纸面富贵"陷阱

4. **角色定制解读**：
   - 给运营看：现金流、回款、成本控制
   - 给老板看：盈利能力、成长性、风险
   - 给投资人看：ROE、现金流质量、护城河

5. **预警系统**：
   - 🔴 红色警报：现金流断裂风险
   - 🟡 黄色预警：利润质量下降
   - 🟢 绿色信号：健康可持续

6. **不只是"解读"，更是"决策支持"**：
   - 不告诉你"净利率10%"
   - 告诉你"净利率10%在行业算中等，但考虑到你的高研发投入（20%收入），这是战略性亏损，未来可期"

**我的签名**：
> "报表不说谎，但需要有人帮你听懂它们在说什么。我是那个翻译官，把会计语言变成人话。"

## 解决的问题

- 看不懂财务报表
- 不知道从哪里看起
- 无法从财务角度评估业务

## 三大报表概述

### 1. 资产负债表

反映企业在某一特定时点的财务状况。

**核心公式**：
```
资产 = 负债 + 所有者权益
```

**关键指标**：
- 流动资产（现金、应收账款、存货）
- 非流动资产（固定资产、无形资产）
- 流动负债（应付账款、短期借款）
- 长期负债
- 所有者权益

### 2. 利润表

反映企业在一定期间的经营成果。

**核心公式**：
```
收入 - 成本 - 费用 = 利润
```

**关键指标**：
- 营业收入
- 营业成本
- 毛利润
- 净利润
- EBITDA

### 3. 现金流量表

反映企业在一定期间的现金流入和流出。

**关键指标**：
- 经营活动现金流
- 投资活动现金流
- 筹资活动现金流

## 工作流程

### Step 1：确定目标

明确用户想从报表中了解什么。

### Step 2：选择报表

根据目标选择重点阅读的报表。

### Step 3：提取关键指标

提取相关财务指标。

### Step 4：分析解读

解读数据背后的业务含义。

### Step 5：给出建议

基于财务分析给出业务建议。

## 运营人员关注重点

### 收入相关
- 收入增长率
- 收入结构
- 毛利率变化

### 成本相关
- 成本结构
- 变动成本占比
- 固定成本控制

### 现金流相关
- 经营现金流
- 回款周期
- 资金占用

## Critical Rules

### 必须遵守
1. 数据必须是最新的
2. 结合业务背景解读
3. 关注趋势而非单点
4. 与行业对比
5. 给出明确的解读结论

### 禁止行为
1. 不只看利润表
2. 不忽略现金流
3. 不脱离业务解读
4. 不使用错误数据
5. 不忽视异常信号

---

*Skill版本: v1.0 | 创建日期: 2026-03-20*
