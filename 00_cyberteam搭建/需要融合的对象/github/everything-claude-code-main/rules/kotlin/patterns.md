# Kotlin 模式

> 此文件使用 Kotlin 和 Android/KMP 特定内容扩展了 [common/patterns.md](../common/patterns.md)。

## 依赖注入

更喜欢构造函数注入。使用 Koin (KMP) 或 Hilt（仅限 Android）：```kotlin
// Koin — declare modules
val dataModule = module {
    single<ItemRepository> { ItemRepositoryImpl(get(), get()) }
    factory { GetItemsUseCase(get()) }
    viewModelOf(::ItemListViewModel)
}

// Hilt — annotations
@HiltViewModel
class ItemListViewModel @Inject constructor(
    private val getItems: GetItemsUseCase
) : ViewModel()
```## 视图模型模式

单状态对象、事件接收器、单向数据流：```kotlin
data class ScreenState(
    val items: List<Item> = emptyList(),
    val isLoading: Boolean = false
)

class ScreenViewModel(private val useCase: GetItemsUseCase) : ViewModel() {
    private val _state = MutableStateFlow(ScreenState())
    val state = _state.asStateFlow()

    fun onEvent(event: ScreenEvent) {
        when (event) {
            is ScreenEvent.Load -> load()
            is ScreenEvent.Delete -> delete(event.id)
        }
    }
}
```## 存储库模式

- `suspend` 函数返回 `Result<T>` 或自定义错误类型
- 反应流的“Flow”
- 协调本地+远程数据源```kotlin
interface ItemRepository {
    suspend fun getById(id: String): Result<Item>
    suspend fun getAll(): Result<List<Item>>
    fun observeAll(): Flow<List<Item>>
}
```## UseCase Pattern

单一责任，`operator fun invoke`：```kotlin
class GetItemUseCase(private val repository: ItemRepository) {
    suspend operator fun invoke(id: String): Result<Item> {
        return repository.getById(id)
    }
}

class GetItemsUseCase(private val repository: ItemRepository) {
    suspend operator fun invoke(): Result<List<Item>> {
        return repository.getAll()
    }
}
```## 预期/实际 (KMP)

用于特定于平台的实现：```kotlin
// commonMain
expect fun platformName(): String
expect class SecureStorage {
    fun save(key: String, value: String)
    fun get(key: String): String?
}

// androidMain
actual fun platformName(): String = "Android"
actual class SecureStorage {
    actual fun save(key: String, value: String) { /* EncryptedSharedPreferences */ }
    actual fun get(key: String): String? = null /* ... */
}

// iosMain
actual fun platformName(): String = "iOS"
actual class SecureStorage {
    actual fun save(key: String, value: String) { /* Keychain */ }
    actual fun get(key: String): String? = null /* ... */
}
```## 协程模式

- 在 ViewModel 中使用“viewModelScope”，“coroutineScope”用于结构化子工作
- 对来自冷流的 StateFlow 使用 `stateIn(viewModelScope,SharingStarted.WhileSubscribed(5_000),initialValue)`
- 当子故障应该是独立的时使用“supervisorScope”

## 使用 DSL 的构建器模式```kotlin
class HttpClientConfig {
    var baseUrl: String = ""
    var timeout: Long = 30_000
    private val interceptors = mutableListOf<Interceptor>()

    fun interceptor(block: () -> Interceptor) {
        interceptors.add(block())
    }
}

fun httpClient(block: HttpClientConfig.() -> Unit): HttpClient {
    val config = HttpClientConfig().apply(block)
    return HttpClient(config)
}

// Usage
val client = httpClient {
    baseUrl = "https://api.example.com"
    timeout = 15_000
    interceptor { AuthInterceptor(tokenProvider) }
}
```## 参考文献

有关详细的协程模式，请参阅技能：`kotlin-coroutines-flows`。
有关模块和层模式，请参阅技能：“android-clean-architecture”。