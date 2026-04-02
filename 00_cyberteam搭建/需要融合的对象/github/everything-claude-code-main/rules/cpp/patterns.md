# C++ 模式

> 此文件使用 C++ 特定内容扩展了 [common/patterns.md](../common/patterns.md)。

## RAII（资源获取即初始化）

将资源生命周期与对象生命周期联系起来：```cpp
class FileHandle {
public:
    explicit FileHandle(const std::string& path) : file_(std::fopen(path.c_str(), "r")) {}
    ~FileHandle() { if (file_) std::fclose(file_); }
    FileHandle(const FileHandle&) = delete;
    FileHandle& operator=(const FileHandle&) = delete;
private:
    std::FILE* file_;
};
```## 五/零规则

- **零规则**：首选不需要自定义析构函数、复制/移动构造函数或赋值的类
- **五规则**：如果定义析构函数/copy-ctor/copy-assign/move-ctor/move-assign 中的任何一个，请定义所有五个

## 值语义

- 按值传递小型/琐碎类型
- 通过 `const&` 传递大类型
- 按值返回（依赖RVO/NRVO）
- 对接收器参数使用移动语义

## 错误处理

- 在特殊情况下使用例外
- 对可能不存在的值使用“std::Optional”
- 使用 `std::expected` (C++23) 或结果类型来处理预期的失败

## 参考

有关全面的 C++ 模式和反模式，请参阅技能：“cpp-coding-standards”。