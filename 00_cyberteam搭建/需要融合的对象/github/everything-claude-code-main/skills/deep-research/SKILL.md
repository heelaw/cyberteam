# 深入研究

使用 firecrawl 和 exa MCP 工具从多个网络来源生成详尽的、引用的研究报告。

## 何时激活

- 用户要求深入研究任何主题
- 竞争分析、技术评估或市场规模
- 对公司、投资者或技术的尽职调查
- 任何需要从多个来源综合的问题
- 用户说“研究”、“深入研究”、“调查”或“当前状态如何”

## MCP 要求

至少其中一项：
- **firecrawl** — `firecrawl_search`、`firecrawl_scrape`、`firecrawl_crawl`
- **exa** — `web_search_exa`、`web_search_advanced_exa`、`crawling_exa`

两者一起提供最佳的覆盖范围。在 `~/.claude.json` 或 `~/.codex/config.toml` 中配置。

## 工作流程

### 第 1 步：了解目标

问 1-2 个快速澄清的问题：
- “你的目标是什么——学习、做出决定还是写东西？”
- “您想要任何特定的角度或深度吗？”

如果用户说“只是研究一下”——跳过合理的默认设置。

### 第 2 步：规划研究

将主题分成 3-5 个研究子问题。示例：
- 主题：“人工智能对医疗保健的影响”
  - 当今医疗保健领域的主要人工智能应用有哪些？
  - 测量了哪些临床结果？
  - 监管挑战是什么？
  - 哪些公司在这个领域处于领先地位？
  - 市场规模和增长轨迹如何？

### 步骤3：执行多源搜索

对于每个子问题，使用可用的 MCP 工具进行搜索：

**随着火爬行：**```
firecrawl_search(query: "<sub-question keywords>", limit: 8)
```**与前：**```
web_search_exa(query: "<sub-question keywords>", numResults: 8)
web_search_advanced_exa(query: "<keywords>", numResults: 5, startPublishedDate: "2025-01-01")
```**搜索策略：**
- 每个子问题使用 2-3 个不同的关键字变体
- 混合一般查询和新闻查询
- 目标是总共 15-30 个独特来源
- 优先考虑：学术、官方、知名新闻 > 博客 > 论坛

### 步骤 4：深入阅读关键来源

对于最有希望的 URL，获取完整内容：

**随着火爬行：**```
firecrawl_scrape(url: "<url>")
```**与前：**```
crawling_exa(url: "<url>", tokensNum: 5000)
```完整阅读 3-5 个关键来源以深入了解。不要仅依赖搜索片段。

### 第 5 步：综合并撰写报告

构建报告：```markdown
# [Topic]: Research Report
*Generated: [date] | Sources: [N] | Confidence: [High/Medium/Low]*

## Executive Summary
[3-5 sentence overview of key findings]

## 1. [First Major Theme]
[Findings with inline citations]
- Key point ([Source Name](url))
- Supporting data ([Source Name](url))

## 2. [Second Major Theme]
...

## 3. [Third Major Theme]
...

## Key Takeaways
- [Actionable insight 1]
- [Actionable insight 2]
- [Actionable insight 3]

## Sources
1. [Title](url) — [one-line summary]
2. ...

## Methodology
Searched [N] queries across web and news. Analyzed [M] sources.
Sub-questions investigated: [list]
```### 第 6 步：交付

- **简短主题**：在聊天中发布完整报告
- **长报告**：发布执行摘要 + 要点，将完整报告保存到文件中

## 与子代理的并行研究

对于广泛的主题，请使用 Claude Code 的任务工具进行并行化：```
Launch 3 research agents in parallel:
1. Agent 1: Research sub-questions 1-2
2. Agent 2: Research sub-questions 3-4
3. Agent 3: Research sub-question 5 + cross-cutting themes
```每个代理都会搜索、读取来源并返回结果。主要会议综合成最终报告。

## 质量规则

1. **每项主张都需要来源。** 没有无来源的断言。
2. **交叉引用。** 如果只有一个来源这么说，请将其标记为未经验证。
3. **新近性很重要。** 优先考虑过去 12 个月的来源。
4. **承认差距。** 如果您在子问题上找不到好的信息，请说出来。
5. **没有幻觉。** 如果您不知道，请说“发现数据不足”。
6. **将事实与推论分开。** 清楚地标记估计、预测和意见。

## 示例```
"Research the current state of nuclear fusion energy"
"Deep dive into Rust vs Go for backend services in 2026"
"Research the best strategies for bootstrapping a SaaS business"
"What's happening with the US housing market right now?"
"Investigate the competitive landscape for AI code editors"
```