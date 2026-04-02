# dmux 工作流程

使用 dmux（用于代理工具的 tmux 窗格管理器）编排并行 AI 代理会话。

## 何时激活

- 并行运行多个代理会话
- 协调 Claude Code、Codex 和其他工具的工作
- 受益于分而治之并行性的复杂任务
- 用户说“并行运行”、“分割这项工作”、“使用 dmux”或“多代理”

## 什么是 dmux

dmux 是一个基于 tmux 的编排工具，用于管理 AI 代理窗格：
- 按“n”创建带有提示的新窗格
- 按“m”将窗格输出合并回主会话
- 支持：Claude Code、Codex、OpenCode、Cline、Gemini、Qwen

**安装：** `npm install -g dmux` 或参见 [github.com/standardagents/dmux](https://github.com/standardagents/dmux)

## 快速入门```bash
# Start dmux session
dmux

# Create agent panes (press 'n' in dmux, then type prompt)
# Pane 1: "Implement the auth middleware in src/auth/"
# Pane 2: "Write tests for the user service"
# Pane 3: "Update API documentation"

# Each pane runs its own agent session
# Press 'm' to merge results back
```## 工作流程模式

### 模式 1：研究 + 实施

将研究和实施分成并行的轨道：```
Pane 1 (Research): "Research best practices for rate limiting in Node.js.
  Check current libraries, compare approaches, and write findings to
  /tmp/rate-limit-research.md"

Pane 2 (Implement): "Implement rate limiting middleware for our Express API.
  Start with a basic token bucket, we'll refine after research completes."

# After Pane 1 completes, merge findings into Pane 2's context
```### 模式 2：多文件功能

跨独立文件并行工作：```
Pane 1: "Create the database schema and migrations for the billing feature"
Pane 2: "Build the billing API endpoints in src/api/billing/"
Pane 3: "Create the billing dashboard UI components"

# Merge all, then do integration in main pane
```### 模式 3：测试 + 修复循环

在一个窗格中运行测试，在另一个窗格中修复：```
Pane 1 (Watcher): "Run the test suite in watch mode. When tests fail,
  summarize the failures."

Pane 2 (Fixer): "Fix failing tests based on the error output from pane 1"
```### 模式 4：交叉安全带

使用不同的人工智能工具来完成不同的任务：```
Pane 1 (Claude Code): "Review the security of the auth module"
Pane 2 (Codex): "Refactor the utility functions for performance"
Pane 3 (Claude Code): "Write E2E tests for the checkout flow"
```### 模式 5：代码审查管道

平行评审视角：```
Pane 1: "Review src/api/ for security vulnerabilities"
Pane 2: "Review src/api/ for performance issues"
Pane 3: "Review src/api/ for test coverage gaps"

# Merge all reviews into a single report
```## 最佳实践

1. **仅限独立任务。** 不要并行化依赖于彼此输出的任务。
2. **清晰的边界。** 每个窗格都应该处理不同的文件或问题。
3. **有策略地合并。** 在合并之前检查窗格输出以避免冲突。
4. **使用 git 工作树。** 对于容易发生文件冲突的工作，请为每个窗格使用单独的工作树。
5. **资源意识。** 每个窗格都使用 API 令牌 — 将窗格总数保持在 5-6 个以下。

## Git 工作树集成

对于涉及重叠文件的任务：```bash
# Create worktrees for isolation
git worktree add -b feat/auth ../feature-auth HEAD
git worktree add -b feat/billing ../feature-billing HEAD

# Run agents in separate worktrees
# Pane 1: cd ../feature-auth && claude
# Pane 2: cd ../feature-billing && claude

# Merge branches when done
git merge feat/auth
git merge feat/billing
```## 补充工具

|工具|它有什么作用 |何时使用 |
|------|-------------|-------------|
| **DMUX** |代理的 tmux 窗格管理 |并行代理会话 |
| **超级组** |用于 10 多个并行代理的终端 IDE |大规模编排 |
| **克劳德代码任务工具** |进程内子代理生成 |会话内的编程并行性
| **Codex 多代理** |内置代理角色 |法典特定并行工作 |

## ECC 助手

ECC 现在包含一个用于使用单独的 git 工作树进行外部 tmux-pane 编排的帮助程序：```bash
node scripts/orchestrate-worktrees.js plan.json --execute
```示例 `plan.json`：```json
{
  "sessionName": "skill-audit",
  "baseRef": "HEAD",
  "launcherCommand": "codex exec --cwd {worktree_path} --task-file {task_file}",
  "workers": [
    { "name": "docs-a", "task": "Fix skills 1-4 and write handoff notes." },
    { "name": "docs-b", "task": "Fix skills 5-8 and write handoff notes." }
  ]
}
```帮手：
- 为每个工作人员创建一个分支支持的 git 工作树
- 可选择将主结帐中选定的“seedPaths”覆盖到每个工作人员工作树中
- 在“.orchestration/<session>/”下写入每个工作人员的“task.md”、“handoff.md”和“status.md”文件
- 启动 tmux 会话，每个工作人员一个窗格
- 在其自己的窗格中启动每个工作命令
- 为协调器保留主窗格

当工作人员需要访问尚未属于“HEAD”的脏或未跟踪的本地文件（例如本地编排脚本、草稿计划或文档）时，请使用“seedPaths”：```json
{
  "sessionName": "workflow-e2e",
  "seedPaths": [
    "scripts/orchestrate-worktrees.js",
    "scripts/lib/tmux-worktree-orchestrator.js",
    ".claude/plan/workflow-e2e-test.json"
  ],
  "launcherCommand": "bash {repo_root}/scripts/orchestrate-codex-worker.sh {task_file} {handoff_file} {status_file}",
  "workers": [
    { "name": "seed-check", "task": "Verify seeded files are present before starting work." }
  ]
}
```## 故障排除

- **窗格没有响应：** 直接切换到窗格或使用 `tmux capture-pane -pt <session>:0.<pane-index>` 检查它。
- **合并冲突：** 使用 git 工作树来隔离每个窗格的文件更改。
- **高令牌使用率：**减少并行窗格的数量。每个窗格都是一个完整的代理会话。
- **找不到 tmux：** 使用 `brew install tmux` (macOS) 或 `apt install tmux` (Linux) 安装。