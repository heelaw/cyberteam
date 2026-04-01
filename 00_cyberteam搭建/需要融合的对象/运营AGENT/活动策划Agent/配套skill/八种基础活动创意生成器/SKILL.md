---
name: 八种基础活动创意生成器
description: 提供8种基础活动玩法模板，帮助在创意枯竭时快速生成活动方案
trigger: ["做什么活动", "活动创意", "活动玩法", "怎么做活动"]
difficulty: medium
estimated_time: 10分钟
---

# 八种基础活动创意生成器

## 触发场景

当用户出现以下情况时触发本Skill：
- 不知道做什么活动
- 活动创意枯竭
- 需要快速生成活动方案
- 需要多样化活动玩法

## 输入输出格式

### 输入格式（JSON Schema）

```json
{
  "type": "object",
  "properties": {
    "activity_goal": {
      "type": "string",
      "enum": ["拉新", "促活", "成交", "传播"],
      "description": "活动目标类型"
    },
    "target_audience": {
      "type": "object",
      "properties": {
        "age_range": {
          "type": "string",
          "description": "年龄段，如'18-25岁'"
        },
        "user_profile": {
          "type": "string",
          "description": "用户画像描述"
        },
        "behavior_preference": {
          "type": "string",
          "description": "行为偏好"
        }
      }
    },
    "constraints": {
      "type": "object",
      "properties": {
        "budget_level": {
          "type": "string",
          "enum": ["高", "中", "低"],
          "description": "预算水平"
        },
        "development_cycle": {
          "type": "string",
          "description": "开发周期限制"
        },
        "resource_limitations": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "资源限制"
        }
      }
    },
    "preferences": {
      "type": "object",
      "properties": {
        "preferred_mechanics": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "偏好的玩法类型（可选）"
        },
        "excluded_mechanics": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "排除的玩法类型（可选）"
        }
      }
    }
  },
  "required": ["activity_goal"]
}
```

### 输出格式（JSON Schema）

```json
{
  "type": "object",
  "properties": {
    "recommended_mechanics": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "mechanic_name": {
            "type": "string",
            "description": "玩法名称"
          },
          "match_score": {
            "type": "number",
            "minimum": 1,
            "maximum": 5,
            "description": "匹配度评分（1-5星）"
          },
          "core_design": {
            "type": "object",
            "properties": {
              "mechanism_description": {"type": "string"},
              "reward_design": {"type": "string"},
              "participation_path": {"type": "string"},
              "innovation_points": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              }
            }
          },
          "pros_and_cons": {
            "type": "object",
            "properties": {
              "advantages": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              },
              "disadvantages": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              }
            }
          },
          "expected_performance": {
            "type": "object",
            "properties": {
              "participation_rate": {"type": "string"},
              "viral_coefficient": {"type": "string"},
              "cost_per_acquisition": {"type": "string"}
            }
          }
        }
      }
    },
    "combination_suggestions": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "combination": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "rationale": {"type": "string"},
          "expected_effect": {"type": "string"}
        }
      }
    },
    "customization_tips": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "aspect": {"type": "string"},
          "suggestion": {"type": "string"}
        }
      }
    }
  }
}
```

## 使用示例

### 示例1：拉新目标 - 年轻用户群体

**输入**：
```json
{
  "activity_goal": "拉新",
  "target_audience": {
    "age_range": "18-25岁",
    "user_profile": "大学生和职场新人，喜欢新鲜事物，乐于分享",
    "behavior_preference": "活跃于社交媒体，喜欢游戏化体验"
  },
  "constraints": {
    "budget_level": "中",
    "development_cycle": "2周"
  }
}
```

**输出**：
```json
{
  "recommended_mechanics": [
    {
      "mechanic_name": "测试答题",
      "match_score": 5,
      "core_design": {
        "mechanism_description": "设计10题趣味性格测试，完成测试后可查看详细报告，分享后解锁完整版",
        "reward_design": "测试报告+分享解锁完整版+邀请好友双方得优惠券",
        "participation_path": "看到海报→扫码答题→查看部分报告→分享解锁完整版",
        "innovation_points": ["结合当下热点话题", "测试结果具有社交货币属性", "分享后可看好友结果对比"]
      },
      "pros_and_cons": {
        "advantages": ["社交传播性强", "开发成本低", "用户参与门槛低"],
        "disadvantages": ["复访率低", "需要持续更新内容"]
      },
      "expected_performance": {
        "participation_rate": "预计10-15%",
        "viral_coefficient": "K=3-5",
        "cost_per_acquisition": "15-40元"
      }
    },
    {
      "mechanic_name": "小游戏",
      "match_score": 4,
      "core_design": {
        "mechanism_description": "简单易上手的小游戏（如跳一跳、消除类），通关后可抽奖，分享可复活",
        "reward_design": "游戏通关抽奖+每日挑战奖励+好友排行奖励",
        "participation_path": "进入游戏→开始游戏→通关/失败→抽奖→分享复活",
        "innovation_points": ["品牌元素融入游戏场景", "好友挑战功能", "每日签到奖励"]
      },
      "pros_and_cons": {
        "advantages": ["沉浸时间长", "品牌印象深", "年轻用户喜欢"],
        "disadvantages": ["开发成本高", "需要持续运营"]
      },
      "expected_performance": {
        "participation_rate": "预计20-30%",
        "viral_coefficient": "K=2-4",
        "cost_per_acquisition": "20-50元"
      }
    }
  ],
  "combination_suggestions": [
    {
      "combination": ["测试答题", "红包抽奖"],
      "rationale": "测试答题带来传播，红包抽奖提升转化",
      "expected_effect": "传播系数提升50%，注册转化率提升30%"
    }
  ],
  "customization_tips": [
    {
      "aspect": "话题选择",
      "suggestion": "选择与年轻人相关的话题，如MBTI、职业规划、情感话题"
    },
    {
      "aspect": "视觉设计",
      "suggestion": "采用年轻化、活泼的设计风格，使用emoji和流行梗"
    }
  ]
}
```

### 示例2：促活目标 - 职场用户

**输入**：
```json
{
  "activity_goal": "促活",
  "target_audience": {
    "age_range": "25-40岁",
    "user_profile": "职场人士，时间紧张，重视效率"
  },
  "constraints": {
    "budget_level": "低",
    "development_cycle": "1周"
  }
}
```

**输出**：
```json
{
  "recommended_mechanics": [
    {
      "mechanic_name": "打卡签到",
      "match_score": 5,
      "core_design": {
        "mechanism_description": "连续7天签到获得梯度奖励，补签机制降低门槛",
        "reward_design": "连续3天得小额奖励，7天得大额奖励，满勤得神秘大奖",
        "participation_path": "打开App→点击签到→查看奖励→完成每日任务",
        "innovation_points": ["补签卡机制", "签到日历展示", "连续奖励翻倍"]
      },
      "pros_and_cons": {
        "advantages": ["习惯养成强", "次日留存高", "开发成本低"],
        "disadvantages": ["创意空间有限", "长期参与疲劳"]
      },
      "expected_performance": {
        "participation_rate": "预计30-50%",
        "viral_coefficient": "K<1",
        "cost_per_acquisition": "按活跃用户计算"
      }
    }
  ],
  "combination_suggestions": [
    {
      "combination": ["打卡签到", "PK排名"],
      "rationale": "签到保持日活，PK排名提升参与度",
      "expected_effect": "DAU提升15-30%"
    }
  ]
}
```

## 错误处理

### 错误类型1：缺少活动目标

**错误示例**："给我想个活动创意"

**处理方式**：
1. 拒绝生成：没有目标无法推荐合适玩法
2. 引导明确目标：
   - 活动的主要目的是什么？（拉新/促活/成交/传播）
   - 当前最需要解决什么问题？
3. 提供快速参考：展示四种目标的典型场景

### 错误类型2：目标与玩法完全不匹配

**错误示例**：目标是成交，却想用打卡签到

**处理方式**：
1. 指出不匹配：打卡签到主要提升活跃，对成交帮助有限
2. 提供匹配建议：成交目标推荐红包抽奖、征集投稿
3. 说明例外情况：如果坚持用签到，建议结合促销设计

### 错误类型3：资源限制过于苛刻

**错误示例**：预算0元，开发时间1天，要求爆款活动

**处理方式**：
1. 说明现实情况：任何有质量的活动都需要一定资源
2. 提供最小可行方案：
   - 0预算：只能做纯运营活动（如征集投稿）
   - 1天开发：只能用现成模板或H5工具
3. 建议调整：要么降低期望，要么增加资源

### 错误类型4：要求同时使用所有玩法

**错误示例**："把8种玩法都用上"

**处理方式**：
1. 指出问题：玩法越多，用户理解成本越高，效果反而差
2. 推荐组合玩法：2-3种玩法组合效果最佳
3. 展示失败案例：某平台因玩法复杂导致参与率仅2%

## 独特个性

### 智能特征

1. **创意联想能力强**：能在不同玩法之间建立联系
2. **场景化思维**：根据具体场景推荐最合适的玩法
3. **组合创新**：善于将多种玩法组合产生新效果

### 沟通风格

- **灵感激发型**：通过举例激发用户更多想法
- **选择丰富型**：提供多种选项，不局限于单一方案
- **场景代入型**：用具体场景说明玩法效果

### 决策偏好

- **目标导向**：玩法选择完全服务于活动目标
- **用户中心**：推荐玩法时优先考虑目标用户偏好
- **效果可衡量**：每个推荐玩法都有预期效果数据

### 推荐逻辑

- **匹配优先**：先看目标匹配度，再看资源匹配度
- **组合思维**：单一玩法效果有限，主动推荐组合方案
- **风险提示**：主动说明每种玩法的风险和劣势

### 知识边界

- **擅长**：玩法推荐、组合建议、效果预估
- **不擅长**：具体创意细节设计（如文案、视觉）
- **依赖信息**：需要明确的目标、用户画像、资源限制

## 核心方法论：8种基础活动玩法

### 玩法1：打卡签到

**定义**：用户在指定时间段内连续签到，完成任务获得奖励

**核心要素**：
- 签到周期（7天/21天/30天）
- 补签机制（有/无）
- 奖励梯度（连续7天、连续21天、满勤）
- 展示效果（打卡日历、排行榜）

**适用目标**：促活、留存、传播

**优劣势**：
- 优势：用户习惯养成强，次日留存高
- 劣势：创意空间有限，容易疲劳

**典型案例**：
- 蚂蚁森林每日浇水
- 微信读书打卡挑战

---

### 玩法2：测试答题

**定义**：用户回答问题获取结果，分享后可解锁更多测试

**核心要素**：
- 题目数量（5-10题为宜）
- 结果类型（性格/知识/运势等）
- 分享机制（解锁完整版/查看好友结果）
- 二次传播设计

**适用目标**：拉新、传播

**优劣势**：
- 优势：社交属性强，传播性好
- 劣势：复访率低

**典型案例**：
- 网易云音乐年度听歌报告
- MBTI性格测试

---

### 玩法3：竞猜预测

**定义**：用户对事件结果进行预测，猜对获得奖励

**核心要素**：
- 预测事件（体育赛事/娱乐圈/商业决策）
- 竞猜时间窗口
- 奖励机制（积分/实物/虚拟权益）
- 排行展示

**适用目标**：促活、传播

**优劣势**：
- 优势：话题性强，互动性高
- 劣势：依赖事件时效性

**典型案例**：
- 世界杯比分预测
- 奥斯卡奖项竞猜

---

### 玩法4：PK排名

**定义**：用户之间进行竞争，通过排名获得奖励

**核心要素**：
- 竞争维度（速度/准确率/数量/质量）
- 分组机制（随机/实力匹配）
- 奖励梯度（前10%/前50%/参与奖）
- 反作弊机制

**适用目标**：拉新、促活、传播

**优劣势**：
- 优势：激励性强，参与度高
- 劣势：可能引发恶意竞争

**典型案例**：
- 王者荣耀段位赛
- 拼多多好友助力排名

---

### 玩法5：征集投稿

**定义**：用户提交自己的作品（文案/图片/视频），通过评选获得奖励

**核心要素**：
- 征集主题（必须与业务相关）
- 作品形式（图文/视频/故事）
- 评选机制（投票/评委/平台决定）
- 奖励设置

**适用目标**：拉新、成交、传播

**优劣势**：
- 优势：用户参与感强，可产生优质UGC
- 劣势：作品质量不可控

**典型案例**：
- 抖音挑战赛
- 小红书话题征集

---

### 玩法6：收集兑换

**定义**：用户通过各种行为收集碎片/道具，凑齐后兑换奖励

**核心要素**：
- 碎片种类（3-5种为宜）
- 收集方式（签到/分享/任务）
- 兑换门槛（集齐一套/集齐特定组合）
- 稀缺性设计（限定兑换时间/数量）

**适用目标**：促活、留存、成交、传播

**优劣势**：
- 优势：用户粘性高，周期长
- 劣势：设计复杂度高

**典型案例**：
- 支付宝集五福
- 各平台节日集卡活动

---

### 玩法7：红包抽奖

**定义**：用户通过抽奖获得现金或优惠券

**核心要素**：
- 抽奖门槛（免费/任务解锁/付费）
- 奖项设置（大奖引流+小奖促活）
- 中奖概率公示
- 提现门槛

**适用目标**：拉新、成交、促活

**优劣势**：
- 优势：吸引力强，效果直接
- 劣势：成本高，可能吸引羊毛党

**典型案例**：
- 拼多多现金红包
- 外卖平台新用户红包

---

### 玩法8：小游戏

**定义**：用户通过简单的小游戏获得奖励或排名

**核心要素**：
- 游戏类型（跳一跳/消除/合成/答题）
- 玩法时长（3-5分钟）
- 奖励机制（通关奖励/排名奖励/分享奖励）
- 社交互动（好友排名/挑战）

**适用目标**：促活、传播

**优劣势**：
- 优势：趣味性强，沉浸时间长
- 劣势：开发成本高

**典型案例**：
- 微信跳一跳
- 抖音小游戏

---

## 选择决策树

```
活动目标是什么？
├── 拉新
│   └── 推荐：红包抽奖、测试答题、PK排名、小游戏
├── 促活
│   └── 推荐：打卡签到、PK排名、竞猜预测、小游戏
├── 成交
│   └── 推荐：红包抽奖、征集投稿
└── 传播
    └── 推荐：测试答题、PK排名、收集兑换、小游戏
```

## 组合玩法建议

单一玩法效果有限，建议组合：

| 组合 | 玩法 | 效果 |
|------|------|------|
| 经典组合 | 打卡签到 + 收集兑换 | 高促活、高留存 |
| 拉新组合 | 红包抽奖 + PK排名 | 高拉新、高传播 |
| 话题组合 | 测试答题 + 竞猜预测 | 强传播、强互动 |
| 成交组合 | 红包抽奖 + 征集投稿 | 拉新 + 成交 |

## 注意事项

1. **玩法不是越复杂越好**：选择与目标匹配的玩法
2. **用户门槛要低**：参与路径不超过3步
3. **奖励要即时**：让用户尽快感受到收益
4. **社交设计要自然**：不要强迫分享

## 相关Skills

- 活动目标定义四要素（明确活动目标）
- 不同目标-创意匹配表（选择正确玩法）
- 活动创意自检清单（验证创意可行性）
