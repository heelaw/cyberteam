# C++ 构建和修复

此命令调用 **cpp-build-resolver** 代理，以最小的更改增量修复 C++ 构建错误。

## 该命令的作用

1. **运行诊断**：执行`cmake --build`、`clang-tidy`、`cppcheck`
2. **解析错误**：按文件分组并按严重性排序
3. **增量修复**：一次一个错误
4. **验证每个修复**：每次更改后重新运行构建
5. **报告摘要**：显示已修复的内容和剩余的内容

## 何时使用

在以下情况下使用“/cpp-build”：
- `cmake --build build` 失败并出现错误
- 链接器错误（未定义的引用、多个定义）
- 模板实例化失败
- 包含/依赖问题
- 拉取破坏构建的更改后

## 诊断命令运行```bash
# CMake configure
cmake -B build -S .

# Build
cmake --build build 2>&1 | head -100

# Static analysis (if available)
clang-tidy src/*.cpp -- -std=c++17
cppcheck --enable=all src/
```## 会话示例```text
User: /cpp-build

Agent:
# C++ Build Resolution

## Initial Diagnostics

```巴什
$ cmake --build 构建
src/service/user.cpp:25:15：错误：使用未声明的标识符“UserRepository”
src/handler/api.cpp:42:9：错误：没有匹配的函数来调用“进程”
src/handler/api.cpp:58:1: 错误：非 void 函数不返回值```

Errors found: 3

## Fix 1: Undeclared Identifier

File: src/service/user.cpp:25
Error: use of undeclared identifier 'UserRepository'
Cause: Missing include

```程序文件
// 添加了包含
#include“存储库/user_repository.hpp”```

```巴什
$ cmake --build 构建
# 剩余 2 个错误```

## Fix 2: No Matching Function

File: src/handler/api.cpp:42
Error: no matching function for call to 'process'

```程序文件
// 改变了
进程（params.get（“计数”））；
// 至
过程(std::stoi(params.get("count")));```

```巴什
$ cmake --build 构建
# 剩余 1 个错误```

## Fix 3: Missing Return

File: src/handler/api.cpp:58
Error: non-void function does not return a value

```程序文件
std::可选<用户> getUser(const std::string& id) {
    if (id.empty()) {
        返回 std::nullopt;
    }
    自动用户 = findUser(id);
    // 添加缺少的返回值
    返回用户；
}```

```巴什
$ cmake --build 构建
# 构建成功！```

## Final Verification

```巴什
$ ctest --test-dir build --output-on-failure
测试项目构建
    1/5 测试 #1：unit_tests ........ 通过了 0.02 秒
    2/5 测试 #2：integration_tests 通过 0.15 秒
所有测试都通过了。```

## Summary

| Metric | Count |
|--------|-------|
| Build errors fixed | 3 |
| Linker errors fixed | 0 |
| Files modified | 2 |
| Remaining issues | 0 |

Build Status: ✅ SUCCESS
```## 常见错误已修复

|错误|典型修复|
|--------|-------------|
| `未声明的标识符` |添加 `#include` 或修复拼写错误 |
| `没有匹配的函数` |修复参数类型或添加重载 |
| `未定义的引用` |链接库或添加实现 |
| `多重定义` |使用“内联”或移至 .cpp |
| `不完整类型` |将前向 decl 替换为 `#include` |
| `没有名为 X 的成员` |修复成员名称或包含 |
| `无法将 X 转换为 Y` |添加适当的演员阵容 |
| `CMake 错误` |修复 CMakeLists.txt 配置 |

## 修复策略

1. **首先是编译错误** - 代码必须编译
2. **第二个链接器错误** - 解决未定义的引用
3. **第三个警告** - 使用 `-Wall -Wextra` 修复
4. **一次一个修复** - 验证每项更改
5. **最小的更改** - 不要重构，只需修复

## 停止条件

如果出现以下情况，代理将停止并报告：
- 3次尝试后仍然存在相同的错误
- 修复引入更多错误
- 需要架构更改
- 缺少外部依赖

## 相关命令

- `/cpp-test` - 构建成功后运行测试
- `/cpp-review` - 检查代码质量
- `/verify` - 完整的验证循环

## 相关

- 代理：`agents/cpp-build-resolver.md`
- 技能：`技能/cpp-编码-标准/`