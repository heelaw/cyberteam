# Rust 构建命令

修复 Rust 构建、clippy 和依赖错误：$ARGUMENTS

## 你的任务

1. **运行货物检查**：`货物检查2>&1`
2. **运行 Cargo Clippy**: `cargo Clippy -- -D warnings 2>&1`
3. **修复错误** 一次一个
4. **验证修复**不要引入新的错误

## 常见 Rust 错误

### 借用检查器```
cannot borrow `x` as mutable because it is also borrowed as immutable
```**修复**：重组以首先结束不可变借用；仅在合理的情况下克隆

### 类型不匹配```
mismatched types: expected `T`, found `U`
```**修复**：添加 `.into()`、`as` 或显式类型转换

### 缺少导入```
unresolved import `crate::module`
```**修复**：修复 `use` 路径或声明模块（仅针对外部 crate 添加 Cargo.toml deps）

### 终身错误```
does not live long enough
```**修复**：使用拥有的类型或添加生命周期注释

### 特征未实现```
the trait `X` is not implemented for `Y`
```**修复**：添加 `#[derive(Trait)]` 或手动实施

## 修复订单

1. **构建错误** - 代码必须编译
2. **Clippy warnings** - 修复可疑结构
3. **格式** - `cargo fmt` 合规性

## 构建命令```bash
cargo check 2>&1
cargo clippy -- -D warnings 2>&1
cargo fmt --check 2>&1
cargo tree --duplicates
cargo test
```## 验证

修复后：```bash
cargo check                  # Should succeed
cargo clippy -- -D warnings  # No warnings allowed
cargo fmt --check            # Formatting should pass
cargo test                   # Tests should pass
```---

**重要**：仅修复错误。没有重构，就没有改进。以最小的改变实现绿色构建。