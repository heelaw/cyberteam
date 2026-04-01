# 快速测试

> 此文件使用 Swift 特定内容扩展了通用测试规则。

## 框架

使用 **Swift 测试**（“导入测试”）进行新测试。使用“@Test”和“#expect”：```swift
@Test("User creation validates email")
func userCreationValidatesEmail() throws {
    #expect(throws: ValidationError.invalidEmail) {
        try User(email: "not-an-email")
    }
}
```## Test Isolation

Each test gets a fresh instance -- set up in `init`, tear down in `deinit`. No shared mutable state between tests.

## Parameterized Tests```swift
@Test("Validates formats", arguments: ["json", "xml", "csv"])
func validatesFormat(format: String) throws {
    let parser = try Parser(format: format)
    #expect(parser.isValid)
}
```## 覆盖范围```bash
swift test --enable-code-coverage
```## 参考

请参阅技能：“swift-protocol-di-testing”，了解基于协议的依赖注入和使用 Swift 测试的模拟模式。