# Rust 测试命令

使用 Rust TDD 方法实现：$ARGUMENTS

## 你的任务

使用 Rust 惯用法应用测试驱动开发：

1. **定义类型** - 结构体、枚举、特征
2. **编写测试** - `#[cfg(test)]` 模块中的单元测试
3. **实施最少的代码** - 通过测试
4. **检查覆盖率** - 目标 80%+

## Rust 的 TDD 周期

### 第 1 步：定义接口```rust
pub struct Input {
    // fields
}

pub fn process(input: &Input) -> Result<Output, Error> {
    todo!()
}
```### 第 2 步：编写测试```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn valid_input_succeeds() {
        let input = Input { /* ... */ };
        let result = process(&input);
        assert!(result.is_ok());
    }

    #[test]
    fn invalid_input_returns_error() {
        let input = Input { /* ... */ };
        let result = process(&input);
        assert!(result.is_err());
    }
}
```### 步骤 3：运行测试（红色）```bash
cargo test
```### 第 4 步：实施（绿色）```rust
pub fn process(input: &Input) -> Result<Output, Error> {
    // Minimal implementation that handles both paths
    validate(input)?;
    Ok(Output { /* ... */ })
}
```### 第 5 步：检查覆盖范围```bash
cargo llvm-cov
cargo llvm-cov --fail-under-lines 80
```## Rust 测试命令```bash
cargo test                        # Run all tests
cargo test -- --nocapture         # Show println output
cargo test test_name              # Run specific test
cargo test --no-fail-fast         # Don't stop on first failure
cargo test --lib                  # Unit tests only
cargo test --test integration     # Integration tests only
cargo test --doc                  # Doc tests only
cargo bench                       # Run benchmarks
```## 测试文件组织```
src/
├── lib.rs             # Library root
├── service.rs         # Implementation
└── service/
    └── tests.rs       # Or inline #[cfg(test)] mod tests {}
tests/
└── integration.rs     # Integration tests
benches/
└── benchmark.rs       # Criterion benchmarks
```---

**提示**：使用“rstest”进行参数化测试，使用“proptest”进行基于属性的测试。