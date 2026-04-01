# 执行 TDD 命令

此命令使用惯用的 Go 测试模式强制执行 Go 代码的测试驱动开发方法。

## 该命令的作用

1. **定义类型/接口**：首先定义支架函数签名
2. **编写表驱动测试**：创建全面的测试用例（红色）
3. **运行测试**：验证测试失败的正确原因
4. **实现代码**：编写最少的代码即可通过（绿色）
5. **重构**：在保持测试绿色的同时进行改进
6. **检查覆盖率**：确保覆盖率超过 80%

## 何时使用

在以下情况下使用“/go-test”：
- 实施新的 Go 功能
- 将测试覆盖率添加到现有代码中
- 修复错误（首先编写失败的测试）
- 构建关键业务逻辑
- 学习 Go 中的 TDD 工作流程

## TDD 周期```
RED     → Write failing table-driven test
GREEN   → Implement minimal code to pass
REFACTOR → Improve code, tests stay green
REPEAT  → Next test case
```## 会话示例````
User: /go-test I need a function to validate email addresses

Agent:
# TDD Session: Email Validator

## Step 1: Define Interface

```去
// 验证器/email.go
包验证器

// ValidateEmail 检查给定字符串是否是有效的电子邮件地址。
// 如果有效则返回 nil，否则返回描述问题的错误。
func ValidateEmail（电子邮件字符串）错误 {
    恐慌（“未实施”）
}```

## Step 2: Write Table-Driven Tests (RED)

```去
// 验证器/email_test.go
包验证器

导入（
    “测试”
）

func TestValidateEmail(t *testing.T) {
    测试 := [] 结构 {
        名称字符串
        电子邮件字符串
        想要错误布尔
    }{
        // 有效邮箱
        {"简单电子邮件", "user@example.com", false},
        {"with subdomain", "user@mail.example.com", false},
        {"with plus", "user+tag@example.com", false},
        {"带点", "first.last@example.com", false},

        // 无效的电子邮件
        {"空字符串", "", true},
        {"没有 at 符号", "userexample.com", true},
        {"无域", "用户@", true},
        {"无本地部分", "@example.com", true},
        {"double at", "user@@example.com", true},
        {“空格”，“用户@example.com”，true}，
        {"无顶级域名", "user@example", true},
    }

    for _, tt := 范围测试 {
        t.Run(tt.name, func(t *testing.T) {
            错误 := 验证电子邮件(tt.email)
            如果 tt.wantErr && err == nil {
                t.Errorf("ValidateEmail(%q) = nil; 想要错误", tt.email)
            }
            if !tt.wantErr && err != nil {
                t.Errorf("ValidateEmail(%q) = %v; 想要 nil", tt.email, err)
            }
        })
    }
}```

## Step 3: Run Tests - Verify FAIL

```巴什
$ 去测试 ./validator/...

--- 失败：TestValidateEmail (0.00s)
    --- 失败：TestValidateEmail/simple_email (0.00s)
        恐慌：未实施

失败```

✓ Tests fail as expected (panic).

## Step 4: Implement Minimal Code (GREEN)

```去
// 验证器/email.go
包验证器

导入（
    “错误”
    “正则表达式”
）

var emailRegex = regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)

变量（
    ErrEmailEmpty = error.New("电子邮件不能为空")
    ErrEmailInvalid =Errors.New("电子邮件格式无效")
）

func ValidateEmail（电子邮件字符串）错误 {
    如果电子邮件==“”{
        返回 ErrEmail 为空
    }
    if !emailRegex.MatchString(email) {
        返回ErrEmail无效
    }
    返回零
}```

## Step 5: Run Tests - Verify PASS

```巴什
$ 去测试 ./validator/...

通行证
好的项目/验证器 0.003s```

✓ All tests passing!

## Step 6: Check Coverage

```巴什
$ go test -cover ./validator/...

通行证
覆盖率： 100.0% 的报表
好的项目/验证器 0.003s```

✓ Coverage: 100%

## TDD Complete!
````

## 测试模式

### 表驱动测试```go
tests := []struct {
    name     string
    input    InputType
    want     OutputType
    wantErr  bool
}{
    {"case 1", input1, want1, false},
    {"case 2", input2, want2, true},
}

for _, tt := range tests {
    t.Run(tt.name, func(t *testing.T) {
        got, err := Function(tt.input)
        // assertions
    })
}
```### 并行测试```go
for _, tt := range tests {
    tt := tt // Capture
    t.Run(tt.name, func(t *testing.T) {
        t.Parallel()
        // test body
    })
}
```### 测试助手```go
func setupTestDB(t *testing.T) *sql.DB {
    t.Helper()
    db := createDB()
    t.Cleanup(func() { db.Close() })
    return db
}
```## 覆盖命令```bash
# Basic coverage
go test -cover ./...

# Coverage profile
go test -coverprofile=coverage.out ./...

# View in browser
go tool cover -html=coverage.out

# Coverage by function
go tool cover -func=coverage.out

# With race detection
go test -race -cover ./...
```## 覆盖目标

|代码类型 |目标|
|------------|--------|
|关键业务逻辑 | 100% |
|公共 API | 90%+ |
|通用代码| 80%+ |
|生成的代码 |排除 |

## TDD 最佳实践

**做：**
- 在任何实施之前先编写测试
- 每次更改后运行测试
- 使用表格驱动测试进行全面覆盖
- 测试行为，而不是实现细节
- 包括边缘情况（空、零、最大值）

**不要：**
- 在测试之前编写实现
- 跳过红色阶段
- 直接测试私有函数
- 在测试中使用“time.Sleep”
- 忽略片状测试

## 相关命令

- `/go-build` - 修复构建错误
- `/go-review` - 实施后审查代码
- `/verify` - 运行完整的验证循环

## 相关

- 技能：`技能/golang-testing/`
- 技能：`技能/tdd-工作流程/`