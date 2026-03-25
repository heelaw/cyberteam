# 快速钩子

> 此文件使用 Swift 特定内容扩展了常见的 hooks 规则。

## PostToolUse 挂钩

在`~/.claude/settings.json`中配置：

- **SwiftFormat**：编辑后自动格式化`.swift`文件
- **SwiftLint**：编辑 `.swift` 文件后运行 lint 检查
- **快速构建**：编辑后对修改后的包进行类型检查

## 警告

标记 `print()` 语句——使用 `os.Logger` 或结构化日志记录代替生产代码。