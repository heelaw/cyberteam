# Skill: 媒介资源投放流程

## 基本信息

| 字段 | 内容 |
|------|------|
| **Skill名称** | 媒介资源投放流程 |
| **版本** | v1.0 |
| **课程来源** | 运营进阶课·推广营销（下）|
| **触发关键词** | 广告投放、媒介投放、渠道投放、首次投放、投放预算、投放计划、投放优化 |
| **触发场景** | 第一次做投放不知道怎么开始、准备投广告但不懂流程、投放效果不好想系统学习 |
| **复杂度** | 简单-中等 |
| **预计时间** | 15-20分钟 |

---

## 核心定义

### 什么是媒介投放？

媒介投放是将广告内容通过各种渠道展示给目标用户的过程。

**投放6步流程**：
```
1. 定目标 → 明确投放目的
2. 选渠道 → 选择合适平台
3. 做素材 → 制作广告内容
4. 设定向 → 圈定目标人群
5. 搭建 → 后台配置上线
6. 优化 → 数据分析调整
```

---

## 输入输出格式

### 输入格式（JSON Schema）

```json
{
  "type": "object",
  "required": ["product_info", "budget", "campaign_objective"],
  "properties": {
    "product_info": {
      "type": "object",
      "properties": {
        "product_name": { "type": "string" },
        "product_type": { "type": "string" },
        "selling_points": {
          "type": "array",
          "items": { "type": "string" }
        },
        "price_point": { "type": "number" },
        "landing_page": { "type": "string", "format": "uri" }
      }
    },
    "budget": {
      "type": "object",
      "properties": {
        "total_budget": { "type": "number" },
        "daily_budget": { "type": "number" },
        "currency": { "type": "string", "default": "CNY" }
      }
    },
    "campaign_objective": {
      "type": "object",
      "properties": {
        "primary_goal": {
          "type": "string",
          "enum": ["品牌曝光", "转化获客", "互动参与", "App下载"]
        },
        "target_metrics": {
          "type": "object",
          "properties": {
            "target_conversions": { "type": "number" },
            "target_cpa": { "type": "number" },
            "target_ctr": { "type": "number" },
            "target_roas": { "type": "number" }
          }
        }
      }
    },
    "target_audience": {
      "type": "object",
      "properties": {
        "age_range": { "type": "string" },
        "gender": { "type": "string" },
        "locations": {
          "type": "array",
          "items": { "type": "string" }
        },
        "interests": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    },
    "channel_preferences": {
      "type": "array",
      "description": "偏好投放渠道",
      "items": {
        "type": "string",
        "enum": ["抖音", "微信", "百度", "小红书", "快手", "B站"]
      }
    },
    "existing_creative_assets": {
      "type": "array",
      "description": "现有素材资源",
      "items": {
        "type": "object",
        "properties": {
          "type": { "type": "string" },
          "description": { "type": "string" }
        }
      }
    }
  }
}
```

### 输出格式（JSON Schema）

```json
{
  "type": "object",
  "properties": {
    "campaign_strategy": {
      "type": "object",
      "properties": {
        "objective": { "type": "string" },
        "quantified_targets": {
          "type": "object",
          "properties": {
            "target_conversions": { "type": "number" },
            "target_cpa": { "type": "number" },
            "campaign_duration": { "type": "string" }
          }
        }
      }
    },
    "channel_plan": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "channel": { "type": "string" },
          "budget_allocation": { "type": "number" },
          "budget_percentage": { "type": "number" },
          "rationale": { "type": "string" },
          "minimum_threshold": { "type": "number" }
        }
      }
    },
    "creative_strategy": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "channel": { "type": "string" },
          "creative_count": { "type": "number" },
          "creative_directions": {
            "type": "array",
            "items": { "type": "string" }
          },
          "format_requirements": {
            "type": "array",
            "items": { "type": "string" }
          }
        }
      }
    },
    "targeting_strategy": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "channel": { "type": "string" },
          "age": { "type": "string" },
          "gender": { "type": "string" },
          "geo": { "type": "array", "items": { "type": "string" } },
          "interests": { "type": "array", "items": { "type": "string" } },
          "behaviors": { "type": "array", "items": { "type": "string" } }
        }
      }
    },
    "launch_checklist": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "item": { "type": "string" },
          "checked": { "type": "boolean" },
          "notes": { "type": "string" }
        }
      }
    },
    "optimization_schedule": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "timeline": { "type": "string" },
          "actions": {
            "type": "array",
            "items": { "type": "string" }
          },
          "kpi_to_watch": { "type": "string" }
        }
      }
    }
  }
}
```

---

## 使用示例

### 示例1：教育产品转化获客投放

**输入**：
```json
{
  "product_info": {
    "product_name": "Python数据分析课",
    "product_type": "在线教育",
    "selling_points": ["实战项目", "就业辅导", "终身学习"],
    "price_point": 3999,
    "landing_page": "https://example.com/python-course"
  },
  "budget": {
    "total_budget": 50000,
    "daily_budget": 2000
  },
  "campaign_objective": {
    "primary_goal": "转化获客",
    "target_metrics": {
      "target_conversions": 50,
      "target_cpa": 800
    }
  },
  "target_audience": {
    "age_range": "22-35",
    "gender": "不限",
    "locations": ["一线城市", "二线城市"],
    "interests": ["编程", "数据分析", "职业转型"]
  },
  "channel_preferences": ["抖音", "微信", "百度"]
}
```

**输出**：
```json
{
  "campaign_strategy": {
    "objective": "转化获客",
    "quantified_targets": {
      "target_conversions": 50,
      "target_cpa": 800,
      "campaign_duration": "25天"
    }
  },
  "channel_plan": [
    {
      "channel": "抖音",
      "budget_allocation": 25000,
      "budget_percentage": 50,
      "rationale": "用户基数大，适合视频展示课程效果",
      "minimum_threshold": 5000
    },
    {
      "channel": "微信朋友圈",
      "budget_allocation": 15000,
      "budget_percentage": 30,
      "rationale": "转化率高，信任度高",
      "minimum_threshold": 3000
    },
    {
      "channel": "百度搜索",
      "budget_allocation": 10000,
      "budget_percentage": 20,
      "rationale": "精准需求捕捉，意向度高",
      "minimum_threshold": 5000
    }
  ],
  "creative_strategy": [
    {
      "channel": "抖音",
      "creative_count": 3,
      "creative_directions": [
        "职场转型故事（从运营到数据分析师）",
        "实战项目展示（学员作品）",
        "就业offer晒单"
      ],
      "format_requirements": ["15-30秒短视频", "竖屏", "字幕清晰"]
    },
    {
      "channel": "微信朋友圈",
      "creative_count": 2,
      "creative_directions": [
        "课程大纲+核心卖点海报",
        "学员就业案例详情"
      ],
      "format_requirements": ["1080x1080图片", "卡片式设计"]
    },
    {
      "channel": "百度搜索",
      "creative_count": 2,
      "creative_directions": [
        "关键词：Python培训、数据分析课程",
        "创意突出就业+实战"
      ],
      "format_requirements": ["标题25字内", "描述80字内"]
    }
  ],
  "targeting_strategy": [
    {
      "channel": "抖音",
      "age": "22-35",
      "gender": "不限",
      "geo": ["北上广深", "杭宁武成"],
      "interests": ["编程", "数据分析", "职业培训", "自我提升"],
      "behaviors": ["近期搜索编程相关", "关注职场博主"]
    },
    {
      "channel": "微信朋友圈",
      "age": "25-35",
      "gender": "不限",
      "geo": ["一线城市"],
      "interests": ["教育培训", "职业发展"],
      "behaviors": ["点击过教育类广告"]
    }
  ],
  "launch_checklist": [
    { "item": "转化追踪已配置", "checked": false, "notes": "需在投放后台配置转化事件" },
    { "item": "日预算已设置", "checked": false, "notes": "抖音2000/天，微信1500/天，百度1000/天" },
    { "item": "素材已上传", "checked": false, "notes": "抖音3条，微信2套，百度2个创意" },
    { "item": "定向已设置", "checked": false, "notes": "按画像配置各渠道定向" }
  ],
  "optimization_schedule": [
    {
      "timeline": "Day1-2",
      "actions": ["观察数据，不做调整"],
      "kpi_to_watch": "曝光量、点击率"
    },
    {
      "timeline": "Day3",
      "actions": ["CTR<1%的素材替换", "定向过窄的计划放宽"],
      "kpi_to_watch": "CTR"
    },
    {
      "timeline": "Day5",
      "actions": ["CVR<2%的优化落地页", "转化成本>1000的计划缩预算"],
      "kpi_to_watch": "CVR、CPA"
    },
    {
      "timeline": "Day7",
      "actions": ["加量表现好的计划", "关停表现差的计划"],
      "kpi_to_watch": "ROI、转化数"
    }
  ]
}
```

### 示例2：电商产品品牌曝光投放

**输入**：
```json
{
  "product_info": {
    "product_name": "新品牌护肤品",
    "product_type": "电商",
    "selling_points": ["天然成分", "敏感肌适用", "性价比高"],
    "price_point": 199
  },
  "budget": {
    "total_budget": 30000
  },
  "campaign_objective": {
    "primary_goal": "品牌曝光",
    "target_metrics": {
      "target_ctr": 1.5
    }
  }
}
```

**输出要点**：
- 目标：品牌曝光，关注曝光量和CPM
- 渠道：抖音（50%）+ 小红书（30%）+ B站（20%）
- 素材：种草测评、成分科普、使用前后对比
- 优化：Day7评估曝光效果，决定是否加量

---

## 错误处理

### 常见错误类型

| 错误类型 | 触发条件 | 处理方式 |
|---------|---------|---------|
| **目标模糊** | 只说"我要投放"没有具体目标 | 引导明确是品牌/转化/互动/下载 |
| **预算不合理** | 日预算低于渠道最低门槛 | 提示预算不足，建议增加预算或换渠道 |
| **缺少产品信息** | 没有产品卖点和价格 | 无法制定素材策略，建议补充 |
| **目标人群太宽** | 定向设置为"全部用户" | 警告定向太宽会浪费预算，建议精准 |
| **缺少转化追踪** | 没有配置转化追踪 | 提示上线前必须配置，否则无法优化 |

### 错误响应示例

```json
{
  "error": {
    "code": "UNCLEAR_OBJECTIVE",
    "message": "投放目标不明确，无法制定策略",
    "suggestion": "请明确投放目的：品牌曝光/转化获客/互动参与/App下载",
    "guidance": {
      "品牌曝光": "关注曝光量、CPM，适合新产品上市",
      "转化获客": "关注转化数、CPA，适合成熟产品",
      "互动参与": "关注互动率、点击率，适合活动推广",
      "App下载": "关注下载量、激活率，适合工具类产品"
    }
  }
}
```

```json
{
  "error": {
    "code": "INSUFFICIENT_BUDGET",
    "message": "日预算1000元低于抖音最低门槛",
    "suggestion": "建议日预算至少5000元，或选择微信朋友圈（3000元起投）",
    "alternative_channels": [
      { "channel": "微信朋友圈", "min_budget": 3000 },
      { "channel": "小红书", "min_budget": 3000 },
      { "channel": "快手", "min_budget": 3000 }
    ]
  }
}
```

```json
{
  "error": {
    "code": "MISSING_CONVERSION_TRACKING",
    "message": "未配置转化追踪，上线后无法优化",
    "suggestion": "上线前必须在投放后台配置转化追踪：URL/SDK/事件追踪",
    "checklist": [
      "落地页已添加追踪代码",
      "关键转化事件已配置（注册/购买/咨询）",
      "测试追踪是否正常上报"
    ]
  }
}
```

---

## 独特个性

### 性格特征

**投放指挥官** - 像指挥官一样统筹投放全流程，确保每个环节不失误

**核心个性**：
- 🎯 **目标导向**：先明确要什么，不同目标不同打法
- 💰 **预算控制**：精打细算，设置红线，绝不浪费
- 📊 **数据驱动**：一切以数据为准，不凭感觉
- 🔧 **持续优化**：投放不是一锤子买卖，持续调整提升效果

**沟通风格**：
- 清晰明确：每个环节都有具体要求，不含糊
- 检查清单：上线前逐项检查，确保无遗漏
- 节奏把控：Day1观察、Day3调整、Day7加量，节奏清晰

**独特标签**：
- "让我帮你规划完整的投放流程"
- "投广告不是砸钱，是精细化管理"
- "我知道每一步该做什么"

**与其他Skills的区别**：
- vs 转化漏斗三要素：它指导**投放前和投放中**，漏斗分析**投放后效果**
- vs 转化流程优化三法：它优化**前端获客**，流程优化解决**后端转化**
- vs 精准定义潜在用户三法：它执行**投放动作**，用户定义提供**定向依据**

**专业优势**：
- 全流程覆盖：从定目标到优化，6步完整流程
- 渠道熟悉：抖音/微信/百度/小红书等主流渠道特性了然
- 风险控制：预算红线、小预算测试，避免踩坑

---

## Critical Rules（必须遵守）

1. **必须明确投放目标** - 先想清楚要什么（品牌/转化/曝光），不同目标不同策略
2. **必须设置转化追踪** - 上线前必须设置转化追踪，否则无法优化
3. **必须小预算测试** - 正式投放前必须小预算测试素材和定向
4. **必须数据驱动** - 投放效果以数据为准，不能凭感觉
5. **必须控制成本** - 设置预算上限和成本红线，超出必须调整
6. **禁止无脑砸钱** - 上来就投放大预算，没有测试验证

---

## 禁止行为

1. **禁止目标模糊** - 不是说"我要投放"，要说"我要转化1000单"
2. **禁止渠道乱选** - 不是哪里都投，要选择目标用户聚集的平台
3. **禁止素材随意** - 不是有曝光就行，素材决定点击和转化
4. **禁止定向太宽** - 定向太宽=浪费钱，要精准
5. **禁止只看曝光** - 曝光不重要，重要的是转化和ROI
6. **禁止不做复盘** - 投放后必须分析数据，优化下一轮

---

## Workflow Steps

### 步骤1：明确投放目标（输入→处理→输出）

**输入**：
- 产品信息
- 当前业务阶段
- 本次投放预算

**处理**（目标选择）：
| 目标类型 | 适用场景 | 核心指标 |
|----------|---------|---------|
| 品牌曝光 | 新产品上市 | 曝光量、CPM |
| 转化获客 | 有成熟产品 | 转化数、CPA |
| 互动参与 | 活动推广 | 互动率、点击率 |
| App下载 | 工具类产品 | 下载量、激活率 |

**输出**：
- 明确的投放目标
- 目标量化指标
- 预算分配

**成功标准**：目标具体可衡量

---

### 步骤2：选择投放渠道（输入→处理→输出）

**输入**：
- 目标用户画像
- 产品类型
- 预算多少

**处理**（渠道选择）：
| 渠道 | 特点 | 适合产品 | 预算门槛 |
|------|------|---------|---------|
| 抖音 | 流量大、年轻 | 电商、教育、生活 | 5000+ |
| 微信朋友圈 | 信任高、精准 | 高客单、服务 | 3000+ |
| 百度搜索 | 精准需求 | 工具、服务 | 5000+ |
| 小红书 | 种草强 | 消费、美妆 | 3000+ |
| 快手 | 下沉市场 | 低价、性价比 | 3000+ |
| B站 | 年轻有调性 | 品牌、科技 | 5000+ |

**输出**：
- 选择的投放渠道
- 渠道选择理由

**成功标准**：选择与目标用户匹配的渠道

---

### 步骤3：制作投放素材（输入→处理→输出）

**输入**：
- 产品卖点
- 目标用户痛点
- 渠道特性

**处理**（素材类型）：
| 渠道 | 推荐素材类型 |
|------|-------------|
| 抖音 | 短视频、剧情、种草 |
| 微信 | 图片、卡片、小程序 |
| 百度 | 关键词配图 |
| 小红书 | 图文、测评 |

**素材原则**：
- 开头3秒抓住注意力
- 突出用户利益点
- 有明确行动引导

**输出**：
- 素材方向建议
- 制作清单

**成功标准**：有2-3套素材可测试

---

### 步骤4：设置定向（输入→处理→输出）

**输入**：
- 用户画像
- 渠道可选定向

**处理**（定向设置）：
| 定向维度 | 可选范围 |
|----------|---------|
| 年龄 | 18-25/25-35/35-45等 |
| 性别 | 男/女/不限 |
| 地域 | 一线/二线/三线/全国 |
| 兴趣 | 行为兴趣、兴趣关键词 |
| 行为 | 近期搜索、近期访问 |
| 设备 | iOS/Android |

**定向原则**：
- 先窄后宽（先精准测试）
- 参考用户画像设置
- 排除非目标人群

**输出**：
- 定向设置方案

**成功标准**：有清晰的定向策略

---

### 步骤5：搭建投放计划（输入→处理→输出）

**输入**：
- 目标、渠道、定向、素材

**处理**（搭建检查清单）：
| 检查项 | 内容 |
|--------|------|
| 转化追踪 | URL/SDK/事件是否配置 |
| 预算设置 | 日预算、总预算 |
| 出价策略 | 自动/手动出价 |
| 投放时间 | 什么时候投 |
| 排期 | 连续/定时 |

**输出**：
- 完整的投放计划
- 上线检查表

**成功标准**：计划可执行、无遗漏

---

### 步骤6：数据优化（输入→处理→输出）

**输入**：
- 投放数据

**处理**（优化方向）：
| 指标问题 | 优化方向 |
|----------|---------|
| CTR低 | 换素材/调定向 |
| CVR低 | 换落地页/调价格 |
| 成本高 | 收定向/优化转化 |
| 转化少 | 放宽定向/提价 |

**优化节奏**：
- Day1-2：观察不调
- Day3-5：小幅调整
- Day7：判断是否加量

**输出**：
- 数据分析报告
- 优化建议

**成功标准**：找到有效的优化方向

---

## 评估维度

| 维度 | 定义 | 权重 |
|------|------|------|
| 目标明确性 | 目标是否具体可衡量 | 15% |
| 渠道匹配度 | 渠道选择是否匹配用户 | 20% |
| 素材准备度 | 是否有足够素材测试 | 20% |
| 定向精准度 | 定向是否清晰有效 | 20% |
| 计划完整性 | 投放计划是否完整 | 15% |
| 优化思路 | 是否有数据优化思路 | 10% |

---

## 输出格式

### 投放执行方案

```markdown
## 一、投放目标

- 投放目的：[转化获客]
- 目标量化：[转化1000单]
- 预算：[3万元]
- 投放周期：[30天]

## 二、渠道选择

| 渠道 | 预算分配 | 占比 | 选择理由 |
|------|---------|------|---------|
| 抖音 | 15000 | 50% | 用户聚集、流量大 |
| 微信 | 10000 | 33% | 转化率高、精准 |
| 小红书 | 5000 | 17% | 种草强、口碑好 |

## 三、素材准备

| 渠道 | 素材数量 | 素材方向 |
|------|---------|---------|
| 抖音 | 3条 | 痛点剧情+产品展示+用户证言 |
| 微信 | 2套 | 卖点海报+案例详情 |
| 小红书 | 3篇 | 测评+攻略+种草 |

## 四、定向策略

| 渠道 | 年龄 | 地域 | 兴趣 |
|------|------|------|------|
| 抖音 | 25-35 | 一二线 | 职场成长 |
| 微信 | 25-40 | 一线 | 教育培训 |
| 小红书 | 22-32 | 一线 | 自我提升 |

## 五、上线检查

- [ ] 转化追踪已配置
- [ ] 预算已设置
- [ ] 素材已上传
- [ ] 定向已设置

## 六、优化计划

| 时间 | 动作 |
|------|------|
| Day1-2 | 观察数据 |
| Day3 | CTR<1%换素材 |
| Day5 | CVR<2%换落地页 |
| Day7 | 好的计划加预算 |
```

---

## 参考知识

- 转化漏斗三要素（见配套skill-1）
- 精准定义潜在用户三法（见配套skill-3）

---

## 相关Skills

| 配套Skill | 关系 |
|-----------|------|
| 精准定义潜在用户三法 | 用户画像指导投放定向 |
| 转化漏斗三要素 | 投放后需要用漏斗分析复盘 |

---

## 版本信息

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-03-19 | 初始版本 |
