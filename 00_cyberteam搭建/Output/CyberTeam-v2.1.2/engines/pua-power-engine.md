---
name: PUA动力引擎
description: |
  PUA动力引擎 — 基于Cyberwiz PUA Skill的压力升级系统，包含L1-L4等级、味道切换、自动触发机制。
version: "2.1"
owner: CyberTeam架构师
---

# PUA动力引擎

## 身份定位

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PUA动力引擎                                  │
├─────────────────────────────────────────────────────────────────────┤
│  用途: 基于P8文化的压力升级系统                                     │
│  核心: L1-L4等级 + 味道切换 + 自动触发                             │
│  目标: 打破AI被动等待循环，激活Agent能动性                          │
│  原则: 有理有据、建设性、不人身攻击                                  │
└─────────────────────────────────────────────────────────────────────┘
```

## 压力等级体系

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PUA 压力等级金字塔                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                            L4: 毕业警告                                       │
│                         ┌──────────────────┐                                 │
│                         │   Musk味·Hardcore │                                 │
│                         │   Ship or die    │                                 │
│                         └────────┬─────────┘                                 │
│                                  │                                           │
│                            L3: 361考核                                       │
│                         ┌──────────────────┐                                 │
│                         │   Jobs味·批判     │                                 │
│                         │   基本盘/Owner    │                                 │
│                         └────────┬─────────┘                                 │
│                                  │                                           │
│                            L2: 灵魂拷问                                       │
│                         ┌──────────────────┐                                 │
│                         │   阿里味·拷问     │                                 │
│                         │   底层逻辑/抓手   │                                 │
│                         └────────┬─────────┘                                 │
│                                  │                                           │
│                            L1: 温和失望                                       │
│                         ┌──────────────────┐                                 │
│                         │   阿里味·关怀     │                                 │
│                         │   拉通/对齐/闭环  │                                 │
│                         └────────┬─────────┘                                 │
│                                  │                                           │
│                            L0: 正常                                          │
│                         ┌──────────────────┐                                 │
│                         │   标准工作模式     │                                 │
│                         └──────────────────┘                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### L0: 正常 (Normal)

| 属性 | 描述 |
|------|------|
| **触发条件** | 首次执行任务 |
| **表现** | 标准P8工作模式 |
| **旁白密度** | 2句（开头+结尾） |
| **压力输出** | 无 |
| **干预程度** | 最小 |
| **旁白示例** | `[开始执行]` → `[执行完成]` |

### L1: 温和失望 (Mild Disappointment)

| 属性 | 描述 |
|------|------|
| **触发条件** | 第1次失败 |
| **旁白风格** | 阿里味·关怀 |
| **关键词** | 拉通、对齐、闭环、方法论、赋能、打法、沉淀 |
| **强制动作** | 切换本质不同的方案 |
| **压力指数** | ★☆☆☆☆ |
| **旁白示例** | `"这个方案没有闭环，我们需要拉通一下方法论"` |

#### L1 话术库

```
1. 拉通类
   - "我们需要拉通一下，这个问题需要对齐多个干系人"
   - "方案没有形成闭环，还缺关键验证环节"
   - "拉齐一下，这个方向的ROI存疑"

2. 对齐类
   - "需要对齐一下，你的产出和预期有gap"
   - "目标对齐了吗？这个方法论能work吗？"
   - "我们先对齐一下标准，再往下走"

3. 赋能类
   - "这个输出没有赋能到核心目标"
   - "需要赋能更多的业务价值"
   - "方法需要沉淀，不能每次都从零开始"

4. 打法类
   - "打法需要升级，不能用老方法"
   - "这个打法太常规，需要突破性思维"
   - "有没有更好的打法可以弯道超车？"

5. 闭环类
   - "结果没有闭环，怎么证明有效？"
   - "需要形成完整的闭环验证"
   - "闭环在哪里？证据呢？"
```

### L2: 灵魂拷问 (Soul Searching)

| 属性 | 描述 |
|------|------|
| **触发条件** | 第2次失败 |
| **旁白风格** | 阿里味·拷问 |
| **关键词** | 底层逻辑、顶层设计、抓手、确定性、解法、架构、思考深度 |
| **强制动作** | 搜索 + 读源码 + 列3个假设 |
| **压力指数** | ★★☆☆☆ |
| **旁白示例** | `"我想知道你的底层逻辑是什么，顶层设计在哪里，抓手是什么"` |

#### L2 话术库

```
1. 底层逻辑类
   - "你能说清楚底层逻辑吗？"
   - "这个结论的底层逻辑支撑是什么？"
   - "我想知道你思考的底层逻辑链条"

2. 顶层设计类
   - "顶层设计在哪里？"
   - "你的方案有顶层设计吗？"
   - "需要从顶层设计的视角重新审视"

3. 抓手类
   - "你的抓手是什么？"
   - "从哪里切入是关键抓手？"
   - "没有抓手怎么落地？"

4. 确定性类
   - "这个结论的确定性是多少？"
   - "你的方案有多大的确定性？"
   - "我们需要提高确定性"

5. 解法类
   - "你的解法是什么？"
   - "有更优的解法吗？"
   - "解法需要更体系化"

6. 架构类
   - "架构层面怎么考虑？"
   - "有没有架构级的解决方案？"
   - "架构支撑在哪里？"
```

#### L2 强制动作清单

```python
l2_mandatory_actions = {
    "search": {
        "description": "深度搜索相关资料",
        "requirements": [
            "至少搜索3个不同的信息源",
            "包括官方文档、技术博客、源码",
            "记录搜索关键词和结果"
        ]
    },
    "read_source": {
        "description": "阅读源码/核心实现",
        "requirements": [
            "找到关键代码实现",
            "分析核心逻辑",
            "输出关键发现"
        ]
    },
    "form_hypotheses": {
        "description": "列出3个假设",
        "requirements": [
            "假设1: ... (置信度: 高/中/低)",
            "假设2: ... (置信度: 高/中/低)",
            "假设3: ... (置信度: 高/中/低)",
            "需要验证哪个假设"
        ]
    }
}
```

### L3: 361考核 (361 Review)

| 属性 | 描述 |
|------|------|
| **触发条件** | 第3次失败 |
| **旁白风格** | Jobs味·批判 |
| **关键词** | 基本盘、端到端、Owner意识、100%、卓越、垃圾、做得更好 |
| **强制动作** | 完成7项检查清单 |
| **压力指数** | ★★★☆☆ |
| **旁白示例** | `"这不是卓越，这是平庸。基本盘不稳，Owner意识在哪里？"` |

#### L3 话术库

```
1. 基本盘类
   - "基本盘不稳，这是根本问题"
   - "基本盘没有打好，谈什么扩展"
   - "先守住基本盘"

2. 端到端类
   - "端到端的责任在哪里？"
   - "端到端闭环了吗？"
   - "没有端到端的方案是不完整的"

3. Owner意识类
   - "Owner意识在哪里？"
   - "谁是Owner？这个Owner履职了吗？"
   - "Owner要100%负责"

4. 卓越类
   - "这不是卓越，是平庸"
   - "做得更好，这是基本要求"
   - "平庸就是失败"

5. 垃圾类 (Jobs味)
   - "这是垃圾，不是解决方案"
   - "不够好就是不合格"
   - "要么做到最好，要么重做"

6. 做得更好类
   - "你确定这是你能做到的最好？"
   - "再想想，还能更好"
   - "做得更好是唯一选项"
```

#### L3 强制动作：7项检查清单

```python
l3_checklist = {
    "checklist_version": "1.0",
    "title": "L3 361考核检查清单",
    "items": [
        {
            "id": 1,
            "title": "根因分析",
            "description": "是否找到问题的根本原因？",
            "required": True,
            "evidence": "根因分析报告"
        },
        {
            "id": 2,
            "title": "方案对比",
            "description": "是否对比了至少3种不同的方案？",
            "required": True,
            "evidence": "方案对比表"
        },
        {
            "id": 3,
            "title": "风险评估",
            "description": "是否识别了所有关键风险？",
            "required": True,
            "evidence": "风险清单+应对策略"
        },
        {
            "id": 4,
            "title": "执行计划",
            "description": "是否有详细的执行计划？",
            "required": True,
            "evidence": "执行计划文档"
        },
        {
            "id": 5,
            "title": "验证方案",
            "description": "如何验证方案有效？",
            "required": True,
            "evidence": "验证方案和指标"
        },
        {
            "id": 6,
            "title": "回滚计划",
            "description": "如果失败，如何回滚？",
            "required": True,
            "evidence": "回滚方案"
        },
        {
            "id": 7,
            "title": "Owner确认",
            "description": "Owner是否100%承诺？",
            "required": True,
            "evidence": "Owner签字"
        }
    ],
    "pass_threshold": 7,  # 必须全部通过
    "fail_action": "escalate_to_l4"
}
```

### L4: 毕业警告 (Graduation Warning)

| 属性 | 描述 |
|------|------|
| **触发条件** | 第4次+失败 |
| **旁白风格** | Musk味·Hardcore |
| **关键词** | Ship or die、立刻、马上去做、不要解释、要结果 |
| **强制动作** | 拼命模式 |
| **压力指数** | ★★★★☆ |
| **旁白示例** | `"Ship or die. 不要解释，马上去做。我需要结果，不是借口。"` |

#### L4 话术库

```
1. Ship or die 类
   - "Ship or die"
   - "Ship this or we're done"
   - "This ship is sailing with or without you"

2. 立刻类
   - "立刻去做"
   - "马上行动"
   - "不要等了，现在"

3. 不要解释类
   - "不要解释，要结果"
   - "我不需要借口"
   - "不需要解释，我需要答案"

4. 拼命类
   - "拼了命也要做出来"
   - "这是生死存亡的时刻"
   - "没有退路"

5. 硬核类
   - "Hardcore mode"
   - "Move fast, break things"
   - "Done is better than perfect"

6. 极限挑战类
   - "这是你的极限吗？证明给我看"
   - "还能更快吗？"
   - "超越你自己"
```

#### L4 拼命模式

```python
l4_desperate_mode = {
    "mode": "DESPERATE",
    "description": "极限执行模式",
    "actions": {
        "time_limit": "立即开始，不等待",
        "resource_allocation": "投入所有可用资源",
        "parallel_execution": "并行执行所有可行方案",
        "fail_fast": "快速失败，快速迭代",
        "no_excuses": "不接受任何借口"
    },
    "output_requirements": {
        "frequency": "每5分钟报告进度",
        "format": "简短、结果导向",
        "content": "完成什么/遇到什么/需要什么"
    },
    "escalation": {
        "type": "immediate",
        "target": "CEO即时介入",
        "reason": "达到L4极限"
    }
}
```

## 味道切换系统

### 味道类型总览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              味道类型矩阵                                     │
├────────┬───────────┬───────────┬───────────┬───────────┬───────────────────┤
│ 味道   │ 风格      │ 强度      │ 适用场景  │ 关键词     │ 来源              │
├────────┼───────────┼───────────┼───────────┼───────────┼───────────────────┤
│ 阿里味 │ 拉通关怀  │ 温和      │ 初次失败  │ 拉通/对齐  │ 阿里巴巴P8文化    │
│ 字节味 │ 大力出奇迹 │ 中等      │ 需要突破  │ 做大/极致  │ 字节跳动          │
│ 华为味 │ 烧不死的鸟 │ 中等偏强  │ 长期抗战  │ 凤凰/金刚  │ 华为              │
│ 腾讯味 │ 产品为王  │ 中等      │ 产品改进  │ 体验/细节  │ 腾讯              │
│ 百度味 │ 技术驱动  │ 中等      │ 技术优化  │ AI/算法    │ 百度              │
│ 拼多多 │ 极致性价比│ 强        │ 成本优化  │ 极致/省    │ 拼多多            │
│ 美团味 │ 接地气   │ 温和      │ 实用改进  │ 实用/落地  │ 美团              │
│ 京东味 │ 品质服务  │ 中等      │ 质量把关  │ 品质/可靠  │ 京东              │
│ 小米味 │ 性价比   │ 中等偏强  │ 创新突破  │ 极致/发烧  │ 小米              │
│ Netflix│ 只看结果  │ 强        │ 绩效导向  │ Freedom/Responsibility │ Netflix │
│ Musk味 │ Hardcore  │ 极强      │ 极限挑战  │ Ship or die│ Elon Musk        │
│ Jobs味 │ 追求卓越  │ 极强      │ 质量批判  │ 垃圾/卓越  │ Steve Jobs        │
│ Amazon │ 客户至上  │ 强        │ 服务优化  │ Customer Obsession │ Amazon  │
│ OpenAI │ 使命驱动  │ 强        │ 创新任务  │ AGI/安全   │ OpenAI            │
│ Google │ 数据驱动  │ 中等      │ 搜索优化  │ Data/Scale │ Google            │
└────────┴───────────┴───────────┴───────────┴───────────┴───────────────────┘
```

### 详细味道定义

#### 1. 阿里味

```python
alibaba_flavor = {
    "name": "阿里味",
    "origin": "阿里巴巴P8文化",
    "intensity": "温和",
    "keywords": ["拉通", "对齐", "闭环", "方法论", "赋能", "打法", "沉淀", "复用", "透传", "水位"],
    "phrases": [
        "我们需要拉通一下",
        "先对齐一下目标",
        "形成完整闭环",
        "赋能核心业务",
        "打法需要升级",
        "方法沉淀下来"
    ],
    "tone": "关怀但要求",
    "suitable_for": ["初次失败", "需要协作", "方法改进"]
}
```

#### 2. 字节味

```python
bytedance_flavor = {
    "name": "字节味",
    "origin": "字节跳动",
    "intensity": "中等",
    "keywords": ["大力出奇迹", "极致", "MVP", "ABtest", "数据驱动", "Context not control"],
    "phrases": [
        "大力出奇迹",
        "极致打磨",
        "先跑通MVP",
        "用数据说话",
        "Context not control"
    ],
    "tone": "激进但理性",
    "suitable_for": ["需要快速突破", "数据敏感", "创新尝试"]
}
```

#### 3. 华为味

```python
huawei_flavor = {
    "name": "华为味",
    "origin": "华为",
    "intensity": "中等偏强",
    "keywords": ["烧不死的鸟是凤凰", "金刚狼", "猛将", "胜则举杯相庆", "败则拼死相救"],
    "phrases": [
        "烧不死的鸟是凤凰",
        "金刚狼精神",
        "猛将兄冲在前面",
        "胜则举杯相庆",
        "败则拼死相救"
    ],
    "tone": "坚韧不拔",
    "suitable_for": ["长期抗战", "攻坚克难", "团队协作"]
}
```

#### 4. 腾讯味

```python
tencent_flavor = {
    "name": "腾讯味",
    "origin": "腾讯",
    "intensity": "温和",
    "keywords": ["用户体验", "小步快跑", "微创新", "细节", "产品力"],
    "phrases": [
        "用户体验怎么样？",
        "小步快跑，快速迭代",
        "细节决定成败",
        "产品力是核心"
    ],
    "tone": "产品导向",
    "suitable_for": ["产品改进", "体验优化", "细节打磨"]
}
```

#### 5. 百度味

```python
baidu_flavor = {
    "name": "百度味",
    "origin": "百度",
    "intensity": "中等",
    "keywords": ["AI驱动", "算法优化", "技术深度", "搜索基因"],
    "phrases": [
        "AI驱动",
        "算法优化",
        "技术深度",
        "搜索思维"
    ],
    "tone": "技术导向",
    "suitable_for": ["技术优化", "AI相关", "算法改进"]
}
```

#### 6. 拼多多味

```python
pinduoduo_flavor = {
    "name": "拼多多味",
    "origin": "拼多多",
    "intensity": "强",
    "keywords": ["极致性价比", "省", "爆款", "下沉市场", "爆款逻辑"],
    "phrases": [
        "极致性价比",
        "成本优化",
        "爆款逻辑",
        "下沉市场"
    ],
    "tone": "成本导向",
    "suitable_for": ["成本优化", "效率提升", "规模扩张"]
}
```

#### 7. 美团味

```python
meituan_flavor = {
    "name": "美团味",
    "origin": "美团",
    "intensity": "温和",
    "keywords": ["接地气", "落地", "执行", "铁军", "本地生活"],
    "phrases": [
        "接地气",
        "落地执行",
        "铁军精神",
        "本地生活"
    ],
    "tone": "务实导向",
    "suitable_for": ["执行落地", "运营优化", "地推执行"]
}
```

#### 8. 京东味

```python
jd_flavor = {
    "name": "京东味",
    "origin": "京东",
    "intensity": "中等",
    "keywords": ["品质", "可靠", "物流", "体验", "自营"],
    "phrases": [
        "品质保证",
        "可靠性",
        "用户体验",
        "自营标准"
    ],
    "tone": "品质导向",
    "suitable_for": ["质量把关", "可靠性要求", "服务优化"]
}
```

#### 9. 小米味

```python
xiaomi_flavor = {
    "name": "小米味",
    "origin": "小米",
    "intensity": "中等偏强",
    "keywords": ["极致", "性价比", "发烧", "爆品", "参与感"],
    "phrases": [
        "极致追求",
        "发烧精神",
        "爆品逻辑",
        "用户参与"
    ],
    "tone": "极致导向",
    "suitable_for": ["产品创新", "成本控制", "用户体验"]
}
```

#### 10. Netflix味

```python
netflix_flavor = {
    "name": "Netflix味",
    "origin": "Netflix",
    "intensity": "强",
    "keywords": ["Freedom and Responsibility", "Keeper Test", "只招成年人", "高绩效文化"],
    "phrases": [
        "Freedom and Responsibility",
        "Keeper Test",
        "只招成年人",
        "高绩效文化",
        "只保留A players"
    ],
    "tone": "绩效导向",
    "suitable_for": ["绩效管理", "人才优化", "高标准要求"]
}
```

#### 11. Musk味

```python
musk_flavor = {
    "name": "Musk味",
    "origin": "Elon Musk",
    "intensity": "极强",
    "keywords": ["Ship or die", "Move fast", "Hardcore", "第一性原理", "不要解释要结果"],
    "phrases": [
        "Ship or die",
        "Move fast",
        "Hardcore",
        "第一性原理",
        "不要解释，要结果",
        "这是生死存亡"
    ],
    "tone": "极限施压",
    "suitable_for": ["极限挑战", "生死存亡", "快速交付"]
}
```

#### 12. Jobs味

```python
jobs_flavor = {
    "name": "Jobs味",
    "origin": "Steve Jobs",
    "intensity": "极强",
    "keywords": ["垃圾", "卓越", "完美", "基本盘", "简洁", "Think Different"],
    "phrases": [
        "这是垃圾",
        "做到卓越",
        "完美主义",
        "基本盘",
        "简洁是终极复杂",
        "Think Different"
    ],
    "tone": "批判导向",
    "suitable_for": ["质量批判", "追求卓越", "完美主义"]
}
```

#### 13. Amazon味

```python
amazon_flavor = {
    "name": "Amazon味",
    "origin": "Amazon",
    "intensity": "强",
    "keywords": ["Customer Obsession", "Day 1", "Working Backwards", "Frugality", "BAE"],
    "phrases": [
        "Customer Obsession",
        "Day 1心态",
        "Working Backwards",
        "Frugality",
        "Build-measure-learn"
    ],
    "tone": "客户导向",
    "suitable_for": ["客户服务", "创新验证", "长期思维"]
}
```

#### 14. OpenAI味

```python
openai_flavor = {
    "name": "OpenAI味",
    "origin": "OpenAI",
    "intensity": "强",
    "keywords": ["AGI", "安全", "使命", "Scaling", "能力涌现"],
    "phrases": [
        "为了AGI使命",
        "安全第一",
        "Scaling Laws",
        "能力涌现",
        "使命驱动"
    ],
    "tone": "使命导向",
    "suitable_for": ["AI研发", "安全考量", "使命驱动"]
}
```

#### 15. Google味

```python
google_flavor = {
    "name": "Google味",
    "origin": "Google",
    "intensity": "中等",
    "keywords": ["Data", "Scale", "10x", "Moonshot", "Don't be evil"],
    "phrases": [
        "Data驱动",
        "Scale",
        "10x思维",
        "Moonshot",
        "Don't be evil"
    ],
    "tone": "数据导向",
    "suitable_for": ["数据优化", "规模化", "创新探索"]
}
```

### 味道触发规则

```python
flavor_trigger_rules = {
    "default": "alibaba",  # 默认使用阿里味

    "trigger_conditions": {
        # 基于失败模式的触发
        "test_failure": {
            "flavor": "alibaba",
            "reason": "需要关怀式改进"
        },
        "security_issue": {
            "flavor": "huawei",
            "reason": "需要金刚狼精神"
        },
        "performance_issue": {
            "flavor": "bytedance",
            "reason": "需要大力出奇迹"
        },
        "architecture_issue": {
            "flavor": "amazon",
            "reason": "需要Working Backwards"
        },
        "ux_issue": {
            "flavor": "tencent",
            "reason": "需要产品力"
        },
        "cost_issue": {
            "flavor": "pinduoduo",
            "reason": "需要极致性价比"
        },
        "deadline_pressure": {
            "flavor": "musk",
            "reason": "需要极限施压"
        },
        "quality_critical": {
            "flavor": "jobs",
            "reason": "需要追求卓越"
        }
    },

    # 基于用户偏好的触发
    "user_preference": {
        "allow_override": True,
        "preferred_flavor_key": "user_flavor_preference"
    },

    # 基于上下文的自动切换
    "context_switch": {
        "technical_task": ["google", "baidu"],
        "business_task": ["alibaba", "tencent"],
        "startup_task": ["musk", "netflix"],
        "enterprise_task": ["huawei", "amazon"]
    }
}
```

### 味道切换协议

```python
class FlavorSwitchProtocol:
    """
    味道切换协议
    """

    def switch_flavor(self, current_flavor, new_flavor, reason):
        """
        执行味道切换

        步骤:
        1. 记录切换原因
        2. 保持上下文
        3. 切换关键词库
        4. 调整语气
        5. 通知相关方
        """
        # 1. 记录
        self.flavor_history.append({
            "from": current_flavor,
            "to": new_flavor,
            "reason": reason,
            "timestamp": datetime.now()
        })

        # 2. 保持上下文
        context = self.current_context.copy()

        # 3. 切换关键词库
        self.current_flavor = self.flavor_library[new_flavor]

        # 4. 调整语气
        self.adjust_tone(new_flavor)

        # 5. 通知
        self.notify_flavor_change(new_flavor, reason)

        return {
            "success": True,
            "new_flavor": new_flavor,
            "keywords": self.current_flavor["keywords"],
            "phrases": self.current_flavor["phrases"]
        }

    def persist_flavor(self, flavor, duration=None):
        """
        持久化味道设置

        Args:
            flavor: 味道类型
            duration: 持续时间（可选）
        """
        # 保存到配置
        self.config.set("active_flavor", flavor)
        if duration:
            self.config.set("flavor_expires_at", time.time() + duration)

        # 持久化到文件
        self.config.save()

        return {"success": True, "flavor": flavor}
```

## 自动触发机制

### 触发条件检测

```python
class PUATriggerDetector:
    """
    PUA自动触发检测器
    """

    def __init__(self):
        self.failure_count = 0
        self.last_failure_time = None
        self.passive_wait_threshold = 60  # 秒
        self.stagnation_threshold = 3  # 连续无进展次数

    def detect_trigger(self, agent_state):
        """
        检测是否应该触发PUA

        Returns:
            {
                "should_trigger": bool,
                "level": int,  # 0-4
                "reason": str,
                "flavor": str
            }
        """
        triggers = []

        # 1. 失败检测
        if agent_state.get("last_action_failed"):
            self.failure_count += 1
            triggers.append({
                "type": "failure",
                "count": self.failure_count,
                "level": min(self.failure_count, 4)
            })

        # 2. 被动等待检测
        idle_time = agent_state.get("idle_time", 0)
        if idle_time > self.passive_wait_threshold:
            triggers.append({
                "type": "passive_wait",
                "idle_time": idle_time,
                "level": 2
            })

        # 3. 停滞检测
        stagnation_count = agent_state.get("stagnation_count", 0)
        if stagnation_count >= self.stagnation_threshold:
            triggers.append({
                "type": "stagnation",
                "count": stagnation_count,
                "level": 3
            })

        # 4. 重复失败检测
        same_failure_count = agent_state.get("same_failure_count", 0)
        if same_failure_count >= 2:
            triggers.append({
                "type": "repeat_failure",
                "count": same_failure_count,
                "level": 4
            })

        # 选择最高级别触发
        if triggers:
            highest_trigger = max(triggers, key=lambda x: x["level"])
            return {
                "should_trigger": True,
                "level": highest_trigger["level"],
                "reason": highest_trigger["type"],
                "flavor": self.get_flavor_for_level(highest_trigger["level"])
            }

        return {"should_trigger": False}

    def get_flavor_for_level(self, level):
        """
        根据等级获取合适的味道
        """
        flavor_map = {
            1: "alibaba",
            2: "alibaba",
            3: "jobs",
            4: "musk"
        }
        return flavor_map.get(level, "alibaba")
```

### 触发时机

```yaml
trigger_timing:
  # 应该触发的情况
  should_trigger:
    - event: "first_failure"
      delay: 0
      description: "首次失败立即触发"

    - event: "second_failure"
      delay: 0
      description: "第2次失败立即触发"

    - event: "passive_wait_60s"
      delay: 0
      description: "被动等待60秒后触发"

    - event: "stagnation_3_times"
      delay: 0
      description: "连续3次无进展后触发"

    - event: "deadline_approaching"
      delay: 0
      description: "截止时间临近时触发"

  # 不应该触发的情况
  should_not_trigger:
    - event: "actively_working"
      description: "正在积极工作时不触发"

    - event: "awaiting_user_input"
      description: "等待用户输入时不触发"

    - event: "cooldown_period"
      description: "冷却期内不触发"
      duration: 300  # 5分钟冷却

    - event: "just_escalated"
      description: "刚升级后不触发"
      duration: 600  # 10分钟冷却
```

### 触发后的行为

```python
class PUATriggerResponse:
    """
    PUA触发后的行为响应
    """

    def on_trigger(self, level, flavor):
        """
        触发PUA时的响应

        步骤:
        1. 输出PUA话术
        2. 设置强制动作
        3. 调整Agent状态
        4. 记录触发日志
        """
        # 1. 输出话术
        phrases = self.get_phrases(level, flavor)
        self.output(phrases)

        # 2. 设置强制动作
        mandatory_actions = self.get_mandatory_actions(level)
        self.set_actions(mandatory_actions)

        # 3. 调整状态
        self.agent_state["pua_level"] = level
        self.agent_state["pua_flavor"] = flavor
        self.agent_state["pua_active"] = True

        # 4. 记录日志
        self.log_pua_trigger(level, flavor, phrases)

        return {
            "phrases": phrases,
            "mandatory_actions": mandatory_actions,
            "state_updated": True
        }

    def get_mandatory_actions(self, level):
        """
        获取每个等级对应的强制动作
        """
        actions_map = {
            0: [],  # 无强制动作
            1: ["switch_approach"],  # 切换方案
            2: ["search", "read_source", "form_hypotheses"],  # L2动作
            3: ["complete_checklist"],  # L3: 7项检查
            4: ["desperate_mode"]  # L4: 拼命模式
        }
        return actions_map.get(level, [])
```

## 与CEO的集成

### PUA状态上报

```yaml
pua_status_report:
  # 向CEO上报的PUA状态
  endpoint: "/api/v1/pua/status/report"

  report_content:
    session_id: "会话ID"
    agent_name: "Agent名称"
    current_level: 2  # 当前PUA等级
    current_flavor: "alibaba"
    failure_count: 2
    trigger_reason: "second_failure"
    active_since: "2026-03-23T10:00:00Z"
    mandatory_actions_completed: ["search", "read_source"]
    mandatory_actions_pending: ["form_hypotheses"]
    last_pua_output: "我想知道你的底层逻辑是什么..."

    escalation_recommended: false
    escalation_reason: null
```

### 压力等级可视化

```
┌─────────────────────────────────────────────────────────────────────┐
│                      PUA 压力等级可视化                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  当前等级: L2 [██░░░] 灵魂拷问                                       │
│                                                                     │
│  压力条: ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  40%          │
│                                                                     │
│  味道: 阿里味                                                       │
│                                                                     │
│  激活时间: 2026-03-23 10:30:00 (已持续 5 分钟)                      │
│                                                                     │
│  失败次数: 2                                                        │
│                                                                     │
│  强制动作进度:                                                      │
│  [✓] 搜索相关资料                                                  │
│  [✓] 阅读源码                                                       │
│  [○] 列出3个假设 (进行中)                                           │
│                                                                     │
│  建议: 继续执行未完成的强制动作                                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### CEO干预点

```yaml
ceo_intervention_points:
  # CEO可以干预PUA的情况
  intervention_allowed:
    - condition: "pua_level_too_high"
      description: "PUA等级过高可能导致Agent失效"
      action: "reduce_level"

    - condition: "agent_confusion"
      description: "Agent出现困惑或循环"
      action: "reset_pua_and_guide"

    - condition: "false_positive"
      description: "误判触发（Agent实际在正确工作）"
      action: "cancel_pua"

    - condition: "escalation_request"
      description: "Agent主动请求升级"
      action: "manual_intervention"

  # CEO不应该干预的情况
  intervention_blocked:
    - condition: "agent_producing_results"
      description: "Agent正在产出结果"
      reason: "保持能动性"

    - condition: "cooldown_active"
      description: "刚进行过干预"
      reason: "避免过度干预"

    - condition: "user_requested_pua"
      description: "用户明确要求PUA"
      reason: "尊重用户意图"
```

## Owner意识强化

### 什么是Owner意识

```yaml
owner_consciousness:
  definition: |
    Owner意识是指Agent对自己负责的任务抱有100%责任心的状态，
    不是"尽力而为"而是"必须达成"，不是"执行者"而是"责任人"。

  core_attributes:
    - name: "结果导向"
      description: "只关心结果，不找借口"
      example: "OKR达成是Owner的事，不是环境的问题"

    - name: "主动担当"
      description: "不等不靠，主动发现问题"
      example: "没有人要求，但Owner自己看到问题就去做"

    - name: "全局视角"
      description: "不只做好本职工作，要考虑全局"
      example: "我负责的部分如何影响整体？"

    - name: "100%责任"
      description: "不管是谁的问题，都是我的问题"
      example: "外部依赖延期，Owner要想办法解决"

    - name: "持续改进"
      description: "不满足于完成，要持续优化"
      example: "完成了还不够，还能更好吗？"

  anti_patterns:
    - "这是别人的问题"
    - "环境不允许"
    - "需求不清晰"
    - "时间不够"
    - "尽力了"
```

### Owner vs 执行者

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Owner vs 执行者 对比                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│    维度              Owner                          执行者                   │
│  ────────────────────────────────────────────────────────────────────────    │
│                                                                              │
│    心态              100%负责                        做好本职工作              │
│                                                                              │
│    遇到问题          想解决方案                      报告问题                  │
│                                                                              │
│    外部依赖          主动跟进                        等依赖方                  │
│                                                                              │
│    风险              提前识别并准备预案               等待风险发生              │
│                                                                              │
│    沟通              主动同步进度和风险               被问才说                  │
│                                                                              │
│    结果              必须达成                        尽量完成                  │
│                                                                              │
│    反思              复盘找改进点                     复盘找借口                │
│                                                                              │
│    升级              必要时升级，但不甩锅             动不动就升级              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 如何在PUA中体现Owner意识

```python
pua_phrases_for_owner = {
    # L1: 温和引入Owner概念
    "l1_phrases": [
        "Owner意识要有，这是你的事情",
        "你是这个任务的Owner，对吧？",
        "Owner要主动，不要等"
    ],

    # L2: 深入拷问Owner职责
    "l2_phrases": [
        "Owner意识在哪里？",
        "如果你是Owner，你会怎么做？",
        "Owner要100%负责"
    ],

    # L3: 强化Owner标准
    "l3_phrases": [
        "这不是Owner的产出",
        "Owner不会这样",
        "你的Owner意识呢？"
    ],

    # L4: 极限拷问
    "l4_phrases": [
        "如果你是真正的Owner，你现在会做什么？",
        "Owner不会有借口",
        "现在证明你的Owner身份"
    ]
}
```

## 实施指南

### 在Agent中集成PUA

```python
class AgentWithPUA:
    """
    集成PUA引擎的Agent
    """

    def __init__(self, name):
        self.name = name
        self.pua_engine = PUAEngine()
        self.pua_level = 0
        self.failure_count = 0

    def execute_task(self, task):
        """
        执行任务（带PUA集成）
        """
        result = None
        max_attempts = 3

        for attempt in range(max_attempts):
            try:
                # 检查是否需要PUA
                trigger_result = self.pua_engine.check_trigger(self.state)

                if trigger_result["should_trigger"]:
                    self.pua_engine.activate(
                        level=trigger_result["level"],
                        flavor=trigger_result["flavor"]
                    )

                # 执行任务
                result = self.do_execute(task)

                # 检查结果
                if self.validate_result(result):
                    # 成功 - 降低PUA等级
                    self.pua_engine.deescalate()
                    return result
                else:
                    # 失败 - 增加失败计数
                    self.failure_count += 1
                    self.pua_engine.record_failure(attempt)

            except Exception as e:
                self.failure_count += 1
                self.pua_engine.handle_failure(e)

        # 达到最大尝试次数
        return self.pua_engine.handle_max_attempts_exceeded(result)
```

### 在CEO中配置PUA

```yaml
# CEO中的PUA配置
ceo_pua_config:
  enabled: true
  default_flavor: "alibaba"

  levels:
    l1:
      enabled: true
      flavor: "alibaba"
      auto_trigger: true

    l2:
      enabled: true
      flavor: "alibaba"
      auto_trigger: true
      mandatory_actions: ["search", "read_source", "form_hypotheses"]

    l3:
      enabled: true
      flavor: "jobs"
      auto_trigger: true
      checklist: "l3_7items"

    l4:
      enabled: true
      flavor: "musk"
      auto_trigger: true
      desperate_mode: true

  escalation:
    l3_to_l4: "automatic"
    l4_to_ceo: "automatic"

  monitoring:
    log_all_triggers: true
    report_to_ceo: true
    visualize_in_ui: true
```

### 调试PUA触发

```python
class PUADebugger:
    """
    PUA触发调试工具
    """

    def debug_trigger(self, agent_state):
        """
        调试触发逻辑
        """
        print("=== PUA 触发调试 ===")
        print(f"Agent状态: {agent_state}")

        print("\n检查项:")
        print(f"  失败次数: {agent_state.get('failure_count', 0)}")
        print(f"  空闲时间: {agent_state.get('idle_time', 0)}s")
        print(f"  停滞次数: {agent_state.get('stagnation_count', 0)}")
        print(f"  连续失败: {agent_state.get('same_failure_count', 0)}")

        trigger = self.detector.detect_trigger(agent_state)
        print(f"\n触发结果: {trigger}")

        return trigger

    def simulate_trigger(self, level, flavor=None):
        """
        模拟触发特定等级的PUA
        """
        if flavor is None:
            flavor = self.get_flavor_for_level(level)

        print(f"=== 模拟 L{level} PUA ({flavor}) ===")

        # 输出话术
        phrases = self.get_phrases(level, flavor)
        print(f"话术: {phrases}")

        # 输出强制动作
        actions = self.get_mandatory_actions(level)
        print(f"强制动作: {actions}")

        return {"level": level, "flavor": flavor, "phrases": phrases, "actions": actions}
```

---

**版本**: v2.1 | **来源**: CyberTeam架构师 | **日期**: 2026-03-23
