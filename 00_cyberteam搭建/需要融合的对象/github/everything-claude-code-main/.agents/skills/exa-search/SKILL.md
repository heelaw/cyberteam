# Exa 搜索

通过 Exa MCP 服务器对网络内容、代码、公司和人员进行神经搜索。

## 何时激活

- 用户需要当前的网络信息或新闻
- 搜索代码示例、API 文档或技术参考
- 研究公司、竞争对手或市场参与者
- 寻找专业人士或某个领域的人员
- 为任何开发任务进行背景研究
- 用户说“搜索”、“查找”、“查找”或“最新消息”

## MCP 要求

必须配置 Exa MCP 服务器。添加到`~/.claude.json`：```json
"exa-web-search": {
  "command": "npx",
  "args": ["-y", "exa-mcp-server"],
  "env": { "EXA_API_KEY": "YOUR_EXA_API_KEY_HERE" }
}
```在 [exa.ai](https://exa.ai) 获取 API 密钥。

## 核心工具

### web_search_exa
当前信息、新闻或事实的一般网络搜索。```
web_search_exa(query: "latest AI developments 2026", numResults: 5)
```**参数：**

|参数 |类型 |默认 |笔记|
|--------|------|---------|--------|
| `查询` |字符串|必填|搜索查询 |
| `numResults` |数量 | 8 |结果数量 |

### web_search_advanced_exa
具有域和日期限制的过滤搜索。```
web_search_advanced_exa(
  query: "React Server Components best practices",
  numResults: 5,
  includeDomains: ["github.com", "react.dev"],
  startPublishedDate: "2025-01-01"
)
```**参数：**

|参数 |类型 |默认 |笔记|
|--------|------|---------|--------|
| `查询` |字符串|必填|搜索查询 |
| `numResults` |数量 | 8 |结果数量 |
| `includeDomains` |字符串[] |无 |限制到特定域 |
| `排除域` |字符串[] |无 |排除特定域 |
| `开始发布日期` |字符串|无 | ISO 日期过滤器（开始）|
| `结束发布日期` |字符串|无 | ISO 日期过滤器（结束）|

### get_code_context_exa
从 GitHub、Stack Overflow 和文档网站查找代码示例和文档。```
get_code_context_exa(query: "Python asyncio patterns", tokensNum: 3000)
```**参数：**

|参数 |类型 |默认 |笔记|
|--------|------|---------|--------|
| `查询` |字符串|必填|代码或API搜索查询|
| `tokensNum` |数量 | 5000 |内容代币（1000-50000）|

### 公司_研究_exa
研究公司的商业情报和新闻。```
company_research_exa(companyName: "Anthropic", numResults: 5)
```**参数：**

|参数 |类型 |默认 |笔记|
|--------|------|---------|--------|
| `公司名称` |字符串|必填|公司名称 |
| `numResults` |数量 | 5 |结果数量 |

### people_search_exa
查找专业简介和简历。```
people_search_exa(query: "AI safety researchers at Anthropic", numResults: 5)
```###爬行_exa
从 URL 中提取完整页面内容。```
crawling_exa(url: "https://example.com/article", tokensNum: 5000)
```**参数：**

|参数 |类型 |默认 |笔记|
|--------|------|---------|--------|
| `网址` |字符串|必填|要提取的 URL |
| `tokensNum` |数量 | 5000 |内容代币 |

### deep_researcher_start / deep_researcher_check
启动异步运行的人工智能研究代理。```
# Start research
deep_researcher_start(query: "comprehensive analysis of AI code editors in 2026")

# Check status (returns results when complete)
deep_researcher_check(researchId: "<id from start>")
```## 使用模式

### 快速查找```
web_search_exa(query: "Node.js 22 new features", numResults: 3)
```### 代码研究```
get_code_context_exa(query: "Rust error handling patterns Result type", tokensNum: 3000)
```### 公司尽职调查```
company_research_exa(companyName: "Vercel", numResults: 5)
web_search_advanced_exa(query: "Vercel funding valuation 2026", numResults: 3)
```### 技术深入探讨```
# Start async research
deep_researcher_start(query: "WebAssembly component model status and adoption")
# ... do other work ...
deep_researcher_check(researchId: "<id>")
```## 提示

- 使用“web_search_exa”进行广泛查询，使用“web_search_advanced_exa”进行过滤结果
- 较低的“tokensNum”（1000-2000）用于集中的代码片段，较高的（5000+）用于全面的上下文
- 将“company_research_exa”与“web_search_advanced_exa”结合起来进行彻底的公司分析
- 使用“crawling_exa”从搜索结果中找到的特定 URL 获取完整内容
- `deep_researcher_start` 最适合受益于 AI 综合的综合主题

## 相关技能

- `deep-research` — 结合使用 firecrawl + exa 的完整研究工作流程
- “市场研究”——具有决策框架的面向业务的研究