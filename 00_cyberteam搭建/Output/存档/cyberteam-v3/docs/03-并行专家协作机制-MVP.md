# 并行专家协作机制 (MVP 版本)

> **版本**: v1.0-MVP
> **创建日期**: 2026-03-24
> **状态**: MVP 实现

---

## 一、MVP 设计原则

### 1.1 核心原则

```yaml
MVP 原则:
  最小可用: 只实现核心功能
  复用现有: 使用 TeamCreate 而非自建
  快速验证: 快速获得用户反馈
  渐进迭代: 后续逐步完善
```

### 1.2 MVP 范围

| 功能 | MVP | 未来 |
|------|-----|------|
| **协作模式** | 仅并行创意风暴 | +串行评审、专家辩论 |
| **专家数量** | 3 个核心专家 | +7 个完整专家 |
| **实现方式** | TeamCreate | +自定义并行框架 |
| **结果整合** | 简单汇总 | +智能整合 |

---

## 二、3 个核心专家定义

### 2.1 专家清单

| 专家 ID | 名称 | 职责 | 类型 |
|---------|------|------|------|
| **expert-user-persona** | 用户画像专家 | 深度理解目标用户 | 分析型 |
| **expert-copywriter** | 文案撰写专家 | 撰写高质量文案 | 创作型 |
| **expert-reviewer** | 内容审核专家 | 多维度质量把控 | 审核型 |

### 2.2 专家能力矩阵

```
┌─────────────────────────────────────────────────────────────────┐
│                      3 专家能力矩阵                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  能力维度          │ 用户画像 │ 文案撰写 │ 内容审核 │         │
│  ──────────────────┼─────────┼─────────┼─────────┤         │
│  用户理解          │ ⭐⭐⭐   │ ⭐⭐    │ ⭐⭐    │         │
│  创意输出          │ ⭐⭐    │ ⭐⭐⭐   │ ⭐      │         │
│  质量把控          │ ⭐      │ ⭐⭐    │ ⭐⭐⭐   │         │
│  数据分析          │ ⭐⭐⭐   │ ⭐      │ ⭐⭐    │         │
│  平台认知          │ ⭐⭐⭐   │ ⭐⭐    │ ⭐⭐⭐   │         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 三、TeamCreate 调用规范

### 3.1 调用时机

```yaml
自动触发:
  - 任务类型 == "内容创作"
  - 任务复杂度 == "高"
  - 用户明确要求专家讨论

手动触发:
  - PM 识别需要专家协作
  - 用户请求 "启用专家协作"
```

### 3.2 调用格式

```yaml
基本格式:
  TeamCreate(
    name="临时协作团队-{timestamp}",
    members=["expert-user-persona", "expert-copywriter", "expert-reviewer"],
    goal="{任务目标}",
    context="{任务上下文}"
  )

示例:
  TeamCreate(
    name="临时协作团队-20260324-151000",
    members=["expert-user-persona", "expert-copywriter", "expert-reviewer"],
    goal="为AI写作工具创作小红书内容",
    context="{
      platform: 小红书,
      product: AI写作工具,
      target_audience: 25-35岁内容创作者
    }"
  )
```

### 3.3 调用流程

```
PM 识别需要协作
    ↓
创建 TeamCreate 任务
    ↓
3 个专家并行分析
    ↓
专家提交分析结果
    ↓
PM 整合结果
    ↓
文案专家基于整合结果创作
    ↓
审核专家审核
    ↓
最终交付
```

---

## 四、协作模式：并行创意风暴

### 4.1 流程设计

```yaml
阶段1: 用户画像专家先行 (5分钟)
  输出:
    - 目标用户画像
    - 用户痛点清单
    - 用户场景卡片

阶段2: 3专家并行创意风暴 (10分钟)
  并行输出:
    - 用户画像专家: 补充分析
    - 文案撰写专家: 初步创意
    - 内容审核专家: 质量标准

阶段3: 创意整合会 (5分钟)
  整合:
    - PM 汇总专家意见
    - 辩论优化创意方案
    - 投票选择最佳方案

阶段4: 文案创作 (15分钟)
  输出:
    - 完整文案初稿
    - 多版本标题备选

阶段5: 质量审核 (10分钟)
  输出:
    - 审核报告
    - 优化建议
    - 通过/打回决策

阶段6: 最终优化 (5分钟)
  输出:
    - 最终文案
    - 发布清单
```

### 4.2 时间估算

| 阶段 | 时长 | 说明 |
|------|------|------|
| 用户画像分析 | 5分钟 | 单专家执行 |
| 并行创意风暴 | 10分钟 | 3专家并行 |
| 创意整合 | 5分钟 | PM主导 |
| 文案创作 | 15分钟 | 文案专家 |
| 质量审核 | 10分钟 | 审核专家 |
| 最终优化 | 5分钟 | 文案+审核 |
| **总计** | **50分钟** | 每篇内容 |

---

## 五、专家输出格式

### 5.1 用户画像专家输出

```json
{
  "expert": "用户画像专家",
  "analysis": {
    "target_audience": {
      "age_range": "25-35岁",
      "gender": "不限",
      "occupation": "内容创作者/自媒体",
      "income_level": "中等",
      "location": "一二线城市"
    },
    "pain_points": [
      "每天不知道写什么",
      "写作耗时长",
      "灵感枯竭",
      "竞争压力大"
    ],
    "needs": [
      "快速生成灵感",
      "提升写作效率",
      "内容质量保证",
      "差异化竞争优势"
    ],
    "scenarios": [
      "深夜加班赶稿",
      "周报/月报撰写",
      "多平台内容分发",
      "热点跟进"
    ]
  },
  "recommendations": {
    "content_angle": "效率提升+质量保证",
    "tone": "专业且亲切",
    "format": "小红书图文笔记"
  }
}
```

### 5.2 文案撰写专家输出

```json
{
  "expert": "文案撰写专家",
  "creative": {
    "angle": "对比法 - AI vs 传统写作",
    "hook": "用AI写作后，我每天多出2小时做这件事",
    "differentiation": "不只讲功能，讲多出来的时间做什么",
    "emotional_value": "效率提升后的生活改善"
  },
  "content": {
    "titles": [
      "用AI写作后，我每天多出2小时做这件事",
      "3个AI写作工具，让你的内容效率翻倍",
      "从每天3小时到30分钟，我的AI写作心法"
    ],
    "structure": {
      "opening": "场景代入 + 痛点共鸣",
      "body": "对比展示 + 实用技巧",
      "closing": "行动号召 + 互动引导"
    }
  },
  "draft": "完整文案初稿..."
}
```

### 5.3 内容审核专家输出

```json
{
  "expert": "内容审核专家",
  "review": {
    "overall_score": 85,
    "verdict": "pass",
    "dimensions": {
      "compliance": {
        "score": 30,
        "max": 30,
        "status": "pass"
      },
      "accuracy": {
        "score": 23,
        "max": 25,
        "status": "pass"
      },
      "viral": {
        "score": 20,
        "max": 25,
        "status": "pass"
      },
      "completeness": {
        "score": 12,
        "max": 20,
        "status": "warning"
      }
    }
  },
  "issues": [
    {
      "level": "warning",
      "dimension": "completeness",
      "description": "配图不足",
      "suggestion": "增加对比配图"
    }
  ],
  "approval": "有条件通过"
}
```

---

## 六、结果整合逻辑

### 6.1 整合流程

```yaml
Step 1: 收集专家输出
  - 接收用户画像专家输出
  - 接收文案撰写专家输出
  - 接收内容审核专家输出

Step 2: 分析冲突
  - 识别专家意见冲突
  - 评估冲突严重程度
  - 决定处理方式

Step 3: 整合方案
  - 综合用户画像
  - 融合创意方案
  - 应用质量标准

Step 4: 生成最终方案
  - 明确内容方向
  - 确定文案结构
  - 列出优化建议
```

### 6.2 整合算法

```python
def integrate_expert_outputs(user_persona, copywriter, reviewer):
    """整合专家输出"""

    # 1. 提取核心要素
    target_audience = user_persona["analysis"]["target_audience"]
    pain_points = user_persona["analysis"]["pain_points"]
    angle = copywriter["creative"]["angle"]
    titles = copywriter["content"]["titles"]
    quality_standard = reviewer["review"]["dimensions"]

    # 2. 生成整合方案
    integrated_plan = {
        "target_audience": target_audience,
        "content_angle": angle,
        "pain_points_to_address": pain_points,
        "recommended_titles": titles,
        "quality_requirements": quality_standard,
        "optimization_suggestions": reviewer["review"]["issues"]
    }

    # 3. 处理冲突
    if reviewer["review"]["verdict"] == "reject":
        # 需要重新创作
        return {"status": "revision_needed", "reasons": reviewer["review"]["issues"]}
    elif reviewer["review"]["verdict"] == "conditional_pass":
        # 需要优化
        return {
            "status": "optimization_needed",
            "plan": integrated_plan,
            "issues": reviewer["review"]["issues"]
        }
    else:
        # 直接通过
        return {"status": "approved", "plan": integrated_plan}
```

---

## 七、PM 协调逻辑

### 7.1 PM 职责

```yaml
PM 在并行协作中的职责:

协调前:
  - 识别是否需要专家协作
  - 创建 TeamCreate 任务
  - 定义协作目标和上下文

协调中:
  - 监控专家进度
  - 收集专家输出
  - 处理专家冲突

协调后:
  - 整合专家结果
  - 生成最终方案
  - 汇报给 CEO
```

### 7.2 PM 决策树

```
收到任务
    ↓
任务复杂度判断
    ↓
  复杂度高?
    ↓ 是
  内容创作?
    ↓ 是
触发专家协作
    ↓
创建 TeamCreate
    ↓
监控进度
    ↓
收集结果
    ↓
整合方案
    ↓
交付结果
```

---

## 八、测试验证方案

### 8.1 功能测试

```yaml
测试场景1: 简单内容创作
  输入: "为咖啡品牌写小红书文案"
  预期: 触发3专家协作，输出高质量文案

测试场景2: 复杂内容创作
  输入: "为SaaS产品创作品牌升级内容"
  预期: 触发3专家协作，输出完整品牌方案

测试场景3: 非内容任务
  输入: "分析增长数据"
  预期: 不触发专家协作，直接执行
```

### 8.2 效果验证

```yaml
验证指标:
  - 协作成功率: >90%
  - 平均协作时间: <50分钟/篇
  - 内容质量评分: >80分
  - 用户满意度: >85%

验证方法:
  - A/B测试: 协作 vs 非协作
  - 用户反馈: 收集用户意见
  - 数据分析: 分析协作效果
```

---

## 九、后续迭代计划

### 9.1 MVP → v1.0

```yaml
v1.0 增强功能:
  - 增加其余4个专家
  - 实现串行评审模式
  - 实现专家辩论模式
  - 优化结果整合算法
  - 增加协作模板
```

### 9.2 v1.0 → v2.0

```yaml
v2.0 高级功能:
  - 自主触发专家协作
  - 动态专家选择
  - 学习型结果整合
  - 实时协作监控
  - 协作效果分析
```

---

## 十、使用示例

### 10.1 完整流程示例

```yaml
用户输入:
  "帮我为AI写作工具创作小红书内容"

CEO 处理:
  - 意图识别: 内容创作
  - 复杂度评估: 高
  - 路由决策: L2 PM + Strategy

Strategy 处理:
  - 需求分析 (5W1H1Y)
  - 任务拆解 (MECE)
  - 方案设计: 触发专家协作

PM 处理:
  - 创建 TeamCreate
  - 监控协作进度
  - 收集专家结果
  - 整合最终方案

TeamCreate 执行:
  - 3专家并行分析
  - 创意整合会
  - 文案创作
  - 质量审核
  - 最终优化

最终交付:
  - 用户画像报告
  - 创意方案
  - 完整文案
  - 审核报告
  - 发布清单
```

---

**文档版本**: v1.0-MVP
**创建日期**: 2026-03-24
**状态**: MVP 实现

---

*本文档定义了并行专家协作机制的 MVP 版本，使用 TeamCreate 实现 3 专家并行协作，快速验证核心架构可行性。*
