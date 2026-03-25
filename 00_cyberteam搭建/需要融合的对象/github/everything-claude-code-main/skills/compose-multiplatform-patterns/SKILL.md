# 构建多平台模式

使用 Compose Multiplatform 和 Jetpack Compose 跨 Android、iOS、桌面和 Web 构建共享 UI 的模式。涵盖状态管理、导航、主题和性能。

## 何时激活

- 构建 Compose UI（Jetpack Compose 或 Compose 多平台）
- 使用 ViewModel 和 Compose 状态管理 UI 状态
- 在KMP或Android项目中实现导航
- 设计可重用的可组合项和设计系统
- 优化重组和渲染性能

## 状态管理

### ViewModel + 单状态对象

对屏幕状态使用单个数据类。将其公开为“StateFlow”并在 Compose 中收集：```kotlin
data class ItemListState(
    val items: List<Item> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
    val searchQuery: String = ""
)

class ItemListViewModel(
    private val getItems: GetItemsUseCase
) : ViewModel() {
    private val _state = MutableStateFlow(ItemListState())
    val state: StateFlow<ItemListState> = _state.asStateFlow()

    fun onSearch(query: String) {
        _state.update { it.copy(searchQuery = query) }
        loadItems(query)
    }

    private fun loadItems(query: String) {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true) }
            getItems(query).fold(
                onSuccess = { items -> _state.update { it.copy(items = items, isLoading = false) } },
                onFailure = { e -> _state.update { it.copy(error = e.message, isLoading = false) } }
            )
        }
    }
}
```### 在 Compose 中收集状态```kotlin
@Composable
fun ItemListScreen(viewModel: ItemListViewModel = koinViewModel()) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    ItemListContent(
        state = state,
        onSearch = viewModel::onSearch
    )
}

@Composable
private fun ItemListContent(
    state: ItemListState,
    onSearch: (String) -> Unit
) {
    // Stateless composable — easy to preview and test
}
```### 事件接收器模式

对于复杂的屏幕，请使用事件的密封接口而不是多个回调 lambda：```kotlin
sealed interface ItemListEvent {
    data class Search(val query: String) : ItemListEvent
    data class Delete(val itemId: String) : ItemListEvent
    data object Refresh : ItemListEvent
}

// In ViewModel
fun onEvent(event: ItemListEvent) {
    when (event) {
        is ItemListEvent.Search -> onSearch(event.query)
        is ItemListEvent.Delete -> deleteItem(event.itemId)
        is ItemListEvent.Refresh -> loadItems(_state.value.searchQuery)
    }
}

// In Composable — single lambda instead of many
ItemListContent(
    state = state,
    onEvent = viewModel::onEvent
)
```## 导航

### 类型安全导航（Compose Navigation 2.8+）

将路由定义为“@Serialized”对象：```kotlin
@Serializable data object HomeRoute
@Serializable data class DetailRoute(val id: String)
@Serializable data object SettingsRoute

@Composable
fun AppNavHost(navController: NavHostController = rememberNavController()) {
    NavHost(navController, startDestination = HomeRoute) {
        composable<HomeRoute> {
            HomeScreen(onNavigateToDetail = { id -> navController.navigate(DetailRoute(id)) })
        }
        composable<DetailRoute> { backStackEntry ->
            val route = backStackEntry.toRoute<DetailRoute>()
            DetailScreen(id = route.id)
        }
        composable<SettingsRoute> { SettingsScreen() }
    }
}
```### 对话框和底部工作表导航

使用“dialog()”和覆盖模式而不是命令式显示/隐藏：```kotlin
NavHost(navController, startDestination = HomeRoute) {
    composable<HomeRoute> { /* ... */ }
    dialog<ConfirmDeleteRoute> { backStackEntry ->
        val route = backStackEntry.toRoute<ConfirmDeleteRoute>()
        ConfirmDeleteDialog(
            itemId = route.itemId,
            onConfirm = { navController.popBackStack() },
            onDismiss = { navController.popBackStack() }
        )
    }
}
```## 可组合设计

### 基于插槽的 API

使用插槽参数设计可组合项以实现灵活性：```kotlin
@Composable
fun AppCard(
    modifier: Modifier = Modifier,
    header: @Composable () -> Unit = {},
    content: @Composable ColumnScope.() -> Unit,
    actions: @Composable RowScope.() -> Unit = {}
) {
    Card(modifier = modifier) {
        Column {
            header()
            Column(content = content)
            Row(horizontalArrangement = Arrangement.End, content = actions)
        }
    }
}
```### 修饰符排序

修饰符顺序很重要 - 按以下顺序应用：```kotlin
Text(
    text = "Hello",
    modifier = Modifier
        .padding(16.dp)          // 1. Layout (padding, size)
        .clip(RoundedCornerShape(8.dp))  // 2. Shape
        .background(Color.White) // 3. Drawing (background, border)
        .clickable { }           // 4. Interaction
)
```## KMP 平台特定的 UI

### 平台可组合项的预期/实际```kotlin
// commonMain
@Composable
expect fun PlatformStatusBar(darkIcons: Boolean)

// androidMain
@Composable
actual fun PlatformStatusBar(darkIcons: Boolean) {
    val systemUiController = rememberSystemUiController()
    SideEffect { systemUiController.setStatusBarColor(Color.Transparent, darkIcons) }
}

// iosMain
@Composable
actual fun PlatformStatusBar(darkIcons: Boolean) {
    // iOS handles this via UIKit interop or Info.plist
}
```## 性能

### 可跳过重组的稳定类型

当所有属性都稳定时，将类标记为“@Stable”或“@Immutable”：```kotlin
@Immutable
data class ItemUiModel(
    val id: String,
    val title: String,
    val description: String,
    val progress: Float
)
```### 正确使用 `key()` 和惰性列表```kotlin
LazyColumn {
    items(
        items = items,
        key = { it.id }  // Stable keys enable item reuse and animations
    ) { item ->
        ItemRow(item = item)
    }
}
```### 使用 `衍生状态` 延迟读取```kotlin
val listState = rememberLazyListState()
val showScrollToTop by remember {
    derivedStateOf { listState.firstVisibleItemIndex > 5 }
}
```### 避免重组中的分配```kotlin
// BAD — new lambda and list every recomposition
items.filter { it.isActive }.forEach { ActiveItem(it, onClick = { handle(it) }) }

// GOOD — key each item so callbacks stay attached to the right row
val activeItems = remember(items) { items.filter { it.isActive } }
activeItems.forEach { item ->
    key(item.id) {
        ActiveItem(item, onClick = { handle(item) })
    }
}
```## 主题化

### Material 3 动态主题```kotlin
@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            if (darkTheme) dynamicDarkColorScheme(LocalContext.current)
            else dynamicLightColorScheme(LocalContext.current)
        }
        darkTheme -> darkColorScheme()
        else -> lightColorScheme()
    }

    MaterialTheme(colorScheme = colorScheme, content = content)
}
```## 要避免的反模式

- 当“MutableStateFlow”与“collectAsStateWithLifecycle”对生命周期更安全时，在 ViewModel 中使用“mutableStateOf”
- 将 `NavController` 深入到可组合项中 — 改为传递 lambda 回调
- `@Composable` 函数内的大量计算 — 移至 ViewModel 或 `记住 {}`
- 使用 `LaunchedEffect(Unit)` 作为 ViewModel init 的替代品 - 它会在某些设置中的配置更改时重新运行
- 在可组合参数中创建新的对象实例 - 导致不必要的重组

## 参考文献

有关模块结构和分层，请参阅技能：`android-clean-architecture`。
有关协程和流模式，请参阅技能：“kotlin-coroutines-flows”。