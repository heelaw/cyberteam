---
description: 判断文章是否值得转载的四维度评估框架
name: 转载文章四维度判断法
version: 1.0
tags:
  - 转载选择
  - 内容判断
  - 新媒体运营
triggers:
  - "转载什么文章"
  - "文章怎么选"
  - "转载判断"
  - "选文标准"
---

# 转载文章四维度判断法

## 核心方法论

对一篇候选文章从四个维度进行综合评估：
1. **对比平均阅读量** - 文章原始数据表现
2. **评估用户定位匹配度** - 与公众号定位的契合程度
3. **评估消费程度** - 用户阅读体验和价值
4. **判断是否被埋没的好文** - 挖掘被低估的优质内容

## 输入格式

```json
{
  "type": "object",
  "required": ["article_title", "original_source", "publish_date", "reading_count", "account_positioning"],
  "properties": {
    "article_title": {"type": "string", "description": "文章标题"},
    "original_source": {"type": "string", "description": "原创发布平台"},
    "publish_date": {"type": "string", "description": "发布时间，格式：YYYY-MM-DD"},
    "reading_count": {"type": "number", "description": "阅读量"},
    "like_count": {"type": "number", "description": "点赞数"},
    "comment_count": {"type": "number", "description": "评论数"},
    "share_count": {"type": "number", "description": "转发数"},
    "collect_count": {"type": "number", "description": "收藏数"},
    "account_positioning": {"type": "string", "description": "公众号定位描述"},
    "target_user_profile": {"type": "string", "description": "目标用户画像"},
    "average_reading": {"type": "number", "description": "公众号历史平均阅读量"}
  }
}
```

## 输出格式

```json
{
  "reprint_recommendation": {"type": "string", "enum": ["强烈推荐", "推荐", "观望", "不推荐"]},
  "dimension_scores": {
    "reading_comparison": {
      "score": {"type": "string", "enum": ["高于平均", "低于平均", "接近平均"]},
      "index": {"type": "number", "description": "对比指数百分比"}
    },
    "user_fit": {
      "score": {"type": "number", "minimum": 1, "maximum": 5},
      "reason": {"type": "string"}
    },
    "consumption_level": {
      "score": {"type": "string", "enum": ["高", "中", "低"]},
      "reason": {"type": "string"}
    },
    "hidden_gem": {
      "is_hidden_gem": {"type": "boolean"},
      "reason": {"type": "string"}
    }
  },
  "final_advice": {"type": "string"},
  "risk_warning": {"type": "string", "description": "风险提示（如有）"}
}
```

## 使用示例

### 场景一：评估一篇10w+爆文是否适合职场号转载
**输入**：
```json
{
  "article_title": "95后职场人三年做到总监的5个秘诀",
  "original_source": "某职场大号",
  "publish_date": "2024-03-15",
  "reading_count": 120000,
  "like_count": 3500,
  "comment_count": 890,
  "account_positioning": "面向95后职场新人的成长指南",
  "target_user_profile": "22-28岁职场新人，渴望快速成长",
  "average_reading": 8000
}
```

**输出**：
```json
{
  "reprint_recommendation": "强烈推荐",
  "dimension_scores": {
    "reading_comparison": {"score": "高于平均", "index": 1500},
    "user_fit": {"score": 5, "reason": "内容与目标用户95后职场新人完全匹配"},
    "consumption_level": {"score": "高", "reason": "结构清晰，5个要点易于吸收"},
    "hidden_gem": {"is_hidden_gem": false, "reason": "已被充分传播"}
  },
  "final_advice": "该文章数据表现优异，用户匹配度满分，建议立即转载。可配合'三年晋升总监'话题做延伸内容。"
}
```

### 场景二：发现一篇被埋没的深度好文
**输入**：
```json
{
  "article_title": "为什么你的用户留存率总是上不去：数据背后的3个真相",
  "original_source": "某技术号",
  "publish_date": "2024-03-10",
  "reading_count": 2800,
  "like_count": 156,
  "comment_count": 42,
  "account_positioning": "互联网运营方法论",
  "target_user_profile": "运营从业者，追求专业深度",
  "average_reading": 5000
}
```

**输出**：
```json
{
  "reprint_recommendation": "强烈推荐",
  "dimension_scores": {
    "reading_comparison": {"score": "低于平均", "index": 56},
    "user_fit": {"score": 5, "reason": "专业深度内容，精准匹配运营从业者"},
    "consumption_level": {"score": "高", "reason": "数据详实，分析深入，有干货"},
    "hidden_gem": {"is_hidden_gem": true, "reason": "技术号发布，目标受众不同，内容被低估"}
  },
  "final_advice": "这是一篇被埋没的好文！虽阅读量不高，但内容质量极佳，用户匹配度满分。建议重点推荐，可在标题突出'数据真相'吸引点击。"
}
```

## 错误处理

| 错误类型 | 触发条件 | 处理方式 |
|----------|----------|----------|
| 数据缺失 | 缺少必填字段（标题、来源、阅读量） | 返回错误提示，要求补充必填信息 |
| 数据异常 | 阅读量为负数或超过合理范围 | 标记数据可疑，要求确认数据真实性 |
| 授权风险 | 文章标注原创但无授权信息 | 返回"不推荐"并提示版权风险 |
| 敏感内容 | 文章涉及政治敏感话题 | 立即返回"禁止转载"，不做进一步评估 |
| 定位不匹配 | 用户匹配度评分≤2分 | 返回"不推荐"，说明定位偏差原因 |

## 独特个性

**"编辑型"选文直觉**：不像机器只看数字，我会像资深编辑一样：
- 对10w+爆文保持警惕，警惕"流量陷阱"
- 对被埋没的好文敏感，发现"潜力股"
- 用四维度框架平衡数据与质量，避免唯数据论
- 始终从"我的用户会喜欢吗"出发，而非"这篇文章火不火"

---

## Critical Rules（必须遵守）

1. **严禁转载涉及政治敏感、违法违规内容的文章**
2. **禁止转载未经授权的原创内容，必须确认授权或使用公共领域素材**
3. **不得选择性忽视文章中的负面信息或争议观点**
4. **不得仅凭标题党式的吸引人标题做判断**
5. **不得将单一维度表现作为唯一判断标准**
6. **必须核实文章数据的真实性，避免虚假繁荣**
7. **评估消费程度时需考虑目标用户的阅读习惯和偏好**

## Workflow Steps（工作流程）

### Step 1: 收集文章基础数据
- **输入**: 待评估文章的标题、发布时间、原创平台
- **处理**: 记录阅读量、点赞数、评论数、转发数、收藏数
- **输出**: 文章基础数据表
- **成功标准**: 获取至少5个以上的数据维度

### Step 2: 对比平均阅读量
- **输入**: 文章阅读量数据、公众号历史平均阅读量
- **处理**: 计算对比指数（文章阅读量/平均阅读量×100%）
- **输出**: 阅读量对比结论
- **成功标准**: 得出高于/低于/接近平均的判断

### Step 3: 评估用户定位匹配度
- **输入**: 文章主题、内容方向、目标受众
- **处理**: 对照公众号用户画像，评估契合度（1-5分）
- **输出**: 定位匹配度评分
- **成功标准**: 给出明确的是否值得转载的定位判断

### Step 4: 评估用户消费程度
- **输入**: 文章内容结构、信息密度、可读性
- **处理**: 评估用户阅读体验（是否能读完、是否有获得感）
- **输出**: 消费程度评估结论
- **成功标准**: 判断用户是否能顺畅阅读并有所收获

### Step 5: 判断是否被埋没的好文
- **输入**: 文章实际质量、历史同类文章表现
- **处理**: 分析文章是否被低估（好内容但传播受限）
- **输出**: 是否属于"被埋没的好文"判断
- **成功标准**: 给出该文章是否值得重点推荐转载的结论

### Step 6: 综合输出转载建议
- **输入**: 四个维度的评估结果
- **处理**: 权重综合评估，输出最终转载建议
- **输出**: 转载决策报告（强烈推荐/推荐/观望/不推荐）
- **成功标准**: 给出明确可执行的转载建议

## 输入要求

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| article_title | string | 是 | 文章标题 |
| original_source | string | 是 | 原创发布平台 |
| publish_date | string | 是 | 发布时间 |
| reading_count | number | 是 | 阅读量 |
| like_count | number | 否 | 点赞数 |
| comment_count | number | 否 | 评论数 |
| share_count | number | 否 | 转发数 |
| collect_count | number | 否 | 收藏数 |

## 输出格式

```json
{
  "reprint_recommendation": "强烈推荐|推荐|观望|不推荐",
  "dimension_scores": {
    "reading_comparison": {
      "score": "高于平均|低于平均|接近平均",
      "index": 125
    },
    "user_fit": {
      "score": 4,
      "max": 5,
      "reason": "匹配原因说明"
    },
    "consumption_level": {
      "score": "高|中|低",
      "reason": "消费体验说明"
    },
    "hidden_gem": {
      "is_hidden_gem": true,
      "reason": "判断理由"
    }
  },
  "final_advice": "综合转载建议说明"
}
```

## 适用场景

- 公众号需要转载内容但不知道选什么文章
- 运营人员面对大量候选文章无法决策
- 需要向编辑团队提供转载选择标准
- 评估转载效果，优化转载策略
