# Kotlin 构建和修复

此命令调用 **kotlin-build-resolver** 代理，以最小的更改增量修复 Kotlin 构建错误。

## 该命令的作用

1. **运行诊断**：执行`./gradlew build`、`detekt`、`ktlintCheck`
2. **解析错误**：按文件分组并按严重性排序
3. **增量修复**：一次一个错误
4. **验证每个修复**：每次更改后重新运行构建
5. **报告摘要**：显示已修复的内容和剩余的内容

## 何时使用

在以下情况下使用 `/kotlin-build`：
- `./gradlew build` 失败并出现错误
- Kotlin 编译器报告错误
- `./gradlew detekt` 报告违规行为
- Gradle依赖解析失败
- 拉取破坏构建的更改后

## 诊断命令运行```bash
# Primary build check
./gradlew build 2>&1

# Static analysis
./gradlew detekt 2>&1 || echo "detekt not configured"
./gradlew ktlintCheck 2>&1 || echo "ktlint not configured"

# Dependency issues
./gradlew dependencies --configuration runtimeClasspath 2>&1 | head -100

# Optional deep refresh when caches or dependency metadata are suspect
./gradlew build --refresh-dependencies
```## 会话示例````text
User: /kotlin-build

Agent:
# Kotlin Build Resolution

## Initial Diagnostics

```巴什
$ ./gradlew 构建
e: src/main/kotlin/com/example/service/UserService.kt:25:15 未解析的参考：UserRepository
e: src/main/kotlin/com/example/routes/UserRoutes.kt:42:9 类型不匹配：推断类型为 String 但预期为 Int
e: src/main/kotlin/com/example/routes/UserRoutes.kt:58:5 'when' 表达式必须详尽```

Errors found: 3

## Fix 1: Unresolved Reference

File: src/main/kotlin/com/example/service/UserService.kt:25
Error: Unresolved reference: UserRepository
Cause: Missing import

```科特林
// 添加导入
导入 com.example.repository.UserRepository```

```巴什
$ ./gradlew 构建
# 剩余 2 个错误```

## Fix 2: Type Mismatch

File: src/main/kotlin/com/example/routes/UserRoutes.kt:42
Error: Type mismatch: inferred type is String but Int was expected

```科特林
// 改变了
val count = call.parameters["count"]
// 至
val count = call.parameters["count"]?.toIntOrNull()
    ?: return@get call.respond(HttpStatusCode.BadRequest, "无效计数")```

```巴什
$ ./gradlew 构建
# 剩余 1 个错误```

## Fix 3: Non-Exhaustive When

File: src/main/kotlin/com/example/routes/UserRoutes.kt:58
Error: 'when' expression must be exhaustive

```科特林
// 添加缺失的分支
当（用户.角色）{
    Role.ADMIN -> handleAdmin(用户)
    Role.USER->handleUser(用户)
    Role.MODERATOR -> handleModerator(user) // 添加
}```

```巴什
$ ./gradlew 构建
# 构建成功！```

## Final Verification

```巴什
$ ./gradlew 检测
# 没有问题

$ ./gradlew 测试
# 所有测试均已通过```

## Summary

| Metric | Count |
|--------|-------|
| Build errors fixed | 3 |
| Detekt issues fixed | 0 |
| Files modified | 2 |
| Remaining issues | 0 |

Build Status: ✅ SUCCESS
````

## 常见错误已修复

|错误|典型修复|
|--------|-------------|
| `未解决的参考：X` |添加导入或依赖|
| `类型不匹配` |修复类型转换或赋值 |
| “何时”必须详尽无遗` |添加缺少的密封类分支 |
| `挂起函数只能从协程中调用` |添加“暂停”修饰符 |
| “智能施放不可能” |使用本地 `val` 或 `let` |
| `以下候选者均不适用` |修复参数类型 |
| `无法解决依赖关系` |修复版本或添加存储库 |

## 修复策略

1. **首先构建错误** - 代码必须编译
2. **第二次检测违规** - 修复代码质量问题
3. **ktlint 警告第三** - 修复格式
4. **一次一个修复** - 验证每项更改
5. **最小的更改** - 不要重构，只需修复

## 停止条件

如果出现以下情况，代理将停止并报告：
- 3次尝试后仍然存在相同的错误
- 修复引入更多错误
- 需要架构更改
- 缺少外部依赖

## 相关命令

- `/kotlin-test` - 构建成功后运行测试
- `/kotlin-review` - 检查代码质量
- `/verify` - 完整的验证循环

## 相关

- 代理：`agents/kotlin-build-resolver.md`
- 技能：`技能/kotlin-patterns/`