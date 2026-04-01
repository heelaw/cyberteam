# Kotlin 编码风格

> 此文件使用 Kotlin 特定内容扩展了 [common/coding-style.md](../common/coding-style.md)。

## 格式化

- **ktlint** 或 **Detekt** 用于样式强制
- 官方 Kotlin 代码风格（“gradle.properties”中的“kotlin.code.style=official”）

## 不变性

- 优先选择“val”而不是“var”——默认为“val”，并且仅在需要突变时才使用“var”
- 使用“数据类”作为值类型；在公共 API 中使用不可变集合（“List”、“Map”、“Set”）
- 写入时复制状态更新：`state.copy(field = newValue)`

## 命名

遵循 Kotlin 约定：
- 函数和属性的“camelCase”
- 用于类、接口、对象和类型别名的“PascalCase”
- `SCREAMING_SNAKE_CASE` 用于常量（`const val` 或 `@JvmStatic`）
- 为接口添加行为前缀，而不是“I”：“Clickable”而不是“IClickable”

## 空安全

- 切勿使用 `!!` — 更喜欢使用 `?.`、`?:`、`requireNotNull()` 或 `checkNotNull()`
- 使用 `?.let {}` 进行作用域空安全操作
- 从合法地没有结果的函数返回可空类型```kotlin
// BAD
val name = user!!.name

// GOOD
val name = user?.name ?: "Unknown"
val name = requireNotNull(user) { "User must be set before accessing name" }.name
```## 密封类型

使用密封类/接口来建模封闭状态层次结构：```kotlin
sealed interface UiState<out T> {
    data object Loading : UiState<Nothing>
    data class Success<T>(val data: T) : UiState<T>
    data class Error(val message: String) : UiState<Nothing>
}
```始终对密封类型使用详尽的“when”——没有“else”分支。

## 扩展函数

使用扩展函数进行实用程序操作，但保持它们可发现：
- 放置在以接收器类型命名的文件中（`StringExt.kt`、`FlowExt.kt`）
- 保持范围有限——不要向“Any”或过于通用的类型添加扩展

## 作用域函数

使用正确的范围函数：
- `let` — 空检查 + 转换：`user?.let {greet(it) }`
- `run` — 使用接收器计算结果：`service.run { fetch(config) }`
- `apply` — 配置一个对象：`builder.apply { timeout = 30 }`
- `also` — 副作用：`result.also { log(it) }`
- 避免作用域函数的深度嵌套（最多 2 层）

## 错误处理

- 使用 `Result<T>` 或自定义密封类型
- 使用“runCatching {}”来包装可抛出代码
- 永远不要捕获“CancellationException”——总是重新抛出它
- 避免使用“try-catch”来控制流程```kotlin
// BAD — using exceptions for control flow
val user = try { repository.getUser(id) } catch (e: NotFoundException) { null }

// GOOD — nullable return
val user: User? = repository.findUser(id)
```