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
该存储库当前的 Exa 设置记录了此处公开的工具界面：“web_search_exa”和“get_code_context_exa”。
如果您的 Exa 服务器公开了其他工具，请在文档或提示中依赖它们之前验证它们的确切名称。

## 核心工具

### web_search_exa
当前信息、新闻或事实的一般网络搜索。```
web_search_exa(query: "latest AI developments 2026", numResults: 5)
```**参数：**

|参数 |类型 |默认 |笔记|
|--------|------|---------|--------|
| `查询` |字符串|必填|搜索查询 |
| `numResults` |数量 | 8 |结果数量 |
| `类型` |字符串| `自动` |搜索模式|
| `活爬行` |字符串| `后备` |需要时更喜欢实时抓取 |
| `类别` |字符串|无 |可选焦点，例如“公司”或“研究论文” |

### get_code_context_exa
从 GitHub、Stack Overflow 和文档网站查找代码示例和文档。```
get_code_context_exa(query: "Python asyncio patterns", tokensNum: 3000)
```**参数：**

|参数 |类型 |默认 |笔记|
|--------|------|---------|--------|
| `查询` |字符串|必填|代码或API搜索查询|
| `tokensNum` |数量 | 5000 |内容代币（1000-50000）|

## 使用模式

### 快速查找```
web_search_exa(query: "Node.js 22 new features", numResults: 3)
```### 代码研究```
get_code_context_exa(query: "Rust error handling patterns Result type", tokensNum: 3000)
```### 公司或人员研究```
web_search_exa(query: "Vercel funding valuation 2026", numResults: 3, category: "company")
web_search_exa(query: "site:linkedin.com/in AI safety researchers Anthropic", numResults: 5)
```### 技术深入探讨```
web_search_exa(query: "WebAssembly component model status and adoption", numResults: 5)
get_code_context_exa(query: "WebAssembly component model examples", tokensNum: 4000)
```## 提示

- 使用“web_search_exa”获取当前信息、公司查找和广泛的发现
- 使用“site:”、引用短语和“intitle:”等搜索运算符来缩小结果范围
- 较低的“tokensNum”（1000-2000）用于集中的代码片段，较高的（5000+）用于全面的上下文
- 当您需要 API 使用或代码示例而不是一般网页时，请使用 `get_code_context_exa`

## 相关技能

- `deep-research` — 结合使用 firecrawl + exa 的完整研究工作流程
- “市场研究”——具有决策框架的面向业务的研究