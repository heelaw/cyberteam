# /search-first — 在编码之前进行研究

将“实施前搜索现有解决方案”工作流程系统化。

## 触发器

在以下情况下使用此技能：
- 启动一项可能已有解决方案的新功能
- 添加依赖项或集成
- 用户询问“添加 X 功能”，您将要编写代码
- 在创建新的实用程序、帮助程序或抽象之前

## 工作流程```
┌─────────────────────────────────────────────┐
│  1. NEED ANALYSIS                           │
│     Define what functionality is needed      │
│     Identify language/framework constraints  │
├─────────────────────────────────────────────┤
│  2. PARALLEL SEARCH (researcher agent)      │
│     ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│     │  npm /   │ │  MCP /   │ │  GitHub / │  │
│     │  PyPI    │ │  Skills  │ │  Web      │  │
│     └──────────┘ └──────────┘ └──────────┘  │
├─────────────────────────────────────────────┤
│  3. EVALUATE                                │
│     Score candidates (functionality, maint, │
│     community, docs, license, deps)         │
├─────────────────────────────────────────────┤
│  4. DECIDE                                  │
│     ┌─────────┐  ┌──────────┐  ┌─────────┐  │
│     │  Adopt  │  │  Extend  │  │  Build   │  │
│     │ as-is   │  │  /Wrap   │  │  Custom  │  │
│     └─────────┘  └──────────┘  └─────────┘  │
├─────────────────────────────────────────────┤
│  5. IMPLEMENT                               │
│     Install package / Configure MCP /       │
│     Write minimal custom code               │
└─────────────────────────────────────────────┘
```## 决策矩阵

|信号|行动|
|--------|--------|
|完全匹配，维护良好，MIT/Apache | **采用** — 直接安装使用 |
|偏搭配，基础好| **扩展** — 安装 + 编写瘦包装器 |
|多个弱匹配| **Compose** — 组合 2-3 个小包 |
|没有找到合适的 | **构建** — 编写自定义内容，但通过研究获得信息 |

## 如何使用

### 快速模式（内联）

在编写实用程序或添加功能之前，请先在心里运行一下：

0. 仓库中已经存在这个吗？ → 首先通过相关模块/测试 `rg`
1. 这是一个常见问题吗？ → 搜索 npm/PyPI
2. 有 MCP 吗？ → 检查 `~/.claude/settings.json` 并搜索
3.有这方面的技巧吗？ → 检查 `~/.claude/skills/`
4. 有 GitHub 实现/模板吗？ → 在编写全新代码之前，运行 GitHub 代码搜索来查找维护的 OSS

### 完整模式（代理）

对于重要的功能，启动研究代理：```
Task(subagent_type="general-purpose", prompt="
  Research existing tools for: [DESCRIPTION]
  Language/framework: [LANG]
  Constraints: [ANY]

  Search: npm/PyPI, MCP servers, Claude Code skills, GitHub
  Return: Structured comparison with recommendation
")
```## 按类别搜索快捷方式

### 开发工具
- Linting → `eslint`、`ruff`、`textlint`、`markdownlint`
- 格式 → `prettier`、`black`、`gofmt`
- 测试 → `jest`、`pytest`、`go test`
- 预提交 → `husky`、`lint-staged`、`预提交`

### 人工智能/法学硕士整合
- Claude SDK → Context7 获取最新文档
- 提示管理→检查MCP服务器
- 文档处理 → `非结构化`、`pdfplumber`、`mammoth`

### 数据和 API
- HTTP 客户端 → `httpx` (Python)、`ky`/`got` (Node)
- 验证 → `zod` (TS)、`pydantic` (Python)
- 数据库 → 首先检查 MCP 服务器

### 内容与出版
- Markdown 处理 → `remark`、`unified`、`markdown-it`
- 图像优化 → `sharp`, `imagemin`

## 集成点

### 与策划代理
规划者应在第一阶段（架构审查）之前调用研究人员：
- 研究人员确定可用的工具
- Planner将它们纳入实施计划
- 避免在计划中“重新发明轮子”

### 与建筑师代理
建筑师应咨询研究人员：
- 技术堆栈决策
- 整合模式发现
- 现有参考架构

### 具有迭代检索技巧
结合起来进行渐进式发现：
- 第 1 周期：广泛搜索（npm、PyPI、MCP）
- 第 2 周期：详细评估最佳候选人
- 周期 3：测试与项目限制的兼容性

## 示例

### 示例 1：“添加死链接检查”```
Need: Check markdown files for broken links
Search: npm "markdown dead link checker"
Found: textlint-rule-no-dead-link (score: 9/10)
Action: ADOPT — npm install textlint-rule-no-dead-link
Result: Zero custom code, battle-tested solution
```### 示例 2：“添加 HTTP 客户端包装器”```
Need: Resilient HTTP client with retries and timeout handling
Search: npm "http client retry", PyPI "httpx retry"
Found: got (Node) with retry plugin, httpx (Python) with built-in retry
Action: ADOPT — use got/httpx directly with retry config
Result: Zero custom code, production-proven libraries
```### 示例 3：“添加配置文件 linter”```
Need: Validate project config files against a schema
Search: npm "config linter schema", "json schema validator cli"
Found: ajv-cli (score: 8/10)
Action: ADOPT + EXTEND — install ajv-cli, write project-specific schema
Result: 1 package + 1 schema file, no custom validation logic
```## 反模式

- **跳转到代码**：编写实用程序而不检查实用程序是否存在
- **忽略 MCP**：不检查 MCP 服务器是否已提供该功能
- **过度定制**：过度包装库会失去其好处
- **依赖膨胀**：为一项小功能安装大量软件包