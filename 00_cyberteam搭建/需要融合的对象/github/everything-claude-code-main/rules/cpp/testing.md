# C++ 测试

> 此文件使用 C++ 特定内容扩展了 [common/testing.md](../common/testing.md)。

## 框架

将 **GoogleTest** (gtest/gmock) 与 **CMake/CTest** 结合使用。

## 运行测试```bash
cmake --build build && ctest --test-dir build --output-on-failure
```## 覆盖范围```bash
cmake -DCMAKE_CXX_FLAGS="--coverage" -DCMAKE_EXE_LINKER_FLAGS="--coverage" ..
cmake --build .
ctest --output-on-failure
lcov --capture --directory . --output-file coverage.info
```## 消毒剂

始终在 CI 中使用消毒剂运行测试：```bash
cmake -DCMAKE_CXX_FLAGS="-fsanitize=address,undefined" ..
```## 参考

请参阅技能：“cpp-testing”，了解详细的 C++ 测试模式、TDD 工作流程和 GoogleTest/GMock 用法。