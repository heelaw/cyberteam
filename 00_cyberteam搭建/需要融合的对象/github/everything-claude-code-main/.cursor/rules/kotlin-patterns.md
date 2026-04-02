# Kotlin 模式

> 此文件使用 Kotlin 特定内容扩展了常见模式规则。

## 密封课程

使用密封类/接口来实现详尽的类型层次结构：```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Failure(val error: AppError) : Result<Nothing>()
}
```## 扩展函数

添加不带继承的行为，范围仅限于使用它们的地方：```kotlin
fun String.toSlug(): String =
    lowercase().replace(Regex("[^a-z0-9\\s-]"), "").replace(Regex("\\s+"), "-")
```## 作用域函数

- `let`：转换可为 null 或作用域的结果
- `apply`：配置一个对象
- `另外`：副作用
- 避免嵌套作用域函数

## 依赖注入

在 Ktor 项目中使用 Koin 进行 DI：```kotlin
val appModule = module {
    single<UserRepository> { ExposedUserRepository(get()) }
    single { UserService(get()) }
}
```## 参考

请参阅技能：“kotlin-patterns”，了解全面的 Kotlin 模式，包括协程、DSL 构建器和委托。