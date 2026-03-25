# Java 编码标准

Spring Boot 服务中可读、可维护的 Java (17+) 代码标准。

## 何时激活

- 在 Spring Boot 项目中编写或审查 Java 代码
- 强制命名、不变性或异常处理约定
- 使用记录、密封类或模式匹配（Java 17+）
- 审查可选、流或泛型的使用
- 构建包和项目布局

## 核心原则

- 比起聪明更喜欢清晰
- 默认情况下不可变；最小化共享可变状态
- 快速失败并出现有意义的异常
- 一致的命名和包结构

## 命名```java
// ✅ Classes/Records: PascalCase
public class MarketService {}
public record Money(BigDecimal amount, Currency currency) {}

// ✅ Methods/fields: camelCase
private final MarketRepository marketRepository;
public Market findBySlug(String slug) {}

// ✅ Constants: UPPER_SNAKE_CASE
private static final int MAX_PAGE_SIZE = 100;
```## 不变性```java
// ✅ Favor records and final fields
public record MarketDto(Long id, String name, MarketStatus status) {}

public class Market {
  private final Long id;
  private final String name;
  // getters only, no setters
}
```## 可选用法```java
// ✅ Return Optional from find* methods
Optional<Market> market = marketRepository.findBySlug(slug);

// ✅ Map/flatMap instead of get()
return market
    .map(MarketResponse::from)
    .orElseThrow(() -> new EntityNotFoundException("Market not found"));
```## 流媒体最佳实践```java
// ✅ Use streams for transformations, keep pipelines short
List<String> names = markets.stream()
    .map(Market::name)
    .filter(Objects::nonNull)
    .toList();

// ❌ Avoid complex nested streams; prefer loops for clarity
```## 例外情况

- 对域错误使用未经检查的异常；用上下文包装技术异常
- 创建特定于域的异常（例如“MarketNotFoundException”）
- 避免广泛的“catch（Exception ex）”，除非集中重新抛出/记录```java
throw new MarketNotFoundException(slug);
```## 泛型和类型安全

- 避免原始类型；声明通用参数
- 对于可重用的实用程序，更喜欢有界泛型```java
public <T extends Identifiable> Map<Long, T> indexById(Collection<T> items) { ... }
```## 项目结构（Maven/Gradle）```
src/main/java/com/example/app/
  config/
  controller/
  service/
  repository/
  domain/
  dto/
  util/
src/main/resources/
  application.yml
src/test/java/... (mirrors main)
```## 格式和样式

- 一致使用 2 或 4 个空格（项目标准）
- 每个文件一个公共顶级类型
- 保持方法简短、重点突出；提取助手
- 顺序成员：常量、字段、构造函数、公共方法、受保护的、私有的

## 要避免的代码异味

- 长参数列表→使用DTO/构建器
- 深度嵌套→提前返回
- 幻数 → 命名常量
- 静态可变状态→更喜欢依赖注入
- 静默捕获块→记录并执行或重新抛出

## 日志记录```java
private static final Logger log = LoggerFactory.getLogger(MarketService.class);
log.info("fetch_market slug={}", slug);
log.error("failed_fetch_market slug={}", slug, ex);
```## 空处理

- 仅在不可避免时才接受“@Nullable”；否则使用`@NonNull`
- 对输入使用 Bean 验证（`@NotNull`、`@NotBlank`）

## 测试期望

- JUnit 5 + AssertJ 用于流畅的断言
- Mockito 用于嘲笑；尽可能避免部分模拟
- 支持确定性测试；没有隐藏的睡眠

**记住**：保持代码的意图、类型和可观察性。除非证明有必要，否则应针对可维护性进行优化而不是微优化。