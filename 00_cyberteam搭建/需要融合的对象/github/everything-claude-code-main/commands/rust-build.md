# Rust 构建和修复

此命令调用 **rust-build-resolver** 代理，以最小的更改增量修复 Rust 构建错误。

## 该命令的作用

1. **运行诊断**：执行 `cargo check`、`cargo Clippy`、`cargo fmt --check`
2. **解析错误**：识别错误代码和受影响的文件
3. **增量修复**：一次一个错误
4. **验证每个修复**：每次更改后重新运行“cargo check”
5. **报告摘要**：显示已修复的内容和剩余的内容

## 何时使用

在以下情况下使用 `/rust-build`：
- `cargo build` 或 `cargo check` 失败并出现错误
- `cargo Clippy` 报告警告
- 借用检查器或生命周期错误块编译
- 货物依赖解析失败
- 拉取破坏构建的更改后

## 诊断命令运行```bash
# Primary build check
cargo check 2>&1

# Lints and suggestions
cargo clippy -- -D warnings 2>&1

# Formatting check
cargo fmt --check 2>&1

# Dependency issues
cargo tree --duplicates

# Security audit (if available)
if command -v cargo-audit >/dev/null; then cargo audit; else echo "cargo-audit not installed"; fi
```## 会话示例````text
User: /rust-build

Agent:
# Rust Build Resolution

## Initial Diagnostics

```巴什
$ 货物支票
错误[E0502]：无法借用“map”作为可变的，因为它也被借用为不可变的
  --> src/service/cache.rs:25:5
错误[E0308]：类型不匹配
  --> src/handler/api.rs:42:12
错误[E0425]：在此范围内找不到值“db”
  --> src/handler/api.rs:58:9```

Errors found: 3

## Fix 1: Borrow Checker Error

File: src/service/cache.rs:25
Error: E0502 — cannot borrow `map` as mutable because also borrowed as immutable
Cause: Immutable borrow still active during mutable insert

```生锈
// 更改：重组为在可变访问之前结束不可变借用
if !map.contains_key("key") {
    map.insert("key".into(), 默认);
}```

```巴什
$ 货物支票
# 剩余 2 个错误```

## Fix 2: Type Mismatch

File: src/handler/api.rs:42
Error: E0308 — mismatched types: expected `usize`, found `&str`

```生锈
// 改变了
让 count = params.get("count");
// 至
让计数： usize = params.get("count")
    .and_then(|s| s.parse().ok())
    .unwrap_or(0);```

```巴什
$ 货物支票
# 剩余 1 个错误```

## Fix 3: Unresolved Name

File: src/handler/api.rs:58
Error: E0425 — cannot find value `db` in this scope
Cause: Missing import

```生锈
// 添加
使用板条箱::db；```

```巴什
$ 货物支票
# 构建成功！```

## Final Verification

```巴什
$ 货物 Clippy -- -D 警告
# 没有警告

$ 货物测试
运行 6 个测试
测试服务::缓存::测试::test_insert ... 好的
测试服务::缓存::测试::test_get ... 好的
测试处理程序::api::tests::test_parse_count ... 好的
测试处理程序::api::tests::test_missing_count ... 好的
测试处理程序::api::tests::test_db_import ... 好的
测试处理程序::api::tests::test_response ... 好的

测试结果：好的。 6个通过； 0 失败； 0 被忽略```

## Summary

| Metric | Count |
|--------|-------|
| Build errors fixed | 3 |
| Clippy warnings fixed | 0 |
| Files modified | 2 |
| Remaining issues | 0 |

Build Status: SUCCESS
````

## 常见错误已修复

|错误|典型修复|
|--------|-------------|
| `不能因为可变而借用` |重组以首先结束不可变借用；仅在合理的情况下克隆 |
| `活得不够长` |使用自有类型或添加生命周期注释 |
| `不能搬出` |重组以获得所有权；克隆仅作为最后手段|
| `不匹配的类型` |添加 `.into()`、`as` 或显式转换 |
| `特征 X 未实现` |添加 `#[derive(Trait)]` 或手动实施 |
| `未解决的导入` |添加到 Cargo.toml 或修复 `use` 路径 |
| `找不到价值` |添加导入或修复路径 |

## 修复策略

1. **首先构建错误** - 代码必须编译
2. **第二个 Clippy 警告** - 修复可疑结构
3. **格式化第三个** - `cargo fmt` 合规性
4. **一次一个修复** - 验证每项更改
5. **最小的更改** - 不要重构，只需修复

## 停止条件

如果出现以下情况，代理将停止并报告：
- 3次尝试后仍然存在相同的错误
- 修复引入更多错误
- 需要架构更改
- 借用检查器错误需要重新设计数据所有权

## 相关命令

- `/rust-test` - 构建成功后运行测试
- `/rust-review` - 检查代码质量
- `/verify` - 完整的验证循环

## 相关

- 代理：`agents/rust-build-resolver.md`
- 技能：`技能/锈迹/`