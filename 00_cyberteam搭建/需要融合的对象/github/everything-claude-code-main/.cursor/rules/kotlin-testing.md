# Kotlin 测试

> 此文件使用 Kotlin 特定内容扩展了通用测试规则。

## 框架

使用带有规范样式（StringSpec、FunSpec、BehaviorSpec）的 **Kotest** 和 **MockK** 进行模拟。

## 协程测试

使用“kotlinx-coroutines-test”中的“runTest”：```kotlin
test("async operation completes") {
    runTest {
        val result = service.fetchData()
        result.shouldNotBeEmpty()
    }
}
```## 覆盖范围

使用 **Kover** 进行覆盖率报告：```bash
./gradlew koverHtmlReport
./gradlew koverVerify
```## 参考

请参阅技能：“kotlin-testing”，了解详细的 Kotest 模式、MockK 用法和基于属性的测试。