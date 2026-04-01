# Java 安全

> 此文件使用 Java 特定内容扩展了 [common/security.md](../common/security.md)。

## 秘密管理

- 切勿在源代码中对 API 密钥、令牌或凭据进行硬编码
- 使用环境变量：`System.getenv("API_KEY")`
- 使用秘密管理器（Vault、AWS Secrets Manager）来存储生产秘密
- 将本地配置文件与机密保存在“.gitignore”中```java
// BAD
private static final String API_KEY = "sk-abc123...";

// GOOD — environment variable
String apiKey = System.getenv("PAYMENT_API_KEY");
Objects.requireNonNull(apiKey, "PAYMENT_API_KEY must be set");
```## SQL注入预防

- 始终使用参数化查询 — 切勿将用户输入连接到 SQL 中
- 使用“PreparedStatement”或框架的参数化查询 API
- 验证和清理本机查询中使用的任何输入```java
// BAD — SQL injection via string concatenation
Statement stmt = conn.createStatement();
String sql = "SELECT * FROM orders WHERE name = '" + name + "'";
stmt.executeQuery(sql);

// GOOD — PreparedStatement with parameterized query
PreparedStatement ps = conn.prepareStatement("SELECT * FROM orders WHERE name = ?");
ps.setString(1, name);

// GOOD — JDBC template
jdbcTemplate.query("SELECT * FROM orders WHERE name = ?", mapper, name);
```## 输入验证

- 在处理之前在系统边界验证所有用户输入
- 使用验证框架时，在 DTO 上使用 Bean 验证（`@NotNull`、`@NotBlank`、`@Size`）
- 使用前清理文件路径和用户提供的字符串
- 拒绝验证失败的输入并提供清晰的错误消息```java
// Validate manually in plain Java
public Order createOrder(String customerName, BigDecimal amount) {
    if (customerName == null || customerName.isBlank()) {
        throw new IllegalArgumentException("Customer name is required");
    }
    if (amount == null || amount.compareTo(BigDecimal.ZERO) <= 0) {
        throw new IllegalArgumentException("Amount must be positive");
    }
    return new Order(customerName, amount);
}
```## 身份验证和授权

- 切勿实现自定义身份验证加密 - 使用已建立的库
- 使用 bcrypt 或 Argon2 存储密码，切勿使用 MD5/SHA1
- 在服务边界强制执行授权检查
- 清除日志中的敏感数据 — 绝不记录密码、令牌或 PII

## 依赖安全

- 运行“mvn dependency:tree”或“./gradlew dependency”来审核传递依赖项
- 使用 OWASP Dependency-Check 或 Snyk 扫描已知的 CVE
- 保持依赖项更新 — 设置 Dependabot 或 Renovate

## 错误信息

- 切勿在 API 响应中暴露堆栈跟踪、内部路径或 SQL 错误
- 将异常映射到处理程序边界处的安全、通用客户端消息
- 在服务器端记录详细错误；将通用消息返回给客户端```java
// Log the detail, return a generic message
try {
    return orderService.findById(id);
} catch (OrderNotFoundException ex) {
    log.warn("Order not found: id={}", id);
    return ApiResponse.error("Resource not found");  // generic, no internals
} catch (Exception ex) {
    log.error("Unexpected error processing order id={}", id, ex);
    return ApiResponse.error("Internal server error");  // never expose ex.getMessage()
}
```## References

See skill: `springboot-security` for Spring Security authentication and authorization patterns.
See skill: `security-review` for general security checklists.