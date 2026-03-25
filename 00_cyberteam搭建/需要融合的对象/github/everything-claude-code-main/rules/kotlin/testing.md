# Kotlin 测试

> 此文件使用 Kotlin 和 Android/KMP 特定内容扩展了 [common/testing.md](../common/testing.md)。

## 测试框架

- **kotlin.test** 用于多平台 (KMP) — `@Test`、`assertEquals`、`assertTrue`
- **JUnit 4/5** 用于 Android 特定测试
- **Turbine** 用于测试 Flows 和 StateFlow
- **kotlinx-coroutines-test** 用于协程测试（`runTest`、`TestDispatcher`）

## 使用 Turbine 进行 ViewModel 测试```kotlin
@Test
fun `loading state emitted then data`() = runTest {
    val repo = FakeItemRepository()
    repo.addItem(testItem)
    val viewModel = ItemListViewModel(GetItemsUseCase(repo))

    viewModel.state.test {
        assertEquals(ItemListState(), awaitItem())     // initial state
        viewModel.onEvent(ItemListEvent.Load)
        assertTrue(awaitItem().isLoading)               // loading
        assertEquals(listOf(testItem), awaitItem().items) // loaded
    }
}
```## 假冒模拟

与模拟框架相比，更喜欢手写的伪造品：```kotlin
class FakeItemRepository : ItemRepository {
    private val items = mutableListOf<Item>()
    var fetchError: Throwable? = null

    override suspend fun getAll(): Result<List<Item>> {
        fetchError?.let { return Result.failure(it) }
        return Result.success(items.toList())
    }

    override fun observeAll(): Flow<List<Item>> = flowOf(items.toList())

    fun addItem(item: Item) { items.add(item) }
}
```## 协程测试```kotlin
@Test
fun `parallel operations complete`() = runTest {
    val repo = FakeRepository()
    val result = loadDashboard(repo)
    advanceUntilIdle()
    assertNotNull(result.items)
    assertNotNull(result.stats)
}
```使用“runTest”——它会自动提前虚拟时间并提供“TestScope”。

## Ktor 模拟引擎```kotlin
val mockEngine = MockEngine { request ->
    when (request.url.encodedPath) {
        "/api/items" -> respond(
            content = Json.encodeToString(testItems),
            headers = headersOf(HttpHeaders.ContentType, ContentType.Application.Json.toString())
        )
        else -> respondError(HttpStatusCode.NotFound)
    }
}

val client = HttpClient(mockEngine) {
    install(ContentNegotiation) { json() }
}
```## Room/SQLDelight 测试

- Room：使用“Room.inMemoryDatabaseBuilder()”进行内存测试
- SQLDelight：使用“JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY)”进行 JVM 测试```kotlin
@Test
fun `insert and query items`() = runTest {
    val driver = JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY)
    Database.Schema.create(driver)
    val db = Database(driver)

    db.itemQueries.insert("1", "Sample Item", "description")
    val items = db.itemQueries.getAll().executeAsList()
    assertEquals(1, items.size)
}
```## 测试命名

使用反引号引起来的描述性名称：```kotlin
@Test
fun `search with empty query returns all items`() = runTest { }

@Test
fun `delete item emits updated list without deleted item`() = runTest { }
```## 测试组织```
src/
├── commonTest/kotlin/     # Shared tests (ViewModel, UseCase, Repository)
├── androidUnitTest/kotlin/ # Android unit tests (JUnit)
├── androidInstrumentedTest/kotlin/  # Instrumented tests (Room, UI)
└── iosTest/kotlin/        # iOS-specific tests
```最小测试覆盖率：每个功能的 ViewModel + UseCase。