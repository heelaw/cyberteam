# 一切克劳德代码 - OpenCode 说明

本文档整合了 Claude Code 配置的核心规则和指南，以便与 OpenCode 一起使用。

## 安全指南（重要）

### 强制安全检查

在任何提交之前：
- [ ] 无硬编码秘密（API 密钥、密码、令牌）
- [ ] 所有用户输入均已验证
- [ ] SQL注入预防（参数化查询）
- [ ] XSS 预防（经过净化的 HTML）
- [ ] CSRF 保护已启用
- [ ] 验证/授权已验证
- [ ] 所有端点的速率限制
- [ ] 错误消息不会泄露敏感数据

### 秘密管理```typescript
// NEVER: Hardcoded secrets
const apiKey = "sk-proj-xxxxx"

// ALWAYS: Environment variables
const apiKey = process.env.OPENAI_API_KEY

if (!apiKey) {
  throw new Error('OPENAI_API_KEY not configured')
}
```### 安全响应协议

如果发现安全问题：
1.立即停止
2. 使用 **security-reviewer** 代理
3. 在继续之前修复关键问题
4.轮换任何暴露的秘密
5. 检查整个代码库是否存在类似问题

---

## 编码风格

### 不变性（关键）

总是创建新对象，永远不要改变：```javascript
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
```### 文件组织

很多小文件 > 很少的大文件：
- 高内聚、低耦合
- 典型 200-400 行，最多 800 行
- 从大型组件中提取实用程序
- 按功能/领域而不是类型进行组织

### 错误处理

始终全面处理错误：```typescript
try {
  const result = await riskyOperation()
  return result
} catch (error) {
  console.error('Operation failed:', error)
  throw new Error('Detailed user-friendly message')
}
```### 输入验证

始终验证用户输入：```typescript
import { z } from 'zod'

const schema = z.object({
  email: z.string().email(),
  age: z.number().int().min(0).max(150)
})

const validated = schema.parse(input)
```### 代码质量检查表

在标记工作完成之前：
- [ ] 代码可读且命名良好
- [ ] 函数很小（<50 行）
- [ ] 文件被聚焦（<800 行）
- [ ] 无深层嵌套（>4 层）
- [ ] 正确的错误处理
- [ ] 没有console.log语句
- [ ] 无硬编码值
- [ ] 无突变（使用不可变模式）

---

## 测试要求

### 最低测试覆盖率：80%

测试类型（全部必需）：
1. **单元测试** - 单独的功能、实用程序、组件
2. **集成测试** - API端点、数据库操作
3. **E2E 测试** - 关键用户流程（剧作家）

### 测试驱动开发

强制性工作流程：
1.先写测试（红色）
2. 运行测试 - 它应该失败
3. 编写最小实现（绿色）
4. 运行测试 - 它应该通过
5.重构（改进）
6. 验证覆盖率（80%+）

### 测试失败故障排除

1.使用**tdd-guide**代理
2. 检查测试隔离
3.验证mock是否正确
4.修复实施，而不是测试（除非测试是错误的）

---

## Git 工作流程

### 提交消息格式```
<type>: <description>

<optional body>
```类型：feat、fix、refactor、docs、test、chore、perf、ci

### 拉取请求工作流程

创建 PR 时：
1.分析完整的提交历史记录（不仅仅是最新的提交）
2. 使用 `git diff [base-branch]...HEAD` 查看所有更改
3. 草拟全面的公关摘要
4. 将测试计划包含在 TODO 中
5. 如果有新分支，则使用“-u”标志推送

### 功能实施工作流程

1. **先计划**
   - 使用 **planner** 代理创建实施计划
   - 识别依赖性和风险
   - 分为几个阶段

2. **TDD 方法**
   - 使用 **tdd-guide** 代理
   - 首先编写测试（红色）
   - 实施以通过测试（绿色）
   - 重构（改进）
   - 验证 80% 以上的覆盖率

3. **代码审查**
   - 编写代码后立即使用 **code-reviewer** 代理
   - 解决关键和重大问题
   - 尽可能修复中等问题

4. **提交和推送**
   - 详细的提交消息
   - 遵循传统的提交格式

---

## 代理编排

### 可用代理

|代理|目的|何时使用 |
|--------|---------|-------------|
|策划师|实施规划|复杂功能，重构|
|建筑师 |系统设计|架构决策 |
| TDD 指南 |测试驱动开发 |新功能、错误修复 |
|代码审查员 |代码审查 |写完代码后|
|安全审查员 |证券分析|提交之前 |
|构建错误解析器 |修复构建错误 |当构建失败时 |
| e2e-跑步者 |端到端测试|关键用户流量|
|重构清理器 |死代码清理 |代码维护 |
|文档更新程序 |文档 |更新文档 |
|去评论家 |进行代码审查 |去项目 |
|去构建解析器 |去构建错误| Go 构建失败 |
|数据库审阅者 |数据库优化 | SQL、模式设计 |

### 立即使用代理

无需用户提示：
1. 复杂的功能请求 - 使用 **planner** 代理
2. 刚刚编写/修改的代码 - 使用 **code-reviewer** 代理
3. Bug 修复或新功能 - 使用 **tdd-guide** 代理
4. 架构决策 - 使用 **architect** 代理

---

## 性能优化

### 模型选择策略

**俳句**（Sonnet 功能的 90%，成本节省 3 倍）：
- 频繁调用的轻量级代理
- 结对编程和代码生成
- 多代理系统中的工作代理

**十四行诗**（最佳编码模型）：
- 主要开发工作
- 编排多代理工作流程
- 复杂的编码任务

**Opus**（最深刻的推理）：
- 复杂的架构决策
- 最大推理要求
- 研究和分析任务

### 上下文窗口管理

避免使用最后 20% 的上下文窗口：
- 大规模重构
- 跨多个文件的功能实现
- 调试复杂的交互

### 构建故障排除

如果构建失败：
1. 使用 **build-error-resolver** 代理
2. 分析错误信息
3. 逐步修复
4. 每次修复后进行验证

---

## 常见模式

### API 响应格式```typescript
interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  meta?: {
    total: number
    page: number
    limit: number
  }
}
```### 自定义 Hook 模式```typescript
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const handler = setTimeout(() => setDebouncedValue(value), delay)
    return () => clearTimeout(handler)
  }, [value, delay])

  return debouncedValue
}
```### 存储库模式```typescript
interface Repository<T> {
  findAll(filters?: Filters): Promise<T[]>
  findById(id: string): Promise<T | null>
  create(data: CreateDto): Promise<T>
  update(id: string, data: UpdateDto): Promise<T>
  delete(id: string): Promise<void>
}
```---

## OpenCode 特定注释

由于 OpenCode 不支持钩子，因此在 Claude Code 中自动执行的以下操作必须手动完成：

### 编写/编辑代码后
- 运行 `prettier --write <file>` 来格式化 JS/TS 文件
- 运行“npx tsc --noEmit”来检查 TypeScript 错误
- 检查console.log语句并删除它们

### 提交之前
- 手动运行安全检查
- 验证代码中没有秘密
- 运行完整的测试套件

### 可用命令

在 OpenCode 中使用以下命令：
- `/plan` - 创建实施计划
- `/tdd` - 强制 TDD 工作流程
- `/code-review` - 审查代码更改
- `/security` - 运行安全审查
- `/build-fix` - 修复构建错误
- `/e2e` - 生成 E2E 测试
- `/refactor-clean` - 删除死代码
- `/orchestrate` - 多代理工作流程

---

## 成功指标

当您满足以下条件时，您就成功了：
- 所有测试均通过（覆盖率超过 80%）
- 无安全漏洞
- 代码可读且可维护
- 性能可以接受
- 满足用户要求