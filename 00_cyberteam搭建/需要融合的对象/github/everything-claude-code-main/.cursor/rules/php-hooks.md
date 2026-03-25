# PHP 钩子

> 该文件使用 PHP 特定内容扩展了常见的钩子规则。

## PostToolUse 挂钩

在`~/.claude/settings.json`中配置：

- **Pint / PHP-CS-Fixer**：自动格式化编辑后的“.php”文件。
- **PHPStan / Psalm**：在类型化代码库中编辑 PHP 后运行静态分析。
- **PHPUnit / Pest**：当编辑影响行为时，对所触及的文件或模块运行有针对性的测试。

## 警告

- 对编辑文件中残留的“var_dump”、“dd”、“dump”或“die()”发出警告。
- 当编辑的 PHP 文件添加原始 SQL 或禁用 CSRF/会话保护时发出警告。