# 生锈测试

> 此文件使用 Rust 特定的内容扩展了 [common/testing.md](../common/testing.md)。

## 测试框架

- **`#[test]`** 使用 `#[cfg(test)]` 模块进行单元测试
- **rstest** 用于参数化测试和夹具
- **proptest** 用于基于属性的测试
- **mockall** 用于基于特征的模拟
- **`#[tokio::test]`** 用于异步测试

## 测试组织```text
my_crate/
├── src/
│   ├── lib.rs           # Unit tests in #[cfg(test)] modules
│   ├── auth/
│   │   └── mod.rs       # #[cfg(test)] mod tests { ... }
│   └── orders/
│       └── service.rs   # #[cfg(test)] mod tests { ... }
├── tests/               # Integration tests (each file = separate binary)
│   ├── api_test.rs
│   ├── db_test.rs
│   └── common/          # Shared test utilities
│       └── mod.rs
└── benches/             # Criterion benchmarks
    └── benchmark.rs
```单元测试位于同一文件中的“#[cfg(test)]”模块内。集成测试位于“tests/”中。

## Unit Test Pattern```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn creates_user_with_valid_email() {
        let user = User::new("Alice", "alice@example.com").unwrap();
        assert_eq!(user.name, "Alice");
    }

    #[test]
    fn rejects_invalid_email() {
        let result = User::new("Bob", "not-an-email");
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("invalid email"));
    }
}
```## 参数化测试```rust
use rstest::rstest;

#[rstest]
#[case("hello", 5)]
#[case("", 0)]
#[case("rust", 4)]
fn test_string_length(#[case] input: &str, #[case] expected: usize) {
    assert_eq!(input.len(), expected);
}
```## 异步测试```rust
#[tokio::test]
async fn fetches_data_successfully() {
    let client = TestClient::new().await;
    let result = client.get("/data").await;
    assert!(result.is_ok());
}
```## 用mockall 进行模拟

在生产代码中定义特征；在测试模块中生成模拟：```rust
// Production trait — pub so integration tests can import it
pub trait UserRepository {
    fn find_by_id(&self, id: u64) -> Option<User>;
}

#[cfg(test)]
mod tests {
    use super::*;
    use mockall::predicate::eq;

    mockall::mock! {
        pub Repo {}
        impl UserRepository for Repo {
            fn find_by_id(&self, id: u64) -> Option<User>;
        }
    }

    #[test]
    fn service_returns_user_when_found() {
        let mut mock = MockRepo::new();
        mock.expect_find_by_id()
            .with(eq(42))
            .times(1)
            .returning(|_| Some(User { id: 42, name: "Alice".into() }));

        let service = UserService::new(Box::new(mock));
        let user = service.get_user(42).unwrap();
        assert_eq!(user.name, "Alice");
    }
}
```## 测试命名

使用描述性名称来解释场景：
- `creates_user_with_valid_email()`
- `当库存不足时拒绝订单()`
- `returns_none_when_not_found()`

## 覆盖范围

- 目标线路覆盖率超过 80%
- 使用 **cargo-llvm-cov** 进行覆盖率报告
- 专注于业务逻辑 — 排除生成的代码和 FFI 绑定```bash
cargo llvm-cov                       # Summary
cargo llvm-cov --html                # HTML report
cargo llvm-cov --fail-under-lines 80 # Fail if below threshold
```## 测试命令```bash
cargo test                       # Run all tests
cargo test -- --nocapture        # Show println output
cargo test test_name             # Run tests matching pattern
cargo test --lib                 # Unit tests only
cargo test --test api_test       # Specific integration test (tests/api_test.rs)
cargo test --doc                 # Doc tests only
```## 参考文献

请参阅技能：“rust-testing”，了解全面的测试模式，包括基于属性的测试、固定装置和 Criterion 基准测试。