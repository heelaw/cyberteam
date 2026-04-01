# 端到端命令

使用 Playwright 生成并运行端到端测试：$ARGUMENTS

## 你的任务

1. **分析用户流程**进行测试
2. **与 Playwright 一起创建测试旅程**
3. **运行测试**并捕获工件
4. **使用屏幕截图/视频报告结果**

## 测试结构```typescript
import { test, expect } from '@playwright/test'

test.describe('Feature: [Name]', () => {
  test.beforeEach(async ({ page }) => {
    // Setup: Navigate, authenticate, prepare state
  })

  test('should [expected behavior]', async ({ page }) => {
    // Arrange: Set up test data

    // Act: Perform user actions
    await page.click('[data-testid="button"]')
    await page.fill('[data-testid="input"]', 'value')

    // Assert: Verify results
    await expect(page.locator('[data-testid="result"]')).toBeVisible()
  })

  test.afterEach(async ({ page }, testInfo) => {
    // Capture screenshot on failure
    if (testInfo.status !== 'passed') {
      await page.screenshot({ path: `test-results/${testInfo.title}.png` })
    }
  })
})
```## 最佳实践

### 选择器
- 更喜欢“data-testid”属性
- 避免 CSS 类（它们会改变）
- 使用语义选择器（角色、标签）

### 等待
- 使用 Playwright 的自动等待
- 避免“page.waitForTimeout()”
- 使用“expect().toBeVisible()”进行断言

### 测试隔离
- 每个测试应该是独立的
- 之后清理测试数据
- 不要依赖测试订单

## 捕获的文物

- 失败时的屏幕截图
- 用于调试的视频
- 用于详细分析的跟踪文件
- 网络日志（如果相关）

## 测试类别

1. **关键用户流程**
   - 身份验证（登录、注销、注册）
   - 核心功能快乐路径
   - 付款/结账流程

2. **边缘情况**
   - 网络故障
   - 无效输入
   - 会话到期

3. **跨浏览器**
   - Chrome、火狐、Safari
   - 移动视口

## 报告格式```
E2E Test Results
================
✅ Passed: X
❌ Failed: Y
⏭️ Skipped: Z

Failed Tests:
- test-name: Error message
  Screenshot: path/to/screenshot.png
  Video: path/to/video.webm
```---

**提示**：使用“--headed”标志运行进行调试：“npx playwright test --headed”