# 用于测试的基于 Swift 协议的依赖注入

通过抽象小型、集中的协议背后的外部依赖项（文件系统、网络、iCloud）来使 Swift 代码可测试的模式。无需 I/O 即可启用确定性测试。

## 何时激活

- 编写访问文件系统、网络或外部 API 的 Swift 代码
- 需要测试错误处理路径而不触发真正的故障
- 构建跨环境工作的模块（应用程序、测试、SwiftUI 预览）
- 使用 Swift 并发设计可测试的架构（参与者、Sendable）

## 核心模式

### 1. 定义小型、集中的协议

每个协议只处理一个外部问题。```swift
// File system access
public protocol FileSystemProviding: Sendable {
    func containerURL(for purpose: Purpose) -> URL?
}

// File read/write operations
public protocol FileAccessorProviding: Sendable {
    func read(from url: URL) throws -> Data
    func write(_ data: Data, to url: URL) throws
    func fileExists(at url: URL) -> Bool
}

// Bookmark storage (e.g., for sandboxed apps)
public protocol BookmarkStorageProviding: Sendable {
    func saveBookmark(_ data: Data, for key: String) throws
    func loadBookmark(for key: String) throws -> Data?
}
```### 2. 创建默认（生产）实现```swift
public struct DefaultFileSystemProvider: FileSystemProviding {
    public init() {}

    public func containerURL(for purpose: Purpose) -> URL? {
        FileManager.default.url(forUbiquityContainerIdentifier: nil)
    }
}

public struct DefaultFileAccessor: FileAccessorProviding {
    public init() {}

    public func read(from url: URL) throws -> Data {
        try Data(contentsOf: url)
    }

    public func write(_ data: Data, to url: URL) throws {
        try data.write(to: url, options: .atomic)
    }

    public func fileExists(at url: URL) -> Bool {
        FileManager.default.fileExists(atPath: url.path)
    }
}
```### 3. 创建用于测试的模拟实现```swift
public final class MockFileAccessor: FileAccessorProviding, @unchecked Sendable {
    public var files: [URL: Data] = [:]
    public var readError: Error?
    public var writeError: Error?

    public init() {}

    public func read(from url: URL) throws -> Data {
        if let error = readError { throw error }
        guard let data = files[url] else {
            throw CocoaError(.fileReadNoSuchFile)
        }
        return data
    }

    public func write(_ data: Data, to url: URL) throws {
        if let error = writeError { throw error }
        files[url] = data
    }

    public func fileExists(at url: URL) -> Bool {
        files[url] != nil
    }
}
```### 4. 使用默认参数注入依赖项

生产代码使用默认值；测试注入模拟。```swift
public actor SyncManager {
    private let fileSystem: FileSystemProviding
    private let fileAccessor: FileAccessorProviding

    public init(
        fileSystem: FileSystemProviding = DefaultFileSystemProvider(),
        fileAccessor: FileAccessorProviding = DefaultFileAccessor()
    ) {
        self.fileSystem = fileSystem
        self.fileAccessor = fileAccessor
    }

    public func sync() async throws {
        guard let containerURL = fileSystem.containerURL(for: .sync) else {
            throw SyncError.containerNotAvailable
        }
        let data = try fileAccessor.read(
            from: containerURL.appendingPathComponent("data.json")
        )
        // Process data...
    }
}
```### 5. 使用 Swift 测试编写测试```swift
import Testing

@Test("Sync manager handles missing container")
func testMissingContainer() async {
    let mockFileSystem = MockFileSystemProvider(containerURL: nil)
    let manager = SyncManager(fileSystem: mockFileSystem)

    await #expect(throws: SyncError.containerNotAvailable) {
        try await manager.sync()
    }
}

@Test("Sync manager reads data correctly")
func testReadData() async throws {
    let mockFileAccessor = MockFileAccessor()
    mockFileAccessor.files[testURL] = testData

    let manager = SyncManager(fileAccessor: mockFileAccessor)
    let result = try await manager.loadData()

    #expect(result == expectedData)
}

@Test("Sync manager handles read errors gracefully")
func testReadError() async {
    let mockFileAccessor = MockFileAccessor()
    mockFileAccessor.readError = CocoaError(.fileReadCorruptFile)

    let manager = SyncManager(fileAccessor: mockFileAccessor)

    await #expect(throws: SyncError.self) {
        try await manager.sync()
    }
}
```## 最佳实践

- **单一职责**：每个协议都应该处理一个问题——不要用多种方法创建“上帝协议”
- **可发送一致性**：跨参与者边界使用协议时需要
- **默认参数**：让生产代码默认使用真实的实现；只有测试需要指定模拟
- **错误模拟**：设计具有可配置错误属性的模拟，用于测试故障路径
- **仅模拟边界**：模拟外部依赖项（文件系统、网络、API），而不是内部类型

## 要避免的反模式

- 创建一个涵盖所有外部访问的单一大型协议
- 模拟没有外部依赖的内部类型
- 使用“#if DEBUG”条件代替正确的依赖注入
- 与演员一起使用时忘记“可发送”一致性
- 过度设计：如果一个类型没有外部依赖，它就不需要协议

## 何时使用

- 任何涉及文件系统、网络或外部 API 的 Swift 代码
- 测试在真实环境中难以触发的错误处理路径
- 构建需要在应用程序、测试和 SwiftUI 预览上下文中工作的模块
- 使用需要可测试架构的 Swift 并发（参与者、结构化并发）的应用程序