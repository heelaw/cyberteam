# 代币优化指南

实用的设置和习惯可减少令牌消耗、提高会话质量并在每日限制内完成更多工作。

> 另请参阅：“rules/common/performance.md”用于模型选择策略，“skills/strategic-compact/”用于自动压缩建议。

---

## 推荐设置

这些是为大多数用户推荐的默认值。高级用户可以根据其工作负载进一步调整值 - 例如，为简单任务设置较低的“MAX_THINKING_TOKENS”，或为复杂的架构工作设置较高的值。

添加到您的“~/.claude/settings.json”：```json
{
  "model": "sonnet",
  "env": {
    "MAX_THINKING_TOKENS": "10000",
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "50",
    "CLAUDE_CODE_SUBAGENT_MODEL": "haiku"
  }
}
```### 每个设置的作用

|设置|默认 |推荐|效果|
|--------|---------|-------------|--------|
| `模型` |作品 | **十四行诗** | Sonnet 可以很好地处理约 80% 的编码任务。使用“/model opus”切换到 Opus 以进行复杂的推理。成本降低约 60%。 |
| `MAX_THINKING_TOKENS` | 31,999 | 31,999 **10,000** |扩展思维为每个请求保留最多 31,999 个输出令牌用于内部推理。减少这一点可将隐性成本降低约 70%。设置为“0”以禁用简单任务。 |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | 95 | 95 **50** |当上下文达到容量的这个百分比时，自动压缩就会触发。默认 95% 已经太晚了——在此之前质量就会下降。压缩到 50% 可以让训练更健康。 |
| `CLAUDE_CODE_SUBAGENT_MODEL` | _（继承主函数）_ | **俳句** |子代理（任务工具）在此模型上运行。 Haiku 便宜约 80%，足以用于探索、文件读取和测试运行。 |

### 切换扩展思维

- **Alt+T** (Windows/Linux) 或 **Option+T** (macOS) — 切换开/关
- **Ctrl+O** — 查看思考输出（详细模式）

---

## 型号选择

使用正确的模型来完成任务：

|型号|最适合 |成本|
|--------|----------|------|
| **俳句** |子代理探索、文件读取、简单查找 |最低|
| **十四行诗** |日常编码、评审、测试编写、实施 |中等|
| **作品** |复杂架构，多步推理，调试微妙问题 |最高|

会话中切换模型：```
/model sonnet     # default for most work
/model opus       # complex reasoning
/model haiku      # quick lookups
```---

## 上下文管理

### 命令

|命令 |何时使用 |
|---------|-------------|
| `/清除` |在不相关的任务之间。过时的上下文会在每个后续消息上浪费令牌。 |
| `/紧凑` |在逻辑任务断点处（计划之后、调试之后、切换焦点之前）。 |
| `/成本` |检查当前会话的令牌支出。 |

### 战略压实

“strategic-compact”技能（在“skills/strategic-compact/”中）建议按逻辑间隔使用“/compact”，而不是依赖自动压缩，因为自动压缩会触发任务中途。有关挂钩设置说明，请参阅技能的自述文件。

**何时压缩：**
- 探索之后，实施之前
- 完成一个里程碑后
- 调试后，继续新工作之前
- 在重大环境转变之前

**何时不压缩：**
- 相关变更的实施中期
- 调试活跃问题时
- 多文件重构期间

### 子代理保护您的上下文

使用子代理（任务工具）进行探索，而不是在主会话中读取许多文件。子代理读取 20 个文件，但仅返回摘要 - 您的主要上下文保持干净。

---

## MCP 服务器管理

每个启用的 MCP 服务器都会将工具定义添加到您的上下文窗口中。自述文件警告：**每个项目启用的数量保持在 10 以下**。

温馨提示：
- 运行“/mcp”以查看活动服务器及其上下文成本
- 首选 CLI 工具（如果可用）（“gh”而不是 GitHub MCP，“aws”而不是 AWS MCP）
- 在项目配置中使用“disabledMcpServers”来禁用每个项目的服务器
- “内存”MCP 服务器是默认配置的，但不被任何技能、代理或挂钩使用 - 考虑禁用它

---

## 代理团队成本警告

[Agent Teams](https://code.claude.com/docs/en/agent-teams)（实验性）生成多个独立的上下文窗口。每个队友单独消耗代币。

- 仅用于并行性增加明显价值的任务（多模块工作、并行审查）
- 对于简单的顺序任务，子代理（任务工具）更具令牌效率
- 启用：设置中的“CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1”

---

## 未来：configure-ecc 集成

“configure-ecc”安装向导可以在安装过程中设置这些环境变量，并解释成本权衡。这将帮助新用户从第一天开始进行优化，而不是在达到限制后才发现这些设置。

---

## 快速参考```bash
# Daily workflow
/model sonnet              # Start here
/model opus                # Only for complex reasoning
/clear                     # Between unrelated tasks
/compact                   # At logical breakpoints
/cost                      # Check spending

# Environment variables (add to ~/.claude/settings.json "env" block)
MAX_THINKING_TOKENS=10000
CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=50
CLAUDE_CODE_SUBAGENT_MODEL=haiku
CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```