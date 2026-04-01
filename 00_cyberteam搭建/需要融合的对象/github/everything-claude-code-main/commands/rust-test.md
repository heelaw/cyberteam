# Rust TDD 命令

此命令使用“#[test]”、rstest、proptest 和mockall 对 Rust 代码实施测试驱动的开发方法。

## 该命令的作用

1. **定义类型/特征**：使用 `todo!()` 的脚手架函数签名
2. **编写测试**：创建综合测试模块（红色）
3. **运行测试**：验证测试失败的正确原因
4. **实现代码**：编写最少的代码即可通过（绿色）
5. **重构**：在保持测试绿色的同时进行改进
6. **检查覆盖率**：确保 Cargo-llvm-cov 的覆盖率超过 80%

## 何时使用

在以下情况下使用“/rust-test”：
- 实现新的 Rust 函数、方法或特征
- 将测试覆盖率添加到现有 Rust 代码中
- 修复错误（首先编写失败的测试）
- 构建关键业务逻辑
- 学习 Rust 中的 TDD 工作流程

## TDD 周期```
RED     -> Write failing test first
GREEN   -> Implement minimal code to pass
REFACTOR -> Improve code, tests stay green
REPEAT  -> Next test case
```## 会话示例````text
User: /rust-test I need a function to validate user registration

Agent:
# TDD Session: Registration Validator

## Step 1: Define Interface

```生锈
// src/validator.rs
pub 结构注册请求 {
    酒吧名称：字符串，
    酒吧电子邮件：字符串，
    发布密码：字符串，
}

pub 枚举 ValidationResult {
    有效，
    无效（Vec<字符串>），
}

pub fn validate_registration(请求: &RegistrationRequest) -> ValidationResult {
    待办事项！()
}```

## Step 2: Write Tests (RED)

```生锈
#[cfg（测试）]
模组测试{
    使用超级::*;

    #[测试]
    fn valid_registration_returns_valid() {
        让请求=注册请求{
            名称：“爱丽丝”.into(),
            电子邮件：“alice@example.com”.into(),
            密码：“SecureP@ss1”.into(),
        };
        断言！（匹配！（validate_registration（＆request），ValidationResult :: Valid））;
    }

    #[测试]
    fn 空白名称返回无效() {
        让请求=注册请求{
            名称：“”.into(),
            电子邮件：“alice@example.com”.into(),
            密码：“SecureP@ss1”.into(),
        };
        匹配 validate_registration(&request) {
            ValidationResult::Invalid(错误) => {
                assert!(errors.contains(&"名称为必填项".to_string()));
            }
            ValidationResult::Valid => 恐慌！("预期无效"),
        }
    }

    #[测试]
    fn invalid_email_returns_invalid() {
        让请求=注册请求{
            名称：“爱丽丝”.into(),
            电子邮件：“不是电子邮件”.into()，
            密码：“SecureP@ss1”.into(),
        };
        断言！（匹配！（
            验证注册（&请求），
            验证结果::无效(_)
        ））；
    }

    #[测试]
    fn Short_password_returns_invalid() {
        让请求=注册请求{
            名称：“爱丽丝”.into(),
            电子邮件：“alice@example.com”.into(),
            密码：“短”.into(),
        };
        断言！（匹配！（
            验证注册（&请求），
            验证结果::无效(_)
        ））；
    }
}```

## Step 3: Run Tests — Verify FAIL

```巴什
$ 货物测试
运行 4 个测试
测试测试::valid_registration_returns_valid ...失败（尚未实施）
测试测试::blank_name_returns_invalid ...失败
测试测试::invalid_email_returns_invalid ...失败
测试测试::short_password_returns_invalid ...失败```

Tests fail as expected (todo! panic).

## Step 4: Implement Minimal Code (GREEN)

```生锈
pub fn validate_registration(请求: &RegistrationRequest) -> ValidationResult {
    让 mut 错误 = Vec::new();

    if request.name.trim().is_empty() {
        error.push("姓名为必填项".into());
    }
    if !request.email.contains('@') {
        error.push("电子邮件格式无效".into());
    }
    if request.password.len() < 8 {
        error.push("密码必须至少8个字符".into());
    }

    如果错误。 is_empty() {
        验证结果::有效
    } 否则{
        验证结果::无效（错误）
    }
}```

## Step 5: Run Tests — Verify PASS

```巴什
$ 货物测试
运行 4 个测试
测试测试::valid_registration_returns_valid ... 好的
测试测试::blank_name_returns_invalid ... 好的
测试测试::invalid_email_returns_invalid ... 好的
测试测试::short_password_returns_invalid ... 好的

测试结果：好的。 4 已通过； 0 失败```

All tests passing!

## Step 6: Check Coverage

```巴什
$ 货物 llvm-cov
覆盖率：100.0%的线路```

Coverage: 100%

## TDD Complete!
````

## 测试模式

### 单元测试```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn adds_two_numbers() {
        assert_eq!(add(2, 3), 5);
    }

    #[test]
    fn handles_error() -> Result<(), Box<dyn std::error::Error>> {
        let result = parse_config(r#"port = 8080"#)?;
        assert_eq!(result.port, 8080);
        Ok(())
    }
}
```### 使用 rstest 进行参数化测试```rust
use rstest::{rstest, fixture};

#[rstest]
#[case("hello", 5)]
#[case("", 0)]
#[case("rust", 4)]
fn test_string_length(#[case] input: &str, #[case] expected: usize) {
    assert_eq!(input.len(), expected);
}
```### 异步测试```rust
#[tokio::test]
async fn fetches_data_successfully() {
    let client = TestClient::new().await;
    let result = client.get("/data").await;
    assert!(result.is_ok());
}
```### 基于属性的测试```rust
use proptest::prelude::*;

proptest! {
    #[test]
    fn encode_decode_roundtrip(input in ".*") {
        let encoded = encode(&input);
        let decoded = decode(&encoded).unwrap();
        assert_eq!(input, decoded);
    }
}
```## 覆盖命令```bash
# Summary report
cargo llvm-cov

# HTML report
cargo llvm-cov --html

# Fail if below threshold
cargo llvm-cov --fail-under-lines 80

# Run specific test
cargo test test_name

# Run with output
cargo test -- --nocapture

# Run without stopping on first failure
cargo test --no-fail-fast
```## 覆盖目标

|代码类型 |目标|
|------------|--------|
|关键业务逻辑 | 100% |
|公共API | 90%+ |
|通用代码| 80%+ |
|生成/FFI 绑定 |排除 |

## TDD 最佳实践

**做：**
- 在任何实施之前先编写测试
- 每次更改后运行测试
- 使用 `assert_eq!` 而不是 `assert!` 以获得更好的错误消息
- 在返回“Result”的测试中使用“?”以获得更清晰的输出
- 测试行为，而不是实现
- 包括边缘情况（空、边界、错误路径）

**不要：**
- 在测试之前编写实现
- 跳过红色阶段
- 当 `Result::is_err()` 工作时使用 `#[should_panic]`
- 在测试中使用 `sleep()` — 使用通道或 `tokio::time::pause()`
- 模拟一切——在可行的情况下更喜欢集成测试

## 相关命令

- `/rust-build` - 修复构建错误
- `/rust-review` - 实施后审查代码
- `/verify` - 运行完整的验证循环

## 相关

- 技能：`技能/生锈测试/`
- 技能：`技能/锈迹/`