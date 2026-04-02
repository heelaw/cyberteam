# 测试驱动的开发工作流程

此技能可确保所有代码开发都遵循 TDD 原则并具有全面的测试覆盖率。

## 何时激活

- 编写新特性或功能
- 修复错误或问题
- 重构现有代码
- 添加API端点
- 创建新组件

## 核心原则

### 1. 在编写代码之前进行测试
始终先编写测试，然后实现代码以使测试通过。

### 2. 覆盖范围要求
- 最低80%覆盖率（单元+集成+E2E）
- 涵盖所有边缘情况
- 测试错误场景
- 边界条件已验证

### 3. 测试类型

#### 单元测试
- 单独的功能和实用程序
- 组件逻辑
- 纯函数
- 助手和实用程序

#### 集成测试
- API端点
- 数据库操作
- 服务交互
- 外部API调用

#### E2E 测试（剧作家）
- 关键用户流量
- 完整的工作流程
- 浏览器自动化
- 用户界面交互

## TDD 工作流程步骤

### 第 1 步：编写用户旅程```
As a [role], I want to [action], so that [benefit]

Example:
As a user, I want to search for markets semantically,
so that I can find relevant markets even without exact keywords.
```### 第 2 步：生成测试用例
对于每个用户旅程，创建全面的测试用例：```typescript
describe('Semantic Search', () => {
  it('returns relevant markets for query', async () => {
    // Test implementation
  })

  it('handles empty query gracefully', async () => {
    // Test edge case
  })

  it('falls back to substring search when Redis unavailable', async () => {
    // Test fallback behavior
  })

  it('sorts results by similarity score', async () => {
    // Test sorting logic
  })
})
```### 步骤 3：运行测试（它们应该会失败）```bash
npm test
# Tests should fail - we haven't implemented yet
```### 步骤 4：实施代码
编写最少的代码以使测试通过：```typescript
// Implementation guided by tests
export async function searchMarkets(query: string) {
  // Implementation here
}
```### 步骤 5：再次运行测试```bash
npm test
# Tests should now pass
```### 第 6 步：重构
提高代码质量，同时保持测试绿色：
- 删除重复项
- 改进命名
- 优化性能
- 增强可读性

### 第 7 步：验证覆盖范围```bash
npm run test:coverage
# Verify 80%+ coverage achieved
```## 测试模式

### 单元测试模式（Jest/Vitest）```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from './Button'

describe('Button Component', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Click</Button>)

    fireEvent.click(screen.getByRole('button'))

    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Click</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })
})
```### API 集成测试模式```typescript
import { NextRequest } from 'next/server'
import { GET } from './route'

describe('GET /api/markets', () => {
  it('returns markets successfully', async () => {
    const request = new NextRequest('http://localhost/api/markets')
    const response = await GET(request)
    const data = await response.json()

    expect(response.status).toBe(200)
    expect(data.success).toBe(true)
    expect(Array.isArray(data.data)).toBe(true)
  })

  it('validates query parameters', async () => {
    const request = new NextRequest('http://localhost/api/markets?limit=invalid')
    const response = await GET(request)

    expect(response.status).toBe(400)
  })

  it('handles database errors gracefully', async () => {
    // Mock database failure
    const request = new NextRequest('http://localhost/api/markets')
    // Test error handling
  })
})
```### E2E 测试模式（剧作家）```typescript
import { test, expect } from '@playwright/test'

test('user can search and filter markets', async ({ page }) => {
  // Navigate to markets page
  await page.goto('/')
  await page.click('a[href="/markets"]')

  // Verify page loaded
  await expect(page.locator('h1')).toContainText('Markets')

  // Search for markets
  await page.fill('input[placeholder="Search markets"]', 'election')

  // Wait for debounce and results
  await page.waitForTimeout(600)

  // Verify search results displayed
  const results = page.locator('[data-testid="market-card"]')
  await expect(results).toHaveCount(5, { timeout: 5000 })

  // Verify results contain search term
  const firstResult = results.first()
  await expect(firstResult).toContainText('election', { ignoreCase: true })

  // Filter by status
  await page.click('button:has-text("Active")')

  // Verify filtered results
  await expect(results).toHaveCount(3)
})

test('user can create a new market', async ({ page }) => {
  // Login first
  await page.goto('/creator-dashboard')

  // Fill market creation form
  await page.fill('input[name="name"]', 'Test Market')
  await page.fill('textarea[name="description"]', 'Test description')
  await page.fill('input[name="endDate"]', '2025-12-31')

  // Submit form
  await page.click('button[type="submit"]')

  // Verify success message
  await expect(page.locator('text=Market created successfully')).toBeVisible()

  // Verify redirect to market page
  await expect(page).toHaveURL(/\/markets\/test-market/)
})
```## 测试文件组织```
src/
├── components/
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.test.tsx          # Unit tests
│   │   └── Button.stories.tsx       # Storybook
│   └── MarketCard/
│       ├── MarketCard.tsx
│       └── MarketCard.test.tsx
├── app/
│   └── api/
│       └── markets/
│           ├── route.ts
│           └── route.test.ts         # Integration tests
└── e2e/
    ├── markets.spec.ts               # E2E tests
    ├── trading.spec.ts
    └── auth.spec.ts
```## 模拟外部服务

### Supabase 模拟```typescript
jest.mock('@/lib/supabase', () => ({
  supabase: {
    from: jest.fn(() => ({
      select: jest.fn(() => ({
        eq: jest.fn(() => Promise.resolve({
          data: [{ id: 1, name: 'Test Market' }],
          error: null
        }))
      }))
    }))
  }
}))
```### Redis 模拟```typescript
jest.mock('@/lib/redis', () => ({
  searchMarketsByVector: jest.fn(() => Promise.resolve([
    { slug: 'test-market', similarity_score: 0.95 }
  ])),
  checkRedisHealth: jest.fn(() => Promise.resolve({ connected: true }))
}))
```### OpenAI 模拟```typescript
jest.mock('@/lib/openai', () => ({
  generateEmbedding: jest.fn(() => Promise.resolve(
    new Array(1536).fill(0.1) // Mock 1536-dim embedding
  ))
}))
```## 测试覆盖率验证

### 运行覆盖率报告```bash
npm run test:coverage
```### 覆盖阈值```json
{
  "jest": {
    "coverageThresholds": {
      "global": {
        "branches": 80,
        "functions": 80,
        "lines": 80,
        "statements": 80
      }
    }
  }
}
```## 要避免的常见测试错误

### ❌错误：测试实施细节```typescript
// Don't test internal state
expect(component.state.count).toBe(5)
```### ✅ 正确：测试用户可见的行为```typescript
// Test what users see
expect(screen.getByText('Count: 5')).toBeInTheDocument()
```### ❌错误：脆弱的选择器```typescript
// Breaks easily
await page.click('.css-class-xyz')
```### ✅ 正确：语义选择器```typescript
// Resilient to changes
await page.click('button:has-text("Submit")')
await page.click('[data-testid="submit-button"]')
```### ❌错误：没有测试隔离```typescript
// Tests depend on each other
test('creates user', () => { /* ... */ })
test('updates same user', () => { /* depends on previous test */ })
```### ✅ 正确：独立测试```typescript
// Each test sets up its own data
test('creates user', () => {
  const user = createTestUser()
  // Test logic
})

test('updates user', () => {
  const user = createTestUser()
  // Update logic
})
```## 持续测试

### 开发期间的观看模式```bash
npm test -- --watch
# Tests run automatically on file changes
```### 预提交挂钩```bash
# Runs before every commit
npm test && npm run lint
```### CI/CD 集成```yaml
# GitHub Actions
- name: Run Tests
  run: npm test -- --coverage
- name: Upload Coverage
  uses: codecov/codecov-action@v3
```## 最佳实践

1. **首先编写测试** - 始终 TDD
2. **每个测试一个断言** - 专注于单一行为
3. **描述性测试名称** - 解释测试的内容
4. **Arrange-Act-Assert** - 清晰的测试结构
5. **模拟外部依赖关系** - 隔离单元测试
6. **测试边缘情况** - Null、未定义、空、大
7. **测试错误路径** - 不仅仅是快乐的路径
8. **保持测试快速** - 每个单元测试< 50ms
9. **测试后清理** - 无副作用
10. **审查覆盖率报告** - 找出差距

## 成功指标

- 代码覆盖率达到 80% 以上
- 所有测试均通过（绿色）
- 没有跳过或禁用的测试
- 快速测试执行（单元测试 < 30 秒）
- 端到端测试涵盖关键用户流程
- 在生产前测试发现错误

---

**记住**：测试不是可选的。它们是安全网，可以实现自信的重构、快速开发和生产可靠性。