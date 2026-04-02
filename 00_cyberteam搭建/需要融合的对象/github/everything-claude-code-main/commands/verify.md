# 验证命令

对当前代码库状态运行全面验证。

## 说明

按以下顺序执行验证：

1. **构建检查**
   - 运行该项目的构建命令
   - 如果失败，报告错误并停止

2. **类型检查**
   - 运行 TypeScript/类型检查器
   - 使用 file:line 报告所有错误

3. **皮棉检查**
   - 运行短绒检查
   - 报告警告和错误

4. **测试套件**
   - 运行所有测试
   - 报告通过/失败计数
   - 报告覆盖率

5. **Console.log审核**
   - 在源文件中搜索console.log
   - 报告地点

6. **Git 状态**
   - 显示未提交的更改
   - 显示自上次提交以来修改的文件

## 输出

生成简明的验证报告：```
VERIFICATION: [PASS/FAIL]

Build:    [OK/FAIL]
Types:    [OK/X errors]
Lint:     [OK/X issues]
Tests:    [X/Y passed, Z% coverage]
Secrets:  [OK/X found]
Logs:     [OK/X console.logs]

Ready for PR: [YES/NO]
```如果有任何关键问题，请列出它们并附上修复建议。

## 参数

$ARGUMENTS 可以是：
- `quick` - 仅构建+类型
- `full` - 所有检查（默认）
- `pre-commit` - 检查提交的相关性
- `pre-pr` - 全面检查加上安全扫描