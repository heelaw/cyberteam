# Kotlin 安全

> 此文件使用 Kotlin 特定内容扩展了通用安全规则。

## 秘密管理```kotlin
val apiKey = System.getenv("API_KEY")
    ?: throw IllegalStateException("API_KEY not configured")
```## SQL注入预防

始终使用 Exposed 的参数化查询：```kotlin
// Good: Parameterized via Exposed DSL
UsersTable.selectAll().where { UsersTable.email eq email }

// Bad: String interpolation in raw SQL
exec("SELECT * FROM users WHERE email = '$email'")
```## 身份验证

将 Ktor 的 Auth 插件与 JWT 结合使用：```kotlin
install(Authentication) {
    jwt("jwt") {
        verifier(
            JWT.require(Algorithm.HMAC256(secret))
                .withAudience(audience)
                .withIssuer(issuer)
                .build()
        )
        validate { credential ->
            val payload = credential.payload
            if (payload.audience.contains(audience) &&
                payload.issuer == issuer &&
                payload.subject != null) {
                JWTPrincipal(payload)
            } else {
                null
            }
        }
    }
}
```## 空安全作为安全

Kotlin 的类型系统可以防止与 null 相关的漏洞——避免使用 `!!` 来维持这种保证。