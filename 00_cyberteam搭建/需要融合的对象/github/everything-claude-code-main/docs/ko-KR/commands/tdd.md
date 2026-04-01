# TDD 测试

커맨드는 **tdd-guide** 에oodle전트를 호출하여 테스트 주도 개발 방법론을 강제합니다。

## 커맨드і 하는 것

1. **인터페이스 스캐폴딩** - 타입/인터페і스를 먼저 정의
2. **테스트 먼저 생성** - 실패하는 테스트 작성 (红色)
3. **최소한의 코드 구현** - 통과하기에 충분한 코드만 작성 (绿色)
4. **리팩토링** - 테스트를 통과시키면서 코드 개선 (REFACTOR)
5. **커버리지 확인** - 80% 커버리지 보장

## 사용 시점

`/tdd`를 사용해야 할 때:
- 새 기능 구현
- 새 함수/컴포넌트 추у
- 버그 수정 (버그를 재현하는 테스트를 먼저 작성)
- 기존 코드 리팩토링
- 핵심 비즈니스 로직 구현

## 작동 방식

tdd-guide 说明：

1. 입출력에 대한 **인터페і스 정의**
2. (코드і 아직 존재하지 않으므로) **실패하는 테스트 작성**
3. 올바른 ה유로 실패하는지 **테스트 실행** 및 확인
4. 테스트를 통과하도록 **최소한의 구현 작성**
5. 통과하는지 **테스트 실행** 및 확인
6. 테스트를 통과시키면서 코드 **리팩토링**
7. **커버리지 확인** 및 80% 미만イ면 테스트 추实例

## TDD 测试```
RED → GREEN → REFACTOR → REPEAT

RED:      실패하는 테스트 작성
GREEN:    통과할 최소한의 코드 작성
REFACTOR: 코드 개선, 테스트 계속 통과 유지
REPEAT:   다음 기능/시나리오
```## 사용 예시````
User: /tdd 마켓 유동성 점수를 계산하는 함수가 필요합니다

Agent (tdd-guide):
# TDD 세션: 마켓 유동성 점수 계산기

## 1단계: 인터페이스 정의 (SCAFFOLD)

```打字稿
// lib/liquidity.ts
导出接口市场数据{
  总体积: 数量
  bidAskSpread: 数字
  活跃交易者：数量
  最后交易时间：日期
}

导出函数calculateLiquidityScore(市场: MarketData): number {
  // TODO: 구현
  抛出新错误（'未实现'）
}```

## 2단계: 실패하는 테스트 작성 (RED)

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
      lastTradeTime: new Date(Date.now() - 86400000) // 1 分钟
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

## 3단계: 테스트 실행 - 실패 확인

```巴什
npm 测试库/liquidity.test.ts

lib/liquidity.test.ts 失败
  ✕ 应返回流动市场的高分（2 毫秒）
    错误：未实施

1 次测试失败，0 次通过```

✅ 예상대로 테스트 실패. 구현 준비 완료.

## 4단계: 최소한의 코드 구현 (GREEN)

```打字稿
// lib/liquidity.ts
导出函数calculateLiquidityScore(市场: MarketData): number {
  // 거래량 0인 엣지 케래량 처리
  if (market.totalVolume === 0) {
    返回0
  }

  // 구성 요소별 점수 계산 (0-100 스케일)
  const volumeScore = Math.min(market.totalVolume / 1000, 100)
  const spreadScore = Math.max(100 - (market.bidAskSpread * 1000), 0)
  const traderScore = Math.min(market.activeTraders / 10, 100)

  // 최근 활동 보너스
  const hoursSinceLastTrade = (Date.now() - market.lastTradeTime.getTime()) / (1000 * 60 * 60)
  const rencyScore = Math.max(100 - (hoursSinceLastTrade * 10), 0)

  // 평균
  常量分数 = (
    体积分数 * 0.4 +
    点差分数 * 0.3 +
    交易者得分 * 0.2 +
    近期得分 * 0.1
  ）

  return Math.min(Math.max(score, 0), 100) // 0-100으로 클램핑
}```

## 5단계: 테스트 실행 - 통과 확인

```巴什
npm 测试库/liquidity.test.ts

通过 lib/liquidity.test.ts
  ✓ 应返回流动市场的高分（3 毫秒）
  ✓ 应针对非流动性市场返回低分（2 毫秒）
  ✓ 应处理边缘情况：零音量（1 ms）

通过了 3 项测试```

✅ 모든 테스트 통과!

## 6단계: 리팩토링 (IMPROVE)

```打字稿
// lib/liquidity.ts - 향상을 위한 리팩토링
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

## 7단계: 테스트가 여전히 통과하는지 확인

```巴什
npm 测试库/liquidity.test.ts

通过 lib/liquidity.test.ts
  ✓ 应返回流动市场的高分（3 毫秒）
  ✓ 应针对非流动性市场返回低分（2 毫秒）
  ✓ 应处理边缘情况：零音量（1 ms）

通过了 3 项测试```

✅ 리팩토링 완료, 테스트 여전히 통과!

## 8단계: 커버리지 확인

```巴什
npm 测试 -- --coverage lib/liquidity.test.ts

文件| % 语句 | % 分支 | % 函数 | % 行数
---------------|---------|----------|---------|--------
流动性.ts |   100 | 100   100 | 100   100 | 100   100

覆盖率：100% ✅ (목표: 80%)```

✅ TDD 세션 완료!
````

## TDD 测试驱动开发

**해야할것:**
- 구현 전에 테스트를 먼저 작성
- 구현 전에 테스트를 실행하여 실패하는지 확인
- 테스트를 통과하기 위한 최소한의 코드 작성
- 테스트і 통과한 후에만 리팩토링
- 엣지 케 Been 스와 에러 시나리오 추у
- 80% 커버리지 목표 (핵심 코드는 100%)

**하지 말아야 할 것:**
- 테스트 전에 구현 작성
- 각 변경 후 테스트 실행 건너뛰기
- 한 번에 너무 많은 코드 작성
- 실패하는 테스트 무시
- 구현 세부사항 테스트 (동작을 테스트)
- 모든 것을 模拟 (통합 테스트 선호)

## 포함할 테스트 유형

**단위 테스트** (함수 수준):
- 정상 경로 시나리오
- 엣지 케값 (빈 값, null, 최대값)
- 에러 조건
- 경계값

**통합 테스트** (컴포넌트 수준):
- API 엔드포인트
- 작업 작업
- 외부 서비스 호출
- hooks 포함된 React 컴포넌트

**E2E 테스트** (`/e2e` 커맨드 사용):
- 핵심 사용자 흐름
- 다단계 프로세스
- 풀 스택 통합

## 커버리지 요구사항

- **80% 최소** - 모든 코드에 대해
- **100% 필수** - 다음 항목에 대해:
  - 금융 계산
  - 인증 로직
  - 보안에 중요한 코드
  - 핵심 비즈니스 로직

## 중요 사항

**필수**：테스트는 반드시 구현 전에 작성해야 합니다。 TDD 的应用：

1. **RED** - 실패하는 테스트 작성
2. **绿色** - 통과하도록 구현
3. **重构** - 코드 개선

절대 RED 단계를 건너뛰지 마세요。 절대 테스트 전에 코드를 작성하지 마세요。

## 다른 커맨드와의 연동

- `/plan`을 먼저 사용하여 무엇을 만들지 ו
- `/tdd`를 사용하여 테스트와 함께 구현
- `/build-fix`를 사용하여 빌드 에러 발생 시 수정
- `/code-review`를 사용하여 구현 리뷰
- `/test-coverage`를 사용하여 커버리지 검증

## 관련 에기전트

커맨드는 `tdd-guide` 的内容：
`~/.claude/agents/tdd-guide.md`

그리고 `tdd-workflow` 的应用程序：
`~/.claude/skills/tdd-workflow/`