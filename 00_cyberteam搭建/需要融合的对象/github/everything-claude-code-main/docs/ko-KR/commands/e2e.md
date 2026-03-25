# E2E 服务

커맨드는 **e2e-runner** 是剧作家，E2E 的编剧。

## 커맨드і 하는 것

1. **테스트 여정 생성** - 사용자 흐름에 대한 剧作家 테스트 생성
2. **E2E 테스트 실행** - 여러 브라우저에서 테스트 실행
3. **아티팩트 캡처** - 실패 시 스크린샷, 비디오, 트레스
4. **결과 업로드** - HTML 和 JUnit XML
5. **불안정한 테스트 식별** - 불안정한 테스트를 격리

## 사용 시점

`/e2e`를 사용해야 할 때:
- 핵심 사용자 여정 테스트 (로그인, 거래, 결제)
- 다단계 흐름 Been E2E로 작동하는지 검증
- UI 인터랙션 및 네비게イ션 테스트
- 프론트엔드와 백엔드 간 통합 검증
- 프로덕션 배포 준비

## 작동 방식

e2e-runner 应用程序：

1. **사용자 흐름 분석** 및 테스트 시나리오 식별
2. 页面对象模型 패턴을 사용한 **剧作家 테스트 생성**
3. 여러 브라우저(Chrome, Firefox, Safari)에서 **테스트 실행**
4. 스크린샷, 비디오, 트레스로 **실패 캡처**
5. 결과와 아티팩트로 **보고서 생성**
6. **불안정한 테스트 식별** 및 수정 권장

## 사용 예시````
User: /e2e 마켓 검색 및 조회 흐름 테스트

Agent (e2e-runner):
# E2E 테스트 생성: 마켓 검색 및 조회 흐름

## 식별된 테스트 시나리오

**사용자 여정:** 마켓 검색 → 결과 확인 → 마켓 클릭 → 상세 정보 확인

**테스트 범위:**
1. 마켓 페이지로 이동
2. 시맨틱 검색 수행
3. 검색 결과 확인
4. 첫 번째 결과 클릭
5. 마켓 상세 페이지 로드 확인
6. 차트 렌더링 확인

## 생성된 테스트 코드

```打字稿
// 测试/e2e/markets/search-and-view.spec.ts
从“@playwright/test”导入{测试，期望}
从 '../../pages/MarketsPage' 导入 { MarketsPage }
从 '../../pages/MarketDetailsPage' 导入 { MarketDetailsPage }

test.describe('市场搜索及查看流程', () => {
  test('用户可以搜索市场并查看详细信息', async ({ page }) => {
    // 1. 마켓 페 Been 지로 동
    const marketPage = new MarketsPage(页)
    等待 marketPage.goto()

    // 로드 확인
    等待期望（页面）.toHaveTitle（/市场/）
    等待期望（page.locator（'h1'））.toContainText（'市场'）

    // 2. 시맨틱 검색 수행
    等待 marketPage.searchMarkets('选举')

    // API 接口
    等待 page.waitForResponse(resp =>
      resp.url().includes('/api/markets/search') && resp.status() === 200
    ）

    // 3. 검색 결과 확인
    const marketCards = marketPage.marketCards
    等待期望(marketCards.first()).toBeVisible()
    const resultCount = 等待 marketCards.count()
    期望（结果计数）.toBeGreaterThan（0）

    // 검색 결과 스크린샷 촬영
    等待 page.screenshot({ 路径: 'artifacts/search-results.png' })

    // 4. 첫 번째 결과 클릭
    const firstMarketTitle = 等待 marketCards.first().textContent()
    等待 marketCards.first().click()

    // 5. 마켓 상세 페イ지 로드 확인
    等待期望（页面）.toHaveURL（/\/市场\/[a-z0-9-]+/）

    const detailsPage = new MarketDetailsPage(页)
    等待期望（detailsPage.marketName）.toBeVisible（）
    等待期望（detailsPage.marketDescription）.toBeVisible（）

    // 6. 차트 렌더링 확인
    等待期望(detailsPage.priceChart).toBeVisible()

    // 마켓 름 일치 확인
    constdetailsTitle=awaitdetailsPage.marketName.textContent()
    期望（detailsTitle？.toLowerCase（））.toContain（
      firstMarketTitle?.toLowerCase().substring(0, 20) || ”
    ）

    // 마켓 상세 스크린샷 촬영
    等待 page.screenshot({ 路径: 'artifacts/market-details.png' })
  })

  test('搜索无结果显示空状态', async ({ page }) => {
    const marketPage = new MarketsPage(页)
    等待 marketPage.goto()

    // 존재하지 않는 마켓 검색
    等待 marketPage.searchMarkets('xyznonexistentmarket123456')

    // 빈 상태 확인
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

    // 초기 마켓 수
    const初始计数=等待marketsPage.marketCards.count()

    // 검색 수행
    等待 marketPage.searchMarkets('特朗普')
    等待 page.waitForLoadState('networkidle')

    // 필터링된 결과 확인
    constfilteredCount=awaitmarketsPage.marketCards.count()
    期望（filteredCount）.toBeLessThan（initialCount）

    // 검색 초기화
    等待 marketPage.searchInput.clear()
    等待 page.waitForLoadState('networkidle')

    // 모든 마켓 Been 다시 표시되는지 확인
    const FinalCount = 等待 marketPage.marketCards.count()
    期望（最终计数）.toBe（初始计数）
  })
})```

## 테스트 실행

```巴什
# 생성된 테스트 실행
npx 剧作家测试测试/e2e/markets/search-and-view.spec.ts

使用 3 个工作人员运行 3 个测试

  ✓ [chromium] › search-and-view.spec.ts:5:3 › 用户可以搜索市场并查看详细信息 (4.2s)
  ✓ [chromium] › search-and-view.spec.ts:52:3 › 搜索无结果显示空状态（1.8s）
  ✓ [chromium] › search-and-view.spec.ts:67:3 › 可以清除搜索并再次查看所有市场（2.9 秒）

  3 通过（9.1 秒）

생성된 아티팩트:
- 工件/搜索结果.png
- 工件/market-details.png
- 剧作家报告/index.html```

## 테스트 보고서

```╔═══════════════════════════════ ═══════════════════════════════╗
║ E2E 테스트 결과 ║
╠═══════════════════════════════ ═══════════════════════════════╣
║ 상태: ✅ 모든 테스트 통과 ║
║ 전체: 3개 테스트 ║
║ 통과: 3 (100%) ║
║ 数量: 0 ║
║ 人数: 0 ║
║ 时间: 9.1s ║
╚═══════════════════════════════ ═══════════════════════════════╝

아티팩트:
📸 스크린샷: 2개 파일
📹 비디오: 0개 파일 (실패 시에만)
🔍 트레스: 0개 파일 (실패 시에만)
📊 HTML 文件：playwright-report/index.html

보고서 확인: npx 剧作家演出报告```

✅ CI/CD 통합 준비가 완료된 E2E 테스트 모음!
````

## 테스트 아티팩트

테스트 실행 시 다음 아티팩트캡처됩니다:

**모든 테스트:**
- 타임라인과 결과і 포함된 HTML 页面
- CI 和 JUnit XML

**실패시에만:**
- 실패 상태의 스크린샷
- 테스트의 비디오 녹화
- 디버깅을 위한 트레스 파일 (단계별 재생)
- 네트워크 로그
- 콘솔 로그

## 아티팩트 확인```bash
# 브라우저에서 HTML 보고서 확인
npx playwright show-report

# 특정 트레이스 파일 확인
npx playwright show-trace artifacts/trace-abc123.zip

# 스크린샷은 artifacts/ 디렉토리에 저장됨
open artifacts/search-results.png
```## 불안정한 테스트 감지

스패하는 경우:```
⚠️  불안정한 테스트 감지됨: tests/e2e/markets/trade.spec.ts

테스트가 10회 중 7회 통과 (70% 통과율)

일반적인 실패 원인:
"요소 '[data-testid="confirm-btn"]'을 대기하는 중 타임아웃"

권장 수정 사항:
1. 명시적 대기 추가: await page.waitForSelector('[data-testid="confirm-btn"]')
2. 타임아웃 증가: { timeout: 10000 }
3. 컴포넌트의 레이스 컨디션 확인
4. 애니메이션에 의해 요소가 숨겨져 있지 않은지 확인

격리 권장: 수정될 때까지 test.fixme()로 표시
```## 브라우저 구성

重要信息：
- 铬（데스크톱 Chrome）
- 火狐 (데스크톱)
- WebKit (데스크톱 Safari)
- 移动 Chrome (선택 사항)

`playwright.config.ts`에서 브라우저를 조정할 수 있습니다.

## CI/CD 表格

CI 파기프라인에 추у:```yaml
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
```## 모범 사례

**해야할것:**
- 页面对象模型应用程序
- data-testid 测试数据
- 임의의 타임아웃 대신 API 응답을 대기
- 핵심 사용자 여정을 E2E로 테스트
- main에 merge하기 전에 테스트 실행
- 테스트 실패 시 아티팩트 검토

**하지 말아야 할 것:**
- 취약한 셀렉터 사용 (CSS 클래스는 변경될 수 있음)
- 구현 세부사항 테스트
- 프로덕션에 대해 테스트 실행
- 불안정한 테스트 무시
- 실패 시 아티팩트 검토 생략
- E2E로 모든 엣지 케い스 테스트 (단위 테스트 사용)

## 다른 커맨드와의 연동

- `/plan`을 사용하여 테스트할 핵심 여정 식별
- `/tdd`를 사용하여 단위 테스트 (더 빠르고 세밀함)
- `/e2e`를 사용하여 통합 및 사용자 여정 테스트
- `/code-review`를 사용하여 테스트 품질 검증

## 관련 에기전트

커맨드는 `e2e-runner` 的作用：
`~/.claude/agents/e2e-runner.md`

## 빠른 커맨드```bash
# 모든 E2E 테스트 실행
npx playwright test

# 특정 테스트 파일 실행
npx playwright test tests/e2e/markets/search.spec.ts

# headed 모드로 실행 (브라우저 표시)
npx playwright test --headed

# 테스트 디버그
npx playwright test --debug

# 테스트 코드 생성
npx playwright codegen http://localhost:3000

# 보고서 확인
npx playwright show-report
```