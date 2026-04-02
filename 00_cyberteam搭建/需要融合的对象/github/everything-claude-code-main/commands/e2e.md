# 端到端命令

此命令调用 **e2e-runner** 代理来使用 Playwright 生成、维护和执行端到端测试。

## 该命令的作用

1. **生成测试旅程** - 为用户流程创建 Playwright 测试
2. **运行 E2E 测试** - 跨浏览器执行测试
3. **捕获工件** - 屏幕截图、视频、失败痕迹
4. **上传结果** - HTML 报告和 JUnit XML
5. **识别不稳定的测试** - 隔离不稳定的测试

## 何时使用

在以下情况下使用“/e2e”：
- 测试关键用户旅程（登录、交易、支付）
- 验证多步骤流程端到端的工作情况
- 测试 UI 交互和导航
- 验证前端和后端之间的集成
- 准备生产部署

## 它是如何工作的

e2e-runner 代理将：

1. **分析用户流程**并确定测试场景
2. **使用页面对象模型模式生成剧作家测试**
3. **跨多个浏览器（Chrome、Firefox、Safari）运行测试**
4. **通过屏幕截图、视频和痕迹捕获失败**
5. **生成包含结果和工件的报告**
6. **识别不稳定的测试**并建议修复

## 用法示例```
User: /e2e Test the market search and view flow

Agent (e2e-runner):
# E2E Test Generation: Market Search and View Flow

## Test Scenario Identified

**User Journey:** Market Search → View Results → Click Market → View Details

**Test Coverage:**
1. Navigate to markets page
2. Perform semantic search
3. Verify search results
4. Click on first result
5. Verify market details page loads
6. Verify chart renders

## Generated Test Code

```打字稿
// 测试/e2e/markets/search-and-view.spec.ts
从“@playwright/test”导入{测试，期望}
从 '../../pages/MarketsPage' 导入 { MarketsPage }
从 '../../pages/MarketDetailsPage' 导入 { MarketDetailsPage }

test.describe('市场搜索及查看流程', () => {
  test('用户可以搜索市场并查看详细信息', async ({ page }) => {
    // 1. 导航至市场页面
    const marketPage = new MarketsPage(页)
    等待 marketPage.goto()

    // 验证页面加载
    等待期望（页面）.toHaveTitle（/市场/）
    等待期望（page.locator（'h1'））.toContainText（'市场'）

    // 2. 执行语义搜索
    等待 marketPage.searchMarkets('选举')

    // 等待API响应
    等待 page.waitForResponse(resp =>
      resp.url().includes('/api/markets/search') && resp.status() === 200
    ）

    // 3. 验证搜索结果
    const marketCards = marketPage.marketCards
    等待期望(marketCards.first()).toBeVisible()
    const resultCount = 等待 marketCards.count()
    期望（结果计数）.toBeGreaterThan（0）

    // 搜索结果截图
    等待 page.screenshot({ 路径: 'artifacts/search-results.png' })

    // 4. 点击第一个结果
    const firstMarketTitle = 等待 marketCards.first().textContent()
    等待 marketCards.first().click()

    // 5. 验证市场详细信息页面加载
    等待期望（页面）.toHaveURL（/\/市场\/[a-z0-9-]+/）

    const detailsPage = new MarketDetailsPage(页)
    等待期望（detailsPage.marketName）.toBeVisible（）
    等待期望（detailsPage.marketDescription）.toBeVisible（）

    // 6. 验证图表渲染
    等待期望(detailsPage.priceChart).toBeVisible()

    // 验证市场名称匹配
    constdetailsTitle=awaitdetailsPage.marketName.textContent()
    期望（detailsTitle？.toLowerCase（））.toContain（
      firstMarketTitle?.toLowerCase().substring(0, 20) || ”
    ）

    // 市场详情截图
    等待 page.screenshot({ 路径: 'artifacts/market-details.png' })
  })

  test('搜索无结果显示空状态', async ({ page }) => {
    const marketPage = new MarketsPage(页)
    等待 marketPage.goto()

    // 搜索不存在的市场
    等待 marketPage.searchMarkets('xyznonexistentmarket123456')

    // 验证空状态
    等待期望（page.locator（'[data-testid =“no-results”]'））.toBeVisible（）
    等待期望（page.locator（'[data-testid =“无结果”]'））。toContainText（
      /号。*结果|号。*市场/i
    ）

    const marketCount =等待marketsPage.marketCards.count()
    期望(marketCount).toBe(0)
  })

  test('可以清除搜索并再次查看所有市场', async ({ page }) => {
    const marketPage = new MarketsPage(页)
    等待 marketPage.goto()

    // 初始市场计数
    const初始计数=等待marketsPage.marketCards.count()

    // 执行搜索
    等待 marketPage.searchMarkets('特朗普')
    等待 page.waitForLoadState('networkidle')

    // 验证过滤结果
    constfilteredCount=awaitmarketsPage.marketCards.count()
    期望（filteredCount）.toBeLessThan（initialCount）

    // 清除搜索
    等待 marketPage.searchInput.clear()
    等待 page.waitForLoadState('networkidle')

    // 再次验证所有显示的市场
    const FinalCount = 等待 marketPage.marketCards.count()
    期望（最终计数）.toBe（初始计数）
  })
})```

## Running Tests

```巴什
# 运行生成的测试
npx 剧作家测试测试/e2e/markets/search-and-view.spec.ts

使用 3 个工作人员运行 3 个测试

  ✓ [chromium] › search-and-view.spec.ts:5:3 › 用户可以搜索市场并查看详细信息 (4.2s)
  ✓ [chromium] › search-and-view.spec.ts:52:3 › 搜索无结果显示空状态（1.8s）
  ✓ [chromium] › search-and-view.spec.ts:67:3 › 可以清除搜索并再次查看所有市场（2.9 秒）

  3 通过（9.1 秒）

生成的工件：
- 工件/搜索结果.png
- 工件/market-details.png
- 剧作家报告/index.html```

## Test Report

```╔═══════════════════════════════ ═══════════════════════════════╗
║ 端到端测试结果 ║
╠═══════════════════════════════ ═══════════════════════════════╣
║ 状态： ✅ 所有测试均已通过 ║
║ 总计：3 次测试 ║
║ 通过：3 (100%) ║
║ 失败：0 ║
║ 片状：0 ║
║ 持续时间：9.1 秒 ║
╚═══════════════════════════════ ═══════════════════════════════╝

文物：
📸 截图：2个文件
📹 视频：0 个文件（仅在失败时）
🔍 痕迹：0 个文件（仅在失败时）
📊 HTML 报告：playwright-report/index.html

查看报告：npx 剧作家演出报告```

✅ E2E test suite ready for CI/CD integration!
```## 测试工件

运行测试时，会捕获以下工件：

**所有测试：**
- 包含时间线和结果的 HTML 报告
- 用于 CI 集成的 JUnit XML

**仅在失败时：**
- 失败状态的屏幕截图
- 测试视频录制
- 用于调试的跟踪文件（逐步重播）
- 网络日志
- 控制台日志

## 查看工件```bash
# View HTML report in browser
npx playwright show-report

# View specific trace file
npx playwright show-trace artifacts/trace-abc123.zip

# Screenshots are saved in artifacts/ directory
open artifacts/search-results.png
```## 片状测试检测

如果测试间歇性失败：```
⚠️  FLAKY TEST DETECTED: tests/e2e/markets/trade.spec.ts

Test passed 7/10 runs (70% pass rate)

Common failure:
"Timeout waiting for element '[data-testid="confirm-btn"]'"

Recommended fixes:
1. Add explicit wait: await page.waitForSelector('[data-testid="confirm-btn"]')
2. Increase timeout: { timeout: 10000 }
3. Check for race conditions in component
4. Verify element is not hidden by animation

Quarantine recommendation: Mark as test.fixme() until fixed
```## 浏览器配置

默认情况下，测试在多个浏览器上运行：
- ✅ Chromium（桌面 Chrome）
- ✅ 火狐（桌面版）
- ✅ WebKit（桌面 Safari）
- ✅ 移动 Chrome（可选）

在`playwright.config.ts`中配置以调整浏览器。

## CI/CD 集成

添加到您的 CI 管道：```yaml
# .github/workflows/e2e.yml
- name: Install Playwright
  run: npx playwright install --with-deps

- name: Run E2E tests
  run: npx playwright test

- name: Upload artifacts
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: playwright-report
    path: playwright-report/
```## PMX 特定关键流程

对于 PMX，优先考虑以下 E2E 测试：

**🔴 关键（必须始终通过）：**
1. 用户可以连接钱包
2.用户可以浏览市场
3. 用户可以搜索市场（语义搜索）
4.用户可以查看市场详情
5. 用户可以进行交易（使用测试资金）
6.市场正确解析
7. 用户可以提取资金

**🟡重要：**
1. 市场创建流程
2. 用户资料更新
3. 实时价格更新
4.图表渲染
5. 过滤和排序市场
6. 移动端响应式布局

## 最佳实践

**做：**
- ✅ 使用页面对象模型来实现可维护性
- ✅ 对选择器使用 data-testid 属性
- ✅ 等待 API 响应，而不是任意超时
- ✅ 端到端测试关键用户旅程
- ✅ 在合并到主程序之前运行测试
- ✅ 测试失败时查看工件

**不要：**
- ❌ 使用脆弱的选择器（CSS 类可以更改）
- ❌ 测试实施细节
- ❌ 针对生产运行测试
- ❌ 忽略不稳定的测试
- ❌ 跳过失败的工件审查
- ❌ 使用 E2E 测试每个边缘情况（使用单元测试）

## 重要提示

**对于 PMX 至关重要：**
- 涉及真钱的 E2E 测试必须仅在测试网/登台上运行
- 切勿针对生产运行交易测试
- 设置 `test.skip(process.env.NODE_ENV === 'product')` 进行财务测试
- 仅使用带有少量测试资金的测试钱包

## 与其他命令集成

- 使用“/plan”来确定要测试的关键旅程
- 使用 `/tdd` 进行单元测试（更快、更精细）
- 使用“/e2e”进行集成和用户旅程测试
- 使用`/code-review`来验证测试质量

## 相关代理

此命令调用 ECC 提供的“e2e-runner”代理。

对于手动安装，源文件位于：
`代理/e2e-runner.md`

## 快速命令```bash
# Run all E2E tests
npx playwright test

# Run specific test file
npx playwright test tests/e2e/markets/search.spec.ts

# Run in headed mode (see browser)
npx playwright test --headed

# Debug test
npx playwright test --debug

# Generate test code
npx playwright codegen http://localhost:3000

# View report
npx playwright show-report
```