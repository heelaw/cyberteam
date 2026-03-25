# 爪命令

启动具有持久降价历史记录和操作控制的交互式 AI 代理会话。

＃＃ 用法```bash
node scripts/claw.js
```或者通过 npm：```bash
npm run claw
```## 环境变量

|变量|默认 |描述 |
|----------|---------|-------------|
| `CLAW_SESSION` | `默认` |会话名称（字母数字 + 连字符）|
| `爪子技能` | *（空）* |启动时加载逗号分隔的技能 |
| `CLAW_MODEL` | `十四行诗` |会话的默认模型 |

## REPL 命令```text
/help                          Show help
/clear                         Clear current session history
/history                       Print full conversation history
/sessions                      List saved sessions
/model [name]                  Show/set model
/load <skill-name>             Hot-load a skill into context
/branch <session-name>         Branch current session
/search <query>                Search query across sessions
/compact                       Compact old turns, keep recent context
/export <md|json|txt> [path]   Export session
/metrics                       Show session metrics
exit                           Quit
```## 注释

- NanoClaw 保持零依赖性。
- 会话存储在`~/.claude/claw/<session>.md`中。
- 压缩保留最近的回合并写入压缩标头。
- 导出支持markdown、JSON转和纯文本。