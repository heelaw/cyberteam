# TypeScript/JavaScript 编码风格

> 此文件使用 TypeScript/JavaScript 特定内容扩展了通用编码样式规则。

## 不变性

使用扩展运算符进行不可变更新：```typescript
// WRONG: Mutation
function updateUser(user, name) {
  user.name = name  // MUTATION!
  return user
}

// CORRECT: Immutability
function updateUser(user, name) {
  return {
    ...user,
    name
  }
}
```## 错误处理

将 async/await 与 try-catch 结合使用：```typescript
try {
  const result = await riskyOperation()
  return result
} catch (error) {
  console.error('Operation failed:', error)
  throw new Error('Detailed user-friendly message')
}
```## 输入验证

使用 Zod 进行基于模式的验证：```typescript
import { z } from 'zod'

const schema = z.object({
  email: z.string().email(),
  age: z.number().int().min(0).max(150)
})

const validated = schema.parse(input)
```## 控制台.log

- 生产代码中没有“console.log”语句
- 使用适当的日志库代替
- 查看钩子以进行自动检测