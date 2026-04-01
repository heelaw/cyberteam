# promotion-plan-architect

## 简介

整合用户画像、渠道选择、漏斗分析、转化诱因设计，输出完整的可落地推广方案。本Skill是S4推广营销进阶的最终输出Skill，涵盖6大要素。

## 触发关键词

```
推广方案、营销方案、推广策划、完整方案、6要素方案、落地计划、推广排期、推广总结
```

## 触发场景描述

```
当需要制定完整推广方案时触发本Skill：
- 制定月度/季度推广计划
- 为新产品制定首批推广方案
- 复盘优化现有推广方案
- 汇报推广策略和排期
```

## 输入

### 必需输入

| 字段 | 类型 | 说明 |
|------|------|------|
| product_info | string | 产品/服务基本信息 |
| target_users | object | 目标用户画像（来自user-targeting-analyzer） |
| selected_channels | array | 选定的推广渠道（来自promotion-channel-selector） |
| funnel_analysis | object | 漏斗分析结果（来自exposure-click-conversion-analyzer） |
| conversion_incentives | object | 转化诱因方案（来自conversion-incentive-designer） |

### 可选输入

| 字段 | 类型 | 说明 |
|------|------|------|
| budget | string | 推广预算 |
| timeline | string | 推广时间范围 |
| existing_kpis | object | 现有KPI数据 |

## 输出

### 完整推广方案

```json
{
  "plan_overview": {
    "product": "产品名称",
    "target_users_summary": "目标用户一句话描述",
    "selected_channels": ["渠道列表"],
    "total_budget": "总预算",
    "timeline": "推广周期"
  },
  "element_1_channel_rules": {
    "channel_name": {
      "rules": "渠道核心规则",
      "targeting": "定向设置",
      "bidding_strategy": "出价策略"
    }
  },
  "element_2_conversion_path": {
    "steps": [
      {
        "step": "步骤序号",
        "name": "步骤名称",
        "expected_users": "预期用户数",
        "design_notes": "设计说明"
      }
    ],
    "total_steps": "总步骤数",
    "optimization_notes": "优化说明"
  },
  "element_3_incentives": {
    "primary_incentive": "主要诱因",
    "supporting_incentives": ["辅助诱因"],
    "arup_boost": "ARUP提升措施"
  },
  "element_4_materials": {
    "creative_assets": [
      {
        "type": "素材类型",
        "specs": "规格要求",
        "count": "数量"
      }
    ],
    "copy_materials": [
      {
        "type": "文案类型",
        "count": "数量",
        "requirements": "要求"
      }
    ]
  },
  "element_5_timeline": {
    "phases": [
      {
        "phase": "阶段名称",
        "duration": "持续时间",
        "main_activities": ["主要活动"],
        "kpis": "阶段KPI"
      }
    ]
  },
  "element_6_data_monitoring": {
    "tracked_metrics": [
      {
        "metric": "指标名称",
        "target": "目标值",
        "frequency": "监控频率"
      }
    ],
    "reporting_rhythm": "汇报周期",
    "optimization_triggers": {
      "metric": "触发条件",
      "action": "调整动作"
    }
  }
}
```

## 方法论：推广方案6要素

一份可落地的营销推广方案应包括：

### 要素1：推广渠道的核心规则和推广逻辑

- 渠道的流量分发机制
- 推广投放的基本规则
- 定向设置和出价策略

### 要素2：用户转化路径和场景设计

- 用户从接触到转化的完整路径
- 各环节的场景设置
- 每步的预期流失

### 要素3：转化诱因设计

- 激发用户行动的关键因素
- 促成转化的动机设计
- ARUP提升措施

### 要素4：推广落地物料

- 所需图片、文案等素材
- 物料规格和标准
- 素材清单和数量

### 要素5：推广落地排期表

- 推广时间安排
- 各阶段工作计划
- 责任人分工

### 要素6：数据监控指标

- 核心监测数据
- 效果评估标准
- 优化触发条件

## 工作流步骤

### Step 1: 整合输入

- **输入:** 所有前置Skill的输出
- **处理:** 检查输入完整性，识别缺失项
- **输出:** 输入完整性报告
- **成功标准:** 所有6大要素都有对应输入

### Step 2: 设计转化路径

- **输入:** user_persona, selected_channels
- **处理:** 设计完整的用户转化路径
- **输出:** 转化路径设计（含步骤数和每步说明）
- **成功标准:** 路径不超过5步

### Step 3: 规划物料清单

- **输入:** conversion_incentives, conversion_path
- **处理:** 列出所需的创意物料和文案
- **输出:** 物料清单（含规格和数量）
- **成功标准:** 清单完整可执行

### Step 4: 制定排期

- **输入:** timeline, budget
- **处理:** 划分推广阶段，制定详细排期
- **输出:** 阶段划分和甘特图
- **成功标准:** 排期清晰可执行

### Step 5: 设计数据监控

- **输入:** funnel_analysis, selected_channels
- **处理:** 确定核心监控指标和优化触发条件
- **输出:** 数据监控方案
- **成功标准:** 指标可量化，触发条件明确

### Step 6: 输出完整方案

- **输入:** 以上所有输出
- **处理:** 整合成完整的推广方案文档
- **输出:** 6要素完整的推广方案
- **成功标准:** 方案可直接用于执行

## Critical Rules

### 必须遵守

1. 6大要素缺一不可
2. 转化路径不超过5步
3. 每个阶段有明确的KPI
4. 数据监控指标可量化
5. 方案可直接执行

### 禁止行为

1. 禁止缺少任何要素
2. 禁止路径超过5步（增加流失）
3. 禁止KPI设定不量化
4. 禁止方案与用户画像脱节
5. 禁止忽视数据监控设计

## 评估清单

### 评估维度

| 维度 | 标准 | 权重 |
|------|------|------|
| 要素完整性 | 6大要素全部包含 | 20% |
| 路径合理性 | 转化路径不超过5步 | 20% |
| KPI可衡量 | KPI设定量化可追踪 | 20% |
| 方案可执行 | 有明确的执行步骤 | 25% |
| 数据闭环 | 有监控和优化机制 | 15% |

### 评估标准

- **90-100分：** 五个维度全部达标，方案完整可执行
- **75-89分：** 四个维度达标，方案基本可行
- **60-74分：** 三个维度达标，需要补充
- **<60分：** 方案不完整，需要重做

## 参考文献

- `references/S4.1-6要素方案.md` - 6要素方案框架
- `references/promotion-plan-template.md` - 推广方案模板
- `references/kpi-design.md` - KPI设计指南
