# 快速安全

> 此文件使用 Swift 特定内容扩展了 [common/security.md](../common/security.md)。

## 秘密管理

- 对敏感数据（令牌、密码、密钥）使用**钥匙串服务** - 切勿使用“UserDefaults”
- 使用环境变量或“.xcconfig”文件作为构建时的秘密
- 切勿在源代码中硬编码秘密 - 反编译工具可以轻松提取它们```swift
let apiKey = ProcessInfo.processInfo.environment["API_KEY"]
guard let apiKey, !apiKey.isEmpty else {
    fatalError("API_KEY not configured")
}
```## 交通安全

- 默认情况下强制执行应用程序传输安全性 (ATS) — 不要禁用它
- 对关键端点使用证书固定
- 验证所有服务器证书

## 输入验证

- 在显示之前清理所有用户输入以防止注入
- 使用“URL(string:)”进行验证而不是强制解包
- 在处理之前验证来自外部来源（API、深层链接、粘贴板）的数据