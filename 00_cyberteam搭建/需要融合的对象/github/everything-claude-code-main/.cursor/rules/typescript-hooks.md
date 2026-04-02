# TypeScript/JavaScript 挂钩

> 此文件使用 TypeScript/JavaScript 特定内容扩展了常见的钩子规则。

## PostToolUse 挂钩

在`~/.claude/settings.json`中配置：

- **Prettier**：编辑后自动格式化 JS/TS 文件
- **TypeScript 检查**：编辑 `.ts`/`.tsx` 文件后运行 `tsc`
- **console.log警告**：警告编辑文件中的“console.log”

## 停止钩子

- **console.log 审核**：在会话结束之前检查所有修改的文件中的 `console.log`