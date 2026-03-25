# 具有成本意识的法学硕士管道

在保持质量的同时控制 LLM API 成本的模式。将模型路由、预算跟踪、重试逻辑和提示缓存组合到可组合管道中。

## 何时激活

- 构建调用 LLM API（Claude、GPT 等）的应用程序
- 处理具有不同复杂程度的批量物品
- 需要将 API 支出保持在预算范围内
- 在不牺牲复杂任务质量的情况下优化成本

## 核心概念

### 1. 按任务复杂性划分的模型路由

自动为简单任务选择更便宜的模型，为复杂任务保留昂贵的模型。```python
MODEL_SONNET = "claude-sonnet-4-6"
MODEL_HAIKU = "claude-haiku-4-5-20251001"

_SONNET_TEXT_THRESHOLD = 10_000  # chars
_SONNET_ITEM_THRESHOLD = 30     # items

def select_model(
    text_length: int,
    item_count: int,
    force_model: str | None = None,
) -> str:
    """Select model based on task complexity."""
    if force_model is not None:
        return force_model
    if text_length >= _SONNET_TEXT_THRESHOLD or item_count >= _SONNET_ITEM_THRESHOLD:
        return MODEL_SONNET  # Complex task
    return MODEL_HAIKU  # Simple task (3-4x cheaper)
```### 2. 不可变的成本跟踪

使用冻结数据类跟踪累积支出。每个 API 调用都会返回一个新的跟踪器——永远不会改变状态。```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class CostRecord:
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float

@dataclass(frozen=True, slots=True)
class CostTracker:
    budget_limit: float = 1.00
    records: tuple[CostRecord, ...] = ()

    def add(self, record: CostRecord) -> "CostTracker":
        """Return new tracker with added record (never mutates self)."""
        return CostTracker(
            budget_limit=self.budget_limit,
            records=(*self.records, record),
        )

    @property
    def total_cost(self) -> float:
        return sum(r.cost_usd for r in self.records)

    @property
    def over_budget(self) -> bool:
        return self.total_cost > self.budget_limit
```### 3. 窄重试逻辑

仅在发生暂时性错误时重试。身份验证或错误请求错误时快速失败。```python
from anthropic import (
    APIConnectionError,
    InternalServerError,
    RateLimitError,
)

_RETRYABLE_ERRORS = (APIConnectionError, RateLimitError, InternalServerError)
_MAX_RETRIES = 3

def call_with_retry(func, *, max_retries: int = _MAX_RETRIES):
    """Retry only on transient errors, fail fast on others."""
    for attempt in range(max_retries):
        try:
            return func()
        except _RETRYABLE_ERRORS:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
    # AuthenticationError, BadRequestError etc. → raise immediately
```### 4. 提示缓存

缓存较长的系统提示，以避免在每次请求时重新发送它们。```python
messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},  # Cache this
            },
            {
                "type": "text",
                "text": user_input,  # Variable part
            },
        ],
    }
]
```## 成分

将所有四种技术结合在一个管道函数中：```python
def process(text: str, config: Config, tracker: CostTracker) -> tuple[Result, CostTracker]:
    # 1. Route model
    model = select_model(len(text), estimated_items, config.force_model)

    # 2. Check budget
    if tracker.over_budget:
        raise BudgetExceededError(tracker.total_cost, tracker.budget_limit)

    # 3. Call with retry + caching
    response = call_with_retry(lambda: client.messages.create(
        model=model,
        messages=build_cached_messages(system_prompt, text),
    ))

    # 4. Track cost (immutable)
    record = CostRecord(model=model, input_tokens=..., output_tokens=..., cost_usd=...)
    tracker = tracker.add(record)

    return parse_result(response), tracker
```## 定价参考（2025-2026）

|型号|输入（$/1M 代币）|产出（$/1M 代币）|相对成本|
|--------|---------------------|----------------------|------------------------|
|俳句 4.5 | 0.80 美元 | 4.00 美元 | 1x |
|十四行诗 4.6 | $3.00 | 15.00 美元 | 〜4x |
|作品 4.5 | 15.00 美元 | 75.00 美元 | 〜19x |

## 最佳实践

- **从最便宜的模型开始**，只有在满足复杂性阈值时才转向昂贵的模型
- **在处理批次之前设置明确的预算限制** - 尽早失败而不是超支
- **记录模型选择决策**，以便您可以根据实际数据调整阈值
- **对超过 1024 个令牌的系统提示使用提示缓存** — 节省成本和延迟
- **永远不要重试身份验证或验证错误** - 仅暂时性故障（网络、速率限制、服务器错误）

## 要避免的反模式

- 无论复杂程度如何，对所有请求都使用最昂贵的模型
- 重试所有错误（永久失败浪费预算）
- 改变成本跟踪状态（使调试和审计变得困难）
- 在整个代码库中硬编码模型名称（使用常量或配置）
- 忽略重复系统提示的提示缓存

## 何时使用

- 任何调用 Claude、OpenAI 或类似 LLM API 的应用程序
- 成本快速增加的批处理管道
- 需要智能路由的多模型架构
- 需要预算护栏的生产系统