# 更新代码映射

分析代码库结构并生成精简的架构文档。

## 步骤 1：扫描项目结构

1. 确定项目类型（monorepo、单一应用程序、库、微服务）
2.查找所有源码目录(src/,lib/,app/,packages/)
3.映射入口点（main.ts、index.ts、app.py、main.go等）

## 步骤 2：生成代码图

在“docs/CODEMAPS/”（或“.reports/codemaps/”）中创建或更新代码映射：

|文件 |内容 |
|------|----------|
| `架构.md` |高层系统图、服务边界、数据流 |
| `后端.md` | API 路由、中间件链、服务 → 存储库映射 |
| `frontend.md` |页面树、组件层次结构、状态管理流程|
| `数据.md` |数据库表、关系、迁移历史 |
| `dependency.md` |外部服务、第三方集成、共享库 |

### 代码图格式

每个代码映射都应该是 token-lean 的——针对 AI 上下文消耗进行了优化：```markdown
# Backend Architecture

## Routes
POST /api/users → UserController.create → UserService.create → UserRepo.insert
GET  /api/users/:id → UserController.get → UserService.findById → UserRepo.findById

## Key Files
src/services/user.ts (business logic, 120 lines)
src/repos/user.ts (database access, 80 lines)

## Dependencies
- PostgreSQL (primary data store)
- Redis (session cache, rate limiting)
- Stripe (payment processing)
```## 步骤 3：差异检测

1.如果之前的codemap存在，计算diff百分比
2. 如果更改> 30%，则显示差异并在覆盖之前请求用户批准
3. 如果变化<= 30%，则就地更新

## 步骤 4：添加元数据

向每个代码映射添加新鲜度标头：```markdown
<!-- Generated: 2026-02-11 | Files scanned: 142 | Token estimate: ~800 -->
```## 步骤5：保存分析报告

将摘要写入`.reports/codemap-diff.txt`：
- 自上次扫描以来添加/删除/修改的文件
- 检测到新的依赖项
- 架构变更（新路线、新服务等）
- 90 多天内未更新的文档的过时警告

## 提示

- 关注**高层结构**，而不是实现细节
- 优先使用**文件路径和函数签名**而不是完整的代码块
- 将每个代码映射保持在 **1000 个标记**之下，以实现高效的上下文加载
- 使用 ASCII 图表来表示数据流，而不是冗长的描述
- 在主要功能添加或重构会话之后运行