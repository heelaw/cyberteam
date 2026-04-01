# 钩子

> 该文件使用 Go 特定内容扩展了常见的 hooks 规则。

## PostToolUse 挂钩

在`~/.claude/settings.json`中配置：

- **gofmt/goimports**：编辑后自动格式化`.go`文件
- **go vet**：编辑`.go`文件后运行静态分析
- **staticcheck**：对修改后的包运行扩展静态检查