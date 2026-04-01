# C++ 测试（代理技能）

使用 GoogleTest/GoogleMock 和 CMake/CTest 的现代 C++ (C++17/20) 以代理为中心的测试工作流程。

## 何时使用

- 编写新的 C++ 测试或修复现有测试
- 设计 C++ 组件的单元/集成测试覆盖率
- 添加测试覆盖率、CI 门控或回归保护
- 配置 CMake/CTest 工作流程以实现一致执行
- 调查测试失败或不稳定的行为
- 启用内存/竞赛诊断的消毒剂

### 何时不使用

- 无需测试更改即可实现新产品功能
- 与测试覆盖率或失败无关的大规模重构
- 性能调整无需测试回归来验证
- 非 C++ 项目或非测试任务

## 核心概念

- **TDD 循环**：红色 → 绿色 → 重构（首先测试，最小修复，然后清理）。
- **隔离**：相对于全局状态，更喜欢依赖注入和伪造。
- **测试布局**：`测试/单元`、`测试/集成`、`测试/测试数据`。
- **Mocks 与 fakes**：mock 用于交互，fake 用于状态行为。
- **CTest 发现**：使用 `gtest_discover_tests()` 进行稳定的测试发现。
- **CI 信号**：首先运行子集，然后使用“--output-on-failure”运行完整套件。

## TDD 工作流程

遵循 RED → GREEN → REFACTOR 循环：

1. **红色**：编写一个捕获新行为的失败测试
2. **绿色**：实现最小的改变以通过
3. **重构**：在测试保持绿色的同时进行清理```cpp
// tests/add_test.cpp
#include <gtest/gtest.h>

int Add(int a, int b); // Provided by production code.

TEST(AddTest, AddsTwoNumbers) { // RED
  EXPECT_EQ(Add(2, 3), 5);
}

// src/add.cpp
int Add(int a, int b) { // GREEN
  return a + b;
}

// REFACTOR: simplify/rename once tests pass
```## 代码示例

### 基本单元测试（gtest）```cpp
// tests/calculator_test.cpp
#include <gtest/gtest.h>

int Add(int a, int b); // Provided by production code.

TEST(CalculatorTest, AddsTwoNumbers) {
    EXPECT_EQ(Add(2, 3), 5);
}
```### 夹具（gtest）```cpp
// tests/user_store_test.cpp
// Pseudocode stub: replace UserStore/User with project types.
#include <gtest/gtest.h>
#include <memory>
#include <optional>
#include <string>

struct User { std::string name; };
class UserStore {
public:
    explicit UserStore(std::string /*path*/) {}
    void Seed(std::initializer_list<User> /*users*/) {}
    std::optional<User> Find(const std::string &/*name*/) { return User{"alice"}; }
};

class UserStoreTest : public ::testing::Test {
protected:
    void SetUp() override {
        store = std::make_unique<UserStore>(":memory:");
        store->Seed({{"alice"}, {"bob"}});
    }

    std::unique_ptr<UserStore> store;
};

TEST_F(UserStoreTest, FindsExistingUser) {
    auto user = store->Find("alice");
    ASSERT_TRUE(user.has_value());
    EXPECT_EQ(user->name, "alice");
}
```### 模拟（gmock）```cpp
// tests/notifier_test.cpp
#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include <string>

class Notifier {
public:
    virtual ~Notifier() = default;
    virtual void Send(const std::string &message) = 0;
};

class MockNotifier : public Notifier {
public:
    MOCK_METHOD(void, Send, (const std::string &message), (override));
};

class Service {
public:
    explicit Service(Notifier &notifier) : notifier_(notifier) {}
    void Publish(const std::string &message) { notifier_.Send(message); }

private:
    Notifier &notifier_;
};

TEST(ServiceTest, SendsNotifications) {
    MockNotifier notifier;
    Service service(notifier);

    EXPECT_CALL(notifier, Send("hello")).Times(1);
    service.Publish("hello");
}
```### CMake/CTest 快速入门```cmake
# CMakeLists.txt (excerpt)
cmake_minimum_required(VERSION 3.20)
project(example LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)
# Prefer project-locked versions. If using a tag, use a pinned version per project policy.
set(GTEST_VERSION v1.17.0) # Adjust to project policy.
FetchContent_Declare(
  googletest
  # Google Test framework (official repository)
  URL https://github.com/google/googletest/archive/refs/tags/${GTEST_VERSION}.zip
)
FetchContent_MakeAvailable(googletest)

add_executable(example_tests
  tests/calculator_test.cpp
  src/calculator.cpp
)
target_link_libraries(example_tests GTest::gtest GTest::gmock GTest::gtest_main)

enable_testing()
include(GoogleTest)
gtest_discover_tests(example_tests)
``````bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build -j
ctest --test-dir build --output-on-failure
```## 运行测试```bash
ctest --test-dir build --output-on-failure
ctest --test-dir build -R ClampTest
ctest --test-dir build -R "UserStoreTest.*" --output-on-failure
``````bash
./build/example_tests --gtest_filter=ClampTest.*
./build/example_tests --gtest_filter=UserStoreTest.FindsExistingUser
```## 调试失败

1. 使用 gtest 过滤器重新运行单一失败测试。
2. 在失败的断言周围添加范围日志记录。
3. 在启用消毒剂的情况下重新运行。
4. 一旦根本原因得到解决，就扩展到整套产品。

## 覆盖范围

更喜欢目标级别设置而不是全局标志。```cmake
option(ENABLE_COVERAGE "Enable coverage flags" OFF)

if(ENABLE_COVERAGE)
  if(CMAKE_CXX_COMPILER_ID MATCHES "GNU")
    target_compile_options(example_tests PRIVATE --coverage)
    target_link_options(example_tests PRIVATE --coverage)
  elseif(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    target_compile_options(example_tests PRIVATE -fprofile-instr-generate -fcoverage-mapping)
    target_link_options(example_tests PRIVATE -fprofile-instr-generate)
  endif()
endif()
```GCC + gcov + lcov：```bash
cmake -S . -B build-cov -DENABLE_COVERAGE=ON
cmake --build build-cov -j
ctest --test-dir build-cov
lcov --capture --directory build-cov --output-file coverage.info
lcov --remove coverage.info '/usr/*' --output-file coverage.info
genhtml coverage.info --output-directory coverage
```铿锵 + llvm-cov：```bash
cmake -S . -B build-llvm -DENABLE_COVERAGE=ON -DCMAKE_CXX_COMPILER=clang++
cmake --build build-llvm -j
LLVM_PROFILE_FILE="build-llvm/default.profraw" ctest --test-dir build-llvm
llvm-profdata merge -sparse build-llvm/default.profraw -o build-llvm/default.profdata
llvm-cov report build-llvm/example_tests -instr-profile=build-llvm/default.profdata
```## 消毒剂```cmake
option(ENABLE_ASAN "Enable AddressSanitizer" OFF)
option(ENABLE_UBSAN "Enable UndefinedBehaviorSanitizer" OFF)
option(ENABLE_TSAN "Enable ThreadSanitizer" OFF)

if(ENABLE_ASAN)
  add_compile_options(-fsanitize=address -fno-omit-frame-pointer)
  add_link_options(-fsanitize=address)
endif()
if(ENABLE_UBSAN)
  add_compile_options(-fsanitize=undefined -fno-omit-frame-pointer)
  add_link_options(-fsanitize=undefined)
endif()
if(ENABLE_TSAN)
  add_compile_options(-fsanitize=thread)
  add_link_options(-fsanitize=thread)
endif()
```## 片状测试护栏

- 切勿使用`sleep`进行同步；使用条件变量或锁存器。
- 使每个测试的临时目录都是唯一的，并始终清理它们。
- 避免单元测试中的实时、网络或文件系统依赖性。
- 使用确定性种子进行随机输入。

## 最佳实践

### 做

- 保持测试的确定性和隔离性
- 更喜欢依赖注入而不是全局变量
- 使用`ASSERT_*`作为前提条件，使用`EXPECT_*`进行多重检查
- CTest 标签或目录中的单独单元测试与集成测试
- 在 CI 中运行清理程序以进行内存和竞争检测

### 不要

- 在单元测试中不依赖实时或网络
- 当可以使用条件变量时，不要使用睡眠作为同步
- 不要过度模拟简单的值对象
- 不要对非关键日志使用脆弱的字符串匹配

### 常见陷阱

- **使用固定临时路径** → 每个测试生成唯一的临时目录并清理它们。
- **依赖挂钟时间** → 注入时钟或使用假时间源。
- **片状并发测试** → 使用条件变量/锁存器和有界等待。
- **隐藏全局状态** → 重置灯具中的全局状态或删除全局变量。
- **过度模拟** → 更喜欢假的状态行为并且仅模拟交互。
- **缺少消毒剂运行** → 在 CI 中添加 ASan/UBSan/TSan 构建。
- **仅调试版本的覆盖率** → 确保覆盖率目标使用一致的标志。

## 可选附录：模糊测试/属性测试

仅当项目已支持 LLVM/libFuzzer 或属性测试库时才使用。

- **libFuzzer**：最适合具有最少 I/O 的纯函数。
- **RapidCheck**：基于属性的测试来验证不变量。

最小 libFuzzer 工具（伪代码：替换 ParseConfig）：```cpp
#include <cstddef>
#include <cstdint>
#include <string>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    std::string input(reinterpret_cast<const char *>(data), size);
    // ParseConfig(input); // project function
    return 0;
}
```## GoogleTest 的替代品

- **Catch2**：仅限标头、富有表现力的匹配器
- **doctest**：轻量级、最小的编译开销