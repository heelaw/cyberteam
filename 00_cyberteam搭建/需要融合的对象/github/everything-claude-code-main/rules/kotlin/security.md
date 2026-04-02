# Kotlin 安全

> 此文件使用 Kotlin 和 Android/KMP 特定内容扩展了 [common/security.md](../common/security.md)。

## 秘密管理

- 切勿在源代码中对 API 密钥、令牌或凭据进行硬编码
- 使用“local.properties”（git-ignored）作为本地开发秘密
- 使用从 CI 密钥生成的“BuildConfig”字段进行发布版本
- 使用“EncryptedSharedPreferences”（Android）或钥匙串（iOS）进行运行时秘密存储```kotlin
// BAD
val apiKey = "sk-abc123..."

// GOOD — from BuildConfig (generated at build time)
val apiKey = BuildConfig.API_KEY

// GOOD — from secure storage at runtime
val token = secureStorage.get("auth_token")
```## 网络安全

- 仅使用 HTTPS — 配置“network_security_config.xml”以阻止明文
- 使用 OkHttp `CertificatePinner` 或 Ktor 等效项为敏感端点固定证书
- 在所有 HTTP 客户端上设置超时 — 切勿保留默认值（可能是无限的）
- 使用前验证并清理所有服务器响应```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
    <base-config cleartextTrafficPermitted="false" />
</network-security-config>
```## 输入验证

- 在处理或发送到 API 之前验证所有用户输入
- 对 Room/SQLDelight 使用参数化查询 — 切勿将用户输入连接到 SQL 中
- 清理用户输入的文件路径以防止路径遍历```kotlin
// BAD — SQL injection
@Query("SELECT * FROM items WHERE name = '$input'")

// GOOD — parameterized
@Query("SELECT * FROM items WHERE name = :input")
fun findByName(input: String): List<ItemEntity>
```## 数据保护

- 对 Android 上的敏感键值数据使用“EncryptedSharedPreferences”
- 使用具有显式字段名称的“@Serialized”——不要泄漏内部属性名称
- 不再需要时从内存中清除敏感数据
- 对序列化类使用“@Keep”或 ProGuard 规则以防止名称损坏

## 身份验证

- 将令牌存储在安全存储中，而不是普通的 SharedPreferences 中
- 通过正确的 401/403 处理实现令牌刷新
- 注销时清除所有身份验证状态（令牌、缓存的用户数据、cookie）
- 使用生物识别身份验证（“BiometricPrompt”）进行敏感操作

## ProGuard / R8

- 保留所有序列化模型的规则（`@Serialized`、Gson、Moshi）
- 保留基于反射的库的规则（Koin、Retrofit）
- 测试发布版本 - 混淆可能会默默地破坏序列化

## WebView 安全

- 除非明确需要，否则禁用 JavaScript：`settings.javaScriptEnabled = false`
- 在 WebView 中加载之前验证 URL
- 切勿公开访问敏感数据的“@JavascriptInterface”方法
- 使用“WebViewClient.shouldOverrideUrlLoading()”控制导航