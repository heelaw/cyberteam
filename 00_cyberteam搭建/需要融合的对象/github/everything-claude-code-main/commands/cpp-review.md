# C++ 代码审查

此命令调用 **cpp-reviewer** 代理来进行全面的 C++ 特定代码审查。

## 该命令的作用

1. **识别 C++ 更改**：通过 `git diff` 查找修改后的 `.cpp`、`.hpp`、`.cc`、`.h` 文件
2. **运行静态分析**：执行`clang-tidy`和`cppcheck`
3. **内存安全扫描**：检查原始新建/删除、缓冲区溢出、释放后使用
4. **并发审查**：分析线程安全、互斥体使用、数据竞争
5. **现代 C++ 检查**：验证代码遵循 C++17/20 约定和最佳实践
6. **生成报告**：按严重程度对问题进行分类

## 何时使用

在以下情况下使用“/cpp-review”：
- 编写或修改C++代码后
- 提交 C++ 更改之前
- 使用 C++ 代码审查拉取请求
- 加入新的 C++ 代码库
- 检查内存安全问题

## 评论类别

### 严重（必须修复）
- 没有 RAII 的原始“新建”/“删除”
- 缓冲区溢出和释放后使用
- 没有同步的数据竞争
- 通过 `system()` 命令注入
- 未初始化的变量读取
- 空指针取消引用

### 高（应该修复）
- 违反五项规则
- 缺少 `std::lock_guard` / `std::scoped_lock`
- 没有适当生命周期管理的分离线程
- C 风格的转换而不是 `static_cast`/`dynamic_cast`
- 缺少“const”正确性

### 中（考虑）
- 不必要的副本（按值传递而不是“const&”）
- 已知大小的容器上缺少“reserve()”
- 标头中的“使用命名空间 std;”
- 重要返回值缺少“[[nodiscard]]”
- 过于复杂的模板元编程

## 自动检查运行```bash
# Static analysis
clang-tidy --checks='*,-llvmlibc-*' src/*.cpp -- -std=c++17

# Additional analysis
cppcheck --enable=all --suppress=missingIncludeSystem src/

# Build with warnings
cmake --build build -- -Wall -Wextra -Wpedantic
```## 用法示例```text
User: /cpp-review

Agent:
# C++ Code Review Report

## Files Reviewed
- src/handler/user.cpp (modified)
- src/service/auth.cpp (modified)

## Static Analysis Results
✓ clang-tidy: 2 warnings
✓ cppcheck: No issues

## Issues Found

[CRITICAL] Memory Leak
File: src/service/auth.cpp:45
Issue: Raw `new` without matching `delete`
```程序文件
自动*会话=新会话（用户ID）；  // 内存泄漏！
缓存[用户ID] = 会话；```
Fix: Use `std::unique_ptr`
```程序文件
自动会话 = std::make_unique<Session>(userId);
缓存[用户ID] = std::move(会话);```

[HIGH] Missing const Reference
File: src/handler/user.cpp:28
Issue: Large object passed by value
```程序文件
void processUser(User user) { // 不必要的复制```
Fix: Pass by const reference
```程序文件
void processUser(const User& user) {```

## Summary
- CRITICAL: 1
- HIGH: 1
- MEDIUM: 0

Recommendation: ❌ Block merge until CRITICAL issue is fixed
```## 批准标准

|状态 |状况 |
|--------|------------|
| ✅ 批准 |没有严重或严重问题 |
| ⚠️警告|仅中等问题（谨慎合并）|
| ❌ 块 |发现严重或严重问题 |

## 与其他命令集成

- 首先使用`/cpp-test`来确保测试通过
- 如果发生构建错误，请使用“/cpp-build”
- 在提交之前使用`/cpp-review`
- 对于非 C++ 特定问题使用“/code-review”

## 相关

- 代理：`agents/cpp-reviewer.md`
- 技能：`技能/cpp-编码-标准/`、`技能/cpp-测试/`