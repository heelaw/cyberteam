# Java 编码风格

> 此文件使用 Java 特定内容扩展了 [common/coding-style.md](../common/coding-style.md)。

## 格式化

- **google-java-format** 或 **Checkstyle**（Google 或 Sun 风格）用于强制执行
- 每个文件一个公共顶级类型
- 一致的缩进：2或4个空格（符合项目标准）
- 成员顺序：常量、字段、构造函数、公共方法、受保护的、私有的

## 不变性

- 对于值类型更喜欢“record”（Java 16+）
- 默认情况下将字段标记为“final”——仅在需要时使用可变状态
- 从公共 API 返回防御副本：`List.copyOf()`、`Map.copyOf()`、`Set.copyOf()`
- 写入时复制：返回新实例而不是改变现有实例```java
// GOOD — immutable value type
public record OrderSummary(Long id, String customerName, BigDecimal total) {}

// GOOD — final fields, no setters
public class Order {
    private final Long id;
    private final List<LineItem> items;

    public List<LineItem> getItems() {
        return List.copyOf(items);
    }
}
```## 命名

遵循标准 Java 约定：
- 用于类、接口、记录、枚举的“PascalCase”
- 方法、字段、参数、局部变量使用“camelCase”
- “SCREAMING_SNAKE_CASE”代表“static Final”常量
- 包：全部小写，反向域名（`com.example.app.service`）

## 现代 Java 特性

使用现代语言功能可以提高清晰度：
- DTO 和值类型的 **记录** (Java 16+)
- 用于封闭类型层次结构的 **密封类** (Java 17+)
- **模式匹配**与 `instanceof` — 无显式强制转换 (Java 16+)
- **多行字符串的文本块** - SQL、JSON 模板（Java 15+）
- **使用箭头语法切换表达式** (Java 14+)
- **开关中的模式匹配** — 详尽的密封类型处理（Java 21+）```java
// Pattern matching instanceof
if (shape instanceof Circle c) {
    return Math.PI * c.radius() * c.radius();
}

// Sealed type hierarchy
public sealed interface PaymentMethod permits CreditCard, BankTransfer, Wallet {}

// Switch expression
String label = switch (status) {
    case ACTIVE -> "Active";
    case SUSPENDED -> "Suspended";
    case CLOSED -> "Closed";
};
```## 可选用法

- 从可能没有结果的查找方法返回“Optional<T>”
- 使用 `map()`、`flatMap()`、`orElseThrow()` — 切勿在没有 `isPresent()` 的情况下调用 `get()`
- 切勿使用“Optional”作为字段类型或方法参数```java
// GOOD
return repository.findById(id)
    .map(ResponseDto::from)
    .orElseThrow(() -> new OrderNotFoundException(id));

// BAD — Optional as parameter
public void process(Optional<String> name) {}
```## 错误处理

- 对于域错误更喜欢未经检查的异常
- 创建扩展“RuntimeException”的特定于域的异常
- 避免广泛的“catch（Exception e）”，除非在顶级处理程序中
- 在异常消息中包含上下文```java
public class OrderNotFoundException extends RuntimeException {
    public OrderNotFoundException(Long id) {
        super("Order not found: id=" + id);
    }
}
```## 流

- 使用流进行转换；保持管道较短（最多 3-4 次操作）
- 可读时首选方法引用：`.map(Order::getTotal)`
- 避免流操作中的副作用
- 对于复杂的逻辑，更喜欢循环而不是复杂的流管道

## 参考文献

请参阅技能：“java-coding-standards”，了解完整的编码标准和示例。
有关 JPA/Hibernate 实体设计模式，请参阅技能：“jpa-patterns”。