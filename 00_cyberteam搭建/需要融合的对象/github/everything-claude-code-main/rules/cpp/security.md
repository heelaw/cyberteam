# C++ 安全性

> 此文件使用 C++ 特定内容扩展了 [common/security.md](../common/security.md)。

## 内存安全

- 切勿使用原始的“new”/“delete”——使用智能指针
- 切勿使用 C 风格数组 — 使用 `std::array` 或 `std::vector`
- 切勿使用 `malloc`/`free` — 使用 C++ 分配
- 除非绝对必要，否则避免使用“reinterpret_cast”

## 缓冲区溢出

- 在“char*”上使用“std::string”
- 当安全问题时使用“.at()”进行边界检查访问
- 切勿使用 `strcpy`、`strcat`、`sprintf` — 使用 `std::string` 或 `fmt::format`

## 未定义的行为

- 始终初始化变量
- 避免有符号整数溢出
- 切勿取消引用空指针或悬空指针
- 在 CI 中使用消毒剂：```bash
  cmake -DCMAKE_CXX_FLAGS="-fsanitize=address,undefined" ..
  ```## 静态分析

- 使用 **clang-tidy** 进行自动检查：```bash
  clang-tidy --checks='*' src/*.cpp
  ```- 使用 **cppcheck** 进行附加分析：```bash
  cppcheck --enable=all src/
  ```## 参考

有关详细的安全指南，请参阅技能：“cpp-coding-standards”。