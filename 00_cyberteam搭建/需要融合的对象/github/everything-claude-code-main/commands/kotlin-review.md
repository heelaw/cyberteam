# Kotlin 代码审查

此命令调用 **kotlin-reviewer** 代理来进行全面的 Kotlin 特定代码审查。

## 该命令的作用

1. **识别 Kotlin 更改**：通过 `git diff` 查找修改后的 `.kt` 和 `.kts` 文件
2. **运行构建和静态分析**：执行`./gradlew build`、`detekt`、`ktlintCheck`
3. **安全扫描**：检查 SQL 注入、命令注入、硬编码机密
4. **空安全审查**：分析 `!!` 用法、平台类型处理、不安全强制转换
5. **协程审查**：检查结构化并发、调度程序使用、取消
6. **生成报告**：按严重程度对问题进行分类

## 何时使用

在以下情况下使用“/kotlin-review”：
- 编写或修改 Kotlin 代码后
- 在提交 Kotlin 更改之前
- 使用 Kotlin 代码审查拉取请求
- 加入新的 Kotlin 代码库
- 学习惯用的 Kotlin 模式

## 评论类别

### 严重（必须修复）
- SQL/命令注入漏洞
- 没有理由地强制解开`!!`
- 平台类型空安全违规
- GlobalScope 使用（结构化并发违规）
- 硬编码凭证
- 不安全的反序列化

### 高（应该修复）
- 不可变就足够的可变状态
- 阻止协程上下文内的调用
- 长循环中缺少取消检查
- 密封类型的非详尽“何时”
- 大型函数（>50 行）
- 深度嵌套（>4 层）

### 中（考虑）
- 非惯用的 Kotlin（Java 风格模式）
- 缺少尾随逗号
- 作用域函数误用或嵌套
- 大型收集链缺少序列
- 冗余显式类型

## 自动检查运行```bash
# Build check
./gradlew build

# Static analysis
./gradlew detekt

# Formatting check
./gradlew ktlintCheck

# Tests
./gradlew test
```## 用法示例````text
User: /kotlin-review

Agent:
# Kotlin Code Review Report

## Files Reviewed
- src/main/kotlin/com/example/service/UserService.kt (modified)
- src/main/kotlin/com/example/routes/UserRoutes.kt (modified)

## Static Analysis Results
✓ Build: Successful
✓ detekt: No issues
⚠ ktlint: 2 formatting warnings

## Issues Found

[CRITICAL] Force-Unwrap Null Safety
File: src/main/kotlin/com/example/service/UserService.kt:28
Issue: Using !! on nullable repository result
```科特林
val user = repository.findById(id)!!  // NPE风险```
Fix: Use safe call with error handling
```科特林
val 用户=repository.findById(id)
    ?: 抛出 UserNotFoundException("未找到用户 $id")```

[HIGH] GlobalScope Usage
File: src/main/kotlin/com/example/routes/UserRoutes.kt:45
Issue: Using GlobalScope breaks structured concurrency
```科特林
GlobalScope.launch {
    notificationService.sendWelcome（用户）
}```
Fix: Use the call's coroutine scope
```科特林
发射{
    notificationService.sendWelcome（用户）
}```

## Summary
- CRITICAL: 1
- HIGH: 1
- MEDIUM: 0

Recommendation: ❌ Block merge until CRITICAL issue is fixed
````

## 批准标准

|状态 |状况 |
|--------|------------|
| ✅ 批准 |没有严重或严重问题 |
| ⚠️警告|仅中等问题（谨慎合并）|
| ❌ 块 |发现严重或严重问题 |

## 与其他命令集成

- 首先使用 `/kotlin-test` 确保测试通过
- 如果发生构建错误，请使用“/kotlin-build”
- 提交前使用 `/kotlin-review`
- 对于非 Kotlin 特定的问题使用“/code-review”

## 相关

- 代理：`agents/kotlin-reviewer.md`
- 技能：`技能/kotlin-patterns/`、`技能/kotlin-testing/`