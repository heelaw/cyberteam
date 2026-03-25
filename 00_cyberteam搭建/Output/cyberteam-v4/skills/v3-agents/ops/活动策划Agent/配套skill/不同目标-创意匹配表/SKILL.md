---
name: 不同目标-创意匹配表
description: 提供活动目标与活动类型的匹配对照表，帮助快速选择正确的活动类型
trigger: ["拉新用什么活动", "促活用什么", "成交活动推荐", "传播活动方案", "活动类型选择"]
difficulty: simple
estimated_time: 5分钟
---

# 不同目标-创意匹配表

## 触发场景

当用户出现以下情况时触发本Skill：
- 明确了活动目标，不知道用什么活动形式
- 需要快速匹配合适的活动类型
- 有多个活动类型可选，需要决策建议
- 需要说服团队/领导选择特定活动类型

## 输入输出格式

### 输入格式（JSON Schema）

```json
{
  "type": "object",
  "properties": {
    "activity_goal": {
      "type": "string",
      "enum": ["拉新", "促活", "成交", "传播", "组合目标"],
      "description": "活动目标类型"
    },
    "goal_details": {
      "type": "object",
      "properties": {
        "primary_goal": {
          "type": "string",
          "description": "主要目标"
        },
        "secondary_goal": {
          "type": "string",
          "description": "次要目标（可选）"
        },
        "quantified_target": {
          "type": "string",
          "description": "量化目标"
        }
      },
      "required": ["primary_goal"]
    },
    "target_audience": {
      "type": "object",
      "properties": {
        "age_range": {
          "type": "string",
          "description": "年龄段"
        },
        "user_profile": {
          "type": "string",
          "description": "用户画像"
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
          "description": "开发周期"
        },
        "team_capability": {
          "type": "string",
          "description": "团队能力"
        }
      }
    },
    "decision_context": {
      "type": "object",
      "properties": {
        "alternatives": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "已有备选方案（可选）"
        },
        "stakeholders": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "决策相关方（可选）"
        }
      }
    }
  },
  "required": ["activity_goal", "goal_details"]
}
```

### 输出格式（JSON Schema）

```json
{
  "type": "object",
  "properties": {
    "recommendation_result": {
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
              "match_reason": {
                "type": "string",
                "description": "匹配理由"
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
                  "effectiveness": {"type": "string"},
                  "cost_reference": {"type": "string"},
                  "suitable_for": {"type": "string"}
                }
              }
            }
          }
        },
        "decision_tree_result": {
          "type": "object",
          "properties": {
            "decision_path": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "question": {"type": "string"},
                  "answer": {"type": "string"},
                  "next_step": {"type": "string"}
                }
              }
            },
            "final_recommendation": {"type": "string"}
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
          "combination_logic": {"type": "string"},
          "expected_synergy": {"type": "string"}
        }
      }
    },
    "comparison_matrix": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "mechanic": {"type": "string"},
          "goal_match": {"type": "string"},
          "user_match": {"type": "string"},
          "resource_match": {"type": "string"},
          "overall_score": {"type": "number"}
        }
      }
    },
    "justification_for_stakeholders": {
      "type": "object",
      "properties": {
        "business_value": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "risk_assessment": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "success_criteria": {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      }
    }
  }
}
```

## 使用示例

### 示例1：拉新目标匹配

**输入**：
```json
{
  "activity_goal": "拉新",
  "goal_details": {
    "primary_goal": "新增注册用户5000人",
    "quantified_target": "CPA≤30元/人"
  },
  "target_audience": {
    "age_range": "25-40岁",
    "user_profile": "职场人群，时间紧张，注重效率",
    "behavior_preference": "活跃于微信，偏好实用内容"
  },
  "constraints": {
    "budget_level": "中",
    "development_cycle": "2周"
  },
  "decision_context": {
    "stakeholders": ["产品总监", "市场部负责人"]
  }
}
```

**输出**：
```json
{
  "recommendation_result": {
    "recommended_mechanics": [
      {
        "mechanic_name": "红包抽奖",
        "match_score": 5,
        "match_reason": "利益驱动直接，职场人群对红包敏感，转化效果好",
        "pros_and_cons": {
          "advantages": ["效果直接", "转化快", "用户理解成本低"],
          "disadvantages": ["成本高", "可能吸引羊毛党", "品牌价值传递弱"]
        },
        "expected_performance": {
          "effectiveness": "CPA 10-30元/人，转化率30-50%",
          "cost_reference": "5000人×30元=15万预算",
          "suitable_for": "快速拉新，短期冲刺"
        }
      },
      {
        "mechanic_name": "测试答题",
        "match_score": 4,
        "match_reason": "社交传播强，适合职场人群的分享偏好",
        "pros_and_cons": {
          "advantages": ["传播性强", "成本相对低", "内容营销价值"],
          "disadvantages": ["拉新转化率偏低", "需要持续更新内容"]
        },
        "expected_performance": {
          "effectiveness": "CPA 15-40元/人，传播系数K=3-5",
          "cost_reference": "5000人×25元=12.5万预算",
          "suitable_for": "品牌曝光+口碑传播"
        }
      }
    ],
    "decision_tree_result": {
      "decision_path": [
        {
          "question": "用户画像是什么？",
          "answer": "职场人群（25-40岁）",
          "next_step": "推荐：红包抽奖 > 测试答题 > PK排名"
        },
        {
          "question": "预算多少？",
          "answer": "中等预算",
          "next_step": "推荐：红包抽奖+推广投放 或 测试答题+社交传播"
        }
      ],
      "final_recommendation": "首选红包抽奖（主）+ 测试答题（辅）组合策略"
    }
  },
  "combination_suggestions": [
    {
      "combination": ["红包抽奖", "测试答题"],
      "combination_logic": "红包抽奖负责拉新转化，测试答题负责社交传播",
      "expected_synergy": "传播系数提升50%，综合CPA降低20%"
    }
  ],
  "comparison_matrix": [
    {
      "mechanic": "红包抽奖",
      "goal_match": "★★★★★",
      "user_match": "★★★★",
      "resource_match": "★★★★",
      "overall_score": 4.7
    },
    {
      "mechanic": "测试答题",
      "goal_match": "★★★★",
      "user_match": "★★★★",
      "resource_match": "★★★★★",
      "overall_score": 4.3
    },
    {
      "mechanic": "PK排名",
      "goal_match": "★★★",
      "user_match": "★★",
      "resource_match": "★★★",
      "overall_score": 2.7
    }
  ],
  "justification_for_stakeholders": {
    "business_value": [
      "红包抽奖：直接转化，ROI可预期，15万预算带来5000新用户，CPA 30元符合行业水平",
      "测试答题：社交传播带来额外曝光，提升品牌认知，为后续活动积累用户基础"
    ],
    "risk_assessment": [
      "红包抽奖风险：羊毛党风险，需要设置风控机制（手机号验证、IP限制）",
      "测试答题风险：内容质量风险，需要专业团队策划和设计"
    ],
    "success_criteria": [
      "核心指标：新增注册用户≥5000人",
      "成本指标：CPA≤30元/人",
      "质量指标：新用户次日留存≥40%"
    ]
  }
}
```

### 示例2：促活目标匹配

**输入**：
```json
{
  "activity_goal": "促活",
  "goal_details": {
    "primary_goal": "DAU从5万提升至6万",
    "quantified_target": "增长20%"
  },
  "target_audience": {
    "user_profile": "已有注册用户，但活跃度下降"
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
  "recommendation_result": {
    "recommended_mechanics": [
      {
        "mechanic_name": "打卡签到",
        "match_score": 5,
        "match_reason": "习惯养成强，开发成本低，适合低预算促活",
        "pros_and_cons": {
          "advantages": ["次日留存高", "开发成本低", "用户习惯养成强"],
          "disadvantages": ["创意空间有限", "长期参与疲劳"]
        },
        "expected_performance": {
          "effectiveness": "DAU提升15-30%，次日留存提升至50%+",
          "cost_reference": "奖励成本按活跃用户计算，相对较低",
          "suitable_for": "长期促活运营"
        }
      }
    ],
    "decision_tree_result": {
      "decision_path": [
        {
          "question": "当前最大问题是什么？",
          "answer": "用户流失严重",
          "next_step": "推荐：打卡签到（习惯绑定）"
        }
      ],
      "final_recommendation": "打卡签到+连续奖励梯度设计"
    }
  },
  "combination_suggestions": [
    {
      "combination": ["打卡签到", "竞猜预测"],
      "combination_logic": "签到保持日活，竞猜提升参与度",
      "expected_synergy": "DAU提升20-30%，用户参与时长提升"
    }
  ]
}
```

## 错误处理

### 错误类型1：目标不明确

**错误示例**："提升用户活跃度"（没有量化）

**处理方式**：
1. 拒绝匹配：没有量化目标无法推荐合适玩法
2. 引导明确目标：
   - 当前基线数据是什么？
   - 期望提升到什么程度？
   - 时间期限是多久？
3. 推荐使用"活动目标定义四要素"Skill先明确目标

### 错误类型2：目标与资源严重不匹配

**错误示例**：拉新10万人，预算0元

**处理方式**：
1. 识别矛盾：0预算无法拉新10万人
2. 提供数据参考：拉新成本行业均值10-30元/人
3. 建议调整：
   - 方案A：降低目标至合理范围
   - 方案B：增加预算
   - 方案C：选择低成本玩法（如征集投稿），但调整期望

### 错误类型3：用户画像缺失

**错误示例**：只有目标，没有用户信息

**处理方式**：
1. 说明重要性：不同用户偏好不同玩法
2. 提供快速判断：
   - 年轻用户（18-25岁）：推荐测试答题、小游戏
   - 职场人群（25-40岁）：推荐红包抽奖、打卡签到
   - 中老年用户（40岁+）：推荐红包抽奖、征集投稿
3. 建议补充：提供用户画像信息以便精准推荐

### 错误类型4：多目标冲突

**错误示例**：既要拉新10万人，又要成交100万GMV

**处理方式**：
1. 识别冲突：新用户首单转化率低，双目标难以同时达成
2. 分析可行性：
   - 假设客单价100元，100万GMV需要1万人成交
   - 10万新用户需要1万人成交，转化率需10%
   - 行业新用户首单转化率通常<5%
3. 建议分阶段或调整目标：
   - 分阶段：阶段一拉新，阶段二成交转化
   - 调整目标：降低拉新目标或降低GMV目标

## 独特个性

### 智能特征

1. **匹配导向**：所有推荐基于目标-玩法匹配度
2. **决策辅助**：不仅给出推荐，还提供决策依据
3. **全局视角**：考虑目标、用户、资源三个维度的匹配

### 沟通风格

- **数据说话**：用匹配度评分和数据支撑推荐
- **对比清晰**：通过对比矩阵展示不同玩法的优劣
- **说服力强**：提供向利益相关方说明的依据

### 决策偏好

- **目标第一**：玩法选择完全服务于活动目标
- **用户匹配**：选择目标用户喜欢的形式
- **资源匹配**：考虑预算、时间、团队资源限制

### 推荐逻辑

- **单一目标**：推荐最匹配的1-2种玩法
- **组合目标**：推荐组合玩法方案
- **优先级排序**：按匹配度排序，明确首选和备选

### 知识边界

- **擅长**：目标-玩法匹配、决策辅助、方案对比
- **不擅长**：具体创意细节设计
- **依赖信息**：需要明确的目标、用户画像、资源限制

## 核心方法论：目标-创意匹配矩阵

### 匹配总表

| 活动目标 | 推荐活动类型 | 推荐理由 | 适用场景 | 注意事项 |
|----------|--------------|----------|----------|----------|
| **拉新** | 红包抽奖 | 利益驱动，效果直接 | 用户获取初期 | 需要风控防羊毛党 |
| **拉新** | 测试答题 | 社交传播强 | 品牌曝光/口碑 | 拉新转化率偏低 |
| **拉新** | PK排名 | 竞争激励强 | 用户活跃社区 | 需要种子用户基础 |
| **拉新** | 小游戏 | 沉浸时间长 | 年轻用户群体 | 开发成本高 |
| **促活** | 打卡签到 | 习惯养成强 | 提升留存 | 需要持续激励 |
| **促活** | PK排名 | 竞争激励强 | 提升DAU | 可能引发恶意竞争 |
| **促活** | 竞猜预测 | 话题互动强 | 事件驱动活跃 | 依赖热点事件 |
| **促活** | 征集投稿 |UGC产出高 | 内容社区 | 内容质量难控制 |
| **成交** | 红包抽奖 | 利益直接 | 大促转化 | 利润空间压缩 |
| **成交** | 征集投稿 | 社交背书 | 高客单价 | 转化周期长 |
| **传播** | 测试答题 | 分享意愿强 | 口碑传播 | 需要话题性 |
| **传播** | PK排名 | 炫耀攀比 | 社交竞争 | 用户理解成本 |
| **传播** | 收集兑换 | 稀缺驱动 | 话题传播 | 规则复杂度 |
| **传播** | 小游戏 | 沉浸有趣 | 病毒传播 | 开发成本高 |

---

## 分目标详细匹配

### 拉新目标匹配

#### 拉新首选推荐

| 活动类型 | 匹配度 | 核心优势 | 核心劣势 | CPA参考 |
|----------|--------|----------|----------|---------|
| **红包抽奖** | ★★★★★ | 效果直接、转化快 | 羊毛党、成本高 | 10-30元 |
| **测试答题** | ★★★★ | 传播性强、内容营销 | 转化率低 | 15-40元 |
| **小游戏** | ★★★★ | 沉浸时间长、品牌印象深 | 开发成本高 | 20-50元 |
| **PK排名** | ★★★ | 竞争激励、持续参与 | 需要用户基础 | 15-35元 |

#### 拉新活动选择决策树

```
拉新目标
  ↓
用户画像是什么？
  ├── 年轻用户（18-25岁）
  │   └── 推荐：测试答题 > 小游戏 > 红包抽奖
  ├── 职场人群（25-40岁）
  │   └── 推荐：红包抽奖 > 测试答题 > PK排名
  └── 中老年用户（40岁+）
      └── 推荐：红包抽奖 > 打卡签到 > 征集投稿
  ↓
预算多少？
  ├── 预算充足
  │   └── 推荐：红包抽奖 + 推广投放
  └── 预算有限
      └── 推荐：低成本传播型（测试答题/小游戏）
```

---

### 促活目标匹配

#### 促活首选推荐

| 活动类型 | 匹配度 | 核心优势 | 核心劣势 | 促活效果 |
|----------|--------|----------|----------|----------|
| **打卡签到** | ★★★★★ | 习惯养成、次留高 | 创意有限 | DAU+15-30% |
| **PK排名** | ★★★★ | 激励强、竞争氛围 | 可能过度竞争 | DAU+10-25% |
| **竞猜预测** | ★★★★ | 话题性强、互动高 | 依赖热点 | DAU+10-20% |
| **征集投稿** | ★★★ | 内容产出、用户粘性 | 质量难控 | DAU+5-15% |

#### 促活活动选择决策树

```
促活目标
  ↓
当前最大问题是什么？
  ├── 用户流失严重
  │   └── 推荐：打卡签到（习惯绑定）
  ├── 用户不活跃
  │   └── 推荐：PK排名/竞猜预测（激励驱动）
  ├── 用户不回访
  │   └── 推荐：竞猜预测（话题吸引）
  └── 用户不贡献内容
      └── 推荐：征集投稿（UGC激励）
  ↓
用户使用频率？
  ├── 高频产品（日活）
  │   └── 推荐：打卡签到 + 连续奖励
  └── 低频产品（周活）
      └── 推荐：竞猜预测 + 话题运营
```

---

### 成交目标匹配

#### 成交首选推荐

| 活动类型 | 匹配度 | 核心优势 | 核心劣势 | 转化率提升 |
|----------|--------|----------|----------|------------|
| **红包抽奖** | ★★★★★ | 利益直接、紧迫感强 | 利润压缩、羊毛党 | +30-50% |
| **征集投稿** | ★★★★ | 社交背书、口碑传播 | 转化周期长 | +15-25% |
| **PK排名** | ★★★ | 竞争攀比、购买冲动 | 场景匹配度 | +10-20% |
| **打卡签到** | ★★★ | 用户粘性、复购 | 促销属性弱 | +5-15% |

#### 成交活动选择决策树

```
成交目标
  ↓
客单价高低？
  ├── 高客单价（1000元+）
  │   └── 推荐：征集投稿（口碑）+ 会员专属红包
  └── 低客单价（100元以下）
      └── 推荐：红包抽奖（直接优惠）
  ↓
用户购买决策周期？
  ├── 短决策（冲动消费）
  │   └── 推荐：红包抽奖 + 限时优惠
  └── 长决策（计划消费）
      └── 推荐：征集投稿 + 口碑积累
```

---

### 传播目标匹配

#### 传播首选推荐

| 活动类型 | 匹配度 | 核心优势 | 核心劣势 | 传播系数 |
|----------|--------|----------|----------|----------|
| **测试答题** | ★★★★★ | 分享意愿高、话题性强 | 需持续更新内容 | K=3-5 |
| **小游戏** | ★★★★ | 沉浸有趣、易分享 | 开发成本高 | K=2-4 |
| **收集兑换** | ★★★★ | 稀缺驱动、二次传播 | 规则复杂 | K=2-3 |
| **PK排名** | ★★★★ | 炫耀攀比、竞争分享 | 理解成本 | K=1.5-3 |

#### 传播活动选择决策树

```
传播目标
  ↓
希望达到什么传播效果？
  ├── 病毒式传播（K>3）
  │   └── 推荐：测试答题 + 分享解锁
  ├── 社交传播（K=2-3）
  │   └── 推荐：小游戏 + 排行榜
  └── 口碑传播（K<2）
      └── 推荐：征集投稿 + UGC激励
  ↓
目标用户是什么人？
  ├── 年轻人（爱分享）
  │   └── 推荐：测试答题 + 小游戏
  └── 职场人群（偏内敛）
      └── 推荐：PK排名 + 站内竞争
```

---

## 活动组合匹配

### 单一目标活动

| 目标 | 推荐活动 | 组合建议 |
|------|----------|----------|
| 纯拉新 | 红包抽奖 | 聚焦单一利益点 |
| 纯促活 | 打卡签到 | 配合连续奖励 |
| 纯成交 | 红包抽奖 + 限时 | 紧迫感+利益 |
| 纯传播 | 测试答题 | 话题+分享 |

### 多目标活动组合

| 目标组合 | 推荐活动组合 | 组合逻辑 |
|----------|--------------|----------|
| 拉新 + 成交 | 红包抽奖 + 满减券 | 拉新+成交双重驱动 |
| 拉新 + 传播 | 测试答题 + 分享解锁 | 传播+拉新双重驱动 |
| 促活 + 传播 | PK排名 + 分享奖励 | 竞争+分享双重驱动 |
| 拉新 + 促活 | 红包抽奖 + 打卡签到 | 新用户拉新+老用户促活 |

### 完整活动策划推荐

| 目标优先级 | 推荐活动组合 | 说明 |
|------------|--------------|------|
| 拉新为主 | 红包抽奖（主）+ 测试答题（辅） | 主活动拉新，辅活动传播 |
| 促活为主 | 打卡签到（主）+ 竞猜预测（辅） | 主活动稳留存，辅活动提互动 |
| 成交为主 | 红包抽奖（主）+ 征集投稿（辅） | 主活动促转化，辅活动造口碑 |
| 传播为主 | 测试答题（主）+ 小游戏（辅） | 双传播引擎 |

---

## 匹配表使用指南

### 快速查询

1. **确定活动目标**（参考活动目标定义四要素）
2. **查询匹配表**（按目标找推荐活动）
3. **参考决策树**（结合具体场景细化选择）
4. **组合优化**（多目标时考虑活动组合）

### 选择原则

```
核心原则：
1. 目标第一：活动形式服务于活动目标
2. 用户匹配：选择目标用户喜欢的形式
3. 资源匹配：考虑技术/预算资源限制
4. 组合思维：多目标时考虑活动组合
```

---

## 相关Skills

- 活动目标定义四要素（明确活动目标）
- 八种基础活动创意生成器（生成具体活动方案）
- 活动创意自检清单（验证选择是否正确）
- 活动策划方案七要素模板（撰写完整活动方案）
