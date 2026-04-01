# FoundationModels：设备上法学硕士 (iOS 26)

使用 FoundationModels 框架将 Apple 设备上语言模型集成到应用程序中的模式。涵盖文本生成、使用“@Generable”的结构化输出、自定义工具调用和快照流 - 所有这些都在设备上运行以实现隐私和离线支持。

## 何时激活

- 使用设备上的 Apple Intelligence 构建人工智能驱动的功能
- 生成或总结文本，无需云依赖
- 从自然语言输入中提取结构化数据
- 实施调用特定领域人工智能操作的自定义工具
- 流式传输结构化响应以实现实时 UI 更新
- 需要保护隐私的人工智能（没有数据离开设备）

## 核心模式——可用性检查

在创建会话之前始终检查模型可用性：```swift
struct GenerativeView: View {
    private var model = SystemLanguageModel.default

    var body: some View {
        switch model.availability {
        case .available:
            ContentView()
        case .unavailable(.deviceNotEligible):
            Text("Device not eligible for Apple Intelligence")
        case .unavailable(.appleIntelligenceNotEnabled):
            Text("Please enable Apple Intelligence in Settings")
        case .unavailable(.modelNotReady):
            Text("Model is downloading or not ready")
        case .unavailable(let other):
            Text("Model unavailable: \(other)")
        }
    }
}
```## 核心模式——基础会话```swift
// Single-turn: create a new session each time
let session = LanguageModelSession()
let response = try await session.respond(to: "What's a good month to visit Paris?")
print(response.content)

// Multi-turn: reuse session for conversation context
let session = LanguageModelSession(instructions: """
    You are a cooking assistant.
    Provide recipe suggestions based on ingredients.
    Keep suggestions brief and practical.
    """)

let first = try await session.respond(to: "I have chicken and rice")
let followUp = try await session.respond(to: "What about a vegetarian option?")
```说明要点：
- 定义模型的角色（“你是导师”）
- 指定要做什么（“帮助提取日历事件”）
- 设置风格偏好（“尽可能简短地回复”）
- 添加安全措施（“对于危险请求，请回复‘我无能为力’”）

## 核心模式——@Generable 引导生成

生成结构化 Swift 类型而不是原始字符串：

### 1. 定义可生成类型```swift
@Generable(description: "Basic profile information about a cat")
struct CatProfile {
    var name: String

    @Guide(description: "The age of the cat", .range(0...20))
    var age: Int

    @Guide(description: "A one sentence profile about the cat's personality")
    var profile: String
}
```### 2.请求结构化输出```swift
let response = try await session.respond(
    to: "Generate a cute rescue cat",
    generating: CatProfile.self
)

// Access structured fields directly
print("Name: \(response.content.name)")
print("Age: \(response.content.age)")
print("Profile: \(response.content.profile)")
```### 支持的@Guide 约束

- `.range(0...20)` — 数字范围
- `.count(3)` — 数组元素计数
- `description:` — 生成的语义指导

## 核心模式——工具调用

让模型调用自定义代码来执行特定于域的任务：

### 1. 定义工具```swift
struct RecipeSearchTool: Tool {
    let name = "recipe_search"
    let description = "Search for recipes matching a given term and return a list of results."

    @Generable
    struct Arguments {
        var searchTerm: String
        var numberOfResults: Int
    }

    func call(arguments: Arguments) async throws -> ToolOutput {
        let recipes = await searchRecipes(
            term: arguments.searchTerm,
            limit: arguments.numberOfResults
        )
        return .string(recipes.map { "- \($0.name): \($0.description)" }.joined(separator: "\n"))
    }
}
```### 2. 使用工具创建会话```swift
let session = LanguageModelSession(tools: [RecipeSearchTool()])
let response = try await session.respond(to: "Find me some pasta recipes")
```### 3. 处理工具错误```swift
do {
    let answer = try await session.respond(to: "Find a recipe for tomato soup.")
} catch let error as LanguageModelSession.ToolCallError {
    print(error.tool.name)
    if case .databaseIsEmpty = error.underlyingError as? RecipeSearchToolError {
        // Handle specific tool error
    }
}
```## 核心模式——快照流

使用“PartiallyGenerator”类型流式传输实时 UI 的结构化响应：```swift
@Generable
struct TripIdeas {
    @Guide(description: "Ideas for upcoming trips")
    var ideas: [String]
}

let stream = session.streamResponse(
    to: "What are some exciting trip ideas?",
    generating: TripIdeas.self
)

for try await partial in stream {
    // partial: TripIdeas.PartiallyGenerated (all properties Optional)
    print(partial)
}
```### SwiftUI 集成```swift
@State private var partialResult: TripIdeas.PartiallyGenerated?
@State private var errorMessage: String?

var body: some View {
    List {
        ForEach(partialResult?.ideas ?? [], id: \.self) { idea in
            Text(idea)
        }
    }
    .overlay {
        if let errorMessage { Text(errorMessage).foregroundStyle(.red) }
    }
    .task {
        do {
            let stream = session.streamResponse(to: prompt, generating: TripIdeas.self)
            for try await partial in stream {
                partialResult = partial
            }
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
```## 关键设计决策

|决定|理由|
|----------|------------|
|设备上执行 |隐私——没有数据离开设备；离线工作 |
| 4,096 个代币限制 |设备上模型约束；跨会话分块大数据|
|快照流（不是增量）|结构化输出友好；每个快照都是一个完整的部分状态 |
| `@Geneable` 宏 |结构化生成的编译时安全性；自动生成 `PartiallyGenerate` 类型 |
|每个会话单个请求 | `isResponding` 防止并发请求；如果需要，创建多个会话 |
| `response.content`（不是`.output`）|正确的 API — 始终通过“.content”属性访问结果 |

## 最佳实践

- **在创建会话之前始终检查`model.availability`** - 处理所有不可用情况
- **使用“指令”**来指导模型行为 - 它们优先于提示
- **在发送新请求之前检查 `isResponding`** — 会话一次处理一个请求
- **访问“response.content”**以获取结果 - 而不是“.output”
- **将大量输入分成块** — 4,096 个令牌限制适用于指令 + 提示 + 输出组合
- **使用`@Generable`**进行结构化输出——比解析原始字符串有更强的保证
- **使用`GenerationOptions(温度:)`**来调整创造力（更高=更有创造力）
- **使用 Instruments 进行监控** — 使用 Xcode Instruments 来分析请求性能

## 要避免的反模式

- 创建会话时不首先检查“model.availability”
- 发送超过 4,096 个令牌上下文窗口的输入
- 尝试在单个会话上并发请求
- 使用`.output`而不是`.content`来访问响应数据
- 当“@Generable”结构化输出起作用时解析原始字符串响应
- 在单个提示中构建复杂的多步骤逻辑 - 分解为多个重点提示
- 假设模型始终可用 - 设备资格和设置各不相同

## 何时使用

- 为隐私敏感应用程序生成设备上文本
- 从用户输入（表单、自然语言命令）中提取结构化数据
- 必须离线工作的人工智能辅助功能
- 渐进式显示生成内容的流式 UI
- 通过工具调用（搜索、计算、查找）进行特定领域的人工智能操作