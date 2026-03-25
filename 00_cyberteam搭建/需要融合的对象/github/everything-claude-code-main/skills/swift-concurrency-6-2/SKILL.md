# Swift 6.2 平易近人的并发

采用 Swift 6.2 并发模型的模式，其中代码默认以单线程运行，并显式引入并发。消除常见的数据争用错误而不牺牲性能。

## 何时激活

- 将 Swift 5.x 或 6.0/6.1 项目迁移到 Swift 6.2
- 解决数据争用安全编译器错误
- 设计基于MainActor的应用程序架构
- 将 CPU 密集型工作卸载到后台线程
- 在 MainActor 隔离类型上实现协议一致性
- 在 Xcode 26 中启用 Approachable Concurrency 构建设置

## 核心问题：隐式后台卸载

在 Swift 6.1 及更早版本中，异步函数可能会隐式卸载到后台线程，即使在看似安全的代码中也会导致数据争用错误：```swift
// Swift 6.1: ERROR
@MainActor
final class StickerModel {
    let photoProcessor = PhotoProcessor()

    func extractSticker(_ item: PhotosPickerItem) async throws -> Sticker? {
        guard let data = try await item.loadTransferable(type: Data.self) else { return nil }

        // Error: Sending 'self.photoProcessor' risks causing data races
        return await photoProcessor.extractSticker(data: data, with: item.itemIdentifier)
    }
}
```Swift 6.2 修复了这个问题：默认情况下，异步函数保留在调用 Actor 上。```swift
// Swift 6.2: OK — async stays on MainActor, no data race
@MainActor
final class StickerModel {
    let photoProcessor = PhotoProcessor()

    func extractSticker(_ item: PhotosPickerItem) async throws -> Sticker? {
        guard let data = try await item.loadTransferable(type: Data.self) else { return nil }
        return await photoProcessor.extractSticker(data: data, with: item.itemIdentifier)
    }
}
```## 核心模式——孤立的一致性

MainActor 类型现在可以安全地符合非隔离协议：```swift
protocol Exportable {
    func export()
}

// Swift 6.1: ERROR — crosses into main actor-isolated code
// Swift 6.2: OK with isolated conformance
extension StickerModel: @MainActor Exportable {
    func export() {
        photoProcessor.exportAsPNG()
    }
}
```编译器确保一致性仅用于主要参与者：```swift
// OK — ImageExporter is also @MainActor
@MainActor
struct ImageExporter {
    var items: [any Exportable]

    mutating func add(_ item: StickerModel) {
        items.append(item)  // Safe: same actor isolation
    }
}

// ERROR — nonisolated context can't use MainActor conformance
nonisolated struct ImageExporter {
    var items: [any Exportable]

    mutating func add(_ item: StickerModel) {
        items.append(item)  // Error: Main actor-isolated conformance cannot be used here
    }
}
```## 核心模式——全局变量和静态变量

使用 MainActor 保护全局/静态状态：```swift
// Swift 6.1: ERROR — non-Sendable type may have shared mutable state
final class StickerLibrary {
    static let shared: StickerLibrary = .init()  // Error
}

// Fix: Annotate with @MainActor
@MainActor
final class StickerLibrary {
    static let shared: StickerLibrary = .init()  // OK
}
```### MainActor 默认推理模式

Swift 6.2 引入了一种默认推断 MainActor 的模式——无需手动注释：```swift
// With MainActor default inference enabled:
final class StickerLibrary {
    static let shared: StickerLibrary = .init()  // Implicitly @MainActor
}

final class StickerModel {
    let photoProcessor: PhotoProcessor
    var selection: [PhotosPickerItem]  // Implicitly @MainActor
}

extension StickerModel: Exportable {  // Implicitly @MainActor conformance
    func export() {
        photoProcessor.exportAsPNG()
    }
}
```此模式是可选的，建议应用程序、脚本和其他可执行目标使用此模式。

## 核心模式 — @concurrent 用于后台工作

当您需要实际并行性时，请使用“@concurrent”显式卸载：

> **重要提示：** 此示例需要 Approachable Concurrency 构建设置 — SE-0466（MainActor 默认隔离）和 SE-0461 (NonisolatedNonsendingByDefault)。启用这些后，“extractSticker”将保留在调用者的参与者上，从而使可变状态访问变得安全。 **如果没有这些设置，此代码就会出现数据竞争** - 编译器将对其进行标记。```swift
nonisolated final class PhotoProcessor {
    private var cachedStickers: [String: Sticker] = [:]

    func extractSticker(data: Data, with id: String) async -> Sticker {
        if let sticker = cachedStickers[id] {
            return sticker
        }

        let sticker = await Self.extractSubject(from: data)
        cachedStickers[id] = sticker
        return sticker
    }

    // Offload expensive work to concurrent thread pool
    @concurrent
    static func extractSubject(from data: Data) async -> Sticker { /* ... */ }
}

// Callers must await
let processor = PhotoProcessor()
processedPhotos[item.id] = await processor.extractSticker(data: data, with: item.id)
```要使用“@concurrent”：
1. 将包含类型标记为“nonisolated”
2. 在函数中添加`@concurrent`
3. 如果还没有异步，则添加“async”
4. 在调用处添加 `await`

## 关键设计决策

|决定|理由|
|----------|------------|
|默认单线程|大多数自然代码都是无数据竞争的；并发是可选的 |
|异步保持在调用 actor |消除导致数据争用错误的隐式卸载
|孤立的一致性| MainActor 类型可以符合协议，而无需不安全的解决方法 |
| `@concurrent` 显式选择加入 |后台执行是一种刻意的性能选择，并非偶然 |
| MainActor 默认推理 |减少应用程序目标的样板“@MainActor”注释
|选择采用 |不间断的迁移路径——逐步启用功能 |

## 迁移步骤

1. **在 Xcode 中启用**：构建设置中的 Swift Compiler > Concurrency 部分
2. **在 SPM 中启用**：在包清单中使用 `SwiftSettings` API
3. **使用迁移工具**：通过 swift.org/migration 自动更改代码
4. **从 MainActor 默认值开始**：为应用程序目标启用推理模式
5. **在需要的地方添加`@concurrent`**：首先分析，然后卸载热路径
6. **彻底测试**：数据争用问题变成编译时错误

## 最佳实践

- **从 MainActor 开始** — 先编写单线程代码，然后再优化
- **仅将“@concurrent”用于CPU密集型工作**——图像处理、压缩、复杂计算
- **为大多数单线程的应用程序目标启用 MainActor 推理模式**
- **卸载前的配置文件** — 使用 Instruments 查找实际瓶颈
- **使用 MainActor 保护全局变量** — 全局/静态可变状态需要 Actor 隔离
- **使用隔离一致性**而不是“非隔离”解决方法或“@Sendable”包装器
- **增量迁移** — 在构建设置中一次启用一个功能

## 要避免的反模式

- 将“@concurrent”应用于每个异步函数（大多数不需要后台执行）
- 在不了解隔离的情况下使用“nonisolated”来抑制编译器错误
- 当参与者提供相同的安全性时，保留遗留的“DispatchQueue”模式
- 跳过并发相关的基础模型代码中的“model.availability”检查
- 对抗编译器——如果它报告数据竞争，则代码存在真正的并发问题
- 假设所有异步代码在后台运行（Swift 6.2 默认：保持调用 actor）

## 何时使用

- 所有新的 Swift 6.2+ 项目（Approachable Concurrency 是建议的默认值）
- 从 Swift 5.x 或 6.0/6.1 并发迁移现有应用程序
- 解决 Xcode 26 采用期间的数据争用安全编译器错误
- 构建以 MainActor 为中心的应用程序架构（大多数 UI 应用程序）
- 性能优化——将特定的繁重计算卸载到后台