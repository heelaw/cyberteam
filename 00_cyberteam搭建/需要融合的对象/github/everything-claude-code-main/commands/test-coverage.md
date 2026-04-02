# 测试覆盖率

分析测试覆盖率、找出差距并生成缺失的测试，以达到 80% 以上的覆盖率。

## 步骤 1：检测测试框架

|指标|覆盖指挥|
|------------|------------------|
| `jest.config.*` 或 `package.json` 玩笑 | `npx jest --coverage --coverageReporters=json-summary` |
| `vitest.config.*` | `npx vitest 运行 --coverage` |
| `pytest.ini` / `pyproject.toml` pytest | `pytest --cov=src --cov-report=json` |
| `Cargo.toml` | `货物 llvm-cov --json` |
| `pom.xml` 与 JaCoCo | `mvn 测试 jacoco:报告` |
| `go.mod` | `去测试-coverprofile=coverage.out ./...` |

## 步骤 2：分析覆盖率报告

1.运行覆盖命令
2. 解析输出（JSON摘要或终端输出）
3. 列出**覆盖率低于 80%** 的文件，按最差优先排序
4. 对于每个未覆盖的文件，确定：
   - 未经测试的函数或方法
   - 缺少分支覆盖（if/else、switch、错误路径）
   - 导致分母膨胀的死代码

## 步骤 3：生成缺失的测试

对于每个未覆盖的文件，按照以下优先级生成测试：

1. **幸福之路**——具有有效输入的核心功能
2. **错误处理** — 无效输入、丢失数据、网络故障
3. **边缘情况** — 空数组、null/未定义、边界值 (0、-1、MAX_INT)
4. **分支覆盖** - 每个 if/else、switch case、三元

### 测试生成规则

- 将测试放在源旁边：`foo.ts`→`foo.test.ts`（或项目约定）
- 使用项目中现有的测试模式（导入样式、断言库、模拟方法）
- 模拟外部依赖项（数据库、API、文件系统）
- 每个测试应该是独立的——测试之间没有共享的可变状态
- 描述性地命名测试：`test_create_user_with_duplicate_email_returns_409`

## 步骤 4：验证

1. 运行完整的测试套件——所有测试都必须通过
2. 重新运行覆盖率——验证改进
3. 如果仍低于 80%，则对剩余间隙重复步骤 3

## 步骤 5：报告

显示前后对比：```
Coverage Report
──────────────────────────────
File                   Before  After
src/services/auth.ts   45%     88%
src/utils/validation.ts 32%    82%
──────────────────────────────
Overall:               67%     84%  ✅
```## 重点领域

- 具有复杂分支的函数（高圈复杂度）
- 错误处理程序和 catch 块
- 跨代码库使用的实用函数
- API端点处理程序（请求→响应流）
- 边缘情况：空、未定义、空字符串、空数组、零、负数