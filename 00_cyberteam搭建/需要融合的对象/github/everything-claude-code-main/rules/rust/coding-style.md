# Rust 编码风格

> 此文件使用 Rust 特定的内容扩展了 [common/coding-style.md](../common/coding-style.md)。

## 格式化

- **rustfmt** 用于强制执行 — 始终在提交之前运行 `cargo fmt`
- **clippy** 用于 lints — `cargo Clippy -- -D warnings` （将警告视为错误）
- 4 个空格缩进（rustfmt 默认）
- 最大行宽：100 个字符（rustfmt 默认值）

## 不变性

Rust 变量默认是不可变的——接受这一点：

- 默认使用`let`；仅当需要突变时才使用 `let mut`
- 更喜欢返回新值而不是就地改变
- 当函数可能需要或不需要分配时使用 `Cow<'_, T>````rust
use std::borrow::Cow;

// GOOD — immutable by default, new value returned
fn normalize(input: &str) -> Cow<'_, str> {
    if input.contains(' ') {
        Cow::Owned(input.replace(' ', "_"))
    } else {
        Cow::Borrowed(input)
    }
}

// BAD — unnecessary mutation
fn normalize_bad(input: &mut String) {
    *input = input.replace(' ', "_");
}
```## 命名

遵循标准 Rust 约定：
- `snake_case` 用于函数、方法、变量、模块、包
- 用于类型、特征、枚举、类型参数的“PascalCase”（UpperCamelCase）
- `SCREAMING_SNAKE_CASE` 用于常量和静态变量
- 生命周期：短小写 (`'a`, `'de`) — 复杂情况的描述性名称 (`'input`)

## 所有权和借款

- 默认借用（`&T`）；仅当您需要存储或消费时才拥有所有权
- 在不了解根本原因的情况下，切勿克隆以满足借用检查员的要求
- 在函数参数中接受“&str”而不是“String”，“&[T]”而不是“Vec<T>”
- 对于需要拥有“String”的构造函数使用“impl Into<String>”```rust
// GOOD — borrows when ownership isn't needed
fn word_count(text: &str) -> usize {
    text.split_whitespace().count()
}

// GOOD — takes ownership in constructor via Into
fn new(name: impl Into<String>) -> Self {
    Self { name: name.into() }
}

// BAD — takes String when &str suffices
fn word_count_bad(text: String) -> usize {
    text.split_whitespace().count()
}
```## 错误处理

- 使用 `Result<T, E>` 和 `?` 进行传播 — 切勿在生产代码中使用 `unwrap()`
- **库**：用 `thiserror` 定义类型错误
- **应用程序**：使用 `anyway` 来实现灵活的错误上下文
- 使用 `.with_context(|| format!("failed to ..."))?` 添加上下文
- 保留 `unwrap()` / `expect()` 用于测试和真正无法到达的状态```rust
// GOOD — library error with thiserror
#[derive(Debug, thiserror::Error)]
pub enum ConfigError {
    #[error("failed to read config: {0}")]
    Io(#[from] std::io::Error),
    #[error("invalid config format: {0}")]
    Parse(String),
}

// GOOD — application error with anyhow
use anyhow::Context;

fn load_config(path: &str) -> anyhow::Result<Config> {
    let content = std::fs::read_to_string(path)
        .with_context(|| format!("failed to read {path}"))?;
    toml::from_str(&content)
        .with_context(|| format!("failed to parse {path}"))
}
```## 循环上的迭代器

优先选择迭代器链进行转换；使用循环进行复杂的控制流：```rust
// GOOD — declarative and composable
let active_emails: Vec<&str> = users.iter()
    .filter(|u| u.is_active)
    .map(|u| u.email.as_str())
    .collect();

// GOOD — loop for complex logic with early returns
for user in &users {
    if let Some(verified) = verify_email(&user.email)? {
        send_welcome(&verified)?;
    }
}
```## 模块组织

按领域而不是按类型组织：```text
src/
├── main.rs
├── lib.rs
├── auth/           # Domain module
│   ├── mod.rs
│   ├── token.rs
│   └── middleware.rs
├── orders/         # Domain module
│   ├── mod.rs
│   ├── model.rs
│   └── service.rs
└── db/             # Infrastructure
    ├── mod.rs
    └── pool.rs
```## 可见性

- 默认为私有；使用 pub(crate) 进行内部共享
- 仅标记“pub”是板条箱公共 API 的一部分
- 从“lib.rs”重新导出公共 API

## 参考文献

请参阅技能：`rust-patterns` 了解全面的 Rust 习语和模式。