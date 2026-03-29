# CyberTeam V4 - 思维注入中台架构

> **核心思想**: 100个思维专家不是独立的 Agent，而是决策工具库。Agent 在做决策时可以注入合适的思维模型。

## 架构概览

```
用户输入
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CEO 路由引擎 (L1)                            │
│  ├── 需求分拣 (简单咨询 vs 正式任务)                              │
│  ├── 意图识别 (8种意图)                                          │
│  ├── 复杂度评估 (高/中/低)                                        │
│  └── 路由决策 (L2/L3A/L3B/L3C/SWARM)                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ 正式任务
┌─────────────────────────────────────────────────────────────────┐
│                     思维注入中台 (Thinking Injector)              │
│  ├── ThinkingLoader   - 加载94个思维模型                        │
│  ├── ThinkingRouter   - 根据任务特征选择模型                     │
│  └── ThinkingInjector - 将模型注入 Agent 决策                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ 注入后的 Agent
┌─────────────────────────────────────────────────────────────────┐
│                         Agent 执行                               │
│  Agent (如 PM/运营/技术) + 思维模型组合                          │
│  ├── 单一模型: 第一性原理 / 六顶思考帽 / SWOT...                  │
│  └── 组合模型: [第一性原理 + 5W1H + 二阶思维]...                 │
└─────────────────────────────────────────────────────────────────┘
```

## 核心模块

### 1. ThinkingLoader - 思维模型加载器

从"需要融合的对象/思考天团Agent/agents/"目录加载所有思维模型。

```python
from engine.thinking import ThinkingLoader

loader = ThinkingLoader()
models = loader.load_all()
# 加载了 94 个思维模型

# 获取单个模型
model = loader.get_model("first-principle")

# 搜索模型
results = loader.search_by_keyword("战略")
```

### 2. ThinkingRouter - 思维路由

根据任务意图和特征，自动选择合适的思维模型组合。

```python
from engine.thinking import ThinkingRouter, TaskContext

router = ThinkingRouter(loader)

context = TaskContext(
    task_description="分析用户增长策略",
    intent="数据分析",
    complexity="高",
    domain="增长"
)

result = router.route(context)
# result.combination.models - 选中的模型列表
# result.confidence - 置信度
```

### 3. ThinkingInjector - 思维注入器

将思维模型注入到 Agent 的决策过程中。

```python
from engine.thinking import ThinkingInjector, InjectionContext

injector = ThinkingInjector()
injector.load_models()

context = InjectionContext(
    agent_name="PM Agent",
    agent_role="产品管理",
    task="设计用户增长策略"
)

result = injector.inject_auto(context)
print(result.injected_prompt)  # 完整的注入 prompt
```

## 意图 → 思维模型映射

| 意图 | 触发的思维模型 | 数量 |
|------|---------------|------|
| 数据分析 | 概率思维、贝叶斯、帕累托、复利效应 | 3 |
| 内容运营 | 六顶思考帽、Hook模型、AI董事会 | 2 |
| 技术研发 | 第一性原理、系统思维、逆向思维 | 3 |
| 安全合规 | 预演失败、二阶思维、证伪原则 | 3 |
| 战略规划 | SWOT/TOWS、博弈论、二阶思维、五力模型 | 3 |
| 财务投资 | 概率思维、贝叶斯、沉没成本、机会成本 | 3 |

## 复杂度 → 模型数量

| 复杂度 | 模型数量 | 说明 |
|--------|---------|------|
| 低 | 1 | 单一模型 |
| 中 | 2 | 双模型组合 |
| 高 | 3 | 三模型组合 |

## CEO 集成

CEO 引擎在路由决策后自动进行思维注入：

```python
from engine.ceo import CEORouter

router = CEORouter()
result = router.route("分析用户增长策略，制定Q2季度计划")

# 路由结果
print(result.target)           # SWARM
print(result.intent)          # 数据分析
print(result.complexity)      # 高

# 思维注入结果
print(result.thinking_models)  # ['类比推理', '风险投资', '生态系统']
print(result.thinking_confidence)  # 0.8
print(result.thinking_prompt)  # 完整的注入 prompt
```

## 使用示例

### 1. 自动注入（推荐）

```python
from engine.thinking import ThinkingInjector, InjectionContext

injector = ThinkingInjector()
injector.load_models()

context = InjectionContext(
    agent_name="PM Agent",
    agent_role="产品管理",
    task="设计用户增长策略"
)

result = injector.inject_auto(context)
print(result.injected_prompt)
```

### 2. 手动指定注入

```python
result = injector.inject_manual(
    agent_name="战略专家",
    agent_role="战略规划",
    task="制定公司三年战略规划",
    model_ids=["first-principle", "swot-tows", "game-theory"],
    intent="战略规划",
    complexity="高"
)
```

### 3. 辩论注入

```python
prompt = injector.inject_for_debate(
    task="是否应该进入下沉市场",
    stance="支持进入",
    models=["first-principle", "swot-tows", "game-theory"]
)
```

## 思维模型分类

| 分类 | 数量 | 示例 |
|------|------|------|
| 分析 (ANALYSIS) | 60 | 概率思维、贝叶斯、帕累托 |
| 创造 (CREATIVE) | 9 | 六顶思考帽、类比推理 |
| 系统 (SYSTEM) | 16 | 系统思维、PDCA、迭代 |
| 决策 (DECISION) | 5 | 博弈论、能力圈 |
| 评估 (EVALUATION) | 4 | 预演失败、证伪原则 |

## 文件结构

```
engine/thinking/
├── __init__.py          # 模块入口
├── models.py            # 数据结构
├── loader.py            # 思维模型加载器
├── router.py            # 思维路由
└── injector.py          # 思维注入器
```

## 关键设计决策

### 1. 思维模型不是 Agent

传统的做法是创建100个独立的 Agent，每个代表一个思维模型。但这会导致：
- Agent 数量过多，难以管理
- Agent 之间通信开销大
- 决策时需要选择用哪个 Agent

我们的做法是：
- 思维模型是**决策工具库**
- Agent 在决策时**按需注入**思维模型
- 一个 Agent 可以同时注入多个思维模型

### 2. 组合优于单一

复杂问题往往需要多个思维模型组合：
- 第一性原理（分解问题）
- 二阶思维（考虑后果）
- 博弈论（竞争分析）

### 3. 自动 + 手动

- **自动注入**：基于任务特征自动选择
- **手动注入**：明确指定使用的模型

## 下一步

1. [ ] 完善思维模型的 `to_prompt()` 方法，输出更详细的思维框架
2. [ ] 增加更多意图类型的路由规则
3. [ ] 实现思维模型的学习和适应（根据使用效果调整优先级）
4. [ ] 集成到 Swarm 系统中，让子 Agent 也能使用思维注入

---

*版本: v4.0.0 | 更新: 2026-03-25*
