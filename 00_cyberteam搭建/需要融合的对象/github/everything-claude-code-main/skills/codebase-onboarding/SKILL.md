# 代码库入门

系统地分析不熟悉的代码库并生成结构化的入门指南。专为加入新项目或首次在现有存储库中设置 Claude Code 的开发人员而设计。

## 何时使用

- 第一次使用 Claude Code 打开项目
- 加入新团队或存储库
- 用户询问“帮助我理解这个代码库”
- 用户要求为项目生成 CLAUDE.md
- 用户说“加入我”或“引导我完成此存储库”

## 它是如何工作的

### 第一阶段：侦察

收集有关项目的原始信号，而无需读取每个文件。并行运行这些检查：```
1. Package manifest detection
   → package.json, go.mod, Cargo.toml, pyproject.toml, pom.xml, build.gradle,
     Gemfile, composer.json, mix.exs, pubspec.yaml

2. Framework fingerprinting
   → next.config.*, nuxt.config.*, angular.json, vite.config.*,
     django settings, flask app factory, fastapi main, rails config

3. Entry point identification
   → main.*, index.*, app.*, server.*, cmd/, src/main/

4. Directory structure snapshot
   → Top 2 levels of the directory tree, ignoring node_modules, vendor,
     .git, dist, build, __pycache__, .next

5. Config and tooling detection
   → .eslintrc*, .prettierrc*, tsconfig.json, Makefile, Dockerfile,
     docker-compose*, .github/workflows/, .env.example, CI configs

6. Test structure detection
   → tests/, test/, __tests__/, *_test.go, *.spec.ts, *.test.js,
     pytest.ini, jest.config.*, vitest.config.*
```### 第 2 阶段：架构映射

从侦察数据中识别：

**技术堆栈**
- 语言和版本限制
- 框架和主要库
- 数据库和 ORM
- 构建工具和捆绑器
- CI/CD 平台

**架构模式**
- 整体式、单一存储库、微服务或无服务器
- 前端/后端拆分或全栈
- API 风格：REST、GraphQL、gRPC、tRPC

**关键目录**
将顶级目录映射到其用途：

<!-- React 项目示例 — 替换为检测到的目录 -->```
src/components/  → React UI components
src/api/         → API route handlers
src/lib/         → Shared utilities
src/db/          → Database models and migrations
tests/           → Test suites
scripts/         → Build and deployment scripts
```**数据流**
跟踪一个请求从进入到响应：
- 请求从哪里输入？ （路由器、处理程序、控制器）
- 如何验证？ （中间件、模式、防护）
- 业务逻辑在哪里？ （服务、模型、用例）
- 它如何到达数据库？ （ORM、原始查询、存储库）

### 第 3 阶段：约定检测

识别代码库已经遵循的模式：

**命名约定**
- 文件命名：kebab-case、camelCase、PascalCase、snake_case
- 组件/类命名模式
- 测试文件命名：`*.test.ts`、`*.spec.ts`、`*_test.go`

**代码模式**
- 错误处理方式：try/catch、结果类型、错误代码
- 依赖注入或直接导入
- 状态管理方法
- 异步模式：回调、承诺、异步/等待、通道

**Git 约定**
- 来自最近分支的分支命名
- 最近提交的提交消息样式
- PR 工作流程（压缩、合并、变基）
- 如果存储库还没有提交或只有浅历史记录（例如`git clone --深度1`），请跳过本节并注意“Git历史记录不可用或太浅而无法检测约定”

### 第 4 阶段：生成入门工件

产生两个输出：

#### 输出 1：入门指南```markdown
# Onboarding Guide: [Project Name]

## Overview
[2-3 sentences: what this project does and who it serves]

## Tech Stack
<!-- Example for a Next.js project — replace with detected stack -->
| Layer | Technology | Version |
|-------|-----------|---------|
| Language | TypeScript | 5.x |
| Framework | Next.js | 14.x |
| Database | PostgreSQL | 16 |
| ORM | Prisma | 5.x |
| Testing | Jest + Playwright | - |

## Architecture
[Diagram or description of how components connect]

## Key Entry Points
<!-- Example for a Next.js project — replace with detected paths -->
- **API routes**: `src/app/api/` — Next.js route handlers
- **UI pages**: `src/app/(dashboard)/` — authenticated pages
- **Database**: `prisma/schema.prisma` — data model source of truth
- **Config**: `next.config.ts` — build and runtime config

## Directory Map
[Top-level directory → purpose mapping]

## Request Lifecycle
[Trace one API request from entry to response]

## Conventions
- [File naming pattern]
- [Error handling approach]
- [Testing patterns]
- [Git workflow]

## Common Tasks
<!-- Example for a Node.js project — replace with detected commands -->
- **Run dev server**: `npm run dev`
- **Run tests**: `npm test`
- **Run linter**: `npm run lint`
- **Database migrations**: `npx prisma migrate dev`
- **Build for production**: `npm run build`

## Where to Look
<!-- Example for a Next.js project — replace with detected paths -->
| I want to... | Look at... |
|--------------|-----------|
| Add an API endpoint | `src/app/api/` |
| Add a UI page | `src/app/(dashboard)/` |
| Add a database table | `prisma/schema.prisma` |
| Add a test | `tests/` matching the source path |
| Change build config | `next.config.ts` |
```#### 输出 2：入门 CLAUDE.md

根据检测到的约定生成或更新项目特定的 CLAUDE.md。如果“CLAUDE.md”已经存在，请先阅读它并对其进行增强 - 保留现有的特定于项目的说明并清楚地指出添加或更改的内容。```markdown
# Project Instructions

## Tech Stack
[Detected stack summary]

## Code Style
- [Detected naming conventions]
- [Detected patterns to follow]

## Testing
- Run tests: `[detected test command]`
- Test pattern: [detected test file convention]
- Coverage: [if configured, the coverage command]

## Build & Run
- Dev: `[detected dev command]`
- Build: `[detected build command]`
- Lint: `[detected lint command]`

## Project Structure
[Key directory → purpose map]

## Conventions
- [Commit style if detectable]
- [PR workflow if detectable]
- [Error handling patterns]
```## 最佳实践

1. **不要读取所有内容** — 侦察应使用 Glob 和 Grep，而不是读取每个文件。仅选择性地读取不明确的信号。
2. **验证，不要猜测** - 如果从配置中检测到框架但实际代码使用不同的东西，请相信该代码。
3. **尊重现有的 CLAUDE.md** — 如果已经存在，请增强它而不是替换它。指出新内容与现有内容。
4. **保持简洁** — 入职指南应可在 2 分钟内浏览完毕。详细信息属于代码，而不是指南。
5. **标记未知** - 如果无法自信地检测到约定，请直接说出来，而不是猜测。 “无法确定测试运行者”比错误的答案要好。

## 要避免的反模式

- 生成超过 100 行的 CLAUDE.md — 保持专注
- 列出每个依赖项 - 仅突出显示影响您编写代码方式的依赖项
- 描述明显的目录名称 - `src/` 不需要解释
- 复制自述文件——入职指南增加了自述文件所缺乏的结构洞察力

## 示例

### 示例 1：第一次在新存储库中
**用户**：“让我加入此代码库”
**行动**：运行完整的 4 阶段工作流程 → 生成入职指南 + Starter CLAUDE.md
**输出**：入职指南直接打印到对话中，加上写入项目根目录的“CLAUDE.md”

### 示例 2：为现有项目生成 CLAUDE.md
**用户**：“为此项目生成 CLAUDE.md”
**操作**：运行阶段 1-3，跳过入门指南，仅生成 CLAUDE.md
**输出**：项目特定的“CLAUDE.md”以及检测到的约定

### 示例 3：增强现有 CLAUDE.md
**用户**：“使用当前项目约定更新 CLAUDE.md”
**行动**：阅读现有的 CLAUDE.md，运行第 1-3 阶段，合并新发现
**输出**：更新了`CLAUDE.md`，添加了明确标记的内容