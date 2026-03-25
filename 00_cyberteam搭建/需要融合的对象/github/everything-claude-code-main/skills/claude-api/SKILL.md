# 克劳德 API

使用 Anthropic Claude API 和 SDK 构建应用程序。

## 何时激活

- 构建调用 Claude API 的应用程序
- 代码导入 `anthropic` (Python) 或 `@anthropic-ai/sdk` (TypeScript)
- 用户询问 Claude API 模式、工具使用、流媒体或愿景
- 使用 Claude Agent SDK 实施代理工作流程
- 优化 API 成本、令牌使用或延迟

## 型号选择

|型号|身份证 |最适合 |
|--------|-----|----------|
|作品 4.1 | `克劳德-opus-4-1` |复杂推理、架构、研究 |
|十四行诗 4 | `克劳德十四行诗-4-0` |平衡编码，大多数开发任务|
|俳句 3.5 | `claude-3-5-俳句-最新` |快速响应、大批量、成本敏感 |

默认为 Sonnet 4，除非任务需要深度推理 (Opus) 或速度/成本优化 (Haiku)。对于生产，优先使用固定快照 ID 而不是别名。

## Python SDK

### 安装```bash
pip install anthropic
```### 基本信息```python
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

message = client.messages.create(
    model="claude-sonnet-4-0",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Explain async/await in Python"}
    ]
)
print(message.content[0].text)
```### 流媒体```python
with client.messages.stream(
    model="claude-sonnet-4-0",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Write a haiku about coding"}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```###系统提示```python
message = client.messages.create(
    model="claude-sonnet-4-0",
    max_tokens=1024,
    system="You are a senior Python developer. Be concise.",
    messages=[{"role": "user", "content": "Review this function"}]
)
```## TypeScript SDK

### 安装```bash
npm install @anthropic-ai/sdk
```### 基本信息```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic(); // reads ANTHROPIC_API_KEY from env

const message = await client.messages.create({
  model: "claude-sonnet-4-0",
  max_tokens: 1024,
  messages: [
    { role: "user", content: "Explain async/await in TypeScript" }
  ],
});
console.log(message.content[0].text);
```### 流媒体```typescript
const stream = client.messages.stream({
  model: "claude-sonnet-4-0",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Write a haiku" }],
});

for await (const event of stream) {
  if (event.type === "content_block_delta" && event.delta.type === "text_delta") {
    process.stdout.write(event.delta.text);
  }
}
```## 工具使用

定义工具并让 Claude 调用它们：```python
tools = [
    {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            },
            "required": ["location"]
        }
    }
]

message = client.messages.create(
    model="claude-sonnet-4-0",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "What's the weather in SF?"}]
)

# Handle tool use response
for block in message.content:
    if block.type == "tool_use":
        # Execute the tool with block.input
        result = get_weather(**block.input)
        # Send result back
        follow_up = client.messages.create(
            model="claude-sonnet-4-0",
            max_tokens=1024,
            tools=tools,
            messages=[
                {"role": "user", "content": "What's the weather in SF?"},
                {"role": "assistant", "content": message.content},
                {"role": "user", "content": [
                    {"type": "tool_result", "tool_use_id": block.id, "content": str(result)}
                ]}
            ]
        )
```## 愿景

发送图像进行分析：```python
import base64

with open("diagram.png", "rb") as f:
    image_data = base64.standard_b64encode(f.read()).decode("utf-8")

message = client.messages.create(
    model="claude-sonnet-4-0",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_data}},
            {"type": "text", "text": "Describe this diagram"}
        ]
    }]
)
```## 延伸思考

对于复杂的推理任务：```python
message = client.messages.create(
    model="claude-sonnet-4-0",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000
    },
    messages=[{"role": "user", "content": "Solve this math problem step by step..."}]
)

for block in message.content:
    if block.type == "thinking":
        print(f"Thinking: {block.thinking}")
    elif block.type == "text":
        print(f"Answer: {block.text}")
```## 提示缓存

缓存大型系统提示或上下文以降低成本：```python
message = client.messages.create(
    model="claude-sonnet-4-0",
    max_tokens=1024,
    system=[
        {"type": "text", "text": large_system_prompt, "cache_control": {"type": "ephemeral"}}
    ],
    messages=[{"role": "user", "content": "Question about the cached context"}]
)
# Check cache usage
print(f"Cache read: {message.usage.cache_read_input_tokens}")
print(f"Cache creation: {message.usage.cache_creation_input_tokens}")
```## 批量API

异步处理大量数据，成本降低 50%：```python
import time

batch = client.messages.batches.create(
    requests=[
        {
            "custom_id": f"request-{i}",
            "params": {
                "model": "claude-sonnet-4-0",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}]
            }
        }
        for i, prompt in enumerate(prompts)
    ]
)

# Poll for completion
while True:
    status = client.messages.batches.retrieve(batch.id)
    if status.processing_status == "ended":
        break
    time.sleep(30)

# Get results
for result in client.messages.batches.results(batch.id):
    print(result.result.message.content[0].text)
```## 克劳德代理SDK

构建多步代理：```python
# Note: Agent SDK API surface may change — check official docs
import anthropic

# Define tools as functions
tools = [{
    "name": "search_codebase",
    "description": "Search the codebase for relevant code",
    "input_schema": {
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"]
    }
}]

# Run an agentic loop with tool use
client = anthropic.Anthropic()
messages = [{"role": "user", "content": "Review the auth module for security issues"}]

while True:
    response = client.messages.create(
        model="claude-sonnet-4-0",
        max_tokens=4096,
        tools=tools,
        messages=messages,
    )
    if response.stop_reason == "end_turn":
        break
    # Handle tool calls and continue the loop
    messages.append({"role": "assistant", "content": response.content})
    # ... execute tools and append tool_result messages
```## 成本优化

|战略|储蓄|何时使用 |
|----------|---------|-------------|
|提示缓存 |缓存令牌高达 90% |重复的系统提示或上下文 |
|批量API | 50% |对时间不敏感的批量处理 |
|俳句代替十四行诗| 〜75% |简单任务、分类、提取|
|更短的 max_tokens |变量|当你知道输出会很短时 |
|流媒体 |无（相同费用）|更好的用户体验，相同的价格 |

## 错误处理```python
import time

from anthropic import APIError, RateLimitError, APIConnectionError

try:
    message = client.messages.create(...)
except RateLimitError:
    # Back off and retry
    time.sleep(60)
except APIConnectionError:
    # Network issue, retry with backoff
    pass
except APIError as e:
    print(f"API error {e.status_code}: {e.message}")
```## 环境设置```bash
# Required
export ANTHROPIC_API_KEY="your-api-key-here"

# Optional: set default model
export ANTHROPIC_MODEL="claude-sonnet-4-0"
```切勿对 API 密钥进行硬编码。始终使用环境变量。