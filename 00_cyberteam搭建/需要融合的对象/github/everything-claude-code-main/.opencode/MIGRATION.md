# 迁移指南：Claude Code 到 OpenCode

本指南可帮助您在使用 Everything Claude Code (ECC) 配置时从 Claude Code 迁移到 OpenCode。

## 概述

OpenCode 是用于 AI 辅助开发的替代 CLI，支持与 Claude Code 的**所有**相同功能，但配置格式存在一些差异。

## Key Differences

|特色 |克劳德·代码 |开放代码 |笔记|
|--------|-------------|----------|--------|
|配置| `CLAUDE.md`、`plugin.json` | `opencode.json` |不同的文件格式|
|代理| Markdown 前言 | JSON 对象 |完全平价|
|命令 | `命令/*.md` | `command` 对象或 `.md` 文件 |完全平价|
|技能 | `技能/*/SKILL.md` | `指令`数组 |加载为上下文 |
| **挂钩** | `hooks.json`（3 个阶段）| **插件系统（20+ 事件）** | **完全平价+更多！** |
|规则| `规则/*.md` | `指令`数组 |合并还是单独|
| MCP|全力支持 | Full support |完全平价|

## 钩子迁移

**OpenCode 通过其插件系统完全支持钩子**，这实际上比拥有 20 多种事件类型的 Claude Code 更复杂。

### 挂钩事件映射

|克劳德·代码胡克 | OpenCode 插件活动 |笔记|
|------------------|----------------------------------|--------|
| `PreToolUse` | `工具.执行.之前` | Can modify tool input |
| `PostToolUse` | `工具.执行后` |可以修改工具输出 |
| `停止` | `session.idle` 或 `session.status` |会话生命周期 |
| `会话开始` | `会话.创建` |会议开始 |
| `会话结束` | `会话.已删除` |会议结束 |
|不适用 | `文件.编辑` |仅限 OpenCode：文件更改 |
|不适用 | `file.watcher.updated` |仅限 OpenCode：文件系统监视 |
|不适用 | `消息.更新` |仅限 OpenCode：消息更改 |
|不适用 | `lsp.client.diagnostics` |仅限 OpenCode：LSP 集成 |
|不适用 | `tui.toast.show` |仅限 OpenCode：通知 |

### 将 Hook 转换为插件

**克劳德代码钩子（hooks.json）：**```json
{
  "PostToolUse": [{
    "matcher": "tool == \"Edit\" && tool_input.file_path matches \"\\\\.(ts|tsx|js|jsx)$\"",
    "hooks": [{
      "type": "command",
      "command": "prettier --write \"$file_path\""
    }]
  }]
}
```**OpenCode 插件 (.opencode/plugins/prettier-hook.ts):**```typescript
export const PrettierPlugin = async ({ $ }) => {
  return {
    "file.edited": async (event) => {
      if (event.path.match(/\.(ts|tsx|js|jsx)$/)) {
        await $`prettier --write ${event.path}`
      }
    }
  }
}
```### 包含 ECC 插件挂钩

ECC OpenCode 配置包括翻译后的挂钩：

|钩|开放代码活动 |目的|
|------|----------------|---------|
|更漂亮的自动格式 | `文件.编辑` |编辑后格式化 JS/TS 文件 |
| TypeScript 检查 | `工具.执行后` |编辑 .ts 文件后运行 tsc |
| console.log 警告 | `文件.编辑` |关于 console.log 语句的警告 |
|会议通知 | `会话.空闲` |任务完成时通知 |
|安检| `工具.执行.之前` |提交前检查机密 |

## 迁移步骤

### 1.安装OpenCode```bash
# Install OpenCode CLI
npm install -g opencode
# or
curl -fsSL https://opencode.ai/install | bash
```### 2. 使用 ECC OpenCode 配置

此存储库中的“.opencode/”目录包含翻译后的配置：```
.opencode/
├── opencode.json              # Main configuration
├── plugins/                   # Hook plugins (translated from hooks.json)
│   ├── ecc-hooks.ts           # All ECC hooks as plugins
│   └── index.ts               # Plugin exports
├── tools/                     # Custom tools
│   ├── run-tests.ts           # Run test suite
│   ├── check-coverage.ts      # Check coverage
│   └── security-audit.ts      # npm audit wrapper
├── commands/                  # All 23 commands (markdown)
│   ├── plan.md
│   ├── tdd.md
│   └── ... (21 more)
├── prompts/
│   └── agents/                # Agent prompt files (12)
├── instructions/
│   └── INSTRUCTIONS.md        # Consolidated rules
├── package.json               # For npm distribution
├── tsconfig.json              # TypeScript config
└── MIGRATION.md               # This file
```### 3. Run OpenCode```bash
# In the repository root
opencode

# The configuration is automatically detected from .opencode/opencode.json
```## 概念图

### 代理

**克劳德代码：**```markdown
---
name: planner
description: Expert planning specialist...
tools: ["Read", "Grep", "Glob"]
model: opus
---

You are an expert planning specialist...
```**开放代码：**```json
{
  "agent": {
    "planner": {
      "description": "Expert planning specialist...",
      "mode": "subagent",
      "model": "anthropic/claude-opus-4-5",
      "prompt": "{file:prompts/agents/planner.txt}",
      "tools": { "read": true, "bash": true }
    }
  }
}
```### 命令

**克劳德代码：**```markdown
---
name: plan
description: Create implementation plan
---

Create a detailed implementation plan for: {input}
```**开放代码 (JSON)：**```json
{
  "command": {
    "plan": {
      "description": "Create implementation plan",
      "template": "Create a detailed implementation plan for: $ARGUMENTS",
      "agent": "planner"
    }
  }
}
```**OpenCode（Markdown - .opencode/commands/plan.md）：**```markdown
---
description: Create implementation plan
agent: planner
---

Create a detailed implementation plan for: $ARGUMENTS
```### 技能

**克劳德代码：** 技能是从 `skills/*/SKILL.md` 文件加载的。

**OpenCode：** 技能被添加到`instructions`数组中：```json
{
  "instructions": [
    "skills/tdd-workflow/SKILL.md",
    "skills/security-review/SKILL.md",
    "skills/coding-standards/SKILL.md"
  ]
}
```### 规则

**Claude Code：** 规则位于单独的 `rules/*.md` 文件中。

**OpenCode：** 规则可以合并为“指令”或单独保存：```json
{
  "instructions": [
    "instructions/INSTRUCTIONS.md",
    "rules/common/security.md",
    "rules/common/coding-style.md"
  ]
}
```## 模型映射

|克劳德·代码 |开放代码 |
|----------|----------|
| `作品` | `人类/克劳德-opus-4-5` |
| `十四行诗` | `人类/克劳德-十四行诗-4-5` |
| ‘俳句’ | `人类/claude-haiku-4-5` |

## 可用命令

迁移后，所有 23 个命令都可用：

|命令 |描述 |
|---------|-------------|
| `/计划` |制定实施计划 |
| `/tdd` |实施 TDD 工作流程 |
| `/代码审查` |查看代码更改 |
| `/安全` |运行安全审查 |
| `/构建修复` |修复构建错误 |
| `/e2e` |生成 E2E 测试 |
| `/refactor-clean` |删除死代码 |
| `/编排` |多代理工作流程 |
| `/学习` |会议中提取模式 |
| `/检查点` |保存验证状态 |
| `/验证` |运行验证循环 |
| `/评估` |运行评估 |
| `/更新文档` |更新文档 |
| `/更新代码映射` |更新代码图 |
| `/测试覆盖率` |检查测试覆盖率 |
| `/setup-pm` |配置包管理器 |
| `/去评论` |进行代码审查 |
| `/去测试` |采用 TDD 工作流程 |
| `/go-build` |修复 Go 构建错误 |
| `/技能创建` |从 git 历史生成技能 |
| `/本能状态` |查看习得的本能 |
| `/本能导入` |进口本能|
| `/本能导出` |出口本能|
| `/进化` |将本能凝聚成技能 |
| `/推广` |将项目本能提升到全球范围 |
| `/项目` |列出已知项目和本能统计数据 |

## 可用代理

|代理|描述 |
|--------|-------------|
| `计划者` |实施规划|
| `建筑师` |系统设计|
| `代码审阅者` |代码审查 |
| `安全审查员` |证券分析|
| `tdd 指南` |测试驱动开发 |
| `构建错误解析器` |修复构建错误 |
| `e2e-runner` |端到端测试|
| `文档更新程序` |文档 |
| `重构清理器` |死代码清理 |
| `去审阅者` |进行代码审查 |
| `go-build-resolver` |去构建错误|
| `数据库审阅者` |数据库优化 |

## 插件安装

### 选项 1：直接使用 ECC 配置

`.opencode/` 目录包含预先配置的所有内容。

### 选项 2：安装为 npm 包```bash
npm install ecc-universal
```然后在你的`opencode.json`中：```json
{
  "plugin": ["ecc-universal"]
}
```This only loads the published ECC OpenCode plugin module (hooks/events and exported plugin tools).
It does **not** automatically inject ECC's full `agent`, `command`, or `instructions` config into your project.

如果您想要完整的 ECC OpenCode 工作流程界面，请使用存储库捆绑的“.opencode/opencode.json”作为您的基本配置或将这些部分复制到您的项目中：
- `.opencode/命令/`
- `.opencode/提示/`
- `.opencode/instructions/INSTRUCTIONS.md`
- the `agent` and `command` sections from `.opencode/opencode.json`

## 故障排除

### 配置未加载

1. 验证存储库根目录中是否存在`.opencode/opencode.json`
2. 检查 JSON 语法是否有效：`cat .opencode/opencode.json | jq。`
3. 确保所有引用的提示文件都存在

### 插件未加载

1.验证`.opencode/plugins/`中是否存在插件文件
2. 检查 TypeScript 语法是否有效
3. 确保 `opencode.json` 中的 `plugin` 数组包含路径

### 未找到代理

1. 检查“agent”对象下的“opencode.json”中是否定义了代理
2.验证提示文件路径是否正确
3.确保指定路径存在提示文件

### 命令不起作用

1. 验证命令是在 `opencode.json` 中定义的还是在 `.opencode/commands/` 中定义为 `.md` 文件
2. 检查引用的代理是否存在
3. 确保模板使用 `$ARGUMENTS` 进行用户输入
4. 如果您仅安装了 `plugin: ["ecc-universal"]`，请注意 npm 插件安装不会自动将 ECC 命令或代理添加到您的项目配置中

## 最佳实践

1. **重新开始**：不要尝试同时运行 Claude Code 和 OpenCode
2. **检查配置**：验证`opencode.json`加载没有错误
3. **测试命令**：运行每个命令一次以验证其是否有效
4. **使用插件**：利用插件挂钩实现自动化
5. **使用代理**：利用专门的代理来实现其预期目的

## 恢复克劳德代码

如果需要切换回来：

1. 只需运行 `claude` 而不是 `opencode`
2. Claude Code将使用自己的配置（`CLAUDE.md`、`plugin.json`等）
3.`.opencode/`目录不会干扰Claude Code

## 功能对比总结

|特色 |克劳德·代码 |开放代码 |状态 |
|--------|-------------|----------|--------|
|代理| ✅ 12 名代理人 | ✅ 12 名代理人 | **完全平价** |
|命令 | ✅ 23 个命令 | ✅ 23 个命令 | **完全平价** |
|技能 | ✅ 16 项技能 | ✅ 16 项技能 | **完全平价** |
|挂钩| ✅ 3 阶段 | ✅ 20+ 活动 | **OpenCode 有更多** |
|规则| ✅ 8 条规则 | ✅ 8 条规则 | **完全平价** |
| MCP 服务器 | ✅ 满 | ✅ 满 | **完全平价** |
|定制工具| ✅ 通过挂钩 | ✅ 原生支持 | **OpenCode 更好** |

## 反馈

对于特定问题：
- **OpenCode CLI**：向 OpenCode 的问题跟踪器报告
- **ECC 配置**：报告给 [github.com/affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code)