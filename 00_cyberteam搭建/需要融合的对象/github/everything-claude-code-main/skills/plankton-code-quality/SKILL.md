# 浮游生物代码质量技能

Plankton 的集成参考（来源：@alxfazio），Claude Code 的写入时代码质量执行系统。 Plankton 通过 PostToolUse 挂钩在每个文件编辑上运行格式化程序和 linter，然后生成 Claude 子进程来修复代理未捕获的违规行为。

## 何时使用

- 您希望在每个文件编辑时自动格式化和检查（不仅仅是在提交时）
- 您需要防御代理修改 linter 配置以通过，而不是修复代码
- 您需要分层模型路由来修复（Haiku 用于简单风格，Sonnet 用于逻辑，Opus 用于类型）
- 您使用多种语言（Python、TypeScript、Shell、YAML、JSON、TOML、Markdown、Dockerfile）

## 它是如何工作的

### 三相架构

每次 Claude Code 编辑或写入文件时，Plankton 的 `multi_linter.sh` PostToolUse 挂钩都会运行：```
Phase 1: Auto-Format (Silent)
├─ Runs formatters (ruff format, biome, shfmt, taplo, markdownlint)
├─ Fixes 40-50% of issues silently
└─ No output to main agent

Phase 2: Collect Violations (JSON)
├─ Runs linters and collects unfixable violations
├─ Returns structured JSON: {line, column, code, message, linter}
└─ Still no output to main agent

Phase 3: Delegate + Verify
├─ Spawns claude -p subprocess with violations JSON
├─ Routes to model tier based on violation complexity:
│   ├─ Haiku: formatting, imports, style (E/W/F codes) — 120s timeout
│   ├─ Sonnet: complexity, refactoring (C901, PLR codes) — 300s timeout
│   └─ Opus: type system, deep reasoning (unresolved-attribute) — 600s timeout
├─ Re-runs Phase 1+2 to verify fixes
└─ Exit 0 if clean, Exit 2 if violations remain (reported to main agent)
```### 主要特工看到了什么

|场景|代理看到|钩出口 |
|----------|------------|------------|
|没有违规|什么都没有| 0 |
|全部由子进程修复|什么都没有| 0 |
|子流程后仍存在违规行为 | `[hook] 仍存在 N 次违规行为` | 2 |
|咨询（重复、旧工具）| `[挂钩：咨询] ...` | 0 |

主代理只能看到子流程无法修复的问题。大多数质量问题都能得到透明解决。

### 配置保护（防御规则游戏）

法学硕士将修改“.ruff.toml”或“biome.json”以禁用规则而不是修复代码。浮游生物通过三层来阻止这一点：

1. **PreToolUse hook** - `protect_linter_configs.sh` 在所有 linter 配置发生编辑之前阻止它们
2. **停止钩子** - `stop_config_guardian.sh` 在会话结束时通过 `git diff` 检测配置更改
3. **受保护文件列表** — `.ruff.toml`、`biome.json`、`.shellcheckrc`、`.yamllint`、`.hadolint.yaml` 等

### 包管理器执行

Bash 上的 PreToolUse 挂钩会阻止旧版包管理器：
- `pip`、`pip3`、`poetry`、`pipenv` → 被阻止（使用 `uv`）
- `npm`、`yarn`、`pnpm` → 被阻止（使用 `bun`）
- 允许的例外：`npmaudit`、`npmview`、`npmpublish`

## 设置

### 快速入门```bash
# Clone Plankton into your project (or a shared location)
# Note: Plankton is by @alxfazio
git clone https://github.com/alexfazio/plankton.git
cd plankton

# Install core dependencies
brew install jaq ruff uv

# Install Python linters
uv sync --all-extras

# Start Claude Code — hooks activate automatically
claude
```没有安装命令，没有插件配置。当您在 Plankton 目录中运行 Claude Code 时，会自动选取“.claude/settings.json”中的挂钩。

### 每个项目集成

要在您自己的项目中使用 Plankton hooks：

1. 将 `.claude/hooks/` 目录复制到您的项目中
2.复制`.claude/settings.json`钩子配置
3. 复制 linter 配置文件（`.ruff.toml`、`biome.json` 等）
4. 安装适合您的语言的 linter

### 特定于语言的依赖关系

|语言 |必填|可选|
|----------|----------|----------|
|蟒蛇 | `ruff`、`uv` | `ty`（类型）、`vulture`（死代码）、`bandit`（安全）|
| TypeScript/JS | `生物群落` | `oxlint`、`semgrep`、`knip` （死导出）|
|壳牌| `shellcheck`、`shfmt` | — |
| yaml | `yamllint` | — |
|降价| `markdownlint-cli2` | — |
| Dockerfile | `hadolint` (>= 2.12.0) | — |
| TOML | `塔普洛` | — |
| JSON | `贾克` | — |

## 与 ECC 配对

### 互补，不重叠

|关注| ECC |浮游生物 |
|---------|-----|----------|
|代码质量执行 | PostToolUse 挂钩（Prettier、tsc）| PostToolUse 挂钩（20 多个 linter + 子进程修复）|
|安全扫描| AgentShield，安全审查代理 | Bandit (Python)、Semgrep (TypeScript) |
|配置保护 | — | PreToolUse 块 + Stop hook 检测 |
|包管理器 |检测+设置|执行（阻止旧 PM）|
| CI 集成 | — | git 的预提交挂钩 |
|模型路由 |手册（`/model opus`）|自动（违规复杂性 → 层）|

### 推荐组合

1. 安装 ECC 作为您的插件（代理、技能、命令、规则）
2. 添加 Plankton 钩子以执行写入时质量
3、使用AgentShield进行安全审计
4. 使用 ECC 的验证循环作为 PR 之前的最后一道门

### 避免钩子冲突

如果同时运行 ECC 和 Plankton 钩子：
- ECC 的 Prettier 钩子和 Plankton 的生物群系格式化程序可能在 JS/TS 文件上发生冲突
- 解决方案：使用 Plankton 时禁用 ECC 的 Prettier PostToolUse 挂钩（Plankton 的生物群落更全面）
- 两者可以在不同的文件类型上共存（ECC 处理 Plankton 未涵盖的内容）

## 配置参考

Plankton 的 `.claude/hooks/config.json` 控制所有行为：```json
{
  "languages": {
    "python": true,
    "shell": true,
    "yaml": true,
    "json": true,
    "toml": true,
    "dockerfile": true,
    "markdown": true,
    "typescript": {
      "enabled": true,
      "js_runtime": "auto",
      "biome_nursery": "warn",
      "semgrep": true
    }
  },
  "phases": {
    "auto_format": true,
    "subprocess_delegation": true
  },
  "subprocess": {
    "tiers": {
      "haiku":  { "timeout": 120, "max_turns": 10 },
      "sonnet": { "timeout": 300, "max_turns": 10 },
      "opus":   { "timeout": 600, "max_turns": 15 }
    },
    "volume_threshold": 5
  }
}
```**关键设置：**
- 禁用您不使用的语言以加快挂钩速度
- `volume_threshold` — 违规 > 此计数自动升级到更高的模型层
- `subprocess_delegation: false` — 完全跳过第 3 阶段（仅报告违规行为）

## 环境覆盖

|变量|目的|
|----------|---------|
| `HOOK_SKIP_SUBPROCESS=1` |跳过第 3 阶段，直接举报违规行为 |
| `HOOK_SUBPROCESS_TIMEOUT=N` |覆盖层超时 |
| `HOOK_DEBUG_MODEL=1` |记录模型选择决策|
| `HOOK_SKIP_PM=1` |绕过包管理器强制执行 |

## 参考文献

- 浮游生物（来源：@alxfazio）
- Plankton REFERENCE.md — 完整的架构文档（来源：@alxfazio）
- Plankton SETUP.md — 详细安装指南（来源：@alxfazio）

## ECC v1.8 新增内容

### 可复制的钩子配置文件

制定严格的质量行为：```bash
export ECC_HOOK_PROFILE=strict
export ECC_QUALITY_GATE_FIX=true
export ECC_QUALITY_GATE_STRICT=true
```### 语言门表

- TypeScript/JavaScript：生物群系首选，Prettier 后备
- Python：Ruff 格式/检查
- 去：gofmt

### 配置防篡改

在质量实施期间，在同一迭代中标记对配置文件的更改：

- `biome.json`、`.eslintrc*`、`prettier.config*`、`tsconfig.json`、`pyproject.toml`

如果更改配置以抑制违规，则需要在合并之前进行明确审查。

### CI 集成模式

在 CI 中使用与本地挂钩相同的命令：

1. 运行格式化程序检查
2. 运行 lint/类型检查
3.严格模式下快速失败
4.发布整改总结

### 健康指标

曲目：
- 由门标记的编辑
- 平均修复时间
- 按类别重复违规
- 由于门故障而合并块