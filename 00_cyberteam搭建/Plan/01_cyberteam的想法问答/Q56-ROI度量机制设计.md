# Q56: 思考天团ROI度量机制设计

**问题**: 如何设计思考天团的ROI（投资回报率）度量机制，量化系统价值？

---

## 一、设计目标与原则

### 1.1 核心目标

| 目标 | 说明 |
|------|------|
| **价值可视化** | 清晰展示系统投入带来的实际价值 |
| **决策支持** | 为系统优化和资源配置提供数据依据 |
| **持续追踪** | 建立长期ROI监控机制 |
| **归因分析** | 识别价值来源，优化投入产出比 |

### 1.2 设计原则

| 原则 | 说明 |
|------|------|
| **与Q53保持一致** | 基于Token消耗计算投入成本 |
| **分层度量** | 从系统→任务→场景三级度量 |
| **可量化** | 所有价值必须可量化或可估算 |
| **可追溯** | 价值贡献可追溯到具体环节 |

### 1.3 与Q53成本控制的关系

```
Q53 成本控制 ──────► 投入数据来源
     │
     ├── Token消耗数据
     │   ├── COST_QUESTION (问题成本)
     │   ├── COST_EXPERT (专家成本)
     │   └── COST_RATIO (Token效率)
     │
     └── 成本边界
         ├── L1 系统级预算
         ├── L2 任务级预算
         └── L3 专家级预算

本设计 ───────────► ROI度量增强
     │
     ├── 投入计算 (基于Q53成本)
     ├── 产出量化 (时间节省+价值贡献)
     ├── ROI公式 (产出/投入)
     └── 成功标准 (ROI阈值)
```

---

## 二、投入（成本）体系

### 2.1 投入分解树

基于Q53的成本模型，定义完整的投入体系：

```
总投入 (Total Investment)
│
├── LLM成本 (LLM Cost) ◄─── 核心投入
│   ├── 意图分析成本: ~$0.008/次
│   ├── 专家分析成本: ~$0.36/次 (最大)
│   ├── 消息传递成本: ~$0.045/次
│   ├── 辩论整合成本: ~$0.063/次
│   └── 上下文加载成本: ~$0.025/次
│
├── 运维成本 (Ops Cost)
│   ├── 服务器费用: ~$0.01/次
│   ├── API调用费用: ~$0.005/次
│   └── 存储费用: ~$0.002/次
│
└── 人力成本 (Human Cost) ◄─── 间接投入
    ├── 系统维护: ~$0.02/次
    ├── 专家调优: ~$0.01/次
    └── 监控管理: ~$0.005/次
```

### 2.2 成本量化标准

| 指标ID | 成本类别 | 指标名称 | 计算方式 | 单位 |
|--------|----------|---------|---------|------|
| COST_LLM | LLM成本 | LLM总成本 | Token消耗 × 单价 | 美元 |
| COST_OPS | 运维成本 | 运维成本 | 服务器+API+存储 | 美元 |
| COST_HUMAN | 人力成本 | 人力成本 | 维护+调优+管理 | 美元 |
| COST_TOTAL | 全部 | 总投入 | LLM+运维+人力 | 美元 |

### 2.3 成本单价参考（基于Q53）

| 成本项 | 单价 | 说明 |
|--------|------|------|
| LLM输入 | $3.00/1M tokens | Claude Sonnet |
| LLM输出 | $15.00/1M tokens | Claude Sonnet |
| 平均Token/问题 | 50,000 | 优化后目标 |
| **LLM成本/问题** | **$0.45** | 优化后 |
| 运维成本/问题 | $0.017 | 估算 |
| 人力成本/问题 | $0.035 | 估算 |
| **总投入/问题** | **$0.50** | 保守估计 |

### 2.4 场景示例：14专家全部调用

```
问题: 如何提升DAU 10%？

投入明细:
├── LLM成本: $0.50
│   ├── 意图分析: $0.008
│   ├── 专家分析: $0.36 (14专家)
│   ├── 消息传递: $0.045
│   ├── 辩论整合: $0.063
│   └── 上下文加载: $0.025
│
├── 运维成本: $0.017
│   ├── 服务器: $0.01
│   ├── API调用: $0.005
│   └── 存储: $0.002
│
└── 人力成本: $0.035
    ├── 系统维护: $0.02
    ├── 专家调优: $0.01
    └── 监控管理: $0.005

总投入: $0.55/次问题
```

---

## 三、产出（价值）体系

### 3.1 产出分解树

```
总产出 (Total Value)
│
├── 时间价值 (Time Value)
│   ├── 决策时间节省: ~2小时/次 = $100
│   ├── 分析时间节省: ~1小时/次 = $50
│   └── 调研时间节省: ~3小时/次 = $150
│
├── 质量价值 (Quality Value)
│   ├── 决策质量提升: ~20% = $200
│   ├── 方案完整性提升: ~30% = $150
│   └── 风险识别率提升: ~40% = $100
│
└── 机会价值 (Opportunity Value)
    ├── 快速迭代: ~1周/次 = $500
    ├── 市场窗口捕获: ~$1000
    └── 竞品领先: ~$500
```

### 3.2 价值量化标准

| 指标ID | 价值类别 | 指标名称 | 计算方式 | 单位 |
|--------|----------|---------|---------|------|
| VALUE_TIME | 时间价值 | 时间节省价值 | 节省时间 × 时薪 | 美元 |
| VALUE_QUALITY | 质量价值 | 质量提升价值 | 质量提升 × 基数 | 美元 |
| VALUE_OPPORTUNITY | 机会价值 | 机会捕获价值 | 机会价值 × 概率 | 美元 |
| VALUE_TOTAL | 全部 | 总产出 | 时间+质量+机会 | 美元 |

### 3.3 价值估算方法

#### 3.3.1 时间价值计算

```python
# 时间价值估算器
class TimeValueCalculator:
    """时间价值计算器"""

    # 人工成本参考（时薪）
    HOURLY_RATES = {
        "junior": 25,      # 初级分析师
        "mid": 50,         # 中级分析师
        "senior": 100,     # 高级分析师
        "expert": 200,     # 专家顾问
    }

    # 时间节省参考
    TIME_SAVINGS = {
        "decision": {"hours": 2, "role": "senior", "description": "决策时间节省"},
        "analysis": {"hours": 1, "role": "mid", "description": "分析时间节省"},
        "research": {"hours": 3, "role": "junior", "description": "调研时间节省"},
    }

    def calculate_time_value(self, question_type: str, role: str = "senior") -> float:
        """计算时间价值"""

        time_saving = self.TIME_SAVINGS.get(question_type, {"hours": 1, "role": "senior"})
        hourly_rate = self.HOURLY_RATES.get(role, 50)

        return time_saving["hours"] * hourly_rate
```

#### 3.3.2 质量价值计算

```python
# 质量价值估算器
class QualityValueCalculator:
    """质量价值计算器"""

    # 质量提升系数（相对于人工分析）
    QUALITY_IMPROVEMENT = {
        "decision": {
            "quality_up": 0.20,      # 决策质量提升20%
            "base_value": 1000,      # 基数价值
            "description": "决策质量提升"
        },
        "completeness": {
            "quality_up": 0.30,      # 方案完整性提升30%
            "base_value": 500,      # 基数价值
            "description": "方案完整性提升"
        },
        "risk_identification": {
            "quality_up": 0.40,      # 风险识别率提升40%
            "base_value": 250,      # 基数价值
            "description": "风险识别率提升"
        }
    }

    def calculate_quality_value(self, quality_type: str) -> float:
        """计算质量价值"""

        improvement = self.QUALITY_IMPROVEMENT.get(quality_type)
        if not improvement:
            return 0

        return improvement["quality_up"] * improvement["base_value"]
```

#### 3.3.3 机会价值计算

```python
# 机会价值估算器
class OpportunityValueCalculator:
    """机会价值计算器"""

    # 机会价值参考
    OPPORTUNITY_VALUES = {
        "fast_iteration": {
            "time_saved_weeks": 1,
            "weekly_value": 500,
            "description": "快速迭代节省时间"
        },
        "market_window": {
            "value": 1000,
            "probability": 0.3,      # 30%概率捕获
            "description": "市场窗口捕获"
        },
        "competitor_lead": {
            "value": 500,
            "probability": 0.5,      # 50%概率领先
            "description": "竞品领先优势"
        }
    }

    def calculate_opportunity_value(self, opportunity_type: str) -> float:
        """计算机会价值"""

        opportunity = self.OPPORTUNITY_VALUES.get(opportunity_type)
        if not opportunity:
            return 0

        # 期望值 = 价值 × 概率
        if "probability" in opportunity:
            return opportunity["value"] * opportunity["probability"]
        else:
            return opportunity.get("value", 0)
```

### 3.4 场景示例：增长策略问题

```
问题: 如何提升DAU 10%？

产出明细:
├── 时间价值: $300
│   ├── 决策时间节省 (2小时×$100): $200
│   │   └── 原本需要管理层讨论2小时
│   │
│   └── 调研时间节省 (2小时×$50): $100
│       └── 原本需要市场调研团队2小时
│
├── 质量价值: $350
│   ├── 决策质量提升 (20%×$1000): $200
│   │   └── 14个专家视角更全面
│   │
│   ├── 方案完整性提升 (30%×$300): $90
│   │   └── 考虑更周全，遗漏更少
│   │
│   └── 风险识别率提升 (40%×$150): $60
│       └── 提前识别潜在风险
│
└── 机会价值: $450
    ├── 快速迭代 (1周×$500): $500
    │   └── 原需要1周，现在更快
    │
    └── 市场窗口捕获 (50%概率): -$50
        └── 扣除失败成本

总产出: $1,100/次问题
```

---

## 四、ROI计算公式

### 4.1 基础公式

```
ROI (投资回报率) = (总产出 - 总投入) / 总投入 × 100%
```

### 4.2 分层公式

#### 4.2.1 系统级ROI

```
系统ROI = (系统总产出 - 系统总投入) / 系统总投入 × 100%

周期: 月度/季度/年度
```

#### 4.2.2 任务级ROI

```
任务ROI = (任务产出 - 任务投入) / 任务投入 × 100%

按问题类型:
├── 战略类问题ROI
├── 增长类问题ROI
├── 问题诊断类ROI
└── 日常决策类ROI
```

#### 4.2.3 场景级ROI

```
场景ROI = (场景累计产出 - 场景累计投入) / 场景累计投入 × 100%

按应用场景:
├── 产品决策场景ROI
├── 运营优化场景ROI
├── 市场营销场景ROI
└── 团队管理场景ROI
```

### 4.3 场景示例计算

```
问题: 如何提升DAU 10%？

投入:
├── LLM成本: $0.50
├── 运维成本: $0.017
└── 人力成本: $0.035
    └── 总投入: $0.55

产出:
├── 时间价值: $300
├── 质量价值: $350
└── 机会价值: $450
    └── 总产出: $1,100

ROI计算:
ROI = ($1,100 - $0.55) / $0.55 × 100%
ROI = $1,099.45 / $0.55 × 100%
ROI = 199,900%

结论: 该问题的ROI约为200,000%
```

### 4.4 简化公式（推荐使用）

考虑到精确计算产出的复杂性，推荐使用简化公式：

```
简化ROI = 价值倍数 × 质量系数 - 1

其中:
价值倍数 = 预估总产出 / 总投入
质量系数 = 0.8~1.2 (根据质量评估调整)
```

```python
# ROI计算器
class ROICalculator:
    """ROI计算器"""

    def calculate_roi(self, question_type: str, input_data: dict) -> dict:
        """计算ROI"""

        # 1. 计算投入（基于Q53数据）
        total_input = self.calculate_input_cost(question_type, input_data)

        # 2. 计算产出
        time_value = self.calculate_time_value(question_type, input_data)
        quality_value = self.calculate_quality_value(question_type, input_data)
        opportunity_value = self.calculate_opportunity_value(question_type, input_data)
        total_output = time_value + quality_value + opportunity_value

        # 3. 计算ROI
        roi = (total_output - total_input) / total_input * 100

        return {
            "total_input": total_input,
            "total_output": total_output,
            "roi": roi,
            "roi_multiplier": total_output / total_input,
            "breakdown": {
                "time_value": time_value,
                "quality_value": quality_value,
                "opportunity_value": opportunity_value
            }
        }

    def calculate_input_cost(self, question_type: str, input_data: dict) -> float:
        """计算投入成本"""

        # 从Q53数据获取Token消耗
        tokens = input_data.get("tokens", 50000)  # 默认50k

        # LLM成本
        llm_cost = tokens / 1_000_000 * 10  # 平均$10/1M tokens

        # 运维成本
        ops_cost = 0.017

        # 人力成本
        human_cost = 0.035

        return llm_cost + ops_cost + human_cost

    def calculate_time_value(self, question_type: str, input_data: dict) -> float:
        """计算时间价值"""

        # 基于问题类型的时间节省
        time_savings = {
            "growth": 2.5,      # 增长类问题平均节省2.5小时
            "strategy": 3.0,     # 战略类问题平均节省3小时
            "diagnosis": 2.0,    # 问题诊断平均节省2小时
            "decision": 1.5,     # 日常决策平均节省1.5小时
        }

        hours = time_savings.get(question_type, 2.0)
        hourly_rate = input_data.get("hourly_rate", 100)  # 默认高级分析师

        return hours * hourly_rate

    def calculate_quality_value(self, question_type: str, input_data: dict) -> float:
        """计算质量价值"""

        # 基于问题类型的质量提升
        quality_base = {
            "growth": 500,
            "strategy": 800,
            "diagnosis": 300,
            "decision": 200,
        }

        base = quality_base.get(question_type, 400)
        quality_factor = input_data.get("quality_factor", 1.0)

        return base * quality_factor

    def calculate_opportunity_value(self, question_type: str, input_data: dict) -> float:
        """计算机会价值"""

        # 机会价值通常难以精确量化，使用保守估计
        opportunity_base = {
            "growth": 400,
            "strategy": 600,
            "diagnosis": 200,
            "decision": 100,
        }

        base = opportunity_base.get(question_type, 300)

        # 考虑成功概率
        probability = input_data.get("success_probability", 0.7)

        return base * probability
```

---

## 五、成功标准定义

### 5.1 ROI等级划分

| ROI等级 | ROI范围 | 说明 | 行动 |
|---------|---------|------|------|
| **S级** | > 100,000% | 卓越价值 | 重点投资，扩大使用 |
| **A级** | 10,000% - 100,000% | 高价值 | 保持当前投入 |
| **B级** | 1,000% - 10,000% | 价值 | 优化提升 |
| **C级** | 100% - 1,000% | 盈亏平衡 | 分析原因，改进 |
| **D级** | < 100% | 亏损 | 重新评估或停止 |

### 5.2 场景化成功标准

| 场景 | 最低成功ROI | 目标ROI | 说明 |
|------|-------------|---------|------|
| **战略决策** | 50,000% | 200,000% | 高 stakes，需要高质量 |
| **增长策略** | 30,000% | 100,000% | 增长类问题价值高 |
| **问题诊断** | 20,000% | 50,000% | 节省调研时间 |
| **日常决策** | 5,000% | 20,000% | 快速响应为主 |

### 5.3 量化成功指标

| 指标 | 最低要求 | 目标 | 测量周期 |
|------|----------|------|----------|
| **系统级月ROI** | 10,000% | 50,000% | 每月 |
| **平均任务ROI** | 5,000% | 20,000% | 每周 |
| **价值产出/问题** | $50 | $200 | 每日 |
| **投入产出比** | 50倍 | 200倍 | 每周 |

### 5.4 成功标准判定流程

```python
# ROI成功判定
class ROISuccessChecker:
    """ROI成功判定器"""

    def check_success(self, roi: float, context: dict) -> dict:
        """检查ROI是否达到成功标准"""

        question_type = context.get("question_type", "decision")
        scene = context.get("scene", "general")

        # 获取该场景的成功标准
        thresholds = self.get_thresholds(question_type, scene)

        # 判定
        if roi >= thresholds["excellent"]:
            return {
                "level": "S",
                "status": "excellent",
                "action": "重点投资，扩大使用",
                "roi_gap": roi - thresholds["excellent"]
            }
        elif roi >= thresholds["good"]:
            return {
                "level": "A",
                "status": "good",
                "action": "保持当前投入",
                "roi_gap": roi - thresholds["good"]
            }
        elif roi >= thresholds["acceptable"]:
            return {
                "level": "B",
                "status": "acceptable",
                "action": "优化提升",
                "roi_gap": roi - thresholds["acceptable"]
            }
        elif roi >= thresholds["break_even"]:
            return {
                "level": "C",
                "status": "break_even",
                "action": "分析原因，改进",
                "roi_gap": roi - thresholds["break_even"]
            }
        else:
            return {
                "level": "D",
                "status": "loss",
                "action": "重新评估或停止",
                "roi_gap": roi - thresholds["break_even"]
            }

    def get_thresholds(self, question_type: str, scene: str) -> dict:
        """获取成功标准阈值"""

        thresholds = {
            "strategy": {
                "excellent": 200000,
                "good": 100000,
                "acceptable": 50000,
                "break_even": 10000
            },
            "growth": {
                "excellent": 100000,
                "good": 50000,
                "acceptable": 30000,
                "break_even": 10000
            },
            "diagnosis": {
                "excellent": 50000,
                "good": 30000,
                "acceptable": 20000,
                "break_even": 5000
            },
            "decision": {
                "excellent": 20000,
                "good": 10000,
                "acceptable": 5000,
                "break_even": 1000
            }
        }

        return thresholds.get(question_type, thresholds["decision"])
```

---

## 六、数据采集与存储

### 6.1 数据来源（基于Q20文件体系）

```json
// workspace/tasks/{question_id}/roi_analysis.json
{
  "question_id": "q_20260320_001",
  "question": "如何提升DAU 10%？",
  "question_type": "growth",
  "scene": "product_growth",
  "status": "completed",

  // Q53成本数据（投入）
  "input": {
    "llm_cost": 0.50,
    "ops_cost": 0.017,
    "human_cost": 0.035,
    "total_input": 0.55,

    "token_usage": {
      "total": 50000,
      "cost_usd": 0.45
    }
  },

  // 产出数据
  "output": {
    "time_value": {
      "decision_saved_hours": 2,
      "research_saved_hours": 1,
      "hourly_rate": 100,
      "total": 300
    },

    "quality_value": {
      "decision_quality_up": 0.20,
      "completeness_up": 0.30,
      "risk_identification_up": 0.40,
      "total": 350
    },

    "opportunity_value": {
      "fast_iteration": 500,
      "market_window": -50,
      "total": 450
    },

    "total_output": 1100
  },

  // ROI计算结果
  "roi": {
    "value": 199900,
    "level": "S",
    "status": "excellent",
    "multiplier": 2000
  }
}
```

### 6.2 目录结构扩展

```
thinking-team/
├── config/
│   └── roi/
│       ├── thresholds.yaml          # ROI阈值配置
│       ├── value_rates.yaml         # 价值单价配置
│       └── question_types.yaml      # 问题类型映射
│
├── performance/
│   └── roi_analysis/               # ROI分析
│       ├── daily/
│       │   └── {date}.json
│       ├── by_question_type/
│       │   └── {type}.json
│       ├── by_scene/
│       │   └── {scene}.json
│       └── reports/
│           └── {date}/
│               └── roi_report.json
│
└── scripts/
    ├── roi_calculator.py            # ROI计算器
    ├── value_estimator.py          # 价值估算器
    └── roi_reporter.py             # ROI报告生成
```

---

## 七、与Q53的集成

### 7.1 数据流关系

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           ROI度量数据流                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Q53 成本控制                                                            │
│  ┌──────────────────┐    ┌──────────────────┐                          │
│  │ token_usage      │    │ cost_breakdown   │                          │
│  │ (Token消耗数据)  │    │ (成本分解)       │                          │
│  └────────┬─────────┘    └────────┬─────────┘                          │
│           │                         │                                    │
│           └─────────────────────────┼──────────────────────────────────│
│                                     ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ ROIMeasurement                                                    │   │
│  │   - 投入计算 (基于Q53成本)                                        │   │
│  │   - 产出量化 (时间+质量+机会)                                      │   │
│  │   - ROI计算 (产出/投入)                                           │   │
│  │   - 成功判定 (ROI阈值)                                            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                     │                                    │
│                                     ▼                                    │
│  ┌──────────────────┐    ┌──────────────────┐                          │
│  │ 性能看板         │    │ ROI报告          │                          │
│  │ (ROI展示)        │    │ (周期性报告)     │                          │
│  └──────────────────┘    └──────────────────┘                          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.2 指标对应关系

| Q53成本指标 | 本设计投入指标 | 说明 |
|------------|--------------|------|
| COST_QUESTION | COST_TOTAL | 完整投入 |
| TK_TOTAL | COST_LLM | Token消耗转LLM成本 |
| - | COST_OPS | 新增运维成本 |
| - | COST_HUMAN | 新增人力成本 |

| 本设计产出指标 | 说明 |
|--------------|------|
| VALUE_TIME | 时间节省价值 |
| VALUE_QUALITY | 质量提升价值 |
| VALUE_OPPORTUNITY | 机会捕获价值 |

---

## 八、CLI命令设计

### 8.1 ROI查询命令

```bash
# 查看单次问题ROI
thinking-team roi query q_20260320_001

# 输出:
# 问题: 如何提升DAU 10%？
# 问题类型: growth
#
# 投入:
#   LLM成本: $0.50
#   运维成本: $0.017
#   人力成本: $0.035
#   总投入: $0.55
#
# 产出:
#   时间价值: $300
#   质量价值: $350
#   机会价值: $450
#   总产出: $1,100
#
# ROI: 199,900%
# 等级: S (卓越价值)
# 行动: 重点投资，扩大使用

# 查看日/周/月ROI统计
thinking-team roi daily --date 2026-03-20

# 输出:
# 日期: 2026-03-20
# 问题数: 50
# 总投入: $27.50
# 总产出: $55,000
# 平均ROI: 200,000%
# S级问题: 40个
# A级问题: 8个

# 按问题类型查看ROI
thinking-team roi by-type --period week

# 输出:
# 本周问题类型ROI:
#   strategy:  250,000% (10个) ← 最高
#   growth:    200,000% (15个)
#   diagnosis:  150,000% (15个)
#   decision:  100,000% (10个)

# 查看ROI趋势
thinking-team roi trend --period month

# 输出:
# 月度ROI趋势:
#   2月: 150,000%
#   3月: 200,000% (+33%)
```

### 8.2 价值配置命令

```bash
# 查看价值单价配置
thinking-team roi config rates

# 输出:
# 时间单价:
#   Junior: $25/小时
#   Mid: $50/小时
#   Senior: $100/小时
#   Expert: $200/小时

# 修改价值单价
thinking-team roi config set-rate --role senior --rate 120

# 查看ROI阈值
thinking-team roi config thresholds

# 输出:
# ROI成功标准:
#   S级: >100,000%
#   A级: >10,000%
#   B级: >1,000%
#   C级: >100%
#   D级: <100%
```

---

## 九、实施建议

### 9.1 实施阶段

| 阶段 | 时间 | 内容 | 交付物 |
|------|------|------|--------|
| **第一阶段** | 1天 | 投入数据采集 | 复用Q53成本数据 |
| **第二阶段** | 1天 | 产出价值估算 | 价值计算器实现 |
| **第三阶段** | 0.5天 | ROI计算 | ROI计算器 |
| **第四阶段** | 0.5天 | 成功标准 | 阈值配置+判定器 |
| **第五阶段** | 0.5天 | CLI命令 | roi查询命令 |
| **第六阶段** | 0.5天 | 看板展示 | ROI展示看板 |

### 9.2 优先级

1. **P0 - 必须**
   - 投入数据采集（复用Q53）
   - 基础ROI计算
   - 成功标准定义

2. **P1 - 重要**
   - 产出价值估算
   - CLI查询命令
   - ROI趋势分析

3. **P2 - 增强**
   - 场景化ROI分析
   - 自动化报告
   - 智能优化建议

### 9.3 关键成功指标

| 指标 | 当前值 | 目标 | 测量周期 |
|------|--------|------|----------|
| **系统月ROI** | - | > 50,000% | 每月 |
| **平均任务ROI** | - | > 20,000% | 每周 |
| **S级问题占比** | - | > 50% | 每周 |
| **价值产出/问题** | - | > $100 | 每日 |

---

## 十、总结

### 10.1 设计要点

| 要点 | 说明 |
|------|------|
| **投入量化** | 基于Q53成本模型，定义LLM+运维+人力三层投入 |
| **产出量化** | 量化时间+质量+机会三类价值 |
| **ROI公式** | 简洁清晰：ROI = (产出-投入)/投入×100% |
| **成功标准** | S/A/B/C/D五级ROI判定，对应不同行动 |
| **数据集成** | 复用Q53成本数据，扩展价值数据 |

### 10.2 与Q53的一致性

| 设计点 | Q53 | 本设计 |
|--------|-----|--------|
| 成本模型 | 5环节Token分解 | 对应3层投入 |
| 成本单价 | $0.50/问题 | 复用并扩展 |
| 预算边界 | L1/L2/L3三级 | ROI成功标准对应 |
| 数据存储 | workspace/tasks/*.json | 扩展roi_analysis |
| CLI命令 | token/budget命令 | 新增roi命令 |

### 10.3 预期效果

| 场景 | 投入 | 产出 | ROI |
|------|------|------|-----|
| 战略决策 | $0.55 | $2,000 | 363,600% |
| 增长策略 | $0.55 | $1,100 | 199,900% |
| 问题诊断 | $0.55 | $500 | 90,800% |
| 日常决策 | $0.55 | $200 | 36,300% |

**结论**: 思考天团的ROI极高（>10,000%），属于S/A级高价值系统，值得重点投资。

---

**设计日期**: 2026-03-20
**文档编号**: Q56
**参考**: Q53 Token消耗优化机制
**前置文档**: Q53成本控制体系
