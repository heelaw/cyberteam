# 液态玻璃设计系统 (iOS 26)

用于实现 Apple 液态玻璃的模式 - 一种动态材料，可以模糊其背后的内容，反射周围内容的颜色和光线，并对触摸和指针交互做出反应。涵盖 SwiftUI、UIKit 和 WidgetKit 集成。

## 何时激活

- 使用新的设计语言构建或更新适用于 iOS 26+ 的应用程序
- 实施玻璃风格的按钮、卡片、工具栏或容器
- 在玻璃元素之间创建变形过渡
- 将液体玻璃效果应用于小部件
- 将现有的模糊/材质效果迁移到新的 Liquid Glass API

## 核心模式——SwiftUI

### 基本玻璃效果

将液体玻璃添加到任何视图的最简单方法：```swift
Text("Hello, World!")
    .font(.title)
    .padding()
    .glassEffect()  // Default: regular variant, capsule shape
```### 自定义形状和色调```swift
Text("Hello, World!")
    .font(.title)
    .padding()
    .glassEffect(.regular.tint(.orange).interactive(), in: .rect(cornerRadius: 16.0))
```关键定制选项：
- `.regular` — 标准玻璃效果
- `.tint(Color)` — 添加色调以突出显示
- `.interactive()` — 对触摸和指针交互做出反应
- 形状：`.capsule`（默认）、`.rect(cornerRadius:)`、`.circle`

### 玻璃按钮样式```swift
Button("Click Me") { /* action */ }
    .buttonStyle(.glass)

Button("Important") { /* action */ }
    .buttonStyle(.glassProminent)
```### 用于多个元素的 GlassEffectContainer

始终将多个玻璃视图包装在一个容器中以提高性能和变形：```swift
GlassEffectContainer(spacing: 40.0) {
    HStack(spacing: 40.0) {
        Image(systemName: "scribble.variable")
            .frame(width: 80.0, height: 80.0)
            .font(.system(size: 36))
            .glassEffect()

        Image(systemName: "eraser.fill")
            .frame(width: 80.0, height: 80.0)
            .font(.system(size: 36))
            .glassEffect()
    }
}
```“间距”参数控制合并距离——较近的元素将它们的玻璃形状混合在一起。

### 结合玻璃效果

使用 glassEffectUnion 将多个视图组合成单个玻璃形状：```swift
@Namespace private var namespace

GlassEffectContainer(spacing: 20.0) {
    HStack(spacing: 20.0) {
        ForEach(symbolSet.indices, id: \.self) { item in
            Image(systemName: symbolSet[item])
                .frame(width: 80.0, height: 80.0)
                .glassEffect()
                .glassEffectUnion(id: item < 2 ? "group1" : "group2", namespace: namespace)
        }
    }
}
```### 变形过渡

当玻璃元素出现/消失时创建平滑变形：```swift
@State private var isExpanded = false
@Namespace private var namespace

GlassEffectContainer(spacing: 40.0) {
    HStack(spacing: 40.0) {
        Image(systemName: "scribble.variable")
            .frame(width: 80.0, height: 80.0)
            .glassEffect()
            .glassEffectID("pencil", in: namespace)

        if isExpanded {
            Image(systemName: "eraser.fill")
                .frame(width: 80.0, height: 80.0)
                .glassEffect()
                .glassEffectID("eraser", in: namespace)
        }
    }
}

Button("Toggle") {
    withAnimation { isExpanded.toggle() }
}
.buttonStyle(.glass)
```### 在侧边栏下扩展水平滚动

要允许水平滚动内容在侧边栏或检查器下方延伸，请确保“ScrollView”内容到达容器的前缘/后缘。当布局延伸到边缘时，系统会自动处理侧边栏下方的滚动行为 - 无需额外的修饰符。

## 核心模式——UIKit

### 基本 UIGlassEffect```swift
let glassEffect = UIGlassEffect()
glassEffect.tintColor = UIColor.systemBlue.withAlphaComponent(0.3)
glassEffect.isInteractive = true

let visualEffectView = UIVisualEffectView(effect: glassEffect)
visualEffectView.translatesAutoresizingMaskIntoConstraints = false
visualEffectView.layer.cornerRadius = 20
visualEffectView.clipsToBounds = true

view.addSubview(visualEffectView)
NSLayoutConstraint.activate([
    visualEffectView.centerXAnchor.constraint(equalTo: view.centerXAnchor),
    visualEffectView.centerYAnchor.constraint(equalTo: view.centerYAnchor),
    visualEffectView.widthAnchor.constraint(equalToConstant: 200),
    visualEffectView.heightAnchor.constraint(equalToConstant: 120)
])

// Add content to contentView
let label = UILabel()
label.text = "Liquid Glass"
label.translatesAutoresizingMaskIntoConstraints = false
visualEffectView.contentView.addSubview(label)
NSLayoutConstraint.activate([
    label.centerXAnchor.constraint(equalTo: visualEffectView.contentView.centerXAnchor),
    label.centerYAnchor.constraint(equalTo: visualEffectView.contentView.centerYAnchor)
])
```### 多个元素的 UIGlassContainerEffect```swift
let containerEffect = UIGlassContainerEffect()
containerEffect.spacing = 40.0

let containerView = UIVisualEffectView(effect: containerEffect)

let firstGlass = UIVisualEffectView(effect: UIGlassEffect())
let secondGlass = UIVisualEffectView(effect: UIGlassEffect())

containerView.contentView.addSubview(firstGlass)
containerView.contentView.addSubview(secondGlass)
```### 滚动边缘效果```swift
scrollView.topEdgeEffect.style = .automatic
scrollView.bottomEdgeEffect.style = .hard
scrollView.leftEdgeEffect.isHidden = true
```### 工具栏玻璃集成```swift
let favoriteButton = UIBarButtonItem(image: UIImage(systemName: "heart"), style: .plain, target: self, action: #selector(favoriteAction))
favoriteButton.hidesSharedBackground = true  // Opt out of shared glass background
```## 核心模式——WidgetKit

### 渲染模式检测```swift
struct MyWidgetView: View {
    @Environment(\.widgetRenderingMode) var renderingMode

    var body: some View {
        if renderingMode == .accented {
            // Tinted mode: white-tinted, themed glass background
        } else {
            // Full color mode: standard appearance
        }
    }
}
```### 视觉层次结构的重音组```swift
HStack {
    VStack(alignment: .leading) {
        Text("Title")
            .widgetAccentable()  // Accent group
        Text("Subtitle")
            // Primary group (default)
    }
    Image(systemName: "star.fill")
        .widgetAccentable()  // Accent group
}
```### 重音模式下的图像渲染```swift
Image("myImage")
    .widgetAccentedRenderingMode(.monochrome)
```### 容器背景```swift
VStack { /* content */ }
    .containerBackground(for: .widget) {
        Color.blue.opacity(0.2)
    }
```## 关键设计决策

|决定|理由|
|----------|------------|
| GlassEffect容器包装|性能优化，实现玻璃元素之间的变形 |
| `间距`参数 |控制合并距离 - 微调元素必须有多接近才能混合 |
| `@Namespace` + `glassEffectID` |在视图层次结构更改时实现平滑的变形过渡 |
| `interactive()` 修饰符 |明确选择触摸/指针反应 - 并非所有玻璃都应该响应 |
| UIKit 中的 UIGlassContainerEffect |与 SwiftUI 相同的容器模式以实现一致性 |
|小部件中的强调渲染模式 |当用户选择有色主屏幕时，系统会应用有色玻璃 |

## 最佳实践

- **将玻璃应用到多个同级视图时，始终使用 GlassEffectContainer** — 它可以实现变形并提高渲染性能
- **在**其他外观修饰符（框架、字体、填充）之后应用`.glassEffect()`
- **仅在响应用户交互的元素（按钮、可切换项目）上使用`.interactive()`**
- **仔细选择容器中的间距**，以控制玻璃效果合并的时间
- **在更改视图层次结构时使用`withAnimation`**以实现平滑的变形过渡
- **跨外观测试** - 浅色模式、深色模式和强调/有色模式
- **确保可访问性对比度** - 玻璃上的文字必须保持可读

## 要避免的反模式

- 在没有 GlassEffectContainer 的情况下使用多个独立的“.glassEffect()”视图
- 嵌套太多玻璃效果 - 降低性能和视觉清晰度
- 将玻璃应用于每个视图 - 为交互元素、工具栏和卡片保留
- 使用角半径时忘记 UIKit 中的 `clipsToBounds = true`
- 忽略小部件中的重音渲染模式 - 破坏主屏幕外观
- 在玻璃后面使用不透明背景 - 破坏半透明效果

## 何时使用

- 采用全新 iOS 26 设计的导航栏、工具栏和选项卡栏
- 浮动操作按钮和卡片式容器
- 需要视觉深度和触摸反馈的交互式控制
- 应与系统的液体玻璃外观集成的小部件
- 相关 UI 状态之间的变形转换