# 配置一切克劳德代码 (ECC)

Everything Claude Code 项目的交互式分步安装向导。使用“AskUserQuestion”引导用户选择性安装技能和规则，然后验证正确性并提供优化。

## 何时激活

- 用户说“配置 ecc”、“安装 ecc”、“设置所有 claude 代码”或类似内容
- 用户想要有选择地安装该项目中的技能或规则
- 用户想要验证或修复现有的 ECC 安装
- 用户想要优化其项目的已安装技能或规则

## 先决条件

在激活之前，克劳德·代码必须可以使用此技能。两种引导方式：
1. **通过插件**：`/plugin install everything-claude-code` — 插件自动加载此技能
2. **手动**：仅将此技能复制到`~/.claude/skills/configure-ecc/SKILL.md`，然后通过说“configure ecc”激活

---

## 步骤 0：克隆 ECC 存储库

在安装之前，将最新的 ECC 源克隆到“/tmp”：```bash
rm -rf /tmp/everything-claude-code
git clone https://github.com/affaan-m/everything-claude-code.git /tmp/everything-claude-code
```将 `ECC_ROOT=/tmp/everything-claude-code` 设置为所有后续复制操作的源。

如果克隆失败（网络问题等），请使用“AskUserQuestion”要求用户提供现有 ECC 克隆的本地路径。

---

## 第 1 步：选择安装级别

使用“AskUserQuestion”询问用户安装位置：```
Question: "Where should ECC components be installed?"
Options:
  - "User-level (~/.claude/)" — "Applies to all your Claude Code projects"
  - "Project-level (.claude/)" — "Applies only to the current project"
  - "Both" — "Common/shared items user-level, project-specific items project-level"
```将选择存储为“INSTALL_LEVEL”。设置目标目录：
- 用户级：`TARGET=~/.claude`
- 项目级别：`TARGET=.claude`（相对于当前项目根目录）
- 两者：`TARGET_USER=~/.claude`、`TARGET_PROJECT=.claude`

如果目标目录不存在，则创建它们：```bash
mkdir -p $TARGET/skills $TARGET/rules
```---

## 第 2 步：选择并安装技能

### 2a：选择范围（核心与利基）

默认为 **Core（建议新用户）** — 复制 `.agents/skills/*` 加上 `skills/search-first/` 以实现研究优先的工作流程。该捆绑包涵盖工程、评估、验证、安全、战略压缩、前端设计和人类跨功能技能（文章写作、内容引擎、市场研究、前端幻灯片）。

使用“AskUserQuestion”（单选）：```
Question: "Install core skills only, or include niche/framework packs?"
Options:
  - "Core only (recommended)" — "tdd, e2e, evals, verification, research-first, security, frontend patterns, compacting, cross-functional Anthropic skills"
  - "Core + selected niche" — "Add framework/domain-specific skills after core"
  - "Niche only" — "Skip core, install specific framework/domain skills"
Default: Core only
```如果用户选择利基或核心+利基，请继续下面的类别选择，并且仅包括他们选择的那些利基技能。

### 2b：选择技能类别

下面有 7 个可选择的类别组。随后的详细确认列表涵盖 8 个类别的 45 项技能，以及 1 个独立模板。将“AskUserQuestion”与“multiSelect: true”结合使用：```
Question: "Which skill categories do you want to install?"
Options:
  - "Framework & Language" — "Django, Laravel, Spring Boot, Go, Python, Java, Frontend, Backend patterns"
  - "Database" — "PostgreSQL, ClickHouse, JPA/Hibernate patterns"
  - "Workflow & Quality" — "TDD, verification, learning, security review, compaction"
  - "Research & APIs" — "Deep research, Exa search, Claude API patterns"
  - "Social & Content Distribution" — "X/Twitter API, crossposting alongside content-engine"
  - "Media Generation" — "fal.ai image/video/audio alongside VideoDB"
  - "Orchestration" — "dmux multi-agent workflows"
  - "All skills" — "Install every available skill"
```### 2c: Confirm Individual Skills

For each selected category, print the full list of skills below and ask the user to confirm or deselect specific ones. If the list exceeds 4 items, print the list as text and use `AskUserQuestion` with an "Install all listed" option plus "Other" for the user to paste specific names.

**Category: Framework & Language (21 skills)**

| Skill | Description |
|-------|-------------|
| `backend-patterns` | Backend architecture, API design, server-side best practices for Node.js/Express/Next.js |
| `coding-standards` | Universal coding standards for TypeScript, JavaScript, React, Node.js |
| `django-patterns` | Django architecture, REST API with DRF, ORM, caching, signals, middleware |
| `django-security` | Django security: auth, CSRF, SQL injection, XSS prevention |
| `django-tdd` | Django testing with pytest-django, factory_boy, mocking, coverage |
| `django-verification` | Django verification loop: migrations, linting, tests, security scans |
| `laravel-patterns` | Laravel architecture patterns: routing, controllers, Eloquent, queues, caching |
| `laravel-security` | Laravel security: auth, policies, CSRF, mass assignment, rate limiting |
| `laravel-tdd` | Laravel testing with PHPUnit and Pest, factories, fakes, coverage |
| `laravel-verification` | Laravel verification: linting, static analysis, tests, security scans |
| `frontend-patterns` | React, Next.js, state management, performance, UI patterns |
| `frontend-slides` | Zero-dependency HTML presentations, style previews, and PPTX-to-web conversion |
| `golang-patterns` | Idiomatic Go patterns, conventions for robust Go applications |
| `golang-testing` | Go testing: table-driven tests, subtests, benchmarks, fuzzing |
| `java-coding-standards` | Java coding standards for Spring Boot: naming, immutability, Optional, streams |
| `python-patterns` | Pythonic idioms, PEP 8, type hints, best practices |
| `python-testing` | Python testing with pytest, TDD, fixtures, mocking, parametrization |
| `springboot-patterns` | Spring Boot architecture, REST API, layered services, caching, async |
| `springboot-security` | Spring Security: authn/authz, validation, CSRF, secrets, rate limiting |
| `springboot-tdd` | Spring Boot TDD with JUnit 5, Mockito, MockMvc, Testcontainers |
| `springboot-verification` | Spring Boot verification: build, static analysis, tests, security scans |

**Category: Database (3 skills)**

| Skill | Description |
|-------|-------------|
| `clickhouse-io` | ClickHouse patterns, query optimization, analytics, data engineering |
| `jpa-patterns` | JPA/Hibernate entity design, relationships, query optimization, transactions |
| `postgres-patterns` | PostgreSQL query optimization, schema design, indexing, security |

**Category: Workflow & Quality (8 skills)**

| Skill | Description |
|-------|-------------|
| `continuous-learning` | Auto-extract reusable patterns from sessions as learned skills |
| `continuous-learning-v2` | Instinct-based learning with confidence scoring, evolves into skills/commands/agents |
| `eval-harness` | Formal evaluation framework for eval-driven development (EDD) |
| `iterative-retrieval` | Progressive context refinement for subagent context problem |
| `security-review` | Security checklist: auth, input, secrets, API, payment features |
| `strategic-compact` | Suggests manual context compaction at logical intervals |
| `tdd-workflow` | Enforces TDD with 80%+ coverage: unit, integration, E2E |
| `verification-loop` | Verification and quality loop patterns |

**Category: Business & Content (5 skills)**

| Skill | Description |
|-------|-------------|
| `article-writing` | Long-form writing in a supplied voice using notes, examples, or source docs |
| `content-engine` | Multi-platform social content, scripts, and repurposing workflows |
| `market-research` | Source-attributed market, competitor, fund, and technology research |
| `investor-materials` | Pitch decks, one-pagers, investor memos, and financial models |
| `investor-outreach` | Personalized investor cold emails, warm intros, and follow-ups |

**Category: Research & APIs (3 skills)**

| Skill | Description |
|-------|-------------|
| `deep-research` | Multi-source deep research using firecrawl and exa MCPs with cited reports |
| `exa-search` | Neural search via Exa MCP for web, code, company, and people research |
| `claude-api` | Anthropic Claude API patterns: Messages, streaming, tool use, vision, batches, Agent SDK |

**Category: Social & Content Distribution (2 skills)**

| Skill | Description |
|-------|-------------|
| `x-api` | X/Twitter API integration for posting, threads, search, and analytics |
| `crosspost` | Multi-platform content distribution with platform-native adaptation |

**Category: Media Generation (2 skills)**

| Skill | Description |
|-------|-------------|
| `fal-ai-media` | Unified AI media generation (image, video, audio) via fal.ai MCP |
| `video-editing` | AI-assisted video editing for cutting, structuring, and augmenting real footage |

**Category: Orchestration (1 skill)**

| Skill | Description |
|-------|-------------|
| `dmux-workflows` | Multi-agent orchestration using dmux for parallel agent sessions |

**Standalone**

| Skill | Description |
|-------|-------------|
| `project-guidelines-example` | Template for creating project-specific skills |

### 2d: Execute Installation

For each selected skill, copy the entire skill directory:```bash
cp -r $ECC_ROOT/skills/<skill-name> $TARGET/skills/
```注意：“连续学习”和“连续学习-v2”有额外的文件（config.json、钩子、脚本）——确保复制整个目录，而不仅仅是 SKILL.md。

---

## 步骤 3：选择并安装规则

将“AskUserQuestion”与“multiSelect: true”结合使用：```
Question: "Which rule sets do you want to install?"
Options:
  - "Common rules (Recommended)" — "Language-agnostic principles: coding style, git workflow, testing, security, etc. (8 files)"
  - "TypeScript/JavaScript" — "TS/JS patterns, hooks, testing with Playwright (5 files)"
  - "Python" — "Python patterns, pytest, black/ruff formatting (5 files)"
  - "Go" — "Go patterns, table-driven tests, gofmt/staticcheck (5 files)"
```执行安装：```bash
# Common rules (flat copy into rules/)
cp -r $ECC_ROOT/rules/common/* $TARGET/rules/

# Language-specific rules (flat copy into rules/)
cp -r $ECC_ROOT/rules/typescript/* $TARGET/rules/   # if selected
cp -r $ECC_ROOT/rules/python/* $TARGET/rules/        # if selected
cp -r $ECC_ROOT/rules/golang/* $TARGET/rules/        # if selected
```**重要**：如果用户选择任何特定于语言的规则而不是通用规则，请警告他们：
> “特定于语言的规则扩展了通用规则。不使用通用规则进行安装可能会导致覆盖不完整。是否也安装通用规则？”

---

## 步骤 4：安装后验证

安装后，执行以下自动检查：

### 4a：验证文件是否存在

列出所有已安装的文件并确认它们存在于目标位置：```bash
ls -la $TARGET/skills/
ls -la $TARGET/rules/
```### 4b：检查路径引用

扫描所有已安装的“.md”文件以获取路径引用：```bash
grep -rn "~/.claude/" $TARGET/skills/ $TARGET/rules/
grep -rn "../common/" $TARGET/rules/
grep -rn "skills/" $TARGET/skills/
```**对于项目级安装**，标记对 `~/.claude/` 路径的任何引用：
- 如果技能引用 `~/.claude/settings.json` — 这通常没问题（设置始终是用户级别的）
- 如果技能引用“~/.claude/skills/”或“~/.claude/rules/”——如果仅在项目级别安装，则可能会被破坏
- 如果一项技能通过名称引用了另一项技能 - 检查所引用的技能是否也已安装

### 4c：检查技能之间的交叉引用

有些技能会参考其他技能。验证这些依赖关系：
- `django-tdd` 可能引用 `django-patterns`
- `laravel-tdd` 可能引用 `laravel-patterns`
- `springboot-tdd` 可能引用 `springboot-patterns`
- `continuous-learning-v2` 引用 `~/.claude/homunculus/` 目录
- `python-testing` 可能引用 `python-patterns`
- `golang-testing` 可能引用 `golang-patterns`
- `crosspost` 引用 `content-engine` 和 `x-api`
- `deep-research` 引用 `exa-search` （补充 MCP 工具）
- `fal-ai-media` 引用 `videodb` （补充媒体技能）
- `x-api` 引用 `content-engine` 和 `crosspost`
- 特定于语言的规则引用“common/”对应项

### 4d：报告问题

对于发现的每个问题，报告：
1. **文件**：包含有问题的参考的文件
2. **行**：行号
3. **问题**：出了什么问题（例如，“引用 ~/.claude/skills/python-patterns 但未安装 python-patterns”）
4. **建议的修复**：该怎么做（例如，“安装 python-patterns 技能”或“更新 .claude/skills/ 的路径”）

---

## 步骤 5：优化已安装的文件（可选）

使用“询问用户问题”：```
Question: "Would you like to optimize the installed files for your project?"
Options:
  - "Optimize skills" — "Remove irrelevant sections, adjust paths, tailor to your tech stack"
  - "Optimize rules" — "Adjust coverage targets, add project-specific patterns, customize tool configs"
  - "Optimize both" — "Full optimization of all installed files"
  - "Skip" — "Keep everything as-is"
```### 如果优化技能：
1. 阅读每个已安装的SKILL.md
2.询问用户他们的项目的技术堆栈是什么（如果还不知道）
3. 对于每项技能，建议删除不相关的部分
4. 在安装目标（不是源存储库）就地编辑 SKILL.md 文件
5. 修复步骤 4 中发现的任何路径问题

### 如果优化规则：
1.读取每个已安装的规则.md文件
2. 询问用户的偏好：
   - 测试覆盖率目标（默认80%）
   - 首选格式化工具
   - Git 工作流程约定
   - 安全要求
3. 在安装目标处就地编辑规则文件

**关键**：仅修改安装目标 (`$TARGET/`) 中的文件，切勿修改源 ECC 存储库 (`$ECC_ROOT/`) 中的文件。

---

## 步骤 6：安装摘要

从 `/tmp` 清理克隆的存储库：```bash
rm -rf /tmp/everything-claude-code
```然后打印总结报告：```
## ECC Installation Complete

### Installation Target
- Level: [user-level / project-level / both]
- Path: [target path]

### Skills Installed ([count])
- skill-1, skill-2, skill-3, ...

### Rules Installed ([count])
- common (8 files)
- typescript (5 files)
- ...

### Verification Results
- [count] issues found, [count] fixed
- [list any remaining issues]

### Optimizations Applied
- [list changes made, or "None"]
```---

## 故障排除

###“克劳德·科德没有拾取技能”
- 验证技能目录包含“SKILL.md”文件（不仅仅是松散的.md文件）
- 对于用户级别：检查 `~/.claude/skills/<skill-name>/SKILL.md` 是否存在
- 对于项目级别：检查 `.claude/skills/<skill-name>/SKILL.md` 是否存在

###“规则不起作用”
- 规则是平面文件，不在子目录中：“$TARGET/rules/coding-style.md”（正确）与“$TARGET/rules/common/coding-style.md”（对于平面安装不正确）
- 安装规则后重新启动 Claude Code

###“项目级安装后路径引用错误”
- 某些技能采用 `~/.claude/` 路径。运行步骤 4 验证来查找并修复这些问题。
- 对于“Continous-learning-v2”，“~/.claude/homunculus/”目录始终是用户级的——这是预期的，而不是错误。