# Kotlin 编码风格

> 此文件使用 Kotlin 特定内容扩展了通用编码风格规则。

## 格式化

- 通过 **ktfmt** 或 **ktlint** 自动格式化（在 `kotlin-hooks.md` 中配置）
- 在多行声明中使用尾随逗号

## 不变性

全局不变性要求在通用编码风格规则中强制执行。
对于 Kotlin 特别是：

- 更喜欢“val”而不是“var”
- 使用不可变集合类型（`List`、`Map`、`Set`）
- 使用“data class”和“copy()”进行不可变更新

## 空安全

- 避免“!!”——使用“?.”、“?:”、“require”或“checkNotNull”
- 在 Java 互操作边界显式处理平台类型

## 表达式体

对于单表达式函数，首选表达式体：```kotlin
fun isAdult(age: Int): Boolean = age >= 18
```## 参考

请参阅技能：`kotlin-patterns` 了解全面的 Kotlin 习语和模式。