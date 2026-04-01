# 文档查找 (Context7)

当用户询问库、框架或 API 时，通过 Context7 MCP（工具“resolve-library-id”和“query-docs”）获取当前文档，而不是依赖训练数据。

## 核心概念

- **Context7**：公开实时文档的 MCP 服务器；使用它代替库和 API 的训练数据。
- **resolve-library-id**：从库名称和查询返回 Context7 兼容的库 ID（例如 `/vercel/next.js`）。
- **query-docs**：获取给定库 ID 和问题的文档和代码片段。始终首先调用resolve-library-id 来获取有效的库ID。

## 何时使用

当用户执行以下操作时激活：

- 询问设置或配置问题（例如“如何配置 Next.js 中间件？”）
- 请求依赖于库的代码（“为...编写 Prisma 查询”）
- 需要 API 或参考信息（“Supabase 身份验证方法是什么？”）
- 提及特定框架或库（React、Vue、Svelte、Express、Tailwind、Prisma、Supabase 等）

当请求依赖于库、框架或 API 的准确、最新行为时，请使用此技能。适用于配置了 Context7 MCP 的线束（例如 Claude Code、Cursor、Codex）。

## 它是如何工作的

### 第 1 步：解析库 ID

使用以下命令调用 **resolve-library-id** MCP 工具：

- **libraryName**：从用户的问题中获取的库或产品名称（例如“Next.js”、“Prisma”、“Supabase”）。
- **查询**：用户的完整问题。这提高了结果的相关性排名。

在查询文档之前，您必须获取 Context7 兼容的库 ID（格式为“/org/project”或“/org/project/version”）。如果没有此步骤中的有效库 ID，请勿调用 query-docs。

### 第 2 步：选择最佳匹配

从解析结果中，使用以下方法选择一个结果：

- **名称匹配**：首选与用户要求的内容完全匹配或最接近的匹配。
- **基准分数**：分数越高表示文档质量越好（100 为最高）。
- **来源声誉**：首选高或中等声誉（如果有）。
- **版本**：如果用户指定了版本（例如“React 19”、“Next.js 15”），则首选版本特定的库 ID（如果列出）（例如 `/org/project/v1.2.0`）。

### 第 3 步：获取文档

使用以下命令调用 **query-docs** MCP 工具：

- **libraryId**：从步骤 2 中选择的 Context7 库 ID（例如 `/vercel/next.js`）。
- **查询**：用户的具体问题或任务。具体获取相关片段。

限制：每个问题调用query-docs（或resolve-library-id）的次数不要超过3次。如果 3 次通话后答案仍不清楚，请说明不确定性并使用您所掌握的最佳信息，而不是猜测。

### 第 4 步：使用文档

- 使用获取的当前信息回答用户的问题。
- 如果有帮助，请包含文档中的相关代码示例。
- 在重要时引用库或版本（例如“在 Next.js 15 中...”）。

## 示例

### 示例：Next.js 中间件

1. 使用 `libraryName: "Next.js"`、`query: "How do I set up Next.js middleware?"` 调用 **resolve-library-id**。
2. 从结果中，按名称和基准分数选择最佳匹配（例如“/vercel/next.js”）。
3. 使用 `libraryId: "/vercel/next.js"`、`query: "How do I set up Next.js middleware?"` 调用 **query-docs**。
4.利用返回的片段和文字进行回答；如果相关，请包含文档中的最小“middleware.ts”示例。

### 示例：Prisma 查询

1. 使用 `libraryName: "Prisma"`、`query: "如何查询关系？"` 调用 **resolve-library-id**。
2. 选择官方 Prisma 库 ID（例如“/prisma/prisma”）。
3. 使用该 `libraryId` 和查询调用 **query-docs**。
4. 使用文档中的简短代码片段返回 Prisma 客户端模式（例如“include”或“select”）。

### 示例：Supabase 身份验证方法

1. 使用 `libraryName: "Supabase"`、`query: "What are the authmethod?"` 调用 **resolve-library-id**。
2. 选择 Supabase 文档库 ID。
3. 调用**query-docs**；总结身份验证方法并显示所获取文档中的最少示例。

## 最佳实践

- **具体**：尽可能使用用户的完整问题作为查询，以获得更好的相关性。
- **版本意识**：当用户提及版本时，请使用解析步骤中可用的版本特定库 ID。
- **优先选择官方来源**：当存在多个匹配项时，优先选择官方或主要软件包而不是社区分叉。
- **无敏感数据**：编辑发送到 Context7 的任何查询中的 API 密钥、密码、令牌和其他秘密。在将用户的问题传递给resolve-library-id 或query-docs 之前，将其视为可能包含机密。