# Q53: 思考天团Token消耗优化机制设计

**问题**: 如何设计思考天团的Token消耗优化机制，控制LLM调用成本？

---

## 一、设计目标与原则

### 1.1 核心目标

| 目标 | 说明 |
|------|------|
| **成本可视化** | 清晰了解Token消耗在哪些环节 |
| **智能节省** | 在保证质量的前提下减少Token消耗 |
| **边界控制** | 设定成本上限，防止无限消耗 |
| **持续优化** | 建立量化指标，持续追踪优化效果 |

### 1.2 设计原则

| 原则 | 说明 |
|------|------|
| **与Q20保持一致** | 基于文件体系存储Token消耗数据 |
| **与Q44对齐** | 复用性能瓶颈分解模型，区分耗时 vs Token消耗 |
| **分层控制** | 从系统→任务→专家三级控制 |
| **质量优先** | 优化不能牺牲输出质量 |

### 1.3 与现有体系的关系

```
Q20 文件体系 ──────► Token数据存储
     │                    │
     │                    ├── workspace/tasks/*.json (含tokens_used)
     │                    ├── messages/* (消息Token统计)
     │                    └── performance/ (Token消耗分析)

Q44 性能瓶颈 ──────► 性能分解模型
     │                    │
     │                    ├── 意图分析 → Token消耗
     │                    ├── 专家分析 → Token消耗 (最大)
     │                    ├── 消息传递 → Token消耗
     │                    └── 辩论整合 → Token消耗

本设计 ───────────► Token优化增强
     │
     ├── 智能路由       (按需调用专家)
     ├── 上下文缓存     (减少重复加载)
     ├── 消息压缩       (精简消息体积)
     ├── 摘要提取       (历史消息压缩)
     └── 成本边界       (预算控制)
```

---

## 二、Token消耗分解模型

### 2.1 系统Token消耗分解树

基于Q44的性能分解模型，Token消耗分解如下：

```
总Token消耗 (Total Tokens)
│
├── 意图分析 (Intent Analysis)
│   ├── 意图识别LLM调用: ~2,000 tokens
│   └── 路由匹配: ~500 tokens
│
├── 专家分析 (Expert Analysis)  ◄─── 最大消耗来源
│   ├── Kahneman专家: ~15,000 tokens
│   ├── FirstPrinciple专家: ~12,000 tokens
│   ├── SixHats专家: ~10,000 tokens
│   └── ...其他专家
│
├── 消息传递 (Message Passing)  ◄─── 隐藏消耗
│   ├── 专家间消息: ~3,000 tokens/轮
│   ├── 消息序列化: ~500 tokens
│   └── 消息解析: ~300 tokens
│
├── 辩论/整合 (Debate/Integration)
│   ├── 观点聚合: ~5,000 tokens
│   ├── 交叉辩论: ~8,000 tokens/轮
│   └── 报告生成: ~3,000 tokens
│
└── 上下文加载 (Context Loading)
    ├── 背景资料加载: ~2,000 tokens
    ├── 历史消息加载: ~5,000 tokens
    └── 系统提示加载: ~1,500 tokens
```

### 2.2 场景示例：14专家全部调用

```
问题: 如何提升DAU 10%？
│
├── 意图分析: 2,500 tokens
│   ├── 意图识别: 2,000 tokens
│   └── 路由匹配: 500 tokens
│
├── 专家分析: 120,000 tokens  ◄─── 最大消耗
│   ├── Kahneman: 15,000 tokens
│   ├── FirstPrinciple: 12,000 tokens
│   ├── SixHats: 10,000 tokens
│   ├── SWOTTows: 8,000 tokens
│   ├── FiveWhy: 8,000 tokens
│   ├── Goldlin: 8,000 tokens
│   ├── GROW: 8,000 tokens
│   ├── KISS: 7,000 tokens
│   ├── McKinsey: 9,000 tokens
│   ├── AIboard: 8,000 tokens
│   ├── ReverseThinking: 8,000 tokens
│   ├── FiveDimension: 9,000 tokens
│   ├── WBS: 10,000 tokens
│   └── ManagerLeap: 10,000 tokens
│
├── 消息传递: 15,000 tokens
│   └── 假设3轮交叉辩论，每轮5,000 tokens
│
├── 辩论整合: 21,000 tokens
│   ├── 观点聚合: 5,000 tokens
│   ├── 交叉辩论(3轮): 3×8,000 = 24,000 tokens
│   └── 报告生成: 3,000 tokens
│
└── 上下文加载: 8,500 tokens
    ├── 背景资料: 2,000 tokens
    ├── 历史消息: 5,000 tokens
    └── 系统提示: 1,500 tokens
│
总Token消耗: ~167,000 tokens
按Claude Sonne定价: ~$0.50/次问题
```

---

## 三、Token消耗量化标准

### 3.1 环节级Token指标

| 指标ID | 环节 | 指标名称 | 计算方式 | 单位 |
|--------|------|---------|---------|------|
| TK_INTENT | 意图分析 | 意图分析Token | LLM调用输入+输出 | tokens |
| TK_EXPERT | 专家分析 | 专家分析Token | 所有专家Token总和 | tokens |
| TK_MESSAGE | 消息传递 | 消息Token | 序列化+反序列化 | tokens |
| TK_DEBATE | 辩论整合 | 辩论Token | 聚合+辩论+报告 | tokens |
| TK_CONTEXT | 上下文加载 | 上下文Token | 背景+历史+系统 | tokens |
| TK_TOTAL | 全部 | 总Token | 以上全部 | tokens |

### 3.2 专家级Token指标

| 指标ID | 指标名称 | 计算方式 | 单位 |
|--------|---------|---------|------|
| EXP_INPUT | 输入Token | 发送给专家的输入 | tokens |
| EXP_OUTPUT | 输出Token | 专家生成的内容 | tokens |
| EXP_TOTAL | 专家总Token | 输入+输出 | tokens |
| EXP_CACHED | 缓存Token | 复用上下文节省 | tokens |

### 3.3 成本指标

| 指标ID | 指标名称 | 计算方式 | 单位 |
|--------|---------|---------|------|
| COST_QUESTION | 问题成本 | 总Token × 单价 |美元 |
| COST_EXPERT | 专家成本 | 专家Token × 单价 | 美元 |
| COST_RATIO | Token效率 | 输出Token / 输入Token | 比例 |

### 3.4 数据来源（基于Q20文件体系）

```json
// workspace/tasks/{question_id}/tasks/{expert_id}.json
{
  "task_id": "task_kahneman_q_001",
  "expert_id": "kahneman",
  "question_id": "q_20260320_001",
  "status": "completed",

  "metadata": {
    "started_at": "2026-03-20T10:00:05Z",
    "completed_at": "2026-03-20T10:02:30Z",
    "duration_seconds": 145,
    "model": "claude-sonnet-4-6",

    // 新增：Token消耗数据
    "tokens": {
      "input": 8000,
      "output": 7000,
      "total": 15000,
      "cached": 2000  // 缓存节省的Token
    },

    // 新增：Token消耗分解
    "token_breakdown": {
      "system_prompt": 1500,
      "context_loading": 2000,
      "user_question": 2500,
      "expert_analysis": 7000,
      "output_generation": 2000
    }
  }
}
```

```json
// workspace/tasks/{question_id}/board.json
{
  "question_id": "q_20260320_001",
  "question": "如何提升DAU 10%？",
  "status": "completed",

  // 新增：Token消耗汇总
  "token_usage": {
    "total": 167000,
    "by_phase": {
      "intent": 2500,
      "expert": 120000,
      "message": 15000,
      "debate": 21000,
      "context": 8500
    },
    "by_expert": {
      "kahneman": 15000,
      "first-principle": 12000,
      "six-hats": 10000,
      ...
    },
    "cost_usd": 0.50,
    "currency": "USD",
    "model": "claude-sonnet-4-6"
  }
}
```

---

## 四、Token优化策略

### 4.1 策略一：智能路由（按需调用专家）

**问题**: 14个专家全部调用，Token消耗大

**优化方案**: 根据问题类型，只调用相关专家

```python
# 智能路由配置
# config/routing/token-optimized-routing.json
{
  "routing_strategies": {
    "growth": {
      "question_types": ["增长策略", "DAU提升", "获客"],
      "recommended_experts": ["kahneman", "grow", "first-principle"],
      "max_experts": 3,
      "estimated_tokens": 35000
    },
    "strategy": {
      "question_types": ["战略规划", "竞争分析"],
      "recommended_experts": ["swottows", "mckinsey", "six-hats"],
      "max_experts": 3,
      "estimated_tokens": 30000
    },
    "problem_solving": {
      "question_types": ["问题诊断", "根因分析"],
      "recommended_experts": ["five-why", "first-principle", "reverse-thinking"],
      "max_experts": 3,
      "estimated_tokens": 28000
    },
    "full_debate": {
      "question_types": ["重大决策"],
      "recommended_experts": ["kahneman", "first-principle", "six-hats", "swottows", "five-why"],
      "max_experts": 5,
      "estimated_tokens": 60000
    }
  }
}
```

**效果**:
| 场景 | 优化前 | 优化后 | 节省 |
|------|--------|--------|------|
| 增长策略 | 14专家 | 3专家 | ~70% |
| 战略规划 | 14专家 | 3专家 | ~70% |
| 重大决策 | 14专家 | 5专家 | ~50% |

### 4.2 策略二：上下文缓存（减少重复加载）

**问题**: 每个专家都重新加载背景资料，浪费Token

**优化方案**: 共享上下文，一次加载多次复用

```python
# 上下文缓存管理器
class ContextCache:
    """上下文缓存，避免重复加载"""

    def __init__(self, cache_ttl_seconds: int = 3600):
        self.cache = {}
        self.cache_ttl = cache_ttl_seconds

    def get_context(self, question_id: str, context_type: str) -> str:
        """获取缓存的上下文"""
        cache_key = f"{question_id}:{context_type}"

        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if time.time() - cached["timestamp"] < self.cache_ttl:
                return cached["content"]

        return None

    def set_context(self, question_id: str, context_type: str, content: str):
        """缓存上下文"""
        cache_key = f"{question_id}:{context_type}"
        self.cache[cache_key] = {
            "content": content,
            "timestamp": time.time()
        }

    def get_cached_tokens(self, question_id: str) -> int:
        """计算缓存节省的Token"""
        cached = 0
        for key, value in self.cache.items():
            if key.startswith(f"{question_id}:"):
                # 估算缓存Token数
                cached += len(value["content"]) // 4

        return cached
```

**效果**:
| 场景 | 优化前 | 优化后 | 节省 |
|------|--------|--------|------|
| 14专家并行 | 14×2,000 = 28,000 | 2,000 | ~93% |
| 3轮辩论 | 9×5,000 = 45,000 | 5,000 | ~89% |

### 4.3 策略三：消息压缩（精简消息体积）

**问题**: 专家间消息冗长，占用大量Token

**优化方案**: 提取关键信息，压缩消息体积

```python
# 消息压缩器
class MessageCompressor:
    """消息压缩，减少Token消耗"""

    def compress_message(self, message: str, max_tokens: int = 500) -> str:
        """压缩消息到指定Token数"""

        # 使用LLM进行智能摘要
        prompt = f"""请将以下消息压缩到{max_tokens}个Token以内，
保留核心观点和关键数据：

{message}

压缩后的消息："""

        response = llm.generate(prompt, max_tokens=max_tokens)
        return response.content

    def extract_key_points(self, expert_output: str) -> dict:
        """从专家输出中提取关键点"""

        prompt = f"""从以下专家分析中提取关键点：

{expert_output}

请以JSON格式输出：
{{
    "key_findings": ["要点1", "要点2"],
    "confidence": 0.9,
    "requires_followup": true/false
}}"""

        return json.loads(llm.generate(prompt))
```

**效果**:
| 消息类型 | 优化前 | 优化后 | 节省 |
|----------|--------|--------|------|
| 专家间消息 | 3,000 tokens | 500 tokens | ~83% |
| 观点聚合 | 5,000 tokens | 1,500 tokens | ~70% |

### 4.4 策略四：历史消息摘要（长期对话压缩）

**问题**: 对话历史越来越长，消耗大量Token

**优化方案**: 定期对历史消息进行摘要

```python
# 历史消息摘要器
class MessageSummarizer:
    """历史消息摘要，减少上下文长度"""

    def __init__(self, max_history_tokens: int = 10000):
        self.max_history_tokens = max_history_tokens
        self.summary_history = []

    def should_summarize(self, messages: list) -> bool:
        """判断是否需要摘要"""
        total_tokens = sum(self.estimate_tokens(m) for m in messages)
        return total_tokens > self.max_history_tokens

    def summarize_history(self, messages: list) -> str:
        """生成历史消息摘要"""

        prompt = f"""请总结以下对话的核心要点：

{self.format_messages(messages)}

摘要要求：
1. 保留关键决策和结论
2. 记录未解决的问题
3. 提炼专家分歧点
4. 控制在500字以内"""

        summary = llm.generate(prompt, max_tokens=1000)
        self.summary_history.append(summary)

        return summary
```

**效果**:
| 对话轮次 | 优化前 | 优化后 | 节省 |
|----------|--------|--------|------|
| 10轮 | 50,000 tokens | 15,000 tokens | ~70% |
| 20轮 | 100,000 tokens | 18,000 tokens | ~82% |

### 4.5 策略五：增量推理（避免重复分析）

**问题**: 同一问题多次分析，重复消耗Token

**优化方案**: 缓存分析结果，复用而非重算

```python
# 增量推理缓存
class IncrementalReasoningCache:
    """增量推理缓存"""

    def __init__(self):
        self.cache = {}

    def get_cached_analysis(self, question_signature: str) -> dict:
        """获取缓存的分析结果"""
        return self.cache.get(question_signature)

    def cache_analysis(self, question_signature: str, analysis: dict):
        """缓存分析结果"""
        self.cache[question_signature] = analysis

    def generate_signature(self, question: str, context: str) -> str:
        """生成问题签名"""
        # 使用哈希而非完整问题，节省存储
        combined = f"{question}:{context}"
        return hashlib.md5(combined.encode()).hexdigest()
```

**效果**:
| 场景 | 优化前 | 优化后 | 节省 |
|------|--------|--------|------|
| 相似问题 | 重新分析 | 复用缓存 | ~80% |
| 追问 | 完整分析 | 增量分析 | ~50% |

---

## 五、成本控制边界

### 5.1 预算层级设计

```
成本控制层级
│
├── L1 系统级预算
│   ├── 每日预算: $100/天
│   ├── 每周预算: $500/周
│   └── 每月预算: $2,000/月
│
├── L2 任务级预算
│   ├── 简单问题: $0.10/个
│   ├── 中等问题: $0.50/个
│   └── 复杂问题: $2.00/个
│
└── L3 专家级预算
    ├── 单专家: $0.05/次
    ├── 3专家组合: $0.15/次
    └── 5专家组合: $0.25/次
```

### 5.2 预算控制规则

```python
# 预算控制器
class BudgetController:
    """Token预算控制器"""

    def __init__(self, config: dict):
        self.daily_budget = config.get("daily_budget", 100)  # 美元
        self.task_budgets = config.get("task_budgets", {
            "simple": 0.10,
            "medium": 0.50,
            "complex": 2.00
        })
        self.expert_budgets = config.get("expert_budgets", {
            "single": 0.05,
            "triple": 0.15,
            "quintuple": 0.25
        })

    def check_task_budget(self, question: str, estimated_cost: float) -> bool:
        """检查任务预算是否超限"""

        # 判定问题复杂度
        complexity = self.estimate_complexity(question)
        budget = self.task_budgets.get(complexity, 0.50)

        if estimated_cost > budget:
            # 触发降级策略
            return False

        return True

    def check_daily_budget(self, current_spend: float) -> dict:
        """检查每日预算"""

        remaining = self.daily_budget - current_spend

        if remaining < 0:
            return {
                "status": "exceeded",
                "action": "暂停新任务",
                "remaining": 0
            }
        elif remaining < self.daily_budget * 0.1:
            return {
                "status": "warning",
                "action": "提醒用户",
                "remaining": remaining
            }
        else:
            return {
                "status": "normal",
                "remaining": remaining
            }
```

### 5.3 成本边界规则

```yaml
# config/budget/boundaries.yaml
budget_boundaries:
  # 每日预算
  daily:
    soft_limit: 100  # 美元
    hard_limit: 150  # 美元
    action_soft: "提醒用户"
    action_hard: "暂停新任务"

  # 单任务预算
  per_task:
    simple: 0.10
    medium: 0.50
    complex: 2.00
    critical: 5.00

  # 专家调用限制
  expert:
    max_per_task: 5
    max_parallel: 3
    min_interval_seconds: 60

  # Token限制
  tokens:
    max_input_per_request: 100000
    max_output_per_request: 10000
    max_context_tokens: 200000

  # 降级策略
  degradation:
    enabled: true
    triggers:
      - type: "daily_budget_exceeded"
        action: "切换到轻量模式"
      - type: "task_cost_exceeded"
        action: "减少专家数量"
      - type: "response_time_slow"
        action: "使用更快模型"
```

### 5.4 降级策略

当成本接近边界时，自动触发降级：

| 触发条件 | 降级策略 | 节省比例 |
|----------|----------|----------|
| 每日预算 > 80% | 减少专家数量 | ~40% |
| 单任务成本 > 预算 | 切换简单模式 | ~60% |
| 响应时间 > 30秒 | 使用更快模型 | ~30% |
| 连续3次超时 | 减少轮次 | ~50% |

```python
# 降级策略执行器
class DegradationExecutor:
    """降级策略执行器"""

    def __init__(self, budget_controller: BudgetController):
        self.controller = budget_controller
        self.degradation_chain = [
            self.reduce_experts,
            self.enable_compression,
            self.use_faster_model,
            self.reduce_rounds,
            self.switch_to_summary_mode
        ]

    def execute(self, current_cost: float, context: dict) -> dict:
        """执行降级策略"""

        # 检查预算使用率
        usage_rate = current_cost / self.controller.daily_budget

        # 选择降级策略
        if usage_rate > 0.9:
            # 严重超支，最大程度降级
            return self.degradation_chain[-1](context)
        elif usage_rate > 0.8:
            return self.degradation_chain[2](context)
        elif usage_rate > 0.7:
            return self.degradation_chain[1](context)
        else:
            return {"action": "none", "reason": "预算充足"}

    def reduce_experts(self, context: dict) -> dict:
        """减少专家数量"""
        return {
            "action": "reduce_experts",
            "from": context.get("expert_count", 5),
            "to": 3,
            "savings": "~40%"
        }

    def enable_compression(self, context: dict) -> dict:
        """启用消息压缩"""
        return {
            "action": "enable_compression",
            "message_compression": True,
            "savings": "~30%"
        }

    def use_faster_model(self, context: dict) -> dict:
        """使用更快模型"""
        return {
            "action": "use_faster_model",
            "from": "claude-sonnet",
            "to": "claude-haiku",
            "savings": "~30%"
        }
```

---

## 六、量化指标体系

### 6.1 核心KPI

| KPI | 计算方式 | 目标 | 监控频率 |
|-----|---------|------|----------|
| **Token/问题** | 总Token / 问题数 | < 50,000 | 每日 |
| **Cost/问题** | 总成本 / 问题数 | < $0.30 | 每日 |
| **缓存命中率** | 缓存Token / 总Token | > 30% | 每周 |
| **专家利用率** | 实际调用 / 最大可能 | < 50% | 每日 |
| **预算使用率** | 实际成本 / 预算 | < 80% | 实时 |

### 6.2 优化效果指标

| 指标 | 优化前 | 目标 | 测量方式 |
|------|--------|------|----------|
| 单问题Token消耗 | 167,000 | < 50,000 | 历史对比 |
| 专家调用数量 | 14 | 3-5 | 路由统计 |
| 上下文复用率 | 0% | > 50% | 缓存统计 |
| 消息压缩率 | 0% | > 70% | 压缩比统计 |
| 平均响应成本 | $0.50 | < $0.15 | 成本追踪 |

### 6.3 成本分析报告

```json
// performance/analysis/{date}/token_report.json
{
  "report_id": "token_report_20260320",
  "date": "2026-03-20",

  "summary": {
    "total_questions": 50,
    "total_tokens": 2500000,
    "total_cost_usd": 7.50,
    "avg_tokens_per_question": 50000,
    "avg_cost_per_question": 0.15
  },

  "by_phase": {
    "intent": {"tokens": 125000, "ratio": 5.0, "cost": 0.38},
    "expert": {"tokens": 2000000, "ratio": 80.0, "cost": 6.00},
    "message": {"tokens": 150000, "ratio": 6.0, "cost": 0.45},
    "debate": {"tokens": 175000, "ratio": 7.0, "cost": 0.53},
    "context": {"tokens": 50000, "ratio": 2.0, "cost": 0.15}
  },

  "optimization_effects": {
    "context_cache": {
      "cached_tokens": 750000,
      "savings_tokens": 750000,
      "savings_cost": 2.25,
      "hit_rate": "35%"
    },
    "expert_reduction": {
      "original_experts": 14,
      "optimized_experts": 3,
      "savings_tokens": 1100000,
      "savings_cost": 3.30
    },
    "message_compression": {
      "original_messages": 50000,
      "compressed_messages": 15000,
      "savings_tokens": 35000,
      "savings_cost": 0.11
    }
  },

  "budget_status": {
    "daily_budget": 100,
    "spent": 7.50,
    "remaining": 92.50,
    "usage_rate": "7.5%",
    "status": "normal"
  },

  "trends": {
    "token_trend": "-15%",  // 较上周
    "cost_trend": "-20%",
    "cache_hit_trend": "+10%"
  }
}
```

---

## 七、与Q20/Q44的集成

### 7.1 数据流关系

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Token优化数据流                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Q20 文件体系                                                            │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐   │
│  │ board.json       │    │ tasks/*.json     │    │ messages/*      │   │
│  │ (含token_usage)  │    │ (含tokens字段)   │    │ (消息压缩)      │   │
│  └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘   │
│           │                         │                         │            │
│           └─────────────────────────┼─────────────────────────┘            │
│                                     ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ TokenOptimizer                                                       │  │
│  │   - 智能路由                                                         │  │
│  │   - 上下文缓存                                                       │  │
│  │   - 消息压缩                                                         │  │
│  │   - 预算控制                                                         │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                     │                                      │
│                                     ▼                                      │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐   │
│  │ performance/     │    │ Web API          │    │ 监控看板         │   │
│  │ token_analysis  │    │ /api/token       │    │ Token消耗展示    │   │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.2 与Q44性能瓶颈的对应

| Q44性能维度 | Token消耗维度 | 优化联动 |
|------------|--------------|---------|
| 意图分析耗时 | 意图分析Token | 简化意图识别prompt |
| 专家分析耗时 | 专家分析Token | 减少专家数量 |
| 消息传递耗时 | 消息传递Token | 消息压缩 |
| 辩论整合耗时 | 辩论Token | 减少辩论轮次 |
| 上下文加载 | 上下文Token | 启用缓存 |

### 7.3 目录结构扩展

基于Q20的目录结构，新增Token优化相关目录：

```
thinking-team/
├── config/
│   ├── routing/
│   │   ├── token-optimized-routing.json  # 智能路由配置
│   │   └── expert-mapping.json
│   │
│   └── budget/
│       └── boundaries.yaml               # 成本边界配置
│
├── performance/
│   ├── token_analysis/                   # Token分析
│   │   ├── daily/
│   │   │   └── {date}.json
│   │   ├── trends/
│   │   │   └── {question_id}.json
│   │   └── reports/
│   │       └── {date}/
│   │           └── token_report.json
│   │
│   └── baselines/
│       └── token_baselines.json          # Token基线
│
└── scripts/
    ├── token_optimizer.py                # Token优化器
    ├── budget_controller.py              # 预算控制器
    ├── context_cache.py                  # 上下文缓存
    ├── message_compressor.py             # 消息压缩器
    └── token_reporter.py                 # Token报告生成
```

---

## 八、CLI命令设计

### 8.1 Token监控命令

```bash
# 查看Token消耗
thinking-team token usage q_20260320_001

# 输出:
# 问题: 如何提升DAU 10%？
# 总Token: 167,000 (成本: $0.50)
#
# 环节分布:
#   意图分析:   2,500 (1.5%)
#   专家分析: 120,000 (71.9%)
#   消息传递:  15,000 (9.0%)
#   辩论整合:  21,000 (12.6%)
#   上下文:    8,500 (5.1%)
#
# 专家分布:
#   Kahneman: 15,000
#   FirstPrinciple: 12,000
#   ...

# 查看每日Token统计
thinking-team token daily --date 2026-03-20

# 输出:
# 日期: 2026-03-20
# 总问题数: 50
# 总Token: 2,500,000
# 总成本: $7.50
# 平均Token/问题: 50,000
# 预算使用: 7.5%

# 查看Token优化效果
thinking-team token optimization --period week

# 输出:
# 本周Token优化效果:
#   上下文缓存节省: 750,000 tokens ($2.25)
#   专家精简节省: 1,100,000 tokens ($3.30)
#   消息压缩节省: 35,000 tokens ($0.11)
#   总节省: 1,885,000 tokens ($5.66)
#   优化率: 43%
```

### 8.2 预算管理命令

```bash
# 查看预算状态
thinking-team budget status

# 输出:
# 每日预算: $100.00
# 已使用: $7.50
# 剩余: $92.50
# 使用率: 7.5%
# 状态: 正常

# 设置预算
thinking-team budget set --daily 100 --per-task 0.50

# 查看专家成本排名
thinking-team token expert-ranking

# 输出:
# 专家Token消耗排名:
#   1. Kahneman: 平均15,000 tokens
#   2. FirstPrinciple: 平均12,000 tokens
#   3. WBS: 平均10,000 tokens
#   ...
```

---

## 九、实施建议

### 9.1 实施阶段

| 阶段 | 时间 | 内容 | 交付物 |
|------|------|------|--------|
| **第一阶段** | 1天 | Token数据采集 | board.json/tasks/*.json 增加 tokens 字段 |
| **第二阶段** | 1天 | 智能路由 | 按需调用专家，减少冗余 |
| **第三阶段** | 1天 | 上下文缓存 | 避免重复加载背景资料 |
| **第四阶段** | 1天 | 消息压缩 | 精简专家间消息 |
| **第五阶段** | 0.5天 | 预算控制 | 设定成本边界 |
| **第六阶段** | 0.5天 | CLI命令 | token/budget 命令 |

### 9.2 优先级

1. **P0 - 必须**
   - Token数据采集和统计
   - 智能路由（最大节省）
   - 预算边界控制

2. **P1 - 重要**
   - 上下文缓存
   - 消息压缩
   - CLI监控命令

3. **P2 - 增强**
   - 历史消息摘要
   - 增量推理缓存
   - 趋势分析和预测

### 9.3 关键成功指标

| 指标 | 当前值 | 目标 | 测量周期 |
|------|--------|------|----------|
| 平均Token/问题 | 167,000 | < 50,000 | 每日 |
| 平均成本/问题 | $0.50 | < $0.15 | 每日 |
| 专家调用数量 | 14 | 3-5 | 每日 |
| 缓存节省率 | 0% | > 30% | 每周 |
| 预算使用率 | - | < 80% | 实时 |

---

## 十、总结

### 10.1 设计要点

| 要点 | 说明 |
|------|------|
| **分层分解** | 将Token消耗分解为5个环节，逐层优化 |
| **智能路由** | 按需调用专家，从14个减少到3-5个 |
| **缓存复用** | 上下文缓存+增量推理，避免重复计算 |
| **消息压缩** | 精简消息体积，减少传递消耗 |
| **预算边界** | 三级预算控制，防止无限消耗 |

### 10.2 与Q20/Q44的一致性

| 设计点 | Q20/Q44 | 本设计 |
|--------|---------|--------|
| 数据存储 | workspace/tasks/*.json | 新增 tokens 字段 |
| 性能分解 | 6环节耗时分解 | 对应5环节Token分解 |
| 基线机制 | 耗时基线 | 新增Token基线 |
| CLI命令 | performance命令 | 新增token/budget命令 |
| 看板展示 | 性能瓶颈 | 新增Token消耗 |

### 10.3 预期效果

| 优化策略 | 节省比例 | 实施难度 |
|----------|----------|----------|
| 智能路由（14→3专家） | ~70% | 低 |
| 上下文缓存 | ~40% | 中 |
| 消息压缩 | ~30% | 中 |
| 历史摘要 | ~20% | 高 |
| **综合优化** | **~60%** | - |

**成本变化**:
- 优化前: $0.50/问题
- 优化后: $0.20/问题
- 节省: 60%

---

**设计日期**: 2026-03-20
**文档编号**: Q53
**参考**: Q20文件体系、Q44性能瓶颈定位机制
**前置文档**: Q18系统全景设计报告
