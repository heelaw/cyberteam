# MCP 服务器模式

模型上下文协议 (MCP) 允许 AI 助手调用工具、读取资源并使用服务器的提示。在构建或维护 MCP 服务器时使用此技能。 SDK API 不断发展；检查 Context7（“MCP”的查询文档）或官方 MCP 文档以了解当前方法名称和签名。

## 何时使用

使用时机：实施新的 MCP 服务器、添加工具或资源、选择 stdio 与 HTTP、升级 SDK 或调试 MCP 注册和传输问题。

## 它是如何工作的

### 核心概念

- **工具**：模型可以调用的操作（例如搜索、运行命令）。根据 SDK 版本，使用 `registerTool()` 或 `tool()` 进行注册。
- **资源**：模型可以获取的只读数据（例如文件内容、API 响应）。使用“registerResource()”或“resource()”进行注册。处理程序通常接收“uri”参数。
- **提示**：客户端可以显示的可重复使用的参数化提示模板（例如在 Claude Desktop 中）。使用“registerPrompt()”或等效函数进行注册。
- **传输**：本地客户端的 stdio（例如 Claude Desktop）；可流式 HTTP 是远程（光标、云）的首选。旧版 HTTP/SSE 是为了向后兼容。

Node/TypeScript SDK 可能会公开 `tool()` / `resource()` 或 `registerTool()` / `registerResource()`；官方 SDK 随着时间的推移而发生变化。始终根据当前的 [MCP 文档](https://modelcontextprotocol.io) 或 Context7 进行验证。

### 与 stdio 连接

对于本地客户端，创建一个 stdio 传输并将其传递给服务器的 connect 方法。确切的 API 因 SDK 版本而异（例如构造函数与工厂）。请参阅官方 MCP 文档或查询 Context7 中的“MCP stdio 服务器”以了解当前模式。

保持服务器逻辑（工具+资源）独立于传输，以便您可以在入口点插入 stdio 或 HTTP。

### 远程（流式 HTTP）

对于 Cursor、云或其他远程客户端，请使用 **Streamable HTTP**（根据当前规范使用单个 MCP HTTP 端点）。仅当需要向后兼容时才支持旧版 HTTP/SSE。

## 示例

### 安装和服务器设置```bash
npm install @modelcontextprotocol/sdk zod
``````typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

const server = new McpServer({ name: "my-server", version: "1.0.0" });
```使用您的 SDK 版本提供的 API 注册工具和资源：某些版本使用 `server.tool(name, description, schema, handler)` （位置参数），其他版本使用 `server.tool({ name, description, inputSchema }, handler)` 或 `registerTool()`。对于资源也是如此——当 API 提供它时，在处理程序中包含一个“uri”。检查官方 MCP 文档或 Context7 中当前的“@modelcontextprotocol/sdk”签名以避免复制粘贴错误。

使用 **Zod** （或 SDK 的首选模式格式）进行输入验证。

## 最佳实践

- **模式优先**：为每个工具定义输入模式；文档参数和返回形状。
- **错误**：返回模型可以解释的结构化错误或消息；避免原始堆栈跟踪。
- **幂等性**：尽可能首选幂等工具，这样重试是安全的。
- **速率和成本**：对于调用外部API的工具，请考虑速率限制和成本；工具说明中的文档。
- **版本控制**：在 package.json 中固定 SDK 版本；升级时检查发行说明。

## 官方 SDK 和文档

- **JavaScript/TypeScript**：`@modelcontextprotocol/sdk` (npm)。使用库名称为“MCP”的 Context7 作为当前注册和传输模式。
- **Go**：GitHub 上的官方 Go SDK (`modelcontextprotocol/go-sdk`)。
- **C#**：.NET 的官方 C# SDK。