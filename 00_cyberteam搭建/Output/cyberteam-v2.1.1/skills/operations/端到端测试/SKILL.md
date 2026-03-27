---
name: 端到端测试
description: |
  端到端测试 — 使用Playwright进行完整用户流程测试。
  配套Agent: QA专家Agent
version: "2.1"
owner: CyberTeam QA专家
agent: qa-agent
trigger: "用户需要: E2E测试/用户流程验证/回归测试"
---

# 端到端测试

## 身份定位

```
+----------------------------------------------------------+
|  端到端测试                                              |
|  用途: Playwright完整用户流程测试                         |
|  覆盖: 登录/核心功能/异常处理                           |
+----------------------------------------------------------+
```

## 测试流程

### Step 1: 测试规划
- 定义用户旅程
- 识别关键路径
- 制定验收标准

### Step 2: 测试用例编写

```javascript
import { test, expect } from '@playwright/test';

test('用户登录流程', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[data-testid="username"]', 'test@example.com');
  await page.fill('[data-testid="password"]', 'password123');
  await page.click('[data-testid="submit"]');
  await expect(page).toHaveURL('/dashboard');
});
```

### Step 3: 执行与验证
- 运行Playwright测试
- 生成测试报告
- 收集覆盖率数据

## 测试场景清单

| 场景 | 优先级 | 覆盖要求 |
|------|--------|----------|
| 用户登录 | P0 | 100% |
| 核心功能 | P0 | 100% |
| 支付流程 | P0 | 100% |
| 表单提交 | P1 | 80% |
| 异常处理 | P1 | 60% |
| 边缘用例 | P2 | 40% |

## Playwright集成

### 安装

```bash
npm install -D @playwright/test
npx playwright install chromium
```

### 配置

```javascript
// playwright.config.js
module.exports = {
  testDir: './tests',
  timeout: 30000,
  retries: 2,
  use: {
    baseURL: 'http://localhost:3000',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
};
```

---

**版本**: v2.1 | **来源**: gstack QA + CyberTeam | **日期**: 2026-03-23
