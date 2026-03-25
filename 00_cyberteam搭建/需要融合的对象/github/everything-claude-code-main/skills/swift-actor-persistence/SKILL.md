# 用于线程安全持久化的 Swift Actor

使用 Swift Actor 构建线程安全数据持久层的模式。将内存缓存与文件支持的存储相结合，利用参与者模型消除编译时的数据竞争。

## 何时激活

- 在 Swift 5.5+ 中构建数据持久层
- 需要对共享可变状态进行线程安全访问
- 想要消除手动同步（锁、DispatchQueues）
- 使用本地存储构建离线优先的应用程序

## 核心模式

### 基于参与者的存储库

参与者模型保证序列化访问——没有数据竞争，由编译器强制执行。```swift
public actor LocalRepository<T: Codable & Identifiable> where T.ID == String {
    private var cache: [String: T] = [:]
    private let fileURL: URL

    public init(directory: URL = .documentsDirectory, filename: String = "data.json") {
        self.fileURL = directory.appendingPathComponent(filename)
        // Synchronous load during init (actor isolation not yet active)
        self.cache = Self.loadSynchronously(from: fileURL)
    }

    // MARK: - Public API

    public func save(_ item: T) throws {
        cache[item.id] = item
        try persistToFile()
    }

    public func delete(_ id: String) throws {
        cache[id] = nil
        try persistToFile()
    }

    public func find(by id: String) -> T? {
        cache[id]
    }

    public func loadAll() -> [T] {
        Array(cache.values)
    }

    // MARK: - Private

    private func persistToFile() throws {
        let data = try JSONEncoder().encode(Array(cache.values))
        try data.write(to: fileURL, options: .atomic)
    }

    private static func loadSynchronously(from url: URL) -> [String: T] {
        guard let data = try? Data(contentsOf: url),
              let items = try? JSONDecoder().decode([T].self, from: data) else {
            return [:]
        }
        return Dictionary(uniqueKeysWithValues: items.map { ($0.id, $0) })
    }
}
```### 用法

由于参与者隔离，所有调用都会自动异步：```swift
let repository = LocalRepository<Question>()

// Read — fast O(1) lookup from in-memory cache
let question = await repository.find(by: "q-001")
let allQuestions = await repository.loadAll()

// Write — updates cache and persists to file atomically
try await repository.save(newQuestion)
try await repository.delete("q-001")
```### 与@Observable ViewModel结合```swift
@Observable
final class QuestionListViewModel {
    private(set) var questions: [Question] = []
    private let repository: LocalRepository<Question>

    init(repository: LocalRepository<Question> = LocalRepository()) {
        self.repository = repository
    }

    func load() async {
        questions = await repository.loadAll()
    }

    func add(_ question: Question) async throws {
        try await repository.save(question)
        questions = await repository.loadAll()
    }
}
```## 关键设计决策

|决定|理由|
|----------|------------|
| Actor（非类+锁）|编译器强制线程安全，无需手动同步 |
|内存缓存+文件持久化 |从缓存快速读取，持久写入磁盘 |
|同步初始化加载 |避免异步初始化复杂性 |
|按 ID 键控的字典 | O(1) 按标识符查找 |
|通用于“可编码和可识别”|可在任何模型类型中重复使用 |
|原子文件写入 (`.atomic`) |防止崩溃时部分写入 |

## 最佳实践

- **对所有跨越参与者边界的数据使用“可发送”类型**
- **保持参与者的公共 API 最少** - 只公开域操作，而不公开持久性细节
- **使用`.atomic`写入**来防止应用程序在写入过程中崩溃时数据损坏
- **在 `init` 中同步加载 - 异步初始化器增加了复杂性，但对本地文件的好处却微乎其微
- **与`@Observable`** ViewModels结合用于反应式UI更新

## 要避免的反模式

- 使用 `DispatchQueue` 或 `NSLock` 代替 actor 来实现新的 Swift 并发代码
- 向外部调用者公开内部缓存字典
- 无需验证即可配置文件 URL
- 忘记所有 actor 方法调用都是“await”——调用者必须处理异步上下文
- 使用“nonisolated”绕过参与者隔离（达不到目的）

## 何时使用

- iOS/macOS 应用程序中的本地数据存储（用户数据、设置、缓存内容）
- 离线优先架构，稍后同步到服务器
- 应用程序的多个部分同时访问的任何共享可变状态
- 用现代 Swift 并发性取代传统的基于“DispatchQueue”的线程安全性