# TDD命令

此命令调用 **tdd-guide** 代理来实施测试驱动的开发方法。

## 该命令的作用

1. **脚手架接口** - 首先定义类型/接口
2. **首先生成测试** - 编写失败的测试（红色）
3. **实现最少代码** - 编写足以通过的代码（绿色）
4. **重构** - 改进代码，同时保持测试绿色（REFACTOR）
5. **验证覆盖率** - 确保 80% 以上的测试覆盖率

## 何时使用

在以下情况下使用“/tdd”：
- 实施新功能
- 添加新功能/组件
- 修复错误（首先编写重现错误的测试）
- 重构现有代码
- 构建关键业务逻辑

## 它是如何工作的

TDD 指南代理将：

1. **定义输入/输出接口**
2. **编写会失败的测试**（因为代码尚不存在）
3. **运行测试**并验证它们因正确原因而失败
4. **编写最少的实现**以使测试通过
5. **运行测试**并验证它们通过
6. **重构**代码，同时保持测试绿色
7. **检查覆盖率**，如果低于 80%，则添加更多测试

## TDD 周期```
RED → GREEN → REFACTOR → REPEAT

RED:      Write a failing test
GREEN:    Write minimal code to pass
REFACTOR: Improve code, keep tests passing
REPEAT:   Next feature/scenario
```## 用法示例```
User: /tdd I need a function to calculate market liquidity score

Agent (tdd-guide):
# TDD Session: Market Liquidity Score Calculator

## Step 1: Define Interface (SCAFFOLD)

```打字稿
// lib/liquidity.ts
导出接口市场数据{
  总体积: 数量
  bidAskSpread: 数字
  活跃交易者：数量
  最后交易时间：日期
}

导出函数calculateLiquidityScore(市场: MarketData): number {
  // TODO：实施
  抛出新错误（'未实现'）
}```

## Step 2: Write Failing Test (RED)

```打字稿
// lib/liquidity.test.ts
从 './liquidity' 导入 {calculateLiquidityScore }

描述（'计算流动性分数'，（）=> {
  it('应该为流动性市场返回高分', () => {
    常量市场={
      总数量：100000，
      出价问价差价：0.01，
      活跃交易者：500，
      最后交易时间：new Date()
    }

    const 分数 = 计算流动性分数（市场）

    期望（分数）.toBeGreaterThan（80）
    期望（分数）.toBeLessThanOrEqual（100）
  })

  it('对于非流动性市场应该返回低分', () => {
    常量市场={
      总数量：100，
      出价询问价差：0.5，
      活跃交易者：2，
      lastTradeTime: new Date(Date.now() - 86400000) // 1 天前
    }

    const 分数 = 计算流动性分数（市场）

    期望（分数）.toBeLessThan（30）
    期望（分数）.toBeGreaterThanOrEqual（0）
  })

  it('应该处理边缘情况：零音量', () => {
    常量市场={
      总音量：0，
      出价问价差价: 0,
      活跃交易者：0，
      最后交易时间：new Date()
    }

    const 分数 = 计算流动性分数（市场）

    期望(分数).toBe(0)
  })
})```

## Step 3: Run Tests - Verify FAIL

```巴什
npm 测试库/liquidity.test.ts

lib/liquidity.test.ts 失败
  ✕ 应返回流动市场的高分（2 毫秒）
    错误：未实施

1 次测试失败，0 次通过```

✅ Tests fail as expected. Ready to implement.

## Step 4: Implement Minimal Code (GREEN)

```打字稿
// lib/liquidity.ts
导出函数calculateLiquidityScore(市场: MarketData): number {
  // 处理零音量边缘情况
  if (market.totalVolume === 0) {
    返回0
  }

  // 计算组件分数（0-100 范围）
  const volumeScore = Math.min(market.totalVolume / 1000, 100)
  const spreadScore = Math.max(100 - (market.bidAskSpread * 1000), 0)
  const traderScore = Math.min(market.activeTraders / 10, 100)

  // 近期活动奖励
  const hoursSinceLastTrade = (Date.now() - market.lastTradeTime.getTime()) / (1000 * 60 * 60)
  const rencyScore = Math.max(100 - (hoursSinceLastTrade * 10), 0)

  // 加权平均值
  常量分数 = (
    体积分数 * 0.4 +
    点差分数 * 0.3 +
    交易者得分 * 0.2 +
    近期得分 * 0.1
  ）

  return Math.min(Math.max(score, 0), 100) // 限制为 0-100
}```

## Step 5: Run Tests - Verify PASS

```巴什
npm 测试库/liquidity.test.ts

通过 lib/liquidity.test.ts
  ✓ 应返回流动市场的高分（3 毫秒）
  ✓ 应针对非流动性市场返回低分（2 毫秒）
  ✓ 应处理边缘情况：零音量（1 ms）

通过了 3 项测试```

✅ All tests passing!

## Step 6: Refactor (IMPROVE)

```打字稿
// lib/liquidity.ts - 使用常量进行重构并提高可读性
常量权重 = {
  体积：0.4，
  传播：0.3，
  交易员：0.2，
  新近度：0.1，
} 作为常量

常量 SCALE_FACTORS = {
  数量：1000，
  传播：1000，
  交易员：10，
  RECENCY_PENALTY: 10,
} 作为常量

函数钳位（值：数字，最小值：数字，最大值：数字）：数字{
  返回 Math.min(Math.max(值, 最小值), 最大值)
}

导出函数calculateLiquidityScore(市场: MarketData): number {
  if (market.totalVolume === 0) 返回 0

  const volumeScore = Math.min(market.totalVolume / SCALE_FACTORS.VOLUME, 100)
  const spreadScore = 钳位(100 - (market.bidAskSpread * SCALE_FACTORS.SPREAD), 0, 100)
  const traderScore = Math.min(market.activeTraders / SCALE_FACTORS.TRADERS, 100)

  const hoursSinceLastTrade = (Date.now() - market.lastTradeTime.getTime()) / (1000 * 60 * 60)
  const 近期得分 = 钳位(100 - (hoursSinceLastTrade * SCALE_FACTORS.RECENCY_PENALTY), 0, 100)

  常量加权分数 =
    体积分数 * 重量.体积 +
    spreadScore * WEIGHTS.SPREAD +
    traderScore * 权重.交易者 +
    最近度得分 * 权重.最近度

  返回钳位(weightedScore, 0, 100)
}```

## Step 7: Verify Tests Still Pass

```巴什
npm 测试库/liquidity.test.ts

通过 lib/liquidity.test.ts
  ✓ 应返回流动市场的高分（3 毫秒）
  ✓ 应针对非流动性市场返回低分（2 毫秒）
  ✓ 应处理边缘情况：零音量（1 ms）

通过了 3 项测试```

✅ Refactoring complete, tests still passing!

## Step 8: Check Coverage

```巴什
npm 测试 -- --coverage lib/liquidity.test.ts

文件| % 语句 | % 分支 | % 函数 | % 行数
---------------|---------|----------|---------|--------
流动性.ts |   100 | 100   100 | 100   100 | 100   100

覆盖率：100% ✅（目标：80%）```

✅ TDD session complete!
```## TDD 最佳实践

**做：**
- ✅ 在任何实施之前先编写测试
- ✅ 在实施之前运行测试并验证它们是否失败
- ✅ 编写最少的代码以使测试通过
- ✅ 仅在测试通过后才进行重构
- ✅ 添加边缘情况和错误场景
- ✅ 目标是 80% 以上的覆盖率（关键代码为 100%）

**不要：**
- ❌ 在测试之前编写实现
- ❌ 每次更改后跳过运行测试
- ❌ 一次写太多代码
- ❌忽略失败的测试
- ❌ 测试实施细节（测试行为）
- ❌ 模拟一切（更喜欢集成测试）

## 要包含的测试类型

**单元测试**（功能级）：
- 快乐路径场景
- 边缘情况（空、空、最大值）
- 错误条件
- 边界值

**集成测试**（组件级）：
- API端点
- 数据库操作
- 外部服务电话
- 用钩子反应组件

**E2E 测试**（使用 `/e2e` 命令）：
- 关键用户流量
- 多步骤流程
- 全栈集成

## 覆盖范围要求

- **所有代码至少 80%**
- **需要 100%** 对于：
  - 财务计算
  - 认证逻辑
  - 安全关键代码
  - 核心业务逻辑

## 重要提示

**强制**：必须在实施之前编写测试。 TDD周期为：

1. **红色** - 编写失败的测试
2. **绿色** - 实施以通过
3. **重构** - 改进代码

切勿跳过红色阶段。永远不要在测试之前编写代码。

## 与其他命令集成

- 首先使用`/plan`来了解要构建什么
- 使用 `/tdd` 来实现测试
- 如果发生构建错误，请使用“/build-fix”
- 使用“/code-review”来审查实施情况
- 使用“/test-coverage”来验证覆盖范围

## 相关代理

此命令调用 ECC 提供的“tdd-guide”代理。

相关的“tdd-workflow”技能也与 ECC 捆绑在一起。

对于手动安装，源文件位于：
- `代理/tdd-guide.md`
- `技能/tdd-workflow/SKILL.md`