# 构建并修复

此命令调用 **go-build-resolver** 代理，以最小的更改增量修复 Go 构建错误。

## 该命令的作用

1. **运行诊断**：执行 `go build`、`go vet`、`staticcheck`
2. **解析错误**：按文件分组并按严重性排序
3. **增量修复**：一次一个错误
4. **验证每个修复**：每次更改后重新运行构建
5. **报告摘要**：显示已修复的内容和剩余的内容

## 何时使用

在以下情况下使用“/go-build”：
- `go build ./...` 失败并出现错误
- `去兽医./...` 报告问题
- `golangci-lint run` 显示警告
- 模块依赖关系被破坏
- 拉取破坏构建的更改后

## 诊断命令运行```bash
# Primary build check
go build ./...

# Static analysis
go vet ./...

# Extended linting (if available)
staticcheck ./...
golangci-lint run

# Module issues
go mod verify
go mod tidy -v
```## 会话示例```text
User: /go-build

Agent:
# Go Build Resolution

## Initial Diagnostics

```巴什
$ 去构建./...
内部/service/user.go:25:15：未定义：UserRepository
Internal/handler/api.go:42:9：无法使用 x（字符串类型）作为 int 类型
Internal/handler/api.go:58:2：函数结束时缺少返回```

Errors found: 3

## Fix 1: Undefined Identifier

File: internal/service/user.go:25
Error: undefined: UserRepository
Cause: Missing import

```去
// 添加导入
导入“项目/内部/存储库”

// 改变了
var repo 用户存储库
// 至
var repo 存储库.UserRepository```

```巴什
$ 去构建./...
# 剩余 2 个错误```

## Fix 2: Type Mismatch

File: internal/handler/api.go:42
Error: cannot use x (type string) as type int

```去
// 改变了
计数 := params.Get("计数")
// 至
countStr := params.Get("计数")
计数, _ := strconv.Atoi(countStr)```

```巴什
$ 去构建./...
# 剩余 1 个错误```

## Fix 3: Missing Return

File: internal/handler/api.go:58
Error: missing return at end of function

```去
func GetUser(id string) (*用户, 错误) {
    如果id==“”{
        返回零，ErrInvalidID
    }
    用户 := 查找用户(id)
    // 添加缺少的返回值
    返回用户，无
}```

```巴什
$ 去构建./...
# 构建成功！```

## Final Verification

```巴什
$ 去看兽医./...
# 没有问题

$ 去测试./...
好的项目/内部/服务0.015s
好的项目/内部/处理程序 0.023s```

## Summary

| Metric | Count |
|--------|-------|
| Build errors fixed | 3 |
| Vet warnings fixed | 0 |
| Files modified | 2 |
| Remaining issues | 0 |

Build Status: ✅ SUCCESS
```## 常见错误已修复

|错误|典型修复|
|--------|-------------|
| `未定义：X` |添加导入或修复拼写错误 |
| `不能将 X 用作 Y` |类型转换或修复赋值 |
| `缺少返回` |添加返回语句 |
| `X 没有实现 Y` |添加缺少的方法 |
| `导入周期` |重组包 |
| `已声明但未使用` |删除或使用变量 |
| `找不到包` | `go get` 或 `go mod tidy` |

## 修复策略

1. **首先构建错误** - 代码必须编译
2. **第二次审查警告** - 修复可疑结构
3. **第三个 Lint 警告** - 风格和最佳实践
4. **一次一个修复** - 验证每项更改
5. **最小的更改** - 不要重构，只需修复

## 停止条件

如果出现以下情况，代理将停止并报告：
- 3次尝试后仍然存在相同的错误
- 修复引入更多错误
- 需要架构更改
- 缺少外部依赖

## 相关命令

- `/go-test` - 构建成功后运行测试
- `/go-review` - 检查代码质量
- `/verify` - 完整的验证循环

## 相关

- 代理：`agents/go-build-resolver.md`
- 技能：`技能/golang-patterns/`