# 上下文预算

分析 Claude Code 会话中每个加载组件的令牌开销，并提出可操作的优化以回收上下文空间。

## 何时使用

- 会话性能感觉迟缓或输出质量下降
- 您最近添加了许多技能、代理或 MCP 服务器
- 你想知道你实际上有多少上下文空间
- 计划添加更多组件并需要知道是否有空间
- 运行`/context-budget`命令（这个技能支持它）

## 它是如何工作的

### 第一阶段：库存

扫描所有组件目录并估计令牌消耗：

**代理** (`代理/*.md`)
- 计算每个文件的行数和标记数（字数 × 1.3）
- 提取“描述”frontmatter 长度
- 标志：文件>200行（重），描述>30字（臃肿的frontmatter）

**技能** (`技能/*/SKILL.md`)
- 计算每个 SKILL.md 的代币数量
- 标志：文件 >400 行
- 检查“.agents/skills/”中的重复副本 - 跳过相同的副本以避免重复计数

**规则** (`rules/**/*.md`)
- 计算每个文件的令牌数
- 标志：文件 >100 行
- 检测同一语言模块中规则文件之间的内容重叠

**MCP 服务器**（`.mcp.json` 或活动 MCP 配置）
- 计算配置的服务器和工具总数
- 估计每个工具约 500 个令牌的架构开销
- 标志：具有超过 20 个工具的服务器、包含简单 CLI 命令的服务器（`gh`、`git`、`npm`、`supabase`、`vercel`）

**CLAUDE.md**（项目+用户级别）
- 计算 CLAUDE.md 链中每个文件的代币数量
- 标志：总计 >300 行

### 第 2 阶段：分类

将每个组件排序到一个桶中：

|桶|标准|行动|
|--------|----------|--------|
| **永远需要** |在 CLAUDE.md 中引用，支持活动命令，或匹配当前项目类型 |保留|
| **有时需要** |特定领域（例如语言模式），未在 CLAUDE.md 中引用 |考虑按需激活 |
| **很少需要** |没有命令引用、内容重叠或没有明显的项目匹配 |删除或延迟加载 |

### 第 3 阶段：检测问题

确定以下问题模式：

- **臃肿的代理描述** — frontmatter 中的描述 >30 个单词会加载到每个任务工具调用中
- **重代理** — 文件 >200 行在每次生成时都会膨胀任务工具上下文
- **冗余组件** — 重复代理逻辑的技能、重复 CLAUDE.md 的规则
- **MCP 超额订阅** — >10 个服务器，或免费提供包含 CLI 工具的服务器
- **CLAUDE.md 膨胀** — 冗长的解释、过时的部分、应该成为规则的说明

### 第四阶段：报告

生成背景预算报告：```
Context Budget Report
═══════════════════════════════════════

Total estimated overhead: ~XX,XXX tokens
Context model: Claude Sonnet (200K window)
Effective available context: ~XXX,XXX tokens (XX%)

Component Breakdown:
┌─────────────────┬────────┬───────────┐
│ Component       │ Count  │ Tokens    │
├─────────────────┼────────┼───────────┤
│ Agents          │ N      │ ~X,XXX    │
│ Skills          │ N      │ ~X,XXX    │
│ Rules           │ N      │ ~X,XXX    │
│ MCP tools       │ N      │ ~XX,XXX   │
│ CLAUDE.md       │ N      │ ~X,XXX    │
└─────────────────┴────────┴───────────┘

⚠ Issues Found (N):
[ranked by token savings]

Top 3 Optimizations:
1. [action] → save ~X,XXX tokens
2. [action] → save ~X,XXX tokens
3. [action] → save ~X,XXX tokens

Potential savings: ~XX,XXX tokens (XX% of current overhead)
```在详细模式下，另外输出每个文件的标记计数、最重文件的逐行细分、重叠组件之间的特定冗余行以及带有每个工具模式大小估计的 MCP 工具列表。

## 示例

**基本审核**```
User: /context-budget
Skill: Scans setup → 16 agents (12,400 tokens), 28 skills (6,200), 87 MCP tools (43,500), 2 CLAUDE.md (1,200)
       Flags: 3 heavy agents, 14 MCP servers (3 CLI-replaceable)
       Top saving: remove 3 MCP servers → -27,500 tokens (47% overhead reduction)
```**详细模式**```
User: /context-budget --verbose
Skill: Full report + per-file breakdown showing planner.md (213 lines, 1,840 tokens),
       MCP tool list with per-tool sizes, duplicated rule lines side by side
```**扩张前检查**```
User: I want to add 5 more MCP servers, do I have room?
Skill: Current overhead 33% → adding 5 servers (~50 tools) would add ~25,000 tokens → pushes to 45% overhead
       Recommendation: remove 2 CLI-replaceable servers first to stay under 40%
```## 最佳实践

- **标记估计**：对于散文使用“words × 1.3”，对于代码较多的文件使用“chars / 4”
- **MCP 是最大的杠杆**：每个工具模式花费约 500 个代币；配备 30 种工具的服务器的成本比您所有技能的总和还要高
- **始终加载代理描述**：即使从未调用代理，其描述字段也存在于每个任务工具上下文中
- **用于调试的详细模式**：当您需要查明导致开销的确切文件时使用，而不是用于定期审核
- **更改后审核**：添加任何代理、技能或 MCP 服务器后运行以尽早捕获蠕变