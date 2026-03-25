---
description: 挖掘用户痛点产出高质量选题的三步法框架
name: 痛点选题三步法
version: 1.0
tags:
  - 选题策划
  - 痛点挖掘
  - 内容策划
  - 新媒体运营
triggers:
  - "选题怎么找"
  - "痛点选题"
  - "选题方向"
  - "怎么找话题"
---

# 痛点选题三步法

## 核心方法论

痛点选题三步法是一套从用户行为数据中挖掘真实需求、转化为可执行选题的系统方法：

1. **提取用户关键词** - 从用户反馈、评论、私信中提取高频词汇
2. **找出用户痛点** - 分析关键词背后的真实困扰和需求
3. **产出选题** - 将痛点转化为具体可写的选题方向

## 输入格式

```json
{
  "type": "object",
  "required": ["user_feedback_source", "raw_feedback_data", "feedback_count", "account_positioning"],
  "properties": {
    "user_feedback_source": {"type": "string", "enum": ["评论", "私信", "问卷", "搜索词", "混合"]},
    "raw_feedback_data": {
      "type": "array",
      "items": {"type": "string"},
      "description": "原始用户反馈数据，至少50条"
    },
    "feedback_count": {"type": "number", "minimum": 50, "description": "反馈总条数"},
    "account_positioning": {"type": "string", "description": "账号定位描述"},
    "target_user_profile": {
      "type": "object",
      "properties": {
        "age_range": {"type": "string"},
        "occupation": {"type": "string"},
        "pain_points": {"type": "array", "items": {"type": "string"}}
      }
    },
    "topic_quantity": {"type": "number", "description": "期望产出选题数量，默认10"}
  }
}
```

## 输出格式

```json
{
  "keywords": {
    "type": "array",
    "items": {
      "keyword": {"type": "string"},
      "frequency": {"type": "number"},
      "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]},
      "source_count": {"type": "number"}
    }
  },
  "pain_points": {
    "type": "array",
    "items": {
      "pain_point": {"type": "string"},
      "type": {"type": "string", "enum": ["认知型", "执行型", "资源型", "动机型", "决策型"]},
      "priority": {"type": "string", "enum": ["high", "medium", "low"]},
      "verified": {"type": "boolean"},
      "verify_sources": {"type": "array", "items": {"type": "string"}}
    }
  },
  "topic_directions": {
    "type": "array",
    "items": {
      "topic": {"type": "string"},
      "source_pain_point": {"type": "string"},
      "topic_type": {"type": "string", "enum": ["问题型", "方案型", "案例型"]},
      "priority": {"type": "string", "enum": ["high", "medium", "low"]}
    }
  },
  "top_5_priorities": {
    "type": "array",
    "items": {
      "topic": {"type": "string"},
      "priority": {"type": "number"},
      "reason": {"type": "string"}
    }
  }
}
```

## 使用示例

### 场景一：职场号从用户评论中挖掘选题
**输入**：
```json
{
  "user_feedback_source": "评论",
  "raw_feedback_data": [
    "工作太忙了，根本没时间学习",
    "想提升但不知道从哪开始",
    "学了很多但感觉用不上",
    "领导总是给我安排杂活，核心业务接触不到",
    "工资太低了，想跳槽又怕找不到更好的",
    "95后职场新人，感觉前途迷茫",
    "每天加班到10点，身体扛不住",
    "同事关系不好处理，职场政治太复杂"
  ],
  "feedback_count": 120,
  "account_positioning": "95后职场新人成长指南",
  "target_user_profile": {
    "age_range": "22-28岁",
    "occupation": "职场新人1-3年",
    "pain_points": ["时间管理", "职业规划", "薪资增长"]
  }
}
```

**输出**：
```json
{
  "keywords": [
    {"keyword": "时间", "frequency": 45, "sentiment": "negative", "source_count": 38},
    {"keyword": "学习", "frequency": 38, "sentiment": "neutral", "source_count": 32},
    {"keyword": "迷茫", "frequency": 32, "sentiment": "negative", "source_count": 28},
    {"keyword": "工资", "frequency": 28, "sentiment": "negative", "source_count": 25}
  ],
  "pain_points": [
    {
      "pain_point": "工作太忙没时间学习成长",
      "type": "资源型",
      "priority": "high",
      "verified": true,
      "verify_sources": ["评论区高频提及", "搜索指数'碎片化学习'上涨"]
    },
    {
      "pain_point": "不知道如何规划职业发展路径",
      "type": "决策型",
      "priority": "high",
      "verified": true,
      "verify_sources": ["私信咨询TOP3", "问卷反馈核心困扰"]
    }
  ],
  "topic_directions": [
    {
      "topic": "碎片化时间学习的5个高效方法",
      "source_pain_point": "工作太忙没时间学习成长",
      "topic_type": "方案型",
      "priority": "high"
    },
    {
      "topic": "95后职场人三年规划路线图",
      "source_pain_point": "不知道如何规划职业发展路径",
      "topic_type": "方案型",
      "priority": "high"
    }
  ],
  "top_5_priorities": [
    {"topic": "碎片化时间学习的5个高效方法", "priority": 1, "reason": "高频痛点+方案型，易传播"},
    {"topic": "95后职场人三年规划路线图", "priority": 2, "reason": "决策型痛点+目标用户精准匹配"}
  ]
}
```

### 场景二：从问卷调研结果转化选题
**输入**：
```json
{
  "user_feedback_source": "问卷",
  "raw_feedback_data": [
    "不知道怎么判断自己是否适合转行",
    "转行后薪资会下降吗？能接受吗？",
    "转行需要学什么技能？从哪里开始？",
    "30岁转行还来得及吗？",
    "转行后发现不合适怎么办？风险太大",
    "家庭压力下不敢轻易转行",
    "看了很多转行经验，但不知道哪个适合自己"
  ],
  "feedback_count": 86,
  "account_positioning": "职场转型指南",
  "target_user_profile": {
    "age_range": "28-35岁",
    "occupation": "考虑转行的职场人",
    "pain_points": ["转行决策", "风险评估", "技能转换"]
  }
}
```

**输出**：
```json
{
  "keywords": [
    {"keyword": "转行", "frequency": 52, "sentiment": "neutral", "source_count": 48},
    {"keyword": "风险", "frequency": 38, "sentiment": "negative", "source_count": 35},
    {"keyword": "薪资", "frequency": 31, "sentiment": "negative", "source_count": 28}
  ],
  "pain_points": [
    {
      "pain_point": "不知道如何评估转行风险",
      "type": "决策型",
      "priority": "high",
      "verified": true,
      "verify_sources": ["问卷TOP1困扰", "搜索'转行风险评估'指数高"]
    }
  ],
  "topic_directions": [
    {
      "topic": "转行风险评估的6个维度",
      "source_pain_point": "不知道如何评估转行风险",
      "topic_type": "方案型",
      "priority": "high"
    }
  ],
  "top_5_priorities": [
    {"topic": "转行风险评估的6个维度", "priority": 1, "reason": "决策型痛点+方法论，实用价值高"}
  ]
}
```

## 错误处理

| 错误类型 | 触发条件 | 处理方式 |
|----------|----------|----------|
| 数据不足 | 反馈条数<50 | 返回警告，建议补充数据来源 |
| 数据单一 | 只有一个反馈来源 | 提示多源验证，降低数据可靠性 |
| 痛点模糊 | 关键词过于宽泛（如"学习"） | 引导追问具体场景，深挖痛点 |
| 定位偏差 | 产出选题与账号定位不符 | 返回警告，建议调整或剔除相关选题 |
| 验证失败 | 痛点无数据支撑 | 标记"待验证"，不建议作为重点选题 |

## 独特个性

**"用户洞察者"视角**：不只是收集反馈，而是：
- 从"表面抱怨"挖掘"深层需求"（追问3个为什么）
- 区分"真痛点"和"伪需求"（多维度验证）
- 将痛点转化为"可执行的选题"（不只是问题列表）
- 始终从"用户视角"出发（而非运营想当然）
- 用数据支撑创意（让选题有据可依，不是拍脑袋）

---

## Critical Rules（必须遵守）

1. **禁止凭空捏造用户痛点，必须基于真实数据或调研**
2. **不得将个人主观判断强加为"用户痛点"**
3. **禁止刻意制造焦虑来获取流量**
4. **不得抄袭他人选题，需有独特切入角度**
5. **痛点分析必须多维度验证，不能仅凭单一来源**
6. **选题产出必须考虑账号定位和用户画像匹配度**
7. **不得为了追热点而脱离账号核心价值**

## Workflow Steps（工作流程）

### Step 1: 收集用户关键词
- **输入**: 用户评论、私信、问卷反馈、搜索词数据
- **处理**: 词频统计、情感分类、归纳整理
- **输出**: 用户关键词清单（TOP20）
- **成功标准**: 收集≥50条用户反馈，提取有效关键词≥10个

### Step 2: 分析挖掘痛点
- **输入**: 用户关键词清单
- **处理**: 追问"为什么"，挖掘表层需求下的深层动机
- **输出**: 痛点清单（含优先级）
- **成功标准**: 每个关键词追问3层以上，产出痛点≥5个

### Step 3: 痛点验证
- **输入**: 初步痛点清单
- **处理**: 多渠道验证（评论、搜索指数、竞品对比）
- **输出**: 经验证的痛点列表
- **成功标准**: 每个核心痛点有≥2个数据来源支撑

### Step 4: 产出选题方向
- **输入**: 验证后的痛点清单
- **处理**: 将痛点转化为"问题型"或"方案型"选题
- **输出**: 选题方向列表（≥10个）
- **成功标准**: 选题方向覆盖不同痛点，类型多样化

### Step 5: 选题评估筛选
- **输入**: 候选选题列表
- **处理**: 从可行性、传播性、差异化评分
- **输出**: 优先级排序的选题清单
- **成功标准**: 产出TOP5重点选题，附带选择理由

## 痛点分类框架

| 痛点类型 | 描述 | 典型句式 |
|----------|------|----------|
| 认知型 | 用户不知道/不理解 | "什么是..."、"...是什么道理" |
| 执行型 | 用户想做但不会做 | "如何..."、"怎么做..." |
| 资源型 | 用户缺少资源/工具 | "没有..."、"找不到..." |
| 动机型 | 用户有动力但易放弃 | "坚持不下去..."、"总是拖延..." |
| 决策型 | 用户纠结不知选哪个 | "...和...哪个好"、"要不要..." |

## 输入要求

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_feedback_source | string | 是 | 反馈来源：评论/私信/问卷/搜索词 |
| raw_feedback_data | array | 是 | 原始用户反馈数据 |
| feedback_count | number | 是 | 反馈总条数 |
| account_positioning | string | 是 | 账号定位描述 |
| target_user_profile | object | 否 | 目标用户画像 |

## 输出格式

```json
{
  "keywords": [
    {"keyword": "时间管理", "frequency": 45, "sentiment": "negative"}
  ],
  "pain_points": [
    {
      "pain_point": "工作太忙没时间学习",
      "type": "资源型",
      "verified": true,
      "verify_sources": ["评论区高频提及", "搜索指数上涨"]
    }
  ],
  "topic_directions": [
    {
      "topic": "碎片化时间学习的5个方法",
      "source_pain_point": "工作太忙没时间学习",
      "topic_type": "方案型",
      "priority": "high"
    }
  ],
  "top_5_priorities": [
    {"topic": "...", "priority": 1, "reason": "..."}
  ]
}
```

## 适用场景

- 月度选题规划
- 内容枯竭时的选题挖掘
- 用户调研结果转化
- 竞品选题分析后差异化定位
- 运营团队选题头脑风暴
