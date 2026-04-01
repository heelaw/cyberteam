# 用户画像模板

## 模板结构

```json
{
  "user_persona": {
    "basic_info": {
      "name": "给用户取一个典型名字",
      "age_range": "年龄范围",
      "gender": "性别",
      "location": "地域",
      "occupation": "职业",
      "income": "收入水平"
    },
    "demographics": {
      "family_status": "婚姻/家庭状况",
      "education": "学历",
      "life_stage": "人生阶段"
    },
    "psychographics": {
      "values": ["核心价值观"],
      "interests": ["兴趣爱好"],
      "personality": "性格特点"
    },
    "behavior_patterns": {
      "online_habits": {
        "daily_online_time": "日均在线时长",
        "preferred_platforms": ["常用平台"],
        "content_preferences": ["内容偏好"],
        "active_time": "活跃时间段"
      },
      "purchase_behavior": {
        "decision_makers": ["购买决策者"],
        "purchase_frequency": "购买频率",
        "price_sensitivity": "价格敏感度",
        "brand_loyalty": "品牌忠诚度"
      },
      "media_consumption": {
        "social_media": ["社交媒体"],
        "news_sources": ["新闻来源"],
        "entertainment": ["娱乐方式"]
      }
    },
    "pain_points": [
      "痛点1：具体描述",
      "痛点2：具体描述"
    ],
    "goals": [
      "目标1：具体可衡量",
      "目标2：具体可衡量"
    ],
    "motivation": "核心购买动机",
    "barriers": [
      "阻碍1：具体描述",
      "阻碍2：具体描述"
    ]
  },
  "targeting_confidence": "high/medium/low",
  "data_sources": ["数据来源列表"],
  "validation_needed": ["需要验证的数据点"]
}
```

## 使用说明

1. **命名：** 给用户画像起一个典型的名字，方便团队沟通
2. **完整性：** 7个维度尽量填满，信息不全的维度需要通过调研补充
3. **数据支撑：** 每个结论都要有数据或访谈支撑
4. **定期更新：** 用户画像需要随着产品发展和数据积累不断迭代
