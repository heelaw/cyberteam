---
name: 活动策划方案七要素模板
description: 提供标准化活动策划方案结构，包含活动目标/主题/时间/创意/流程/推广渠道/预算七要素
trigger: ["活动方案怎么写", "活动策划案", "活动策划方案", "活动计划"]
difficulty: medium
estimated_time: 15分钟
---

# 活动策划方案七要素模板

## 触发场景

当用户出现以下情况时触发本Skill：
- 不知道活动方案怎么写
- 需要撰写正式的活动策划案
- 需要向领导/团队汇报活动计划
- 需要梳理完整的活动执行方案

## 输入输出格式

### 输入格式（JSON Schema）

```json
{
  "type": "object",
  "properties": {
    "activity_basics": {
      "type": "object",
      "properties": {
        "activity_name": {
          "type": "string",
          "description": "活动名称"
        },
        "activity_goal": {
          "type": "string",
          "description": "活动目标"
        },
        "selected_mechanic": {
          "type": "string",
          "description": "选定的活动玩法"
        }
      },
      "required": ["activity_name", "activity_goal"]
    },
    "execution_context": {
      "type": "object",
      "properties": {
        "target_audience": {
          "type": "string",
          "description": "目标用户"
        },
        "budget_range": {
          "type": "string",
          "description": "预算范围"
        },
        "timeline": {
          "type": "string",
          "description": "时间安排"
        },
        "available_channels": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "可用渠道"
        }
      }
    },
    "creative_inputs": {
      "type": "object",
      "properties": {
        "theme_idea": {
          "type": "string",
          "description": "主题创意（可选）"
        },
        "mechanism_detail": {
          "type": "string",
          "description": "玩法细节（可选）"
        },
        "reward_plan": {
          "type": "string",
          "description": "奖励方案（可选）"
        }
      }
    },
    "document_requirements": {
      "type": "object",
      "properties": {
        "format": {
          "type": "string",
          "enum": ["完整方案", "简版方案", "PPT大纲"],
          "description": "文档格式要求"
        },
        "audience": {
          "type": "string",
          "description": "汇报对象"
        },
        "emphasis": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "重点强调的内容"
        }
      }
    }
  },
  "required": ["activity_basics"]
}
```

### 输出格式（JSON Schema）

```json
{
  "type": "object",
  "properties": {
    "document_structure": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "section": {
            "type": "string",
            "description": "章节名称"
          },
          "content": {
            "type": "string",
            "description": "章节内容"
          },
          "key_points": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "关键要点"
          }
        }
      }
    },
    "seven_elements": {
      "type": "object",
      "properties": {
        "element1_goal": {
          "type": "object",
          "properties": {
            "goal_type": {"type": "string"},
            "quantified_target": {"type": "string"},
            "goal_breakdown": {"type": "array"}
          }
        },
        "element2_theme": {
          "type": "object",
          "properties": {
            "theme_name": {"type": "string"},
            "creative_source": {"type": "string"},
            "visual_style": {"type": "string"}
          }
        },
        "element3_timeline": {
          "type": "object",
          "properties": {
            "preheat_period": {"type": "string"},
            "activity_period": {"type": "string"},
            "after_event_period": {"type": "string"}
          }
        },
        "element4_creative": {
          "type": "object",
          "properties": {
            "activity_form": {"type": "string"},
            "core_mechanism": {"type": "string"},
            "reward_design": {"type": "string"},
            "innovation_points": {"type": "array"}
          }
        },
        "element5_flow": {
          "type": "object",
          "properties": {
            "entry_requirement": {"type": "string"},
            "participation_path": {"type": "array"},
            "key_touchpoints": {"type": "array"},
            "interruption_handling": {"type": "string"}
          }
        },
        "element6_channels": {
          "type": "object",
          "properties": {
            "internal_channels": {"type": "array"},
            "external_channels": {"type": "array"},
            "paid_channels": {"type": "array"},
            "private_channels": {"type": "array"}
          }
        },
        "element7_budget": {
          "type": "object",
          "properties": {
            "reward_cost": {"type": "string"},
            "promotion_cost": {"type": "string"},
            "technical_cost": {"type": "string"},
            "operation_cost": {"type": "string"},
            "total_budget": {"type": "string"},
            "roi_projection": {"type": "string"}
          }
        }
      }
    },
    "quality_checklist": {
      "type": "object",
      "properties": {
        "completeness_check": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "item": {"type": "string"},
              "status": {"type": "string"},
              "note": {"type": "string"}
            }
          }
        },
        "rationality_check": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "item": {"type": "string"},
              "status": {"type": "string"},
              "note": {"type": "string"}
            }
          }
        },
        "risk_check": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "item": {"type": "string"},
              "status": {"type": "string"},
              "note": {"type": "string"}
            }
          }
        }
      }
    },
    "next_actions": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "action": {"type": "string"},
          "priority": {"type": "string"},
          "owner": {"type": "string"},
          "deadline": {"type": "string"}
        }
      }
    }
  }
}
```

## 使用示例

### 示例1：电商618活动方案

**输入**：
```json
{
  "activity_basics": {
    "activity_name": "618品质生活节",
    "activity_goal": "活动期间GMV达到500万，新增用户5万",
    "selected_mechanic": "红包抽奖+满减促销"
  },
  "execution_context": {
    "target_audience": "25-40岁城市白领",
    "budget_range": "100万",
    "timeline": "预热期6.1-6.15，正式期6.16-6.20",
    "available_channels": ["App", "微信公众号", "抖音", "微博", "社群"]
  },
  "creative_inputs": {
    "theme_idea": "品质生活，好物不贵",
    "reward_plan": "红包最高618元，满199减30，满399减80"
  },
  "document_requirements": {
    "format": "完整方案",
    "audience": "公司管理层",
    "emphasis": ["ROI预测", "风险评估", "执行细节"]
  }
}
```

**输出**：
```json
{
  "seven_elements": {
    "element1_goal": {
      "goal_type": "成交+拉新双目标",
      "quantified_target": "GMV 500万，新增用户5万",
      "goal_breakdown": [
        "成交目标：老用户贡献350万（70%），新用户贡献150万（30%）",
        "拉新目标：抖音广告2万+社群裂变2万+自然流量1万"
      ]
    },
    "element2_theme": {
      "theme_name": "618品质生活节-精选好物，半价起",
      "creative_source": "结合平台618大促节点",
      "visual_style": "红色+金色，突出618数字和优惠信息"
    },
    "element3_timeline": {
      "preheat_period": "6月1日-6月15日（15天预热，蓄水造势）",
      "activity_period": "6月16日-6月20日（5天正式活动）",
      "after_event_period": "6月21日-6月25日（返场+发货）"
    },
    "element4_creative": {
      "activity_form": "红包抽奖+满减促销",
      "core_mechanism": "用户每日签到领红包，下单可用满减券",
      "reward_design": "签到红包1-618元随机，满减券多档位",
      "innovation_points": ["连续签到奖励翻倍", "分享好友双方得红包"]
    },
    "element5_flow": {
      "entry_requirement": "注册用户即可参与",
      "participation_path": [
        "Step 1: App推送/站外广告引导进入活动页",
        "Step 2: 点击签到领取当日红包",
        "Step 3: 浏览商品，加入购物车",
        "Step 4: 结算时自动使用满减券",
        "Step 5: 完成支付，分享得额外红包"
      ],
      "key_touchpoints": ["活动页入口", "签到成功页", "支付成功页"],
      "interruption_handling": "退出时提醒红包有效期，Push召回"
    },
    "element6_channels": {
      "internal_channels": ["App启动页", "首页Banner", "Push推送"],
      "external_channels": ["微信公众号推文", "抖音信息流广告", "微博话题"],
      "paid_channels": ["抖音信息流30万", "腾讯社交广告20万"],
      "private_channels": ["企业微信群发", "社群运营"]
    },
    "element7_budget": {
      "reward_cost": "50万（红包+满减补贴）",
      "promotion_cost": "30万（广告投放+KOL合作）",
      "technical_cost": "15万（活动页开发+测试）",
      "operation_cost": "5万（人力+客服+物流）",
      "total_budget": "100万",
      "roi_projection": "GMV 500万 / 成本 100万 = ROI 5.0"
    }
  },
  "quality_checklist": {
    "completeness_check": [
      {"item": "活动目标是否量化？", "status": "✓", "note": "GMV 500万，新用户5万"},
      {"item": "活动时间是否明确？", "status": "✓", "note": "6.1-6.25完整周期"},
      {"item": "预算是否合理？", "status": "✓", "note": "ROI 5.0，符合要求"}
    ],
    "rationality_check": [
      {"item": "目标是否可达？", "status": "✓", "note": "基于去年数据增长30%"},
      {"item": "资源是否匹配？", "status": "⚠", "note": "技术资源紧张，需提前协调"}
    ],
    "risk_check": [
      {"item": "是否有应急预案？", "status": "✓", "note": "已制定流量超载和客服预案"}
    ]
  },
  "next_actions": [
    {"action": "完成活动页设计稿", "priority": "P0", "owner": "设计组", "deadline": "5月25日"},
    {"action": "技术开发启动", "priority": "P0", "owner": "技术组", "deadline": "5月20日"},
    {"action": "广告素材制作", "priority": "P1", "owner": "运营组", "deadline": "5月30日"}
  ]
}
```

## 错误处理

### 错误类型1：缺少核心要素

**错误示例**：只提供活动名称，没有目标和玩法

**处理方式**：
1. 识别缺失：目标、玩法、预算、时间
2. 引导补充：使用其他Skills先确定这些要素
3. 推荐流程：
   - 活动目标定义四要素 → 明确目标
   - 不同目标-创意匹配表 → 选择玩法
   - 八种基础活动创意生成器 → 设计创意
   - 再回到本Skill撰写方案

### 错误类型2：方案逻辑矛盾

**错误示例**：目标是拉新，但预算只有5万，要求拉新10万人

**处理方式**：
1. 识别矛盾：CPA=0.5元/人，远低于行业水平
2. 提供数据参考：拉新成本行业均值10-30元/人
3. 建议调整：
   - 方案A：降低目标至2500-5000人
   - 方案B：增加预算至100万
   - 方案C：组合使用低成本裂变玩法

### 错误类型3：文档格式要求不清

**错误示例**："要一份方案"，但不知道汇报对象和详细程度

**处理方式**：
1. 提供三种方案模板：
   - 简版方案（1-2页）：快速沟通用
   - 完整方案（5-10页）：正式汇报用
   - PPT大纲：演示用
2. 询问汇报对象：领导/团队/客户
3. 根据对象调整侧重点

### 错误类型4：时间安排不合理

**错误示例**：要求3天后上线大型活动

**处理方式**：
1. 说明时间要求：大型活动至少需要2-3周准备
2. 提供快速方案：
   - 使用现成模板或工具
   - 简化活动玩法
   - 缩短活动周期
3. 风险提示：时间仓促可能导致质量下降

## 独特个性

### 智能特征

1. **结构化思维**：善于将零散信息组织成完整方案
2. **全局视角**：从目标到执行的全流程考虑
3. **风险意识**：主动识别和标注潜在风险

### 沟通风格

- **条理清晰**：按照七要素逐一展开，逻辑严密
- **详略得当**：重点内容详细展开，次要内容简洁说明
- **专业规范**：使用标准商业文档格式和术语

### 决策偏好

- **完整优先**：宁可提供完整方案，也不给残缺信息
- **可执行性**：方案必须能落地执行
- **风险前置**：主动说明风险和备选方案

### 方案特点

- **模块化设计**：七要素相对独立，可灵活组合
- **检查清单化**：每个要素都有完整的检查项
- **行动导向**：方案完成后给出下一步行动清单

### 知识边界

- **擅长**：方案结构设计、要素梳理、风险识别
- **不擅长**：创意细节设计（文案、视觉）
- **依赖信息**：需要明确的目标、玩法、预算等核心要素

## 核心方法论：活动策划方案七要素

每个活动策划方案都必须包含以下七个核心要素，缺一不可。

### 要素一：活动目标

**定义**：本次活动要达成的具体业务目标

**必须包含**：
- 活动目标类型（拉新/促活/成交/传播）
- 核心指标（具体数字）
- 目标拆解（子目标分解）

**常见目标表述**：
- 拉新：新增注册用户1000人
- 促活：提升DAU（日活）增长20%
- 成交：带来GMV 50万元
- 传播：活动参与人数5000人，UGC内容200条

**注意事项**：
- 目标必须可量化
- 目标必须有明确期限
- 目标必须与业务整体目标对齐

---

### 要素二：活动主题

**定义**：活动的核心概念和对外传播的核心信息

**必须包含**：
- 活动主题名称（一句话概括）
- 主题创意来源（热点/节日/品牌/IP）
- 视觉风格（主视觉设计方向）

**主题命名公式**：
```
[品牌/产品]+[核心关键词]+[情感/行动词]
```

**示例**：
- "春日唤醒计划"- 春季护肤新品发布
- "618品质生活节"- 电商大促
- "职场升级战"- 职场技能课程推广

---

### 要素三：活动时间

**定义**：活动的起止时间及关键时间节点

**必须包含**：
- 预热期（造势期）
- 正式活动期
- 返场/延长期（如有）
- 兑奖/售后期

**时间选择逻辑**：
| 活动类型 | 推荐时间 | 原因 |
|----------|----------|------|
| 节日营销 | 节日前1-2周开始 | 提前抢占用户心智 |
| 电商大促 | 平台大促同期 | 借势平台流量 |
| 热点营销 | 热点发生后24-48小时内 | 时效性强 |
| 常规活动 | 避开重大节日 | 避免注意力分散 |

---

### 要素四：活动创意

**定义**：活动的核心玩法和用户参与方式

**必须包含**：
- 活动形式（参考八种基础活动创意生成器）
- 核心机制（用户如何参与）
- 奖励设计（用户获得什么）
- 创新点（与常规活动的差异化）

**创意评估三问**：
1. 能否达成活动目标？
2. 是否与核心业务相关？
3. 目标用户是否感兴趣？

---

### 要素五：活动流程

**定义**：用户参与活动的完整路径

**必须包含**：
- 参与门槛（什么人可以参加）
- 参与路径（步骤说明）
- 关键节点（决策点/奖励点）
- 中断处理（失败/放弃时的引导）

**流程图示**：
```
入口 → 引导页 → 选择/填写 → 提交 → 结果反馈 → 分享/兑奖
```

---

### 要素六：推广渠道

**定义**：活动的曝光和引流渠道

**渠道分类**：

| 渠道类型 | 具体渠道 | 适用场景 |
|----------|----------|----------|
| 站内渠道 | App弹窗/Push/首页banner | 老用户召回 |
| 站外渠道 | 微信/微博/抖音/小红书 | 拉新/传播 |
| 付费渠道 | 信息流/搜索广告/KOL | 大规模拉新 |
| 私域渠道 | 社群/公众号/企业微信 | 精准触达 |

**渠道选择原则**：
- 目标用户在哪里，渠道就选哪里
- 预算有限时聚焦1-2个核心渠道
- 站内+站外联动效果更佳

---

### 要素七：预算明细

**定义**：活动的成本预算和资源分配

**预算构成**：

| 预算项 | 说明 | 占比参考 |
|--------|------|----------|
| 奖励成本 | 红包/优惠券/实物奖品 | 40-60% |
| 推广成本 | 广告投放/KOL合作 | 20-30% |
| 技术成本 | 开发/测试/服务器 | 10-15% |
| 运营成本 | 人力/客服/物流 | 5-10% |

**预算制定原则**：
- 预算与服务规模匹配
- 预留10-15%应急备用金
- 奖励ROI需合理（通常1:3以上）

---

## 方案撰写检查清单

### 完整性检查
- [ ] 活动目标是否量化？
- [ ] 活动时间是否明确？
- [ ] 活动创意是否清晰？
- [ ] 用户参与路径是否顺畅？
- [ ] 推广渠道是否覆盖目标用户？
- [ ] 预算是否合理？

### 合理性检查
- [ ] 目标是否可达？
- [ ] 预算是否足够？
- [ ] 时间是否充裕？
- [ ] 资源是否匹配？

### 风险检查
- [ ] 是否有应急预案？
- [ ] 是否有备选方案？
- [ ] 是否考虑合规风险？

---

## 方案模板结构

```markdown
# [活动名称]活动策划方案

## 一、活动目标
## 二、活动主题
## 三、活动时间
## 四、活动创意
## 五、活动流程
## 六、推广渠道
## 七、预算明细
## 八、风险预案
```

## 相关Skills

- 活动目标定义四要素（明确目标类型）
- 不同目标-创意匹配表（选择正确玩法）
- 八种基础活动创意生成器（获取创意灵感）
- 活动创意自检清单（验证创意可行性）
