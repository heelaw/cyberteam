# 去安全

> 此文件使用 Go 特定内容扩展了通用安全规则。

## 秘密管理```go
apiKey := os.Getenv("OPENAI_API_KEY")
if apiKey == "" {
    log.Fatal("OPENAI_API_KEY not configured")
}
```## 安全扫描

- 使用 **gosec** 进行静态安全分析：```bash
  gosec ./...
  ```## 上下文和超时

始终使用 context.Context 进行超时控制：```go
ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
defer cancel()
```