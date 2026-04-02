# Swift 编码风格

> 此文件使用 Swift 特定内容扩展了 [common/coding-style.md](../common/coding-style.md)。

## 格式化

- **SwiftFormat** 用于自动格式化，**SwiftLint** 用于样式强制
- `swift-format` 与 Xcode 16+ 捆绑在一起作为替代方案

## 不变性

- 优先选择 `let` 而不是 `var` — 将所有内容定义为 `let`，并且仅在编译器需要时才更改为 `var`
- 默认情况下使用具有值语义的“struct”；仅当需要标识或引用语义时才使用“类”

## 命名

遵循 [Apple API 设计指南](https://www.swift.org/documentation/api-design-guidelines/)：

- 使用时清晰——省略不必要的词语
- 根据其角色而不是其类型来命名方法和属性
- 对全局常量上的常量使用“static let”

## 错误处理

使用类型化抛出（Swift 6+）和模式匹配：```swift
func load(id: String) throws(LoadError) -> Item {
    guard let data = try? read(from: path) else {
        throw .fileNotFound(id)
    }
    return try decode(data)
}
```## 并发

启用 Swift 6 严格并发检查。更喜欢：

- 跨越隔离边界的数据的“可发送”值类型
- 共享可变状态的参与者
- 非结构化“Task {}”上的结构化并发（“async let”、“TaskGroup”）