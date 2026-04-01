# Python 钩子

> 此文件使用 Python 特定内容扩展了常见的钩子规则。

## PostToolUse 挂钩

在`~/.claude/settings.json`中配置：

- **black/ruff**：编辑后自动格式化`.py`文件
- **mypy/pyright**：编辑`.py`文件后运行类型检查

## 警告

- 警告编辑文件中的“print()”语句（使用“logging”模块代替）