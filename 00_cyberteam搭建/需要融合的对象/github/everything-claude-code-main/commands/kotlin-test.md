# Kotlin TDD 命令

此命令使用 Kotest、MockK 和 Kover 对 Kotlin 代码实施测试驱动开发方法。

## 该命令的作用

1. **定义类型/接口**：首先定义支架函数签名
2. **编写 Kotest 测试**：创建全面的测试规范（红色）
3. **运行测试**：验证测试失败的正确原因
4. **实现代码**：编写最少的代码即可通过（绿色）
5. **重构**：在保持测试绿色的同时进行改进
6. **检查覆盖率**：确保 Kover 的覆盖率超过 80%

## 何时使用

在以下情况下使用 `/kotlin-test`：
- 实现新的 Kotlin 函数或类
- 向现有 Kotlin 代码添加测试覆盖率
- 修复错误（首先编写失败的测试）
- 构建关键业务逻辑
- 学习 Kotlin 中的 TDD 工作流程

## TDD 周期```
RED     -> Write failing Kotest test
GREEN   -> Implement minimal code to pass
REFACTOR -> Improve code, tests stay green
REPEAT  -> Next test case
```## 会话示例````text
User: /kotlin-test I need a function to validate user registration requests

Agent:
# TDD Session: Registration Validator

## Step 1: Define Interface

```科特林
// 验证器/RegistrationValidator.kt
包 com.example.validator

数据类注册请求（
    值名称：字符串，
    val 电子邮件：字符串，
    val 密码：字符串，
）

密封类 ValidationResult {
    数据对象有效：ValidationResult()
    数据类无效（val 错误：List<String>）：ValidationResult()
}

有趣的 validateRegistration（请求：RegistrationRequest）：ValidationResult {
    TODO(“未实现”)
}```

## Step 2: Write Kotest Tests (RED)

```科特林
// 验证器/RegistrationValidatorTest.kt
包 com.example.validator

导入 io.kotest.core.spec.style.FunSpec
导入 io.kotest.matchers.shouldBe
导入 io.kotest.matchers.types.shouldBeInstanceOf

类 RegistrationValidatorTest : FunSpec({
    test("有效注册返回Valid") {
        val 请求 = 注册请求(
            名称=“爱丽丝”，
            电子邮件=“alice@example.com”，
            密码=“SecureP@ss1”，
        ）

        val 结果 = 验证注册（请求）

        result.shouldBeInstanceOf<ValidationResult.Valid>()
    }

    test("空白名称返回无效") {
        val 请求 = 注册请求(
            名称=“”，
            电子邮件=“alice@example.com”，
            密码=“SecureP@ss1”，
        ）

        val 结果 = 验证注册（请求）

        val 无效 = result.shouldBeInstanceOf<ValidationResult.Invalid>()
        invalid.errors shouldBe listOf("姓名为必填项")
    }

    test("无效的电子邮件返回 Invalid") {
        val 请求 = 注册请求(
            名称=“爱丽丝”，
            电子邮件=“不是电子邮件”，
            密码=“SecureP@ss1”，
        ）

        val 结果 = 验证注册（请求）

        val 无效 = result.shouldBeInstanceOf<ValidationResult.Invalid>()
        invalid.errors shouldBe listOf("电子邮件格式无效")
    }

    test("短密码返回无效") {
        val 请求 = 注册请求(
            名称=“爱丽丝”，
            电子邮件=“alice@example.com”，
            密码=“短”，
        ）

        val 结果 = 验证注册（请求）

        val 无效 = result.shouldBeInstanceOf<ValidationResult.Invalid>()
        invalid.errors shouldBe listOf("密码必须至少为 8 个字符")
    }

    test("多个错误返回所有错误") {
        val 请求 = 注册请求(
            名称=“”，
            电子邮件=“坏”，
            密码=“短”，
        ）

        val 结果 = 验证注册（请求）

        val 无效 = result.shouldBeInstanceOf<ValidationResult.Invalid>()
        invalid.errors.size 应该是 3
    }
})```

## Step 3: Run Tests - Verify FAIL

```巴什
$ ./gradlew 测试

RegistrationValidatorTest > 有效注册返回 Valid FAILED
  kotlin.NotImplementedError：操作未实现

失败（5 次测试，0 次通过，5 次失败）```

✓ Tests fail as expected (NotImplementedError).

## Step 4: Implement Minimal Code (GREEN)

```科特林
// 验证器/RegistrationValidator.kt
包 com.example.validator

private val EMAIL_REGEX = Regex("^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$")
私有常量 VAL MIN_PASSWORD_LENGTH = 8

有趣的 validateRegistration（请求：RegistrationRequest）：ValidationResult {
    val 错误 = buildList {
        if (request.name.isBlank()) add("姓名为必填项")
        if (!EMAIL_REGEX.matches(request.email)) add("电子邮件格式无效")
        if (request.password.length < MIN_PASSWORD_LENGTH) add("密码必须至少包含 $MIN_PASSWORD_LENGTH 个字符")
    }

    返回 if (errors.isEmpty()) ValidationResult.Valid
    否则 ValidationResult.Invalid（错误）
}```

## Step 5: Run Tests - Verify PASS

```巴什
$ ./gradlew 测试

RegistrationValidatorTest > 有效注册返回 Valid PASSED
RegistrationValidatorTest > 空白名称返回 Invalid PASSED
RegistrationValidatorTest > 无效电子邮件返回 Invalid PASSED
RegistrationValidatorTest > 短密码返回 Invalid PASSED
RegistrationValidatorTest > 多个错误返回所有错误已通过

通过（5 次测试，5 次通过，0 次失败）```

✓ All tests passing!

## Step 6: Check Coverage

```巴什
$ ./gradlew koverHtmlReport

覆盖率：100.0% 的报表```

✓ Coverage: 100%

## TDD Complete!
````

## 测试模式

### StringSpec（最简单）```kotlin
class CalculatorTest : StringSpec({
    "add two positive numbers" {
        Calculator.add(2, 3) shouldBe 5
    }
})
```### 行为规范 (BDD)```kotlin
class OrderServiceTest : BehaviorSpec({
    Given("a valid order") {
        When("placed") {
            Then("should be confirmed") { /* ... */ }
        }
    }
})
```### 数据驱动测试```kotlin
class ParserTest : FunSpec({
    context("valid inputs") {
        withData("2026-01-15", "2026-12-31", "2000-01-01") { input ->
            parseDate(input).shouldNotBeNull()
        }
    }
})
```### 协程测试```kotlin
class AsyncServiceTest : FunSpec({
    test("concurrent fetch completes") {
        runTest {
            val result = service.fetchAll()
            result.shouldNotBeEmpty()
        }
    }
})
```## 覆盖命令```bash
# Run tests with coverage
./gradlew koverHtmlReport

# Verify coverage thresholds
./gradlew koverVerify

# XML report for CI
./gradlew koverXmlReport

# Open HTML report
open build/reports/kover/html/index.html

# Run specific test class
./gradlew test --tests "com.example.UserServiceTest"

# Run with verbose output
./gradlew test --info
```## 覆盖目标

|代码类型 |目标|
|------------|--------|
|关键业务逻辑 | 100% |
|公共 API | 90%+ |
|通用代码| 80%+ |
|生成的代码 |排除 |

## TDD 最佳实践

**做：**
- 在任何实施之前先编写测试
- 每次更改后运行测试
- 使用 Kotest 匹配器进行表达性断言
- 使用 MockK 的 `coEvery`/`coVerify` 来实现挂起功能
- 测试行为，而不是实现细节
- 包括边缘情况（空、空、最大值）

**不要：**
- 在测试之前编写实现
- 跳过红色阶段
- 直接测试私有函数
- 在协程测试中使用“Thread.sleep()”
- 忽略片状测试

## 相关命令

- `/kotlin-build` - 修复构建错误
- `/kotlin-review` - 实施后审查代码
- `/verify` - 运行完整的验证循环

## 相关

- 技能：`技能/kotlin-testing/`
- 技能：`技能/tdd-工作流程/`