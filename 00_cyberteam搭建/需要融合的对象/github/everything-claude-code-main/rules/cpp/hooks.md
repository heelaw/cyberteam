# C++ 钩子

> 此文件使用 C++ 特定内容扩展了 [common/hooks.md](../common/hooks.md)。

## 构建钩子

在提交 C++ 更改之前运行这些检查：```bash
# Format check
clang-format --dry-run --Werror src/*.cpp src/*.hpp

# Static analysis
clang-tidy src/*.cpp -- -std=c++17

# Build
cmake --build build

# Tests
ctest --test-dir build --output-on-failure
```## 推荐的 CI 管道

1. **clang-format** — 格式检查
2. **clang-tidy**——静态分析
3. **cppcheck**——附加分析
4. **cmake build**——编译
5. **ctest** — 使用消毒剂进行测试执行