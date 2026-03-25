# 验证循环技巧

克劳德代码会话的综合验证系统。

## 何时使用

调用该技能：
- 完成功能或重大代码更改后
- 创建 PR 之前
- 当您想确保质量关卡通过时
- 重构后

## 验证阶段

### 第 1 阶段：构建验证```bash
# Check if project builds
npm run build 2>&1 | tail -20
# OR
pnpm build 2>&1 | tail -20
```如果构建失败，请停止并修复，然后再继续。

### 第 2 阶段：类型检查```bash
# TypeScript projects
npx tsc --noEmit 2>&1 | head -30

# Python projects
pyright . 2>&1 | head -30
```报告所有类型错误。在继续之前修复关键问题。

### 第 3 阶段：Lint 检查```bash
# JavaScript/TypeScript
npm run lint 2>&1 | head -30

# Python
ruff check . 2>&1 | head -30
```### 第 4 阶段：测试套件```bash
# Run tests with coverage
npm run test -- --coverage 2>&1 | tail -50

# Check coverage threshold
# Target: 80% minimum
```报告：
- 总测试：X
- 通过：X
- 失败：X
- 覆盖率：X%

### 第 5 阶段：安全扫描```bash
# Check for secrets
grep -rn "sk-" --include="*.ts" --include="*.js" . 2>/dev/null | head -10
grep -rn "api_key" --include="*.ts" --include="*.js" . 2>/dev/null | head -10

# Check for console.log
grep -rn "console.log" --include="*.ts" --include="*.tsx" src/ 2>/dev/null | head -10
```### 第 6 阶段：差异审查```bash
# Show what changed
git diff --stat
git diff HEAD~1 --name-only
```检查每个更改的文件：
- 意外的改变
- 缺少错误处理
- 潜在的边缘情况

## 输出格式

运行所有阶段后，生成验证报告：```
VERIFICATION REPORT
==================

Build:     [PASS/FAIL]
Types:     [PASS/FAIL] (X errors)
Lint:      [PASS/FAIL] (X warnings)
Tests:     [PASS/FAIL] (X/Y passed, Z% coverage)
Security:  [PASS/FAIL] (X issues)
Diff:      [X files changed]

Overall:   [READY/NOT READY] for PR

Issues to Fix:
1. ...
2. ...
```## 连续模式

对于长时间会话，每 15 分钟或在重大更改后运行验证：```markdown
Set a mental checkpoint:
- After completing each function
- After finishing a component
- Before moving to next task

Run: /verify
```## 与 Hook 集成

此技能补充了 PostToolUse 挂钩，但提供了更深入的验证。
Hooks 立即发现问题；该技能提供全面的审查。