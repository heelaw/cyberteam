# Rust 安全

> 此文件使用 Rust 特定的内容扩展了 [common/security.md](../common/security.md)。

## 秘密管理

- 切勿在源代码中对 API 密钥、令牌或凭据进行硬编码
- 使用环境变量：`std::env::var("API_KEY")`
- 如果启动时缺少所需的机密，则会快速失败
- 将`.env`文件保存在`.gitignore`中```rust
// BAD
const API_KEY: &str = "sk-abc123...";

// GOOD — environment variable with early validation
fn load_api_key() -> anyhow::Result<String> {
    std::env::var("PAYMENT_API_KEY")
        .context("PAYMENT_API_KEY must be set")
}
```## SQL注入预防

- 始终使用参数化查询 — 切勿将用户输入格式化为 SQL 字符串
- 使用带有绑定参数的查询生成器或 ORM（sqlx、diesel、sea-orm）```rust
// BAD — SQL injection via format string
let query = format!("SELECT * FROM users WHERE name = '{name}'");
sqlx::query(&query).fetch_one(&pool).await?;

// GOOD — parameterized query with sqlx
// Placeholder syntax varies by backend: Postgres: $1  |  MySQL: ?  |  SQLite: $1
sqlx::query("SELECT * FROM users WHERE name = $1")
    .bind(&name)
    .fetch_one(&pool)
    .await?;
```## 输入验证

- 在处理之前在系统边界验证所有用户输入
- 使用类型系统来强制不变量（新类型模式）
- 解析，不验证——将非结构化数据转换为边界处的类型化结构
- 拒绝无效输入并提供清晰的错误消息```rust
// Parse, don't validate — invalid states are unrepresentable
pub struct Email(String);

impl Email {
    pub fn parse(input: &str) -> Result<Self, ValidationError> {
        let trimmed = input.trim();
        let at_pos = trimmed.find('@')
            .filter(|&p| p > 0 && p < trimmed.len() - 1)
            .ok_or_else(|| ValidationError::InvalidEmail(input.to_string()))?;
        let domain = &trimmed[at_pos + 1..];
        if trimmed.len() > 254 || !domain.contains('.') {
            return Err(ValidationError::InvalidEmail(input.to_string()));
        }
        // For production use, prefer a validated email crate (e.g., `email_address`)
        Ok(Self(trimmed.to_string()))
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}
```## 不安全代码

- 最小化“不安全”块——更喜欢安全抽象
- 每个“不安全”块必须有一个“// SAFETY：”注释来解释不变性
- 为了方便起见，切勿使用“不安全”来绕过借用检查器
- 在审查期间审核所有“不安全”代码——这是一个没有理由的危险信号
- 更喜欢 C 库周围的“安全”FFI 包装器```rust
// GOOD — safety comment documents ALL required invariants
let widget: &Widget = {
    // SAFETY: `ptr` is non-null, aligned, points to an initialized Widget,
    // and no mutable references or mutations exist for its lifetime.
    unsafe { &*ptr }
};

// BAD — no safety justification
unsafe { &*ptr }
```## 依赖安全

- 运行“cargoaudit”来扫描依赖项中的已知 CVE
- 运行“货物拒绝检查”以确保许可证和咨询合规性
- 使用“货物树”来审核传递依赖关系
- 保持依赖项更新 — 设置 Dependabot 或 Renovate
- 最大限度地减少依赖项数量——在添加新箱子之前进行评估```bash
# Security audit
cargo audit

# Deny advisories, duplicate versions, and restricted licenses
cargo deny check

# Inspect dependency tree
cargo tree
cargo tree -d  # Show duplicates only
```## 错误信息

- 切勿在 API 响应中暴露内部路径、堆栈跟踪或数据库错误
- 在服务器端记录详细错误；将通用消息返回给客户端
- 使用“tracing”或“log”进行结构化服务器端日志记录```rust
// Map errors to appropriate status codes and generic messages
// (Example uses axum; adapt the response type to your framework)
match order_service.find_by_id(id) {
    Ok(order) => Ok((StatusCode::OK, Json(order))),
    Err(ServiceError::NotFound(_)) => {
        tracing::info!(order_id = id, "order not found");
        Err((StatusCode::NOT_FOUND, "Resource not found"))
    }
    Err(e) => {
        tracing::error!(order_id = id, error = %e, "unexpected error");
        Err((StatusCode::INTERNAL_SERVER_ERROR, "Internal server error"))
    }
}
```## 参考文献

有关不安全代码指南和所有权模式，请参阅技能：“rust-patterns”。
有关一般安全检查表，请参阅技能：“安全审查”。