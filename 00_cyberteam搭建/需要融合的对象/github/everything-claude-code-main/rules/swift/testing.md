# 快速测试

> 此文件使用 Swift 特定内容扩展了 [common/testing.md](../common/testing.md)。

## 框架

使用 **Swift 测试**（“导入测试”）进行新测试。使用“@Test”和“#expect”：```swift
@Test("User creation validates email")
func userCreationValidatesEmail() throws {
    #expect(throws: ValidationError.invalidEmail) {
        try User(email: "not-an-email")
    }
}
```## 测试隔离

每个测试都会获得一个新的实例——在“init”中设置，在“deinit”中拆除。测试之间没有共享可变状态。

## 参数化测试```swift
@Test("Validates formats", arguments: ["json", "xml", "csv"])
func validatesFormat(format: String) throws {
    let parser = try Parser(format: format)
    #expect(parser.isValid)
}
```## 覆盖范围```bash
swift test --enable-code-coverage
```## 参考

请参阅技能：“swift-protocol-di-testing”，了解基于协议的依赖注入和使用 Swift 测试的模拟模式。