# 进行代码审查

此命令调用 **go-reviewer** 代理来进行全面的特定于 Go 的代码审查。

## 该命令的作用

1. **识别 Go 更改**：通过 `git diff` 查找修改后的 `.go` 文件
2. **运行静态分析**：执行 `go vet`、`staticcheck` 和 `golangci-lint`
3. **安全扫描**：检查SQL注入、命令注入、竞争条件
4. **并发审查**：分析goroutine安全性、通道使用情况、互斥模式
5. **惯用的 Go Check**：验证代码是否遵循 Go 约定和最佳实践
6. **生成报告**：按严重程度对问题进行分类

## 何时使用

在以下情况下使用“/go-review”：
- 编写或修改Go代码后
- 在提交 Go 更改之前
- 使用 Go 代码审查拉取请求
- 加入新的 Go 代码库
- 学习惯用的围棋模式

## 评论类别

### 严重（必须修复）
- SQL/命令注入漏洞
- 没有同步的竞争条件
- Goroutine 泄漏
- 硬编码凭证
- 不安全的指针使用
- 忽略关键路径中的错误

### 高（应该修复）
- 缺少上下文错误包装
- 恐慌而不是错误返回
- 上下文未传播
- 无缓冲的通道导致死锁
- 接口不满足错误
- 缺少互斥锁保护

### 中（考虑）
- 非惯用的代码模式
- 缺少关于导出的 godoc 注释
- 低效的字符串连接
- 切片未预先分配
- 未使用表驱动测试

## 自动检查运行```bash
# Static analysis
go vet ./...

# Advanced checks (if installed)
staticcheck ./...
golangci-lint run

# Race detection
go build -race ./...

# Security vulnerabilities
govulncheck ./...
```## 用法示例```text
User: /go-review

Agent:
# Go Code Review Report

## Files Reviewed
- internal/handler/user.go (modified)
- internal/service/auth.go (modified)

## Static Analysis Results
✓ go vet: No issues
✓ staticcheck: No issues

## Issues Found

[CRITICAL] Race Condition
File: internal/service/auth.go:45
Issue: Shared map accessed without synchronization
```去
var cache = map[string]*Session{} // 并发访问！

func GetSession(id 字符串) *Session {
    return cache[id] // 竞态条件
}```
Fix: Use sync.RWMutex or sync.Map
```去
变量（
    缓存 = 地图[字符串]*会话{}
    缓存Mu同步.RWMutex
）

func GetSession(id 字符串) *Session {
    cacheMu.RLock()
    延迟cacheMu.RUNlock()
    返回缓存[id]
}```

[HIGH] Missing Error Context
File: internal/handler/user.go:28
Issue: Error returned without context
```去
return err // 无上下文```
Fix: Wrap with context
```去
return fmt.Errorf("获取用户 %s: %w", userID, err)```

## Summary
- CRITICAL: 1
- HIGH: 1
- MEDIUM: 0

Recommendation: ❌ Block merge until CRITICAL issue is fixed
```## 批准标准

|状态 |状况 |
|--------|------------|
| ✅ 批准 |没有严重或严重问题 |
| ⚠️警告|仅中等问题（谨慎合并）|
| ❌ 块 |发现严重或严重问题 |

## 与其他命令集成

- 首先使用 `/go-test` 确保测试通过
- 如果发生构建错误，请使用“/go-build”
- 提交前使用“/go-review”
- 对于非 Go 特定问题使用“/code-review”

## 相关

- 代理：`agents/go-reviewer.md`
- 技能：`技能/golang-patterns/`、`技能/golang-testing/`