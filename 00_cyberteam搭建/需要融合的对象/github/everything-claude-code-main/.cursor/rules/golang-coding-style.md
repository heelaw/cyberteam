# Go 编码风格

> 该文件使用 Go 特定内容扩展了通用编码风格规则。

## 格式化

- **gofmt** 和 **goimports** 是强制性的——没有风格争论

## 设计原则

- 接受接口，返回结构
- 保持接口较小（1-3 种方法）

## 错误处理

始终用上下文包装错误：```go
if err != nil {
    return fmt.Errorf("failed to create user: %w", err)
}
```## 参考

请参阅技能：“golang-patterns”，了解全面的 Go 习惯用法和模式。