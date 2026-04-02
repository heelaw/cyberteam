# 示例项目 CLAUDE.md

这是一个示例项目级 CLAUDE.md 文件。将其放置在您的项目根目录中。

## 项目概述

[您的项目的简要描述 - 它的用途、技术堆栈]

## 关键规则

### 1. 代码组织

- 许多小文件覆盖少数大文件
- 高内聚、低耦合
- 典型 200-400 行，每个文件最多 800 行
- 按功能/领域而不是类型进行组织

### 2. 代码风格

- 代码、注释或文档中没有表情符号
- 始终不变性 - 永远不会改变对象或数组
- 生产代码中没有console.log
- 使用 try/catch 进行正确的错误处理
- 使用 Zod 或类似工具进行输入验证

### 3. 测试

- TDD：首先编写测试
- 最低覆盖率 80%
- 实用程序的单元测试
- API 集成测试
- 关键流程的端到端测试

### 4. 安全

- 没有硬编码的秘密
- 敏感数据的环境变量
- 验证所有用户输入
- 仅参数化查询
- 启用CSRF保护

## 文件结构```
src/
|-- app/              # Next.js app router
|-- components/       # Reusable UI components
|-- hooks/            # Custom React hooks
|-- lib/              # Utility libraries
|-- types/            # TypeScript definitions
```## 关键模式

### API 响应格式```typescript
interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
}
```### 错误处理```typescript
try {
  const result = await operation()
  return { success: true, data: result }
} catch (error) {
  console.error('Operation failed:', error)
  return { success: false, error: 'User-friendly message' }
}
```## 环境变量```bash
# Required
DATABASE_URL=
API_KEY=

# Optional
DEBUG=false
```## 可用命令

- `/tdd` - 测试驱动的开发工作流程
- `/plan` - 创建实施计划
- `/code-review` - 检查代码质量
- `/build-fix` - 修复构建错误

## Git 工作流程

- 常规提交：`feat:`、`fix:`、`refactor:`、`docs:`、`test:`
- 永远不要直接提交到 main
- PR 需要审核
- 合并之前必须通过所有测试