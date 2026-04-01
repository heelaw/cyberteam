### 插件清单陷阱

如果您打算编辑 `.claude-plugin/plugin.json`，请注意 Claude 插件验证器会强制执行一些**未记录但严格的约束**，这些约束可能会导致安装失败并出现模糊错误（例如，`agents: Invalid input`）。特别是，组件字段必须是数组，“代理”必须使用显式文件路径而不是目录，并且需要“版本”字段来进行可靠的验证和安装。

从公开的例子来看，这些限制并不明显，并且在过去曾多次导致安装失败。它们详细记录在“.claude-plugin/PLUGIN_SCHEMA_NOTES.md”中，在对插件清单进行任何更改之前应进行审查。

### 自定义端点和网关

ECC 不会覆盖 Claude 代码传输设置。如果 Claude Code 配置为通过官方 LLM 网关或兼容的自定义端点运行，则该插件将继续工作，因为在 CLI 成功启动后，挂钩、命令和技能会在本地执行。

使用Claude Code自己的环境/配置进行传输选择，例如：```bash
export ANTHROPIC_BASE_URL=https://your-gateway.example.com
export ANTHROPIC_AUTH_TOKEN=your-token
claude
```