# Java 钩子

> 此文件使用 Java 特定内容扩展了 [common/hooks.md](../common/hooks.md)。

## PostToolUse 挂钩

在`~/.claude/settings.json`中配置：

- **google-java-format**：编辑后自动格式化`.java`文件
- **checkstyle**：编辑 Java 文件后运行样式检查
- **./mvnwcompile**或**./gradlewcompileJava**：更改后验证编译