# Rust 代码审查

此命令调用 **rust-reviewer** 代理来进行全面的 Rust 特定代码审查。

## 该命令的作用

1. **验证自动检查**：运行 `cargo check`、`cargo Clippy -- -D warnings`、`cargo fmt --check` 和 `cargo test` — 如果失败则停止
2. **识别 Rust 更改**：通过“git diff HEAD~1”（或 PR 的“git diff main...HEAD”）查找修改后的“.rs”文件
3. **运行安全审计**：执行“货物审计”（如果可用）
4. **安全扫描**：检查不安全的使用、命令注入、硬编码的秘密
5. **所有权审查**：分析不必要的克隆、生命周期问题、借用模式
6. **生成报告**：按严重程度对问题进行分类

## 何时使用

在以下情况下使用“/rust-review”：
- 编写或修改 Rust 代码后
- 在提交 Rust 更改之前
- 使用 Rust 代码审查拉取请求
- 加入新的 Rust 代码库
- 学习惯用的 Rust 模式

## 评论类别

### 严重（必须修复）
- 在生产代码路径中未选中“unwrap()”/“expect()”
- 没有记录不变量的“// SAFETY:”注释的“不安全”
- 通过查询中的字符串插值进行 SQL 注入
- 通过“std::process::Command”中未经验证的输入进行命令注入
- 硬编码凭证
- 通过原始指针释放后使用

### 高（应该修复）
- 不必要的`.clone()`来满足借用检查器
- `String` 参数，其中 `&str` 或 `impl AsRef<str>` 就足够了
- 在异步上下文中阻塞（`std::thread::sleep`、`std::fs`）
- 共享类型缺少“Send”/“Sync”界限
- 通配符 `_ =>` 匹配业务关键型枚举
- 大型函数（>50 行）

### 中（考虑）
- 热路径中不必要的分配
- 当大小已知时缺少“with_capacity”
- 没有理由地抑制剪辑警告
- 没有 `///` 文档的公共 API
- 在非“must_use”返回类型上考虑“#[must_use]”，其中忽略值可能是一个错误

## 自动检查运行```bash
# Build gate (must pass before review)
cargo check

# Lints and suggestions
cargo clippy -- -D warnings

# Formatting
cargo fmt --check

# Tests
cargo test

# Security audit (if available)
if command -v cargo-audit >/dev/null; then cargo audit; else echo "cargo-audit not installed"; fi
```## 用法示例````text
User: /rust-review

Agent:
# Rust Code Review Report

## Files Reviewed
- src/service/user.rs (modified)
- src/handler/api.rs (modified)

## Static Analysis Results
- Build: Successful
- Clippy: No warnings
- Formatting: Passed
- Tests: All passing

## Issues Found

[CRITICAL] Unchecked unwrap in Production Path
File: src/service/user.rs:28
Issue: Using `.unwrap()` on database query result
```生锈
让用户= db.find_by_id(id).unwrap();  // 丢失用户时出现恐慌```
Fix: Propagate error with context
```生锈
让用户= db.find_by_id(id)
    .context("获取用户失败")?;```

[HIGH] Unnecessary Clone
File: src/handler/api.rs:45
Issue: Cloning String to satisfy borrow checker
```生锈
让 name = user.name.clone();
进程（&用户，&名称）；```
Fix: Restructure to avoid clone
```生锈
let result = process_name(&user.name);
use_user(&用户, 结果);```

## Summary
- CRITICAL: 1
- HIGH: 1
- MEDIUM: 0

Recommendation: Block merge until CRITICAL issue is fixed
````

## 批准标准

|状态 |状况 |
|--------|------------|
|批准 |没有严重或严重问题 |
|警告|仅中等问题（谨慎合并）|
|块|发现严重或严重问题 |

## 与其他命令集成

- 首先使用 `/rust-test` 确保测试通过
- 如果发生构建错误，请使用“/rust-build”
- 在提交之前使用`/rust-review`
- 使用 `/code-review` 来解决非 Rust 特定的问题

## 相关

- 代理：`agents/rust-reviewer.md`
- 技能：`技能/生锈模式/`、`技能/生锈测试/`