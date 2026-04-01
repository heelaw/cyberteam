# C++ 编码风格

> 此文件使用 C++ 特定内容扩展了 [common/coding-style.md](../common/coding-style.md)。

## 现代 C++ (C++17/20/23)

- 相比 C 风格的结构，更喜欢 **现代 C++ 功能**
- 当类型从上下文中显而易见时使用“auto”
- 使用 `constexpr` 作为编译时常量
- 使用结构化绑定：`auto [key, value] = map_entry;`

## 资源管理

- **RAII 无处不在** — 无需手动“新建”/“删除”
- 使用 `std::unique_ptr` 获得独占所有权
- 仅当真正需要共享所有权时才使用“std::shared_ptr”
- 在原始的“new”上使用“std::make_unique”/“std::make_shared”

## 命名约定

- 类型/类：`PascalCase`
- 函数/方法：“snake_case”或“camelCase”（遵循项目约定）
- 常量：`kPascalCase` 或 `UPPER_SNAKE_CASE`
- 命名空间：`小写`
- 成员变量：`snake_case_`（尾随下划线）或`m_`前缀

## 格式化

- 使用 **clang-format** — 没有风格争论
- 在提交之前运行 `clang-format -i <file>`

## 参考

请参阅技能：“cpp-coding-standards”，了解全面的 C++ 编码标准和指南。