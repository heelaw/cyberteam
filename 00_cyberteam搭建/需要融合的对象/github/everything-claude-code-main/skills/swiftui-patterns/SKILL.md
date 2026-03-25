# SwiftUI 模式

用于在 Apple 平台上构建声明式高性能用户界面的现代 SwiftUI 模式。涵盖观察框架、视图组合、类型安全导航和性能优化。

## 何时激活

- 构建 SwiftUI 视图并管理状态（`@State`、`@Observable`、`@Binding`）
- 使用“NavigationStack”设计导航流程
- 构建视图模型和数据流
- 优化列表和复杂布局的渲染性能
- 在 SwiftUI 中使用环境值和依赖注入

## 状态管理

### 属性包装选择

选择适合的最简单的包装：

|包装|使用案例|
|---------|----------|
| `@State` |视图本地值类型（切换、表单字段、工作表呈现）|
| `@Binding` |对父级`@State`的双向引用
| `@Observable` 类 + `@State` |拥有多种属性的模型 |
| `@Observable` 类（无包装器）|从父级传递的只读引用 |
| `@Bindable` |双向绑定到`@Observable`属性|
| `@Environment` |通过 `.environment()` 注入共享依赖项 |

### @Observable ViewModel

使用“@Observable”（而不是“ObservableObject”）——它跟踪属性级别的更改，因此 SwiftUI 仅重新渲染读取已更改属性的视图：```swift
@Observable
final class ItemListViewModel {
    private(set) var items: [Item] = []
    private(set) var isLoading = false
    var searchText = ""

    private let repository: any ItemRepository

    init(repository: any ItemRepository = DefaultItemRepository()) {
        self.repository = repository
    }

    func load() async {
        isLoading = true
        defer { isLoading = false }
        items = (try? await repository.fetchAll()) ?? []
    }
}
```### View 使用 ViewModel```swift
struct ItemListView: View {
    @State private var viewModel: ItemListViewModel

    init(viewModel: ItemListViewModel = ItemListViewModel()) {
        _viewModel = State(initialValue: viewModel)
    }

    var body: some View {
        List(viewModel.items) { item in
            ItemRow(item: item)
        }
        .searchable(text: $viewModel.searchText)
        .overlay { if viewModel.isLoading { ProgressView() } }
        .task { await viewModel.load() }
    }
}
```### 环境注入

将“@EnvironmentObject”替换为“@Environment”：```swift
// Inject
ContentView()
    .environment(authManager)

// Consume
struct ProfileView: View {
    @Environment(AuthManager.self) private var auth

    var body: some View {
        Text(auth.currentUser?.name ?? "Guest")
    }
}
```## 查看成分

### 提取子视图以限制失效

将视图分解为小的、集中的结构。当状态改变时，只有读取该状态的子视图才会重新渲染：```swift
struct OrderView: View {
    @State private var viewModel = OrderViewModel()

    var body: some View {
        VStack {
            OrderHeader(title: viewModel.title)
            OrderItemList(items: viewModel.items)
            OrderTotal(total: viewModel.total)
        }
    }
}
```### 用于可重用样式的 ViewModifier```swift
struct CardModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding()
            .background(.regularMaterial)
            .clipShape(RoundedRectangle(cornerRadius: 12))
    }
}

extension View {
    func cardStyle() -> some View {
        modifier(CardModifier())
    }
}
```## 导航

### 类型安全的 NavigationStack

将“NavigationStack”与“NavigationPath”结合使用以实现编程式、类型安全的路由：```swift
@Observable
final class Router {
    var path = NavigationPath()

    func navigate(to destination: Destination) {
        path.append(destination)
    }

    func popToRoot() {
        path = NavigationPath()
    }
}

enum Destination: Hashable {
    case detail(Item.ID)
    case settings
    case profile(User.ID)
}

struct RootView: View {
    @State private var router = Router()

    var body: some View {
        NavigationStack(path: $router.path) {
            HomeView()
                .navigationDestination(for: Destination.self) { dest in
                    switch dest {
                    case .detail(let id): ItemDetailView(itemID: id)
                    case .settings: SettingsView()
                    case .profile(let id): ProfileView(userID: id)
                    }
                }
        }
        .environment(router)
    }
}
```## 性能

### 对大型集合使用惰性容器

`LazyVStack` 和 `LazyHStack` 仅在可见时创建视图：```swift
ScrollView {
    LazyVStack(spacing: 8) {
        ForEach(items) { item in
            ItemRow(item: item)
        }
    }
}
```### 稳定标识符

始终在“ForEach”中使用稳定、唯一的 ID — 避免使用数组索引：```swift
// Use Identifiable conformance or explicit id
ForEach(items, id: \.stableID) { item in
    ItemRow(item: item)
}
```### 避免体内昂贵的工作

- 切勿在“body”内执行 I/O、网络调用或繁重计算
- 使用“.task {}”进行异步工作——当视图消失时它会自动取消
- 在滚动视图中谨慎使用“.sensoryFeedback()”和“.geometryGroup()”
- 最小化列表中的“.shadow()”、“.blur()”和“.mask()”——它们会触发离屏渲染

### 等值一致性

对于具有昂贵主体的视图，请遵循“Equatable”以跳过不必要的重新渲染：```swift
struct ExpensiveChartView: View, Equatable {
    let dataPoints: [DataPoint] // DataPoint must conform to Equatable

    static func == (lhs: Self, rhs: Self) -> Bool {
        lhs.dataPoints == rhs.dataPoints
    }

    var body: some View {
        // Complex chart rendering
    }
}
```## 预览

将“#Preview”宏与内联模拟数据一起使用以实现快速迭代：```swift
#Preview("Empty state") {
    ItemListView(viewModel: ItemListViewModel(repository: EmptyMockRepository()))
}

#Preview("Loaded") {
    ItemListView(viewModel: ItemListViewModel(repository: PopulatedMockRepository()))
}
```## 要避免的反模式

- 在新代码中使用 `ObservableObject` / `@Published` / `@StateObject` / `@EnvironmentObject` — 迁移到 `@Observable`
- 将异步工作直接放入“body”或“init”中 - 使用“.task {}”或显式加载方法
- 在不拥有数据的子视图中将视图模型创建为“@State”——而是从父视图传递
- 使用“AnyView”类型擦除 - 对于条件视图更喜欢“@ViewBuilder”或“Group”
- 在向/从参与者传递数据时忽略“可发送”要求

## 参考文献

请参阅技能：“swift-actor-persistence”，了解基于 actor 的持久性模式。
请参阅技能：“swift-protocol-di-testing”，了解基于协议的 DI 和使用 Swift 测试进行测试。