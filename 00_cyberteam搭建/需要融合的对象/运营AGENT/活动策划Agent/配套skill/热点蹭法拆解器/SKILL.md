---
name: 热点蹭法拆解器
description: 提供可预测热点和不可预测热点的蹭法方法论，帮助借势营销
trigger: ["蹭热点", "热点营销", "热点蹭法", "节日营销", "借势营销"]
difficulty: medium
estimated_time: 12分钟
---

# 热点蹭法拆解器

## 触发场景

当用户出现以下情况时触发本Skill：
- 不知道如何蹭热点
- 想借势营销但没有思路
- 需要规划节日营销活动
- 需要建立热点监测机制

## 输入输出格式

### 输入格式（JSON Schema）

```json
{
  "type": "object",
  "properties": {
    "hot_topic_type": {
      "type": "string",
      "enum": ["可预测热点", "突发热点", "不确定"],
      "description": "热点类型"
    },
    "predictable_hotspot": {
      "type": "object",
      "properties": {
        "hotspot_name": {
          "type": "string",
          "description": "热点名称，如'春节'、'618'、'世界杯'"
        },
        "hotspot_date": {
          "type": "string",
          "description": "热点时间"
        },
        "preparation_time": {
          "type": "string",
          "description": "可准备时间"
        }
      },
      "required": ["hotspot_name"]
    },
    "unpredictable_hotspot": {
      "type": "object",
      "properties": {
        "topic_name": {
          "type": "string",
          "description": "话题名称"
        },
        "topic_source": {
          "type": "string",
          "description": "来源平台"
        },
        "topic_heat": {
          "type": "string",
          "enum": ["S级", "A级", "B级", "C级"],
          "description": "热度等级"
        },
        "topic_description": {
          "type": "string",
          "description": "话题描述"
        }
      }
    },
    "brand_context": {
      "type": "object",
      "properties": {
        "brand_name": {
          "type": "string",
          "description": "品牌名称"
        },
        "product_category": {
          "type": "string",
          "description": "产品品类"
        },
        "brand_tone": {
          "type": "string",
          "description": "品牌调性"
        },
        "target_audience": {
          "type": "string",
          "description": "目标用户"
        }
      },
      "required": ["brand_name", "product_category"]
    },
    "resource_constraints": {
      "type": "object",
      "properties": {
        "budget": {
          "type": "string",
          "description": "预算"
        },
        "production_cycle": {
          "type": "string",
          "description": "制作周期"
        },
        "team_capability": {
          "type": "string",
          "description": "团队能力"
        }
      }
    }
  },
  "required": ["brand_context"]
}
```

### 输出格式（JSON Schema）

```json
{
  "type": "object",
  "properties": {
    "hotspot_analysis": {
      "type": "object",
      "properties": {
        "hotspot_type": {"type": "string"},
        "hotspot_level": {"type": "string"},
        "relevance_score": {
          "type": "number",
          "description": "与品牌相关度评分（1-10）"
        },
        "risk_assessment": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "风险评估"
        }
      }
    },
    "angle_recommendations": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "angle_name": {
            "type": "string",
            "description": "蹭法角度"
          },
          "angle_description": {"type": "string"},
          "feasibility": {
            "type": "string",
            "enum": ["高", "中", "低"]
          },
          "expected_effect": {"type": "string"},
          "implementation_difficulty": {
            "type": "string",
            "enum": ["容易", "中等", "困难"]
          }
        }
      }
    },
    "content_ideas": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "content_type": {"type": "string"},
          "content_description": {"type": "string"},
          "channel": {"type": "string"},
          "timeline": {"type": "string"}
        }
      }
    },
    "action_plan": {
      "type": "object",
      "properties": {
        "preparation_phase": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "action": {"type": "string"},
              "owner": {"type": "string"},
              "deadline": {"type": "string"}
            }
          }
        },
        "execution_phase": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "action": {"type": "string"},
              "timing": {"type": "string"}
            }
          }
        }
      }
    },
    "risk_control": {
      "type": "object",
      "properties": {
        "forbidden_topics": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "禁止参与的话题"
        },
        "risk_checklist": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "contingency_plan": {"type": "string"}
      }
    }
  }
}
```

## 使用示例

### 示例1：春节热点营销（可预测热点）

**输入**：
```json
{
  "hot_topic_type": "可预测热点",
  "predictable_hotspot": {
    "hotspot_name": "春节",
    "hotspot_date": "2024年2月10日",
    "preparation_time": "1个月"
  },
  "brand_context": {
    "brand_name": "美食外卖平台",
    "product_category": "本地生活服务",
    "brand_tone": "温暖、便捷、亲民",
    "target_audience": "25-35岁城市白领"
  },
  "resource_constraints": {
    "budget": "20万",
    "production_cycle": "2周",
    "team_capability": "内容创作+设计"
  }
}
```

**输出**：
```json
{
  "hotspot_analysis": {
    "hotspot_type": "可预测热点-节日类",
    "hotspot_level": "S级",
    "relevance_score": 9,
    "risk_assessment": [
      "政治风险：低",
      "品牌匹配度：高",
      "竞争激烈度：高"
    ]
  },
  "angle_recommendations": [
    {
      "angle_name": "情绪共鸣法",
      "angle_description": "围绕'回家过年'的情感，打造'年夜饭不用做，外卖来帮忙'主题",
      "feasibility": "高",
      "expected_effect": "情感共鸣强，品牌好感度提升",
      "implementation_difficulty": "容易"
    },
    {
      "angle_name": "产品关联法",
      "angle_description": "春节场景+外卖服务，主打'春节不打烊，外卖送到家'",
      "feasibility": "高",
      "expected_effect": "直接促进订单转化",
      "implementation_difficulty": "容易"
    },
    {
      "angle_name": "福利蹭法",
      "angle_description": "推出'春节红包雨'，下单即可得红包",
      "feasibility": "高",
      "expected_effect": "直接拉动成交",
      "implementation_difficulty": "中等"
    }
  ],
  "content_ideas": [
    {
      "content_type": "短视频",
      "content_description": "《过年回家，外卖帮忙》系列短视频，展示外卖员春节期间配送场景",
      "channel": "抖音、快手",
      "timeline": "节前1周上线"
    },
    {
      "content_type": "H5互动",
      "content_description": "春节红包雨活动，下单得红包",
      "channel": "App、小程序",
      "timeline": "春节前3天-初六"
    },
    {
      "content_type": "海报",
      "content_description": "春节不打烊主题海报",
      "channel": "微信公众号、社群",
      "timeline": "节前1周发布"
    }
  ],
  "action_plan": {
    "preparation_phase": [
      {"action": "完成内容策划", "owner": "内容组", "deadline": "节前2周"},
      {"action": "完成设计制作", "owner": "设计组", "deadline": "节前10天"},
      {"action": "完成技术开发", "owner": "技术组", "deadline": "节前7天"}
    ],
    "execution_phase": [
      {"action": "启动预热推广", "timing": "节前1周"},
      {"action": "正式活动上线", "timing": "春节前3天"},
      {"action": "活动持续运营", "timing": "春节-初六"}
    ]
  },
  "risk_control": {
    "forbidden_topics": [
      "政治敏感话题",
      "负面社会新闻",
      "竞品对比"
    ],
    "risk_checklist": [
      "内容是否符合品牌调性？",
      "是否有版权风险？",
      "是否涉及敏感话题？"
    ],
    "contingency_plan": "如遇负面舆情，立即下线相关内容并启动应急预案"
  }
}
```

### 示例2：突发热点营销

**输入**：
```json
{
  "hot_topic_type": "突发热点",
  "unpredictable_hotspot": {
    "topic_name": "某知名运动员夺冠",
    "topic_source": "微博热搜",
    "topic_heat": "S级",
    "topic_description": "中国运动员在奥运会夺得金牌，引发全民庆祝"
  },
  "brand_context": {
    "brand_name": "运动饮料品牌",
    "product_category": "饮料",
    "brand_tone": "活力、拼搏、胜利"
  }
}
```

**输出**：
```json
{
  "hotspot_analysis": {
    "hotspot_type": "突发热点-体育赛事",
    "hotspot_level": "S级",
    "relevance_score": 10,
    "risk_assessment": [
      "时效性：极高（需24小时内响应）",
      "品牌匹配度：极高",
      "舆论风险：低"
    ]
  },
  "angle_recommendations": [
    {
      "angle_name": "情绪共鸣法",
      "angle_description": "围绕'拼搏精神'，打造'为胜利喝彩'主题",
      "feasibility": "高",
      "expected_effect": "品牌形象提升",
      "implementation_difficulty": "容易"
    },
    {
      "angle_name": "产品关联法",
      "angle_description": "运动饮料+胜利庆祝，主打'胜利时刻，喝XXX'",
      "feasibility": "高",
      "expected_effect": "直接促进销售",
      "implementation_difficulty": "容易"
    }
  ],
  "content_ideas": [
    {
      "content_type": "社交媒体海报",
      "content_description": "祝贺海报+品牌产品露出",
      "channel": "微博、微信公众号",
      "timeline": "热点发生后6小时内"
    },
    {
      "content_type": "短视频",
      "content_description": "致敬拼搏精神，品牌植入",
      "channel": "抖音、快手",
      "timeline": "热点发生后12小时内"
    }
  ],
  "action_plan": {
    "preparation_phase": [
      {"action": "快速评估热点", "owner": "运营负责人", "deadline": "10分钟内"},
      {"action": "内容创意", "owner": "内容组", "deadline": "30分钟内"},
      {"action": "设计制作", "owner": "设计组", "deadline": "2小时内"}
    ],
    "execution_phase": [
      {"action": "社交媒体发布", "timing": "内容完成后立即发布"},
      {"action": "监测舆情反馈", "timing": "发布后持续监测"}
    ]
  },
  "risk_control": {
    "forbidden_topics": [
      "政治敏感话题",
      "悲剧事件",
      "争议性话题"
    ],
    "risk_checklist": [
      "话题是否有政治风险？",
      "话题是否涉及悲剧？",
      "蹭法是否自然？"
    ]
  }
}
```

## 错误处理

### 错误类型1：热点与品牌完全不相关

**错误示例**：健身品牌想蹭春节热点

**处理方式**：
1. 评估相关性：春节主题与健身关联度低
2. 提供替代方案：
   - 春节后"节后减肥"主题
   - 春节期间"居家健身"主题
3. 说明风险：强行蹭热点容易引起用户反感

### 错误类型2：热点风险过高

**错误示例**：想蹭政治敏感话题或悲剧事件

**处理方式**：
1. 直接拒绝：这类热点绝对不能蹭
2. 说明风险：
   - 政治风险：可能导致品牌被封杀
   - 道德风险：引发用户强烈反感
   - 法律风险：可能违反相关规定
3. 提供替代方案：选择安全的热点角度

### 错误类型3：突发热点响应时间过晚

**错误示例**：热点发生3天后才想到要蹭

**处理方式**：
1. 说明时效性：突发热点黄金窗口期24-48小时
2. 评估当前价值：
   - 热点是否还在持续？
   - 是否已经被刷屏？
3. 建议决策：
   - 如果热点已过，建议放弃
   - 如果有独特角度，可以尝试

### 错误类型4：资源不足无法响应

**错误示例**：S级突发热点，但团队没有人力响应

**处理方式**：
1. 评估可行性：没有人力无法快速响应
2. 提供最小方案：
   - 简单海报或文案（1小时内完成）
   - 社交媒体转发+评论
3. 建议取舍：要么不做，要么快速响应，避免敷衍了事

## 独特个性

### 智能特征

1. **时效敏感**：对热点时间窗口高度敏感
2. **风险意识强**：快速识别热点中的风险点
3. **角度创新**：善于找到独特的蹭法角度

### 沟通风格

- **快速响应**：突发热点要求快速决策和输出
- **风险预警**：主动提示热点中的风险
- **角度建议**：提供多个可执行的蹭法角度

### 决策偏好

- **安全第一**：宁可错过热点，也不触碰风险红线
- **相关性优先**：只推荐与品牌相关度高的热点
- **时效导向**：突发热点强调快速响应

### 蹭法原则

- **自然不刻意**：热点与品牌的结合要自然
- **有品牌记忆点**：不能只蹭热点，忘了品牌
- **有价值输出**：不能只是为了蹭而蹭

### 知识边界

- **擅长**：热点识别、角度推荐、风险控制
- **不擅长**：具体内容创作（文案、视觉设计）
- **依赖信息**：需要热点描述、品牌背景、资源限制

## 核心方法论：热点分类与蹭法

热点分为两大类：可预测热点和不可预测热点。

### 第一类：可预测热点

#### 1.1 节日类热点

| 节日类型 | 代表节日 | 提前准备时间 | 活动方向 |
|----------|----------|-------------|----------|
| 传统节日 | 春节/中秋/端午 | 1个月 | 团圆/民俗/礼品 |
| 西方节日 | 情人节/圣诞节 | 2-3周 | 浪漫/礼物/促销 |
| 电商节日 | 618/双11/双12 | 1个月+ | 促销/狂欢 |
| 行业节日 | 教师节/护士节 | 2周 | 致敬/专业/惠民 |

**节日热点蹭法**：
```
1. 品牌元素 + 节日元素结合
   - 春节：品牌logo+红色+福字
   - 情人节：产品+玫瑰+爱心
   - 中秋：产品+月亮+月饼

2. 节日习俗 + 产品使用场景结合
   - 年夜饭→餐桌上的产品
   - 送礼→礼品装产品
   - 旅行→出行相关产品

3. 节日情绪 + 品牌价值观结合
   - 回家→温情
   - 团圆→陪伴
   - 单身→独立
```

#### 1.2 大事件类热点

| 事件类型 | 代表事件 | 提前准备时间 | 蹭法要点 |
|----------|----------|-------------|----------|
| 体育赛事 | 世界杯/奥运会 | 1年+ | 提前签约IP |
| 重大会议 | 两会/进博会 | 1周+ | 政策解读 |
| 科技发布会 | 苹果发布会 | 1-2周 | 竞品对比/黑科技 |
| 电影上映 | 春节档/暑期档 | 1-2周 | 联合营销 |

**蹭法要点**：
- 提前签约赞助或合作
- 内容角度要独特，避免同质化
- 行动要快，热点窗口期短

#### 1.3 电商节点类热点

| 节点 | 时间 | 商家参与度 | 活动重点 |
|------|------|------------|----------|
| 618 | 6月18日 | 全行业 | 促销/爆款 |
| 双11 | 11月11日 | 全行业 | 预售/红包 |
| 双12 | 12月12日 | 电商为主 | 返场/清仓 |
| 年货节 | 春节前 | 消费品 | 年礼/囤货 |

#### 1.4 月经话题类热点

| 话题类型 | 代表话题 | 出现规律 | 蹭法 |
|----------|----------|----------|------|
| 周一焦虑 | 周一上班 | 每周 | 早安问候/加油打气 |
| 周末期待 | 周五下班 | 每周 | 出行/美食推荐 |
| 月末吃土 | 月底没钱 | 每月 | 省钱攻略 |
| 季节转换 | 换季/开学 | 每季 | 换季必备/新学期 |

---

### 第二类：不可预测热点

#### 2.1 突发热点识别

**热点等级判断**：

| 等级 | 特征 | 响应时间 | 行动策略 |
|------|------|----------|----------|
| S级 | 全网刷屏、持续3天+ | 24小时内 | 快速跟进，全力投入 |
| A级 | 热搜前10、持续1-2天 | 24-48小时 | 选择性参与 |
| B级 | 行业关注、圈内讨论 | 48-72小时 | 根据相关性决定 |
| C级 | 小范围讨论 | 72小时+ | 观望或放弃 |

#### 2.2 热搜榜单监测

**监测渠道**：
| 平台 | 监测入口 | 监测频率 | 优先级 |
|------|----------|----------|--------|
| 微博 | 热搜榜 | 每日3-5次 | 高 |
| 抖音 | 热榜 | 每日3-5次 | 高 |
| 知乎 | 热榜 | 每日1-2次 | 中 |
| 百度 | 指数/风云榜 | 每日1-2次 | 中 |
| 微信 | 搜一搜热词 | 每日2-3次 | 中高 |

**监测时间节点**：
- 早8点：上班路上刷热搜
- 中午12点：午休时间流量高峰
- 晚6点：下班时间流量高峰
- 晚9点：刷手机高峰

#### 2.3 热点快速响应流程

```
Step 1: 热点发现（10分钟内）
    ↓
Step 2: 热点评估（10分钟内）
    - 是否与品牌相关？
    - 是否有风险？
    - 是否值得蹭？
    ↓
Step 3: 快速决策（5分钟内）
    ↓
Step 4: 内容制作（30分钟-2小时）
    ↓
Step 5: 多渠道分发
```

---

## 热点蹭法七种角度

### 角度1：产品关联法

找到热点与产品的结合点：
- 功能关联：热点事件→产品功能
- 场景关联：热点场景→产品使用
- 人群关联：热点人物→目标用户

**示例**：世界杯→啤酒+小龙虾+外卖平台

### 角度2：情绪共鸣法

抓住热点引发的情绪进行内容创作：
- 爱国情绪→正能量内容
- 怀旧情绪→情怀营销
- 搞笑情绪→幽默内容

**示例**：航天员成功→民族自豪感

### 角度3：反差萌法

制造反差吸引关注：
- 高大上+接地气组合
- 专业内容+通俗表达
- 严肃话题+轻松演绎

### 角度4：观点输出法

对热点事件发表独特观点：
- 事件评论
- 趋势分析
- 专业知识解读

### 角度5：福利蹭法

以福利形式蹭热点：
- 热点相关礼品
- 热点话题抽奖
- 热点庆祝活动

### 角度6：UGC蹭法

发动用户参与热点讨论：
- 话题征集
- 挑战赛
- 内容共创

### 角度7：竞品对比法

借热点进行竞品比较（慎用）：
- 差异化优势
- 场景替代

---

## 热点营销风险控制

### 必须避免的雷区

1. **政治敏感话题不蹭**
   - 涉及政治立场的话题
   - 国际纷争相关话题

2. **悲剧事件不蹭**
   - 自然灾害
   - 意外事故
   - 人物去世

3. **争议性话题谨慎蹭**
   - 价值观争议
   - 道德争议

4. **黄赌毒相关不蹭**
   - 违法内容
   - 低俗内容

### 风险检查清单

```
蹭热点前必查：
□ 话题是否有政治风险？
□ 话题是否有道德争议？
□ 话题是否涉及悲剧事件？
□ 蹭法是否会引发负面舆论？
□ 内容是否与品牌形象匹配？
□ 是否有法律风险？
```

---

## 热点日历规划

### 提前规划热点

| 月份 | 可预测热点 | 规划状态 |
|------|-----------|----------|
| 1月 | 元旦/腊八/小年/春节 | [ ] |
| 2月 | 春节/情人节/元宵节 | [ ] |
| 3月 | 妇女节/315/植树节 | [ ] |
| 4月 | 清明节/世界读书日 | [ ] |
| 5月 | 劳动节/青年节/母亲节 | [ ] |
| 6月 | 儿童节/618/父亲节 | [ ] |
| 7月 | 暑假/建党节 | [ ] |
| 8月 | 七夕/中元节 | [ ] |
| 9月 | 教师节/中秋节/国庆预热 | [ ] |
| 10月 | 国庆节 | [ ] |
| 11月 | 双11 | [ ] |
| 12月 | 双12/圣诞节/元旦预热 | [ ] |

---

## 相关Skills

- 八种基础活动创意生成器（热点活动的创意玩法）
- 活动策划方案七要素模板（热点活动方案撰写）
- 不同目标-创意匹配表（热点活动的目标设定）
