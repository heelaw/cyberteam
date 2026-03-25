# TypeScript/JavaScript 编码风格

> 此文件使用 TypeScript/JavaScript 特定内容扩展 [common/coding-style.md](../common/coding-style.md)。

## 类型和接口

使用类型使公共 API、共享模型和组件属性显式、可读和可重用。

### 公共 API

- 向导出函数、共享实用程序和公共类方法添加参数和返回类型
- 让 TypeScript 推断明显的局部变量类型
- 将重复的内联对象形状提取到命名类型或接口中```typescript
// WRONG: Exported function without explicit types
export function formatUser(user) {
  return `${user.firstName} ${user.lastName}`
}

// CORRECT: Explicit types on public APIs
interface User {
  firstName: string
  lastName: string
}

export function formatUser(user: User): string {
  return `${user.firstName} ${user.lastName}`
}
```### 接口与类型别名

- 对可以扩展或实现的对象形状使用“接口”
- 对并集、交集、元组、映射类型和实用程序类型使用“type”
- 优先使用字符串文字联合而不是“enum”，除非需要“enum”来实现互操作性```typescript
interface User {
  id: string
  email: string
}

type UserRole = 'admin' | 'member'
type UserWithRole = User & {
  role: UserRole
}
```### 避免“任何”

- 避免应用程序代码中的“any”
- 对外部或不受信任的输入使用“未知”，然后安全地缩小范围
- 当值的类型取决于调用者时使用泛型```typescript
// WRONG: any removes type safety
function getErrorMessage(error: any) {
  return error.message
}

// CORRECT: unknown forces safe narrowing
function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message
  }

  return 'Unexpected error'
}
```### 反应道具

- 使用命名的“interface”或“type”定义组件道具
- 明确输入回调道具
- 除非有特定原因，否则不要使用“React.FC”```typescript
interface User {
  id: string
  email: string
}

interface UserCardProps {
  user: User
  onSelect: (id: string) => void
}

function UserCard({ user, onSelect }: UserCardProps) {
  return <button onClick={() => onSelect(user.id)}>{user.email}</button>
}
```### JavaScript 文件

- 在“.js”和“.jsx”文件中，当类型提高清晰度并且 TypeScript 迁移不切实际时，请使用 JSDoc
- 保持 JSDoc 与运行时行为保持一致```javascript
/**
 * @param {{ firstName: string, lastName: string }} user
 * @returns {string}
 */
export function formatUser(user) {
  return `${user.firstName} ${user.lastName}`
}
```## 不变性

使用扩展运算符进行不可变更新：```typescript
interface User {
  id: string
  name: string
}

// WRONG: Mutation
function updateUser(user: User, name: string): User {
  user.name = name // MUTATION!
  return user
}

// CORRECT: Immutability
function updateUser(user: Readonly<User>, name: string): User {
  return {
    ...user,
    name
  }
}
```## 错误处理

将 async/await 与 try-catch 结合使用并安全地缩小未知错误：```typescript
interface User {
  id: string
  email: string
}

declare function riskyOperation(userId: string): Promise<User>

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message
  }

  return 'Unexpected error'
}

const logger = {
  error: (message: string, error: unknown) => {
    // Replace with your production logger (for example, pino or winston).
  }
}

async function loadUser(userId: string): Promise<User> {
  try {
    const result = await riskyOperation(userId)
    return result
  } catch (error: unknown) {
    logger.error('Operation failed', error)
    throw new Error(getErrorMessage(error))
  }
}
```## 输入验证

使用 Zod 进行基于模式的验证并从模式推断类型：```typescript
import { z } from 'zod'

const userSchema = z.object({
  email: z.string().email(),
  age: z.number().int().min(0).max(150)
})

type UserInput = z.infer<typeof userSchema>

const validated: UserInput = userSchema.parse(input)
```## 控制台.log

- 生产代码中没有“console.log”语句
- 使用适当的日志库代替
- 查看钩子以进行自动检测