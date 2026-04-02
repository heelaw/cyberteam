# C++ 编码标准（C++ 核心指南）

现代 C++ (C++17/20/23) 的综合编码标准源自 [C++ 核心指南](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)。强制类型安全、资源安全、不变性和清晰度。

## 何时使用

- 编写新的 C++ 代码（类、函数、模板）
- 审查或重构现有的 C++ 代码
- 在 C++ 项目中做出架构决策
- 在 C++ 代码库中强制执行一致的风格
- 在语言功能之间进行选择（例如，“枚举”与“枚举类”、原始指针与智能指针）

### 何时不使用

- 非C++项目
- 无法采用现代 C++ 功能的旧版 C 代码库
- 特定准则与硬件限制相冲突的嵌入式/裸机环境（有选择地适应）

## 横切原则

这些主题在整个指南中反复出现并构成基础：

1. **RAII 无处不在** (P.8、R.1、E.6、CP.20)：将资源生命周期绑定到对象生命周期
2. **默认不变性**（P.10、Con.1-5、ES.25）：以 `const`/`constexpr` 开头；可变性是例外
3. **类型安全** (P.4, I.4, ES.46-49, Enum.3)：使用类型系统来防止编译时出现错误
4. **表达意图**（P.3、F.1、NL.1-2、T.10）：名称、类型和概念应传达目的
5. **最小化复杂性**（F.2-3、ES.5、Per.4-5）：简单的代码就是正确的代码
6. **值语义优于指针语义** (C.10、R.3-5、F.20、CP.31)：更喜欢按值和作用域对象返回

## 原理与接口 (P.*, I.*)

### 关键规则

|规则|总结|
|------|---------|
| **第1页** |直接用代码表达想法 |
| **第3页** |表达意向 |
| **第4页** |理想情况下，程序应该是静态类型安全的 |
| **第 5 页** |优先选择编译时检查而不是运行时检查 |
| **第8页** |请勿泄露任何资源 |
| **第 10 页** |与可变数据相比，更喜欢不可变数据 |
| **I.1** |使接口显式 |
| **I.2** |避免非常量全局变量 |
| **I.4** |使接口精确且强类型化 |
| **I.11** |切勿通过原始指针或引用转移所有权 |
| **I.23** |保持函数参数数量较少 |

＃＃＃ 做```cpp
// P.10 + I.4: Immutable, strongly typed interface
struct Temperature {
    double kelvin;
};

Temperature boil(const Temperature& water);
```＃＃＃ 不```cpp
// Weak interface: unclear ownership, unclear units
double boil(double* temp);

// Non-const global variable
int g_counter = 0;  // I.2 violation
```## 函数 (F.*)

### 关键规则

|规则|总结|
|------|---------|
| **F.1** |将有意义的操作封装为精心命名的函数 |
| **F.2** |函数应该执行单个逻辑操作 |
| **F.3** |保持功能简短 |
| **F.4** |如果一个函数可能在编译时求值，请将其声明为 `constexpr` |
| **F.6** |如果你的函数不能抛出异常，请将其声明为“noexcept” |
| **F.8** |更喜欢纯函数 |
| **F.16** |对于“in”参数，通过值传递廉价复制的类型，通过 `const&` | 传递其他类型。
| **F.20** |对于“out”值，更喜欢返回值而不是输出参数 |
| **F.21** |要返回多个“out”值，最好返回一个 struct |
| **F.43** |永远不要返回本地对象的指针或引用

### 参数传递```cpp
// F.16: Cheap types by value, others by const&
void print(int x);                           // cheap: by value
void analyze(const std::string& data);       // expensive: by const&
void transform(std::string s);               // sink: by value (will move)

// F.20 + F.21: Return values, not output parameters
struct ParseResult {
    std::string token;
    int position;
};

ParseResult parse(std::string_view input);   // GOOD: return struct

// BAD: output parameters
void parse(std::string_view input,
           std::string& token, int& pos);    // avoid this
```### 纯函数和 constexpr```cpp
// F.4 + F.8: Pure, constexpr where possible
constexpr int factorial(int n) noexcept {
    return (n <= 1) ? 1 : n * factorial(n - 1);
}

static_assert(factorial(5) == 120);
```### 反模式

- 从函数返回 `T&&` (F.45)
- 使用 `va_arg` / C 风格变量 (F.55)
- 通过传递给其他线程的 lambda 中的引用进行捕获 (F.53)
- 返回抑制移动语义的“const T”（F.49）

## 类和类层次结构 (C.*)

### 关键规则

|规则|总结|
|------|---------|
| **C.2** |如果存在不变量，则使用“class”；如果数据成员独立变化则为“struct” |
| **C.9** |最大限度地减少会员的曝光 |
| **C.20** |如果可以避免定义默认操作，请执行（零规则）|
| **C.21** |如果您定义或“=删除”任何复制/移动/析构函数，请处理所有这些（五规则）|
| **C.35** |基类析构函数：公共虚拟或受保护的非虚拟 |
| **C.41** |构造函数应该创建一个完全初始化的对象 |
| **C.46** |声明单参数构造函数 `explicit` |
| **C.67** |多态类应该禁止公共复制/移动 |
| **C.128** |虚拟函数：准确指定“virtual”、“override”或“final”之一 |

### 零规则```cpp
// C.20: Let the compiler generate special members
struct Employee {
    std::string name;
    std::string department;
    int id;
    // No destructor, copy/move constructors, or assignment operators needed
};
```### 五法则```cpp
// C.21: If you must manage a resource, define all five
class Buffer {
public:
    explicit Buffer(std::size_t size)
        : data_(std::make_unique<char[]>(size)), size_(size) {}

    ~Buffer() = default;

    Buffer(const Buffer& other)
        : data_(std::make_unique<char[]>(other.size_)), size_(other.size_) {
        std::copy_n(other.data_.get(), size_, data_.get());
    }

    Buffer& operator=(const Buffer& other) {
        if (this != &other) {
            auto new_data = std::make_unique<char[]>(other.size_);
            std::copy_n(other.data_.get(), other.size_, new_data.get());
            data_ = std::move(new_data);
            size_ = other.size_;
        }
        return *this;
    }

    Buffer(Buffer&&) noexcept = default;
    Buffer& operator=(Buffer&&) noexcept = default;

private:
    std::unique_ptr<char[]> data_;
    std::size_t size_;
};
```### 类层次结构```cpp
// C.35 + C.128: Virtual destructor, use override
class Shape {
public:
    virtual ~Shape() = default;
    virtual double area() const = 0;  // C.121: pure interface
};

class Circle : public Shape {
public:
    explicit Circle(double r) : radius_(r) {}
    double area() const override { return 3.14159 * radius_ * radius_; }

private:
    double radius_;
};
```### 反模式

- 在构造函数/析构函数中调用虚函数（C.82）
- 在非平凡类型上使用 `memset`/`memcpy` (C.90)
- 为虚函数和重写器提供不同的默认参数（C.140）
- 使数据成员成为“const”或引用，从而抑制移动/复制（C.12）

## 资源管理 (R.*)

### 关键规则

|规则|总结|
|------|---------|
| **R.1** |使用 RAII 自动管理资源 |
| **R.3** |原始指针 (`T*`) 是非拥有的 |
| **R.5** |优先选择作用域对象；不要进行不必要的堆分配 |
| **R.10** |避免 `malloc()`/`free()` |
| **R.11** |避免显式调用 `new` 和 `delete` |
| **R.20** |使用`unique_ptr`或`shared_ptr`来表示所有权 |
| **R.21** |优先选择“unique_ptr”而不是“shared_ptr”，除非共享所有权 |
| **R.22** |使用`make_shared()`来创建`shared_ptr`s |

### 智能指针的使用```cpp
// R.11 + R.20 + R.21: RAII with smart pointers
auto widget = std::make_unique<Widget>("config");  // unique ownership
auto cache  = std::make_shared<Cache>(1024);        // shared ownership

// R.3: Raw pointer = non-owning observer
void render(const Widget* w) {  // does NOT own w
    if (w) w->draw();
}

render(widget.get());
```### RAII 模式```cpp
// R.1: Resource acquisition is initialization
class FileHandle {
public:
    explicit FileHandle(const std::string& path)
        : handle_(std::fopen(path.c_str(), "r")) {
        if (!handle_) throw std::runtime_error("Failed to open: " + path);
    }

    ~FileHandle() {
        if (handle_) std::fclose(handle_);
    }

    FileHandle(const FileHandle&) = delete;
    FileHandle& operator=(const FileHandle&) = delete;
    FileHandle(FileHandle&& other) noexcept
        : handle_(std::exchange(other.handle_, nullptr)) {}
    FileHandle& operator=(FileHandle&& other) noexcept {
        if (this != &other) {
            if (handle_) std::fclose(handle_);
            handle_ = std::exchange(other.handle_, nullptr);
        }
        return *this;
    }

private:
    std::FILE* handle_;
};
```### 反模式

- 裸“新建”/“删除”（R.11）
- C++ 代码中的 `malloc()`/`free()` (R.10)
- 单个表达式中的多个资源分配（R.13——异常安全隐患）
- `shared_ptr` 其中 `unique_ptr` 就足够了 (R.21)

## 表达式和语句 (ES.*)

### 关键规则

|规则|总结|
|------|---------|
| **ES.5** |保持较小的范围 |
| **ES.20** |总是初始化一个对象 |
| **ES.23** |首选 `{}` 初始化语法 |
| **ES.25** |除非有意修改，否则声明对象 `const` 或 `constexpr`
| **ES.28** |使用 lambda 表达式对 `const` 变量进行复杂的初始化 |
| **ES.45** |避免魔法常量；使用符号常量 |
| **ES.46** |避免缩小/有损算术转换 |
| **ES.47** |使用 `nullptr` 而不是 `0` 或 `NULL` |
| **ES.48** |避免强制转换 |
| **ES.50** |不要抛弃 `const` |

### 初始化```cpp
// ES.20 + ES.23 + ES.25: Always initialize, prefer {}, default to const
const int max_retries{3};
const std::string name{"widget"};
const std::vector<int> primes{2, 3, 5, 7, 11};

// ES.28: Lambda for complex const initialization
const auto config = [&] {
    Config c;
    c.timeout = std::chrono::seconds{30};
    c.retries = max_retries;
    c.verbose = debug_mode;
    return c;
}();
```### 反模式

- 未初始化的变量（ES.20）
- 使用 `0` 或 `NULL` 作为指针（ES.47 -- 使用 `nullptr`）
- C 风格的强制转换（ES.48——使用 `static_cast`、`const_cast` 等）
- 抛弃 `const` (ES.50)
- 没有命名常量的幻数 (ES.45)
- 混合有符号和无符号算术（ES.100）
- 在嵌套范围内重用名称（ES.12）

## 错误处理 (E.*)

### 关键规则

|规则|总结|
|------|---------|
| **E.1** |在设计早期制定错误处理策略 |
| **E.2** |抛出异常以表明函数无法执行分配的任务 |
| **E.6** |使用 RAII 防止泄漏 |
| **E.12** |当抛出不可能或不可接受时使用“noexcept” |
| **E.14** |使用专门设计的用户定义类型作为例外 |
| **E.15** |按值抛出，按引用捕获 |
| **E.16** |析构函数、解除分配和交换绝不能失败 |
| **E.17** |不要试图捕获每个函数中的每个异常 |

### 异常层次结构```cpp
// E.14 + E.15: Custom exception types, throw by value, catch by reference
class AppError : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

class NetworkError : public AppError {
public:
    NetworkError(const std::string& msg, int code)
        : AppError(msg), status_code(code) {}
    int status_code;
};

void fetch_data(const std::string& url) {
    // E.2: Throw to signal failure
    throw NetworkError("connection refused", 503);
}

void run() {
    try {
        fetch_data("https://api.example.com");
    } catch (const NetworkError& e) {
        log_error(e.what(), e.status_code);
    } catch (const AppError& e) {
        log_error(e.what());
    }
    // E.17: Don't catch everything here -- let unexpected errors propagate
}
```### 反模式

- 抛出内置类型，如“int”或字符串文字（E.14）
- 按价值捕获（切片风险）（E.15）
- 空的 catch 块会默默地吞掉错误
- 使用异常进行流量控制（E.3）
- 基于全局状态的错误处理，如“errno”（E.28）

## 常量和不变性（Con.*）

### 所有规则

|规则|总结|
|------|---------|
| **Con.1** |默认情况下，使对象不可变 |
| **Con.2** |默认情况下，使成员函数为 `const` |
| **Con.3** |默认情况下，将指针和引用传递给 `const` |
| **Con.4** |对于构造后不改变的值使用 const |
| **Con.5** |使用 `constexpr` 来获取编译时可计算的值 |```cpp
// Con.1 through Con.5: Immutability by default
class Sensor {
public:
    explicit Sensor(std::string id) : id_(std::move(id)) {}

    // Con.2: const member functions by default
    const std::string& id() const { return id_; }
    double last_reading() const { return reading_; }

    // Only non-const when mutation is required
    void record(double value) { reading_ = value; }

private:
    const std::string id_;  // Con.4: never changes after construction
    double reading_{0.0};
};

// Con.3: Pass by const reference
void display(const Sensor& s) {
    std::cout << s.id() << ": " << s.last_reading() << '\n';
}

// Con.5: Compile-time constants
constexpr double PI = 3.14159265358979;
constexpr int MAX_SENSORS = 256;
```## 并发与并行 (CP.*)

### 关键规则

|规则|总结|
|------|---------|
| **CP.2** |避免数据竞争 |
| **CP.3** |最大限度地减少可写数据的显式共享 |
| **CP.4** |从任务而不是线程的角度思考 |
| **CP.8** |不要使用“易失性”进行同步 |
| **CP.20** |使用 RAII，切勿使用简单的 `lock()`/`unlock()` |
| **CP.21** |使用 `std::scoped_lock` 获取多个互斥体 |
| **CP.22** |持有锁时切勿调用未知代码 |
| **CP.42** |不要无条件等待|
| **CP.44** |请记住命名您的“lock_guard”和“unique_lock” |
| **CP.100** |除非绝对必要，否则不要使用无锁编程 |

### 安全锁定```cpp
// CP.20 + CP.44: RAII locks, always named
class ThreadSafeQueue {
public:
    void push(int value) {
        std::lock_guard<std::mutex> lock(mutex_);  // CP.44: named!
        queue_.push(value);
        cv_.notify_one();
    }

    int pop() {
        std::unique_lock<std::mutex> lock(mutex_);
        // CP.42: Always wait with a condition
        cv_.wait(lock, [this] { return !queue_.empty(); });
        const int value = queue_.front();
        queue_.pop();
        return value;
    }

private:
    std::mutex mutex_;             // CP.50: mutex with its data
    std::condition_variable cv_;
    std::queue<int> queue_;
};
```### 多个互斥锁```cpp
// CP.21: std::scoped_lock for multiple mutexes (deadlock-free)
void transfer(Account& from, Account& to, double amount) {
    std::scoped_lock lock(from.mutex_, to.mutex_);
    from.balance_ -= amount;
    to.balance_ += amount;
}
```### 反模式

- 用于同步的“易失性”（CP.8——仅用于硬件 I/O）
- 分离线程（CP.26——生命周期管理几乎变得不可能）
- 未命名的锁保护： `std::lock_guard<std::mutex>(m);` 立即销毁 (CP.44)
- 调用回调时持有锁（CP.22——死锁风险）
- 无需深厚专业知识的无锁编程（CP.100）

## 模板和通用编程 (T.*)

### 关键规则

|规则|总结|
|------|---------|
| **T.1** |使用模板提高抽象级别 |
| **T.2** |使用模板来表达多种参数类型的算法 |
| **T.10** |指定所有模板参数的概念 |
| **T.11** |尽可能使用标准概念 |
| **T.13** |更喜欢简单概念的简写符号 |
| **T.43** |优先选择“using”而不是“typedef” |
| **T.120** |仅当确实需要时才使用模板元编程 |
| **T.144** |不要专门化函数模板（而是重载）|

### 概念 (C++20)```cpp
#include <concepts>

// T.10 + T.11: Constrain templates with standard concepts
template<std::integral T>
T gcd(T a, T b) {
    while (b != 0) {
        a = std::exchange(b, a % b);
    }
    return a;
}

// T.13: Shorthand concept syntax
void sort(std::ranges::random_access_range auto& range) {
    std::ranges::sort(range);
}

// Custom concept for domain-specific constraints
template<typename T>
concept Serializable = requires(const T& t) {
    { t.serialize() } -> std::convertible_to<std::string>;
};

template<Serializable T>
void save(const T& obj, const std::string& path);
```### 反模式

- 可见命名空间中的不受约束的模板（T.47）
- 专门化函数模板而不是重载（T.144）
- `constexpr` 就足够的模板元编程 (T.120)
- `typedef` 而不是 `using` (T.43)

## 标准库 (SL.*)

### 关键规则

|规则|总结|
|------|---------|
| **SL.1** |尽可能使用库 |
| **SL.2** |与其他库相比，更喜欢标准库 |
| **SL.con.1** |与 C 数组相比，更喜欢 `std::array` 或 `std::vector` |
| **SL.con.2** |默认情况下更喜欢 `std::vector` |
| **SL.str.1** |使用 `std::string` 拥有字符序列 |
| **SL.str.2** |使用 `std::string_view` 引用字符序列 |
| **SL.io.50** |避免“endl”（使用“\n”——“endl”强制刷新）|```cpp
// SL.con.1 + SL.con.2: Prefer vector/array over C arrays
const std::array<int, 4> fixed_data{1, 2, 3, 4};
std::vector<std::string> dynamic_data;

// SL.str.1 + SL.str.2: string owns, string_view observes
std::string build_greeting(std::string_view name) {
    return "Hello, " + std::string(name) + "!";
}

// SL.io.50: Use '\n' not endl
std::cout << "result: " << value << '\n';
```## 枚举（Enum.*）

### 关键规则

|规则|总结|
|------|---------|
| **枚举1** |优先使用枚举而不是宏 |
| **枚举3** |更喜欢“枚举类”而不是普通的“枚举” |
| **枚举5** |不要对枚举器使用 ALL_CAPS |
| **枚举6** |避免无名枚举 |```cpp
// Enum.3 + Enum.5: Scoped enum, no ALL_CAPS
enum class Color { red, green, blue };
enum class LogLevel { debug, info, warning, error };

// BAD: plain enum leaks names, ALL_CAPS clashes with macros
enum { RED, GREEN, BLUE };           // Enum.3 + Enum.5 + Enum.6 violation
#define MAX_SIZE 100                  // Enum.1 violation -- use constexpr
```## 源文件和命名（SF.*、NL.*）

### 关键规则

|规则|总结|
|------|---------|
| **SF.1** |使用 `.cpp` 作为代码文件，使用 `.h` 作为接口文件 |
| **SF.7** |不要在标头中的全局范围内编写“using namespace” |
| **SF.8** |对所有“.h”文件使用“#include”保护 |
| **SF.11** |头文件应该是独立的 |
| **NL.5** |避免在名称中编码类型信息（无匈牙利表示法） |
| **NL.8** |使用一致的命名风格 |
| **NL.9** |仅对宏名称使用 ALL_CAPS |
| **NL.10** |更喜欢 `underscore_style` 名称 |

### 头护卫```cpp
// SF.8: Include guard (or #pragma once)
#ifndef PROJECT_MODULE_WIDGET_H
#define PROJECT_MODULE_WIDGET_H

// SF.11: Self-contained -- include everything this header needs
#include <string>
#include <vector>

namespace project::module {

class Widget {
public:
    explicit Widget(std::string name);
    const std::string& name() const;

private:
    std::string name_;
};

}  // namespace project::module

#endif  // PROJECT_MODULE_WIDGET_H
```### 命名约定```cpp
// NL.8 + NL.10: Consistent underscore_style
namespace my_project {

constexpr int max_buffer_size = 4096;  // NL.9: not ALL_CAPS (it's not a macro)

class tcp_connection {                 // underscore_style class
public:
    void send_message(std::string_view msg);
    bool is_connected() const;

private:
    std::string host_;                 // trailing underscore for members
    int port_;
};

}  // namespace my_project
```### 反模式

- 全局范围内的标头中的“using namespace std;”（SF.7）
- 取决于包含顺序的标头（SF.10、SF.11）
- 匈牙利表示法，如 `strName`、`iCount` (NL.5)
- ALL_CAPS 用于除宏之外的任何内容 (NL.9)

## 性能（每人*）

### 关键规则

|规则|总结|
|------|---------|
| **每1** |不要无故优化 |
| **每2** |不要过早优化 |
| **每 6** |不要在没有测量的情况下就性能做出声明 |
| **每 7** |设计以实现优化|
| **每 10** |依赖静态类型系统|
| **每11** |将计算从运行时移至编译时 |
| **每 19** |可预测地访问内存 |

### 指南```cpp
// Per.11: Compile-time computation where possible
constexpr auto lookup_table = [] {
    std::array<int, 256> table{};
    for (int i = 0; i < 256; ++i) {
        table[i] = i * i;
    }
    return table;
}();

// Per.19: Prefer contiguous data for cache-friendliness
std::vector<Point> points;           // GOOD: contiguous
std::vector<std::unique_ptr<Point>> indirect_points; // BAD: pointer chasing
```### 反模式

- 无需分析数据即可优化（Per.1、Per.6）
- 选择“聪明”的低级代码而不是清晰的抽象（Per.4、Per.5）
- 忽略数据布局和缓存行为（Per.19）

## 快速参考清单

在将 C++ 工作标记为完成之前：

- [ ] 没有原始的 `new`/`delete` -- 使用智能指针或 RAII (R.11)
- [ ] 在声明时初始化的对象 (ES.20)
- [ ] 变量默认为 `const`/`constexpr` (Con.1, ES.25)
- [ ] 成员函数尽可能为 `const` (Con.2)
- [ ] `enum class` 而不是普通的 `enum` (Enum.3)
- [ ] `nullptr` 而不是 `0`/`NULL` (ES.47)
- [ ] 无缩小转换 (ES.46)
- [ ] 没有 C 风格的强制转换 (ES.48)
- [ ] 单参数构造函数是“显式的”(C.46)
- [ ] 应用零规则或五规则（C.20、C.21）
- [ ] 基类析构函数是 public virtual 或 protected non-virtual (C.35)
- [ ] 模板受概念约束 (T.10)
- [ ] 全局范围内的标头中没有“使用命名空间”(SF.7)
- [ ] 标头包含防护并且是独立的（SF.8、SF.11）
- [ ] 锁使用 RAII (`scoped_lock`/`lock_guard`) (CP.20)
- [ ] 异常是自定义类型，按值抛出，按引用捕获（E.14、E.15）
- [ ] `'\n'` 而不是 `std::endl` (SL.io.50)
- [ ] 没有幻数 (ES.45)