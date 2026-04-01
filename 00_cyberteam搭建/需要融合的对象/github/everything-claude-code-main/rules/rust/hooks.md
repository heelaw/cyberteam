# 生锈钩子

> 此文件使用 Rust 特定的内容扩展了 [common/hooks.md](../common/hooks.md)。

## PostToolUse 挂钩

在`~/.claude/settings.json`中配置：

- **cargo fmt**：编辑后自动格式化`.rs`文件
- **cargo Clippy**：编辑 Rust 文件后运行 lint 检查
- **cargo check**：验证更改后的编译（比 `cargo build` 更快）