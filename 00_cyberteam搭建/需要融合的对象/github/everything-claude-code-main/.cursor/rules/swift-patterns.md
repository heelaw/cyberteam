# Swift 模式

> 此文件使用 Swift 特定内容扩展了常见模式规则。

## 面向协议的设计

定义小型、集中的协议。使用共享默认值的协议扩展：```swift
protocol Repository: Sendable {
    associatedtype Item: Identifiable & Sendable
    func find(by id: Item.ID) async throws -> Item?
    func save(_ item: Item) async throws
}
```## 值类型

- 使用数据传输对象和模型的结构
- 使用具有关联值的枚举来模拟不同的状态：```swift
enum LoadState<T: Sendable>: Sendable {
    case idle
    case loading
    case loaded(T)
    case failed(Error)
}
```## 演员模式

使用参与者来共享可变状态而不是锁或调度队列：```swift
actor Cache<Key: Hashable & Sendable, Value: Sendable> {
    private var storage: [Key: Value] = [:]

    func get(_ key: Key) -> Value? { storage[key] }
    func set(_ key: Key, value: Value) { storage[key] = value }
}
```## 依赖注入

使用默认参数注入协议——生产使用默认值，测试注入模拟：```swift
struct UserService {
    private let repository: any UserRepository

    init(repository: any UserRepository = DefaultUserRepository()) {
        self.repository = repository
    }
}
```## 参考文献

请参阅技能：“swift-actor-persistence”，了解基于 actor 的持久性模式。
请参阅技能：“swift-protocol-di-testing”，了解基于协议的 DI 和测试。