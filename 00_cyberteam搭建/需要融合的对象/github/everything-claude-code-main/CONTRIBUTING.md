# 为所有克劳德代码做出贡献

感谢您愿意贡献！此存储库是 Claude Code 用户的社区资源。

## 目录

- [我们在寻找什么](#what-were-looking-for)
- [快速启动](#quick-start)
- [贡献技能](#contributing-skills)
- [贡献代理](#contributing-agents)
- [贡献 Hooks](#contributing-hooks)
- [贡献命令](#contributing-commands)
- [MCP 和文档（例如 Context7）](#mcp-and-documentation-eg-context7)
- [交叉线束和翻译](#cross-harness-and-translations)
- [拉请求流程](#pull-request-process)

---

## 我们正在寻找什么

### 代理
能够很好地处理特定任务的新代理：
- 特定语言的审阅者（Python、Go、Rust）
- 框架专家（Django、Rails、Laravel、Spring）
- DevOps 专家（Kubernetes、Terraform、CI/CD）
- 领域专家（机器学习管道、数据工程、移动）

### 技能
工作流程定义和领域知识：
- 语言最佳实践
- 框架模式
- 测试策略
- 架构指南

### 挂钩
有用的自动化：
- 绒毛/格式化挂钩
- 安全检查
- 验证挂钩
- 通知挂钩

### 命令
调用有用工作流程的斜线命令：
- 部署命令
- 测试命令
- 代码生成命令

---

## 快速入门```bash
# 1. Fork and clone
gh repo fork affaan-m/everything-claude-code --clone
cd everything-claude-code

# 2. Create a branch
git checkout -b feat/my-contribution

# 3. Add your contribution (see sections below)

# 4. Test locally
cp -r skills/my-skill ~/.claude/skills/  # for skills
# Then test with Claude Code

# 5. Submit PR
git add . && git commit -m "feat: add my-skill" && git push -u origin feat/my-contribution
```---

## 贡献技能

技能是 Claude Code 根据上下文加载的知识模块。

### 目录结构```
skills/
└── your-skill-name/
    └── SKILL.md
```### SKILL.md 模板```markdown
---
name: your-skill-name
description: Brief description shown in skill list
origin: ECC
---

# Your Skill Title

Brief overview of what this skill covers.

## Core Concepts

Explain key patterns and guidelines.

## Code Examples

\`\`\`typescript
// Include practical, tested examples
function example() {
  // Well-commented code
}
\`\`\`

## Best Practices

- Actionable guidelines
- Do's and don'ts
- Common pitfalls to avoid

## When to Use

Describe scenarios where this skill applies.
```### 技能清单

- [ ] 专注于一个领域/技术
- [ ] 包括实际的代码示例
- [ ] 500行以下
- [ ] 使用清晰的节标题
- [ ] 使用 Claude 代码进行测试

### 技能示例

|技能|目的|
|--------|---------|
| `编码标准/` | TypeScript/JavaScript 模式 |
| `前端模式/` | React 和 Next.js 最佳实践 |
| `后端模式/` | API 和数据库模式 |
| `安全审查/` |安全检查表 |

---

## 特约代理

代理是通过任务工具调用的专业助手。

### 文件位置```
agents/your-agent-name.md
```### 代理模板```markdown
---
name: your-agent-name
description: What this agent does and when Claude should invoke it. Be specific!
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
model: sonnet
---

You are a [role] specialist.

## Your Role

- Primary responsibility
- Secondary responsibility
- What you DO NOT do (boundaries)

## Workflow

### Step 1: Understand
How you approach the task.

### Step 2: Execute
How you perform the work.

### Step 3: Verify
How you validate results.

## Output Format

What you return to the user.

## Examples

### Example: [Scenario]
Input: [what user provides]
Action: [what you do]
Output: [what you return]
```### 代理字段

|领域|描述 |选项|
|--------|-------------|---------|
| `名称` |小写，连字符 | `代码审阅者` |
| `描述` |用于决定何时调用 |具体一点！ |
| `工具` |只提供所需的 |当代理使用 MCP | 时，“Read、Write、Edit、Bash、Grep、Glob、WebFetch、Task”或 MCP 工具名称（例如“mcp__context7__resolve-library-id”、“mcp__context7__query-docs”）
| `模型` |复杂程度| `haiku`（简单）、`sonnet`（编码）、`opus`（复杂）|

### 代理示例

|代理|目的|
|--------|---------|
| `tdd-guide.md` |测试驱动开发 |
| `code-reviewer.md` |代码审查 |
| `security-reviewer.md` |安全扫描|
| `build-error-resolver.md` |修复构建错误 |

---

## 贡献 Hook

挂钩是由 Claude Code 事件触发的自动行为。

### 文件位置```
hooks/hooks.json
```### 钩子类型

|类型 |触发|使用案例|
|------|---------|----------|
| `PreToolUse` |工具运行之前 |验证、警告、阻止 |
| `PostToolUse` |工具运行后 |格式化、检查、通知 |
| `会话开始` |会议开始 |加载上下文 |
| `停止` |会议结束 |清理、审核|

### 挂钩格式```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "tool == \"Bash\" && tool_input.command matches \"rm -rf /\"",
        "hooks": [
          {
            "type": "command",
            "command": "echo '[Hook] BLOCKED: Dangerous command' && exit 1"
          }
        ],
        "description": "Block dangerous rm commands"
      }
    ]
  }
}
```### 匹配器语法```javascript
// Match specific tools
tool == "Bash"
tool == "Edit"
tool == "Write"

// Match input patterns
tool_input.command matches "npm install"
tool_input.file_path matches "\\.tsx?$"

// Combine conditions
tool == "Bash" && tool_input.command matches "git push"
```### 钩子示例```json
// Block dev servers outside tmux
{
  "matcher": "tool == \"Bash\" && tool_input.command matches \"npm run dev\"",
  "hooks": [{"type": "command", "command": "echo 'Use tmux for dev servers' && exit 1"}],
  "description": "Ensure dev servers run in tmux"
}

// Auto-format after editing TypeScript
{
  "matcher": "tool == \"Edit\" && tool_input.file_path matches \"\\.tsx?$\"",
  "hooks": [{"type": "command", "command": "npx prettier --write \"$file_path\""}],
  "description": "Format TypeScript files after edit"
}

// Warn before git push
{
  "matcher": "tool == \"Bash\" && tool_input.command matches \"git push\"",
  "hooks": [{"type": "command", "command": "echo '[Hook] Review changes before pushing'"}],
  "description": "Reminder to review before push"
}
```### 钩子清单

- [ ] 匹配器是特定的（不是过于宽泛）
- [ ] 包括明确的错误/信息消息
- [ ] 使用正确的退出代码（`exit 1` 阻止，`exit 0` 允许）
- [ ] 彻底测试
- [ ] 有说明

---

## 贡献命令

命令是用户通过“/command-name”调用的操作。

### 文件位置```
commands/your-command.md
```### 命令模板```markdown
---
description: Brief description shown in /help
---

# Command Name

## Purpose

What this command does.

## Usage

\`\`\`
/your-command [args]
\`\`\`

## Workflow

1. First step
2. Second step
3. Final step

## Output

What the user receives.
```### 命令示例

|命令 |目的|
|---------|---------|
| `commit.md` |创建 git 提交 |
| `代码审查.md` |查看代码更改 |
| `tdd.md` | TDD 工作流程 |
| `e2e.md` |端到端测试|

---

## MCP 和文档（例如 Context7）

技能和代理可以使用 **MCP（模型上下文协议）** 工具来提取最新数据，而不是仅依赖训练数据。这对于文档特别有用。

- **Context7** 是一个公开 `resolve-library-id` 和 `query-docs` 的 MCP 服务器。当用户询问库、框架或 API 时使用它，以便答案反映当前的文档和代码示例。
- 当贡献依赖于实时文档的**技能**（例如设置、API 使用）时，描述如何使用相关的 MCP 工具（例如解析库 ID，然后查询文档）并指出“文档查找”技能或 Context7 作为模式。
- 在贡献回答文档/API 问题的 **代理** 时，请在代理工具中包含 Context7 MCP 工具名称（例如 `mcp__context7__resolve-library-id`、`mcp__context7__query-docs`）并记录解析 → 查询工作流程。
- **mcp-configs/mcp-servers.json** 包含 Context7 条目；用户在他们的工具（例如 Claude Code、Cursor）中启用它以使用文档查找技能（在“skills/documentation-lookup/”中）和“/docs”命​​令。

---

## 交叉利用和翻译

### 技能子集（Codex 和 Cursor）

ECC 为其他安全带提供了技能子集：

- **Codex:** `.agents/skills/` — `agents/openai.yaml` 中列出的技能由 Codex 加载。
- **Cursor:** `.cursor/skills/` — 技能的子集与 Cursor 捆绑在一起。

当您**添加应在 Codex 或 Cursor 上可用的新技能**时：

1. 像平常一样在`skills/your-skill-name/`下添加技能。
2. 如果它应该在 **Codex** 上可用，请将其添加到 `.agents/skills/` （复制技能目录或添加引用），并确保在需要时在 `agents/openai.yaml` 中引用它。
3. 如果它应该在 **Cursor** 上可用，请根据 Cursor 的布局将其添加到 `.cursor/skills/` 下。

检查这些目录中的现有技能是否符合预期结构。保持这些子集同步是手动的；如果您更新了它们，请在您的 PR 中提及。

### 翻译

翻译位于“docs/”下（例如“docs/zh-CN”、“docs/zh-TW”、“docs/ja-JP”）。如果您更改已翻译的代理、命令或技能，请考虑更新相应的翻译文件或提出问题，以便维护人员或翻译人员可以更新它们。

---

## 拉取请求流程

### 1. PR 标题格式```
feat(skills): add rust-patterns skill
feat(agents): add api-designer agent
feat(hooks): add auto-format hook
fix(skills): update React patterns
docs: improve contributing guide
```### 2.公关说明```markdown
## Summary
What you're adding and why.

## Type
- [ ] Skill
- [ ] Agent
- [ ] Hook
- [ ] Command

## Testing
How you tested this.

## Checklist
- [ ] Follows format guidelines
- [ ] Tested with Claude Code
- [ ] No sensitive info (API keys, paths)
- [ ] Clear descriptions
```### 3. 审核流程

1.维护者48小时内审核
2. 根据要求处理反馈
3. 审核通过后，合并到main

---

## 指南

### 做
- 保持贡献的针对性和模块化
- 包括清晰的描述
- 提交前测试
- 遵循现有模式
- 文档依赖关系

### 不要
- 包括敏感数据（API 密钥、令牌、路径）
- 添加过于复杂或小众的配置
- 提交未经测试的贡献
- 创建现有功能的副本

---

## 文件命名

- 使用小写字母和连字符：`python-reviewer.md`
- 具有描述性：“tdd-workflow.md”而不是“workflow.md”
- 将名称与文件名匹配

---

## 有问题吗？

- **问题：** [github.com/affaan-m/everything-claude-code/issues](https://github.com/affaan-m/everything-claude-code/issues)
- **X/Twitter：** [@affaanmustafa](https://x.com/affaanmustafa)

---

感谢您的贡献！让我们一起构建一个伟大的资源。