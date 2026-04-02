# 执行测试命令

使用 Go TDD 方法实现：$ARGUMENTS

## 你的任务

使用 Go 惯用法应用测试驱动开发：

1. **定义类型** - 接口和结构
2. **编写表驱动测试** - 全面覆盖
3. **实施最少的代码** - 通过测试
4. **基准** - 验证性能

## Go 的 TDD 周期

### 第 1 步：定义接口```go
type Calculator interface {
    Calculate(input Input) (Output, error)
}

type Input struct {
    // fields
}

type Output struct {
    // fields
}
```### 步骤 2：表驱动测试```go
func TestCalculate(t *testing.T) {
    tests := []struct {
        name    string
        input   Input
        want    Output
        wantErr bool
    }{
        {
            name:  "valid input",
            input: Input{...},
            want:  Output{...},
        },
        {
            name:    "invalid input",
            input:   Input{...},
            wantErr: true,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := Calculate(tt.input)
            if (err != nil) != tt.wantErr {
                t.Errorf("Calculate() error = %v, wantErr %v", err, tt.wantErr)
                return
            }
            if !reflect.DeepEqual(got, tt.want) {
                t.Errorf("Calculate() = %v, want %v", got, tt.want)
            }
        })
    }
}
```### 步骤 3：运行测试（红色）```bash
go test -v ./...
```### 第 4 步：实施（绿色）```go
func Calculate(input Input) (Output, error) {
    // Minimal implementation
}
```### 第 5 步：基准测试```go
func BenchmarkCalculate(b *testing.B) {
    input := Input{...}
    for i := 0; i < b.N; i++ {
        Calculate(input)
    }
}
```## Go Testing Commands```bash
# Run all tests
go test ./...

# Run with verbose output
go test -v ./...

# Run with coverage
go test -cover ./...

# Run with race detector
go test -race ./...

# Run benchmarks
go test -bench=. ./...

# Generate coverage report
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out
```## 测试文件组织```
package/
├── calculator.go       # Implementation
├── calculator_test.go  # Tests
├── testdata/           # Test fixtures
│   └── input.json
└── mock_test.go        # Mock implementations
```---

**提示**：使用 `testify/assert` 来获得更清晰的断言，或者为了简单起见，坚持使用 stdlib。