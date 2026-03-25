# Codex CLI 的 ECC

这通过特定于 Codex 的指导补充了根“AGENTS.md”。

## 型号推荐

|任务类型 |推荐型号 |
|------------|--------------------|
|例行编码、测试、格式化 | GPT 5.4 |
|复杂的功能、架构 | GPT 5.4 |
|调试、重构 | GPT 5.4 |
|安全审查| GPT 5.4 |

## 技能发现

技能是从“.agents/skills/”自动加载的。每个技能包含：
- `SKILL.md` — 详细说明和工作流程
- `agents/openai.yaml` — Codex 接口元数据

可用技能：
- tdd-workflow — 测试驱动开发，覆盖率超过 80%
- security-review — 全面的安全检查表
-coding-standards——通用编码标准
- 前端模式 — React/Next.js 模式
- frontend-slides — 视口安全的 HTML 演示文稿和 PPTX 到 Web 的转换
- 文章写作——根据笔记和语音参考进行长篇写作
- 内容引擎——平台原生社交内容和再利用
- 市场研究——来源市场和竞争对手研究
- 投资者材料——幻灯片、备忘录、模型和单页纸
- 投资者外展——个性化的投资者外展和跟进
- 后端模式 — API 设计、数据库、缓存
- e2e-testing — Playwright E2E 测试
- eval-harness — Eval 驱动的开发
- 战略紧凑——上下文管理
- api-design — REST API 设计模式
- 验证循环——构建、测试、lint、类型检查、安全性
- 深度研究——Firecrawl 和 exa MCP 的多源研究
- exa-search — 通过 Exa MCP 对网络、代码和公司进行神经搜索
- claude-api — Anthropic Claude API 模式和 SDK
- x-api — 用于发布、话题和分析的 X/Twitter API 集成
- crosspost — 多平台内容分发
- fal-ai-media — 通过 fal.ai 生成 AI 图像/视频/音频
- dmux-workflows — 使用 dmux 进行多代理编排

## MCP 服务器

将项目本地“.codex/config.toml”视为 ECC 的默认 Codex 基线。当前的 ECC 基线支持 GitHub、Context7、Exa、Memory、Playwright 和 Sequential Thinking；仅当任务实际需要时才在“~/.codex/config.toml”中添加较重的额外内容。

## 多代理支持

Codex 现在支持实验性“features.multi_agent”标志背后的多代理工作流程。

- 在“.codex/config.toml”中使用“[features] multi_agent = true”启用它
- 在“[agents.<name>]”下定义项目本地角色
- 将每个角色指向 `.codex/agents/` 下的 TOML 层
- 在 Codex CLI 中使用 `/agent` 来检查和引导子代理

此存储库中的示例角色配置：
- `.codex/agents/explorer.toml` — 只读证据收集
- `.codex/agents/reviewer.toml` — 正确性/安全审查
- `.codex/agents/docs-researcher.toml` — API 和发行说明验证

## 与 Claude Code 的主要区别

|特色 |克劳德·代码 |法典 CLI |
|--------|------------|------------|
|挂钩| 8+ 事件类型 |尚不支持 |
|上下文文件 |克劳德.md + 代理.md |仅限 AGENTS.md |
|技能 |通过插件加载技能 | `.agents/skills/` 目录 |
|命令 | `/slash` 命令 |基于指令|
|代理|子代理任务工具 |通过 `/agent` 和 `[agents.<name>]` 角色进行多代理 |
|安全|基于钩子的执行 |指令+沙盒|
| MCP|全力支持 |通过 `config.toml` 和 `codex mcp add` 支持 |

## 没有钩子的安全性

由于 Codex 缺乏钩子，安全执行是基于指令的：
1. 始终在系统边界验证输入
2.永远不要对秘密进行硬编码——使用环境变量
3. 在提交之前运行`npmaudit`/`pipaudit`
4. 每次推送前查看`git diff`
5. 在配置中使用 `sandbox_mode = "workspace-write"`