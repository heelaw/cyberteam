# C++ TDD 命令

此命令使用 GoogleTest/GoogleMock 和 CMake/CTest 对 C++ 代码实施测试驱动的开发方法。

## 该命令的作用

1. **定义接口**：首先定义脚手架类/函数签名
2. **编写测试**：创建全面的 GoogleTest 测试用例（红色）
3. **运行测试**：验证测试失败的正确原因
4. **实现代码**：编写最少的代码即可通过（绿色）
5. **重构**：在保持测试绿色的同时进行改进
6. **检查覆盖率**：确保覆盖率超过 80%

## 何时使用

在以下情况下使用“/cpp-test”：
- 实现新的 C++ 函数或类
- 将测试覆盖率添加到现有代码中
- 修复错误（首先编写失败的测试）
- 构建关键业务逻辑
- 学习 C++ 中的 TDD 工作流程

## TDD 周期```
RED     → Write failing GoogleTest test
GREEN   → Implement minimal code to pass
REFACTOR → Improve code, tests stay green
REPEAT  → Next test case
```## 会话示例````
User: /cpp-test I need a function to validate email addresses

Agent:
# TDD Session: Email Validator

## Step 1: Define Interface

```程序文件
// 验证器/email.hpp
#pragma 一次
#include <字符串>
#include <预期>

枚举类 EmailError {
    空，
    格式无效
};

std::expected<void, EmailError> validate_email(const std::string& email);```

## Step 2: Write Tests (RED)

```程序文件
// 验证器/email_test.cpp
#include <gtest/gtest.h>
#include“电子邮件.hpp”

测试（验证电子邮件，接受简单电子邮件）{
    自动结果 = validate_email("user@example.com");
    EXPECT_TRUE(结果.has_value());
}

测试（验证电子邮件，接受子域）{
    EXPECT_TRUE(validate_email("user@mail.example.com").has_value());
}

测试（验证电子邮件，AcceptsPlus）{
    EXPECT_TRUE(validate_email("user+tag@example.com").has_value());
}

测试（验证电子邮件，拒绝空）{
    自动结果 = validate_email("");
    ASSERT_FALSE(结果.has_value());
    EXPECT_EQ(result.error(), EmailError::Empty);
}

测试（验证电子邮件，拒绝NoAtSign）{
    EXPECT_FALSE(validate_email("userexample.com").has_value());
}

测试（验证电子邮件，拒绝NoDomain）{
    EXPECT_FALSE(validate_email("user@").has_value());
}

测试（验证电子邮件，拒绝NoLocalPart）{
    EXPECT_FALSE(validate_email("@example.com").has_value());
}```

## Step 3: Run Tests - Verify FAIL

```巴什
$ cmake --build build && ctest --test-dir build --output-on-failure

1/1 测试#1：email_validator_test .....***失败
    --- 对“validate_email”的未定义引用

失败```

✓ Tests fail as expected (unimplemented).

## Step 4: Implement Minimal Code (GREEN)

```程序文件
// 验证器/email.cpp
#include“电子邮件.hpp”
#include <正则表达式>

std::expected<void, EmailError> validate_email(const std::string& email) {
    如果（电子邮件.空（））{
        返回 std::unexpected(EmailError::Empty);
    }
    静态 const std::regex 模式(R"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})");
    if (!std::regex_match(电子邮件、模式)) {
        返回 std::unexpected(EmailError::InvalidFormat);
    }
    返回 {};
}```

## Step 5: Run Tests - Verify PASS

```巴什
$ cmake --build build && ctest --test-dir build --output-on-failure

1/1 测试 #1：email_validator_test ..... 通过 0.01 秒

100% 测试通过。```

✓ All tests passing!

## Step 6: Check Coverage

```巴什
$ cmake -DCMAKE_CXX_FLAGS="--coverage" -B 构建 && cmake --build 构建
$ ctest --test-dir 构建
$ lcov --capture --目录构建 --输出文件覆盖率.info
$ lcov --列出覆盖范围.info

验证器/email.cpp | 100%```

✓ Coverage: 100%

## TDD Complete!
````

## 测试模式

### 基本测试```cpp
TEST(SuiteName, TestName) {
    EXPECT_EQ(add(2, 3), 5);
    EXPECT_NE(result, nullptr);
    EXPECT_TRUE(is_valid);
    EXPECT_THROW(func(), std::invalid_argument);
}
```### 赛程```cpp
class DatabaseTest : public ::testing::Test {
protected:
    void SetUp() override { db_ = create_test_db(); }
    void TearDown() override { db_.reset(); }
    std::unique_ptr<Database> db_;
};

TEST_F(DatabaseTest, InsertsRecord) {
    db_->insert("key", "value");
    EXPECT_EQ(db_->get("key"), "value");
}
```### 参数化测试```cpp
class PrimeTest : public ::testing::TestWithParam<std::pair<int, bool>> {};

TEST_P(PrimeTest, ChecksPrimality) {
    auto [input, expected] = GetParam();
    EXPECT_EQ(is_prime(input), expected);
}

INSTANTIATE_TEST_SUITE_P(Primes, PrimeTest, ::testing::Values(
    std::make_pair(2, true),
    std::make_pair(4, false),
    std::make_pair(7, true)
));
```## 覆盖命令```bash
# Build with coverage
cmake -DCMAKE_CXX_FLAGS="--coverage" -DCMAKE_EXE_LINKER_FLAGS="--coverage" -B build

# Run tests
cmake --build build && ctest --test-dir build

# Generate coverage report
lcov --capture --directory build --output-file coverage.info
lcov --remove coverage.info '/usr/*' --output-file coverage.info
genhtml coverage.info --output-directory coverage_html
```## 覆盖目标

|代码类型 |目标|
|------------|--------|
|关键业务逻辑 | 100% |
|公共 API | 90%+ |
|通用代码| 80%+ |
|生成的代码 |排除 |

## TDD 最佳实践

**做：**
- 在任何实施之前先编写测试
- 每次更改后运行测试
- 在适当的时候使用“EXPECT_*”（继续）而不是“ASSERT_*”（停止）
- 测试行为，而不是实现细节
- 包括边缘情况（空、空、最大值、边界条件）

**不要：**
- 在测试之前编写实现
- 跳过红色阶段
- 直接测试私有方法（通过公共API测试）
- 在测试中使用“sleep”
- 忽略片状测试

## 相关命令

- `/cpp-build` - 修复构建错误
- `/cpp-review` - 实施后审查代码
- `/verify` - 运行完整的验证循环

## 相关

- 技能：`技能/cpp-测试/`
- 技能：`技能/tdd-工作流程/`