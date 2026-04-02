# Perl 钩子

> 此文件使用 Perl 特定内容扩展了 [common/hooks.md](../common/hooks.md)。

## PostToolUse 挂钩

在`~/.claude/settings.json`中配置：

- **perltidy**：编辑后自动格式化`.pl`和`.pm`文件
- **perlcritic**：编辑 `.pm` 文件后运行 lint 检查

## 警告

- 警告非脚本 `.pm` 文件中的 `print` — 使用 `say` 或日志记录模块（例如，`Log::Any`）