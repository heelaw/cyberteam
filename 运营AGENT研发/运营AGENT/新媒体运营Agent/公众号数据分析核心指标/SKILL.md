---
description: 公众号数据分析的标准方法论和核心指标解读
name: 公众号数据分析核心指标
version: 1.0
tags:
  - 数据分析
  - 公众号运营
  - 指标解读
  - 新媒体运营
triggers:
  - "数据怎么分析"
  - "公众号数据分析"
  - "数据分析指标"
  - "阅读量分析"
---

# 公众号数据分析核心指标

## 核心方法论

公众号数据分析围绕两大核心板块：
1. **用户增长分析** - 净增用户数、累计用户数、增长趋势
2. **图文分析** - 阅读量、转化率、分享数、收藏数

## 输入格式

```json
{
  "type": "object",
  "required": ["analysis_period", "account_type", "follower_count", "new_followers", "cancelled_followers", "article_delivered", "article_reading"],
  "properties": {
    "analysis_period": {"type": "string", "description": "分析周期，如'2024年3月'"},
    "account_type": {"type": "string", "enum": ["订阅号", "服务号"]},
    "follower_count": {"type": "number", "description": "累计粉丝数"},
    "new_followers": {"type": "number", "description": "新增关注数"},
    "cancelled_followers": {"type": "number", "description": "取消关注数"},
    "article_delivered": {"type": "number", "description": "图文送达人数"},
    "article_reading": {"type": "number", "description": "阅读人数"},
    "article_original_click": {"type": "number", "description": "原文阅读数"},
    "article_shares": {"type": "number", "description": "分享人数"},
    "article_collects": {"type": "number", "description": "收藏人数"},
    "benchmark_data": {"type": "object", "description": "行业基准数据（可选）"}
  }
}
```

## 输出格式

```json
{
  "analysis_period": {"type": "string"},
  "user_growth": {
    "net_growth": {"type": "number"},
    "growth_rate": {"type": "number"},
    "trend": {"type": "string", "enum": ["上升", "稳定", "下降"]},
    "is_healthy": {"type": "boolean"},
    "analysis": {"type": "string"}
  },
  "content_performance": {
    "reading_rate": {"type": "number"},
    "conversion_rate": {"type": "number"},
    "share_rate": {"type": "number"},
    "collect_rate": {"type": "number"},
    "overall_score": {"type": "string"}
  },
  "diagnosis": {
    "strengths": {"type": "array", "items": {"type": "string"}},
    "weaknesses": {"type": "array", "items": {"type": "string"}},
    "opportunities": {"type": "array", "items": {"type": "string"}}
  },
  "recommendations": {
    "type": "array",
    "items": {
      "priority": {"type": "string", "enum": ["high", "medium", "low"]},
      "action": {"type": "string"},
      "expected_impact": {"type": "string"}
    }
  }
}
```

## 使用示例

### 场景一：月度数据复盘，诊断增长放缓原因
**输入**：
```json
{
  "analysis_period": "2024年3月",
  "account_type": "订阅号",
  "follower_count": 35000,
  "new_followers": 1200,
  "cancelled_followers": 900,
  "article_delivered": 34000,
  "article_reading": 4250,
  "article_shares": 120,
  "article_collects": 65
}
```

**输出**：
```json
{
  "analysis_period": "2024年3月",
  "user_growth": {
    "net_growth": 300,
    "growth_rate": 0.86,
    "trend": "放缓",
    "is_healthy": false,
    "analysis": "净增用户仅300，取消关注数900处高位，需排查内容方向是否偏离用户预期"
  },
  "content_performance": {
    "reading_rate": 12.5,
    "conversion_rate": 0,
    "share_rate": 2.8,
    "collect_rate": 1.5,
    "overall_score": "阅读率优秀，但分享转化偏低"
  },
  "diagnosis": {
    "strengths": ["阅读率12.5%高于行业平均5-10%"],
    "weaknesses": ["取消关注率过高(2.6%)", "分享率未达3%行业平均"],
    "opportunities": ["读者愿意阅读，但缺少分享动力"]
  },
  "recommendations": [
    {"priority": "high", "action": "分析取消关注用户特征，调整内容方向", "expected_impact": "降低取关率"},
    {"priority": "medium", "action": "在文章结尾增加分享引导", "expected_impact": "提升分享率至3%+"}
  ]
}
```

### 场景二：单篇爆文效果分析
**输入**：
```json
{
  "analysis_period": "2024-03-15单篇文章",
  "account_type": "订阅号",
  "follower_count": 35000,
  "article_delivered": 34000,
  "article_reading": 8500,
  "article_original_click": 680,
  "article_shares": 450,
  "article_collects": 320
}
```

**输出**：
```json
{
  "analysis_period": "2024-03-15单篇文章",
  "user_growth": {
    "net_growth": 520,
    "growth_rate": 1.5,
    "trend": "激增",
    "is_healthy": true,
    "analysis": "单篇带来520新增，是日常的1.7倍，属于有效增长"
  },
  "content_performance": {
    "reading_rate": 25.0,
    "conversion_rate": 8.0,
    "share_rate": 5.3,
    "collect_rate": 3.8,
    "overall_score": "全面超越行业平均，属于爆文级别"
  },
  "diagnosis": {
    "strengths": ["阅读率25%远超平均", "转化率8%是行业2-5%的2-4倍", "分享收藏双高"],
    "weaknesses": ["暂无明显短板"],
    "opportunities": ["可复制该内容形式，形成系列"]
  },
  "recommendations": [
    {"priority": "high", "action": "分析该文章结构，提炼可复用模板", "expected_impact": "持续产出爆文"},
    {"priority": "medium", "action": "跟进该话题做系列内容", "expected_impact": "延长流量周期"}
  ]
}
```

## 错误处理

| 错误类型 | 触发条件 | 处理方式 |
|----------|----------|----------|
| 数据不一致 | 送达人数大于粉丝数 | 标记数据异常，要求确认统计口径 |
| 计算错误 | 增长率计算结果超出合理范围 | 返回警告，建议人工核对原始数据 |
| 指标缺失 | 关键指标为零或空值 | 标注无法分析部分，提供部分分析结果 |
| 时效性警告 | 分析周期超过3个月 | 提示数据时效性问题，建议更新数据 |
| 基准缺失 | 无行业基准数据对比 | 基于历史数据做纵向对比，标注无横向对比 |

## 独特个性

**"数据侦探"思维模式**：不只是罗列数字，而是：
- 从数据异常中发现问题（如取关率突然升高）
- 用多维度交叉验证（不是单一看阅读量）
- 结合业务场景给出建议（而非泛泛而谈）
- 既看"好不好"，更问"为什么"（追根溯源）
- 用数据讲故事，让冰冷的数字有温度

---

## Critical Rules（必须遵守）

1. **严禁将单一指标作为唯一判断标准**
2. **禁止忽视数据的时效性，警惕"历史数据"陷阱**
3. **不得选择性解读数据，必须完整呈现正负两面**
4. **禁止用虚假数据或伪造对比基数美化表现**
5. **不得将相关性当作因果性，谨慎推断数据原因**
6. **数据分析必须结合业务背景，不能脱离实际场景**
7. **发现数据异常必须追根溯源，不能忽视异常值**

## Workflow Steps（工作流程）

### Step 1: 收集数据基础信息
- **输入**: 数据时间范围、公众号基本信息、账号类型
- **处理**: 确认数据来源、获取数据时间点、标注统计口径
- **输出**: 数据基础信息表
- **成功标准**: 明确数据边界和限制条件

### Step 2: 用户增长数据分析
- **输入**: 净增用户数、取消关注数、累计用户数
- **处理**: 计算增长绝对值和百分比，分析增长趋势
- **输出**: 用户增长分析报告
- **成功标准**: 判断增长是否健康，给出趋势判断

### Step 3: 图文阅读量分析
- **输入**: 图文送达人数、阅读量、原文阅读人数
- **处理**: 计算阅读率（阅读量/送达人数）、原文转化率
- **输出**: 阅读量分析结论
- **成功标准**: 得出阅读效率的判断

### Step 4: 互动指标分析
- **输入**: 分享人数、收藏人数、在看数、评论数
- **处理**: 分析互动率、分享率、收藏率
- **输出**: 互动指标分析结论
- **成功标准**: 判断用户互动程度

### Step 5: 综合数据诊断
- **输入**: 所有指标数据
- **处理**: 横向对比（与往期对比）、纵向参考（与行业对比）
- **输出**: 数据诊断报告
- **成功标准**: 识别问题点和增长点

### Step 6: 输出改进建议
- **输入**: 数据诊断结果
- **处理**: 结合业务场景，产出可落地建议
- **输出**: 改进建议清单
- **成功标准**: 建议具体、可执行、有优先级

## 核心指标定义

| 指标名称 | 定义 | 计算公式 | 健康区间 |
|----------|------|----------|----------|
| 阅读量 | 实际阅读文章的人数 | 微信后台统计 | - |
| 送达人数 | 图文消息已送达的用户数 | 推送用户数 | - |
| 阅读率 | 阅读量与送达人数比 | 阅读量/送达人数×100% | 5%-15% |
| 原文阅读数 | 点击"阅读原文"的人数 | 统计入口点击 | - |
| 转化率 | 原文阅读/阅读量 | 原文阅读/阅读量×100% | 2%-5% |
| 分享人数 | 转发至好友/朋友圈的人数 | 去重统计 | - |
| 分享率 | 分享人数/阅读人数 | 分享人数/阅读人数×100% | 1%-5% |
| 收藏人数 | 收藏文章的用户数 | 收藏操作去重 | - |
| 收藏率 | 收藏人数/阅读人数 | 收藏人数/阅读人数×100% | 0.5%-3% |
| 净增用户 | 新增关注减去取消关注 | 新增-取消 | 正值即健康 |
| 增长趋势 | 连续周期变化方向 | 环比/同比 | 上升/稳定/下降 |

## 输入要求

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| analysis_period | string | 是 | 分析周期，如"2024年3月" |
| account_type | string | 是 | 账号类型：订阅号/服务号 |
| follower_count | number | 是 | 累计粉丝数 |
| new_followers | number | 是 | 新增关注数 |
| cancelled_followers | number | 是 | 取消关注数 |
| article送达人数 | number | 是 | 图文送达人数 |
| article阅读量 | number | 是 | 阅读人数 |
| article原文阅读数 | number | 否 | 原文阅读数 |
| article分享人数 | number | 否 | 分享人数 |
| article收藏人数 | number | 否 | 收藏人数 |

## 输出格式

```json
{
  "analysis_period": "2024年3月",
  "user_growth": {
    "net_growth": 1200,
    "growth_rate": 3.5,
    "trend": "上升",
    "is_healthy": true
  },
  "content_performance": {
    "reading_rate": 12.5,
    "conversion_rate": 3.2,
    "share_rate": 2.8,
    "collect_rate": 1.5
  },
  "diagnosis": {
    "strengths": ["阅读率高于行业平均"],
    "weaknesses": ["分享率偏低"],
    "opportunities": ["可尝试增加互动引导"]
  },
  "recommendations": [
    {
      "priority": "high",
      "action": "优化文章结尾的分享引导",
      "expected_impact": "提升分享率"
    }
  ]
}
```

## 适用场景

- 月度/季度运营数据复盘
- 单篇文章表现分析
- 用户增长异常诊断
- 运营效果对比评估
- 制定下一阶段运营策略
