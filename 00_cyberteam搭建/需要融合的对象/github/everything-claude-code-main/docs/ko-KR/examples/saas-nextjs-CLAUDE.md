# SaaS 애플리케օ — 프로젝트 CLAUDE.md

> Next.js + Supabase + Stripe SaaS 应用程序。
> 프로젝트 루트에 복사한 후 기술 스택에 맞게 커스터마기즈하세요。

## 프로젝트 개요

**主要应用:** Next.js 15 (App Router)、TypeScript、Supabase (인증 + DB)、Stripe (결제)、Tailwind CSS、Playwright (E2E)

**아키텍처:** 服务端组件。客户端组件是由客户端组件组成的。 API 路由和 webhook、服务器操作和突变。

## 핵심 규칙

### 데기베스

- 모든 쿼리는 RLSі 활성화된 Supabase 客户端사용 — RLS를 절대 우회하지 않음
- 마그레션은 `supabase/migrations/`에 저장 — 데dling터베֊를 직접 수정하지 않음
- `select('*')` 选择`select()` 方法
- 모든 사용자 대상 쿼리에는 무제한 결과를 방지하기 위해 `.limit()` 포함 필수

### 인증

- 服务器组件`@supabase/ssr`和`createServerClient()`
- 客户端组件`@supabase/ssr`和`createBrowserClient()`
- 보호된 라우트는 `getUser()`로 확인 — 인증에 `getSession()`만 단독으로 신뢰하지 않음
- `middleware.ts`의 Middlewareі 매 요청마다 인증 토큰 갱신

### 결제

- Stripe webhook 핸들러는 `app/api/webhooks/stripe/route.ts`에 위치
- 항상 서버 측에서 Stripe로부터 조회
- 구독 상태는 webhook에 의해 동기화되는 `subscription_status` 컬럼으로 확인
- 参数设置: 프로젝트 3개, 일일 API 호출 100회

### 코드 스타일

- 코드나 주석에 ה모지 사용 금지
- 불변 패턴만 사용 — 传播 연산자 사용, 직접 변경 금지
- 服务器组件：“使用客户端”、“useState”/“useEffect”
- 客户端组件：파일 상단에 `'use client'` 작성, 최소한으로 유지 — 로직은 hooks로 분리
- 모든 입력 유효성 검사에 Zod 스키마 사용 선호 (API 路线, 폼, 환경 변수)

## 파일 구조```
src/
  app/
    (auth)/          # 인증 페이지 (로그인, 회원가입, 비밀번호 찾기)
    (dashboard)/     # 보호된 대시보드 페이지
    api/
      webhooks/      # Stripe, Supabase webhooks
    layout.tsx       # Provider가 포함된 루트 레이아웃
  components/
    ui/              # Shadcn/ui 컴포넌트
    forms/           # 유효성 검사가 포함된 폼 컴포넌트
    dashboard/       # 대시보드 전용 컴포넌트
  hooks/             # 커스텀 React hooks
  lib/
    supabase/        # Supabase client 팩토리
    stripe/          # Stripe client 및 헬퍼
    utils.ts         # 범용 유틸리티
  types/             # 공유 TypeScript 타입
supabase/
  migrations/        # 데이터베이스 마이그레이션
  seed.sql           # 개발용 시드 데이터
```## 주요 패턴

### API 응답 형식```typescript
type ApiResponse<T> =
  | { success: true; data: T }
  | { success: false; error: string; code?: string }
```### 服务器操作```typescript
'use server'

import { z } from 'zod'
import { createServerClient } from '@/lib/supabase/server'

const schema = z.object({
  name: z.string().min(1).max(100),
})

export async function createProject(formData: FormData) {
  const parsed = schema.safeParse({ name: formData.get('name') })
  if (!parsed.success) {
    return { success: false, error: parsed.error.flatten() }
  }

  const supabase = await createServerClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) return { success: false, error: 'Unauthorized' }

  const { data, error } = await supabase
    .from('projects')
    .insert({ name: parsed.data.name, user_id: user.id })
    .select('id, name, created_at')
    .single()

  if (error) return { success: false, error: 'Failed to create project' }
  return { success: true, data }
}
```## 환경 변수```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=     # 서버 전용, 클라이언트에 절대 노출 금지

# Stripe
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=

# 앱
NEXT_PUBLIC_APP_URL=http://localhost:3000
```## 테스트 전략```bash
/tdd                    # 새 기능에 대한 단위 + 통합 테스트
/e2e                    # 인증 흐름, 결제, 대시보드에 대한 Playwright 테스트
/test-coverage          # 80% 이상 커버리지 확인
```### 핵심 E2E 흐름

1. 회원і입 → 메일 인증 → 첫 프로젝트 생성
2. 로그인 → 대시보드 → CRUD 작업
3. 플랜 업그레드 → Stripe 结账 → 구독 활성화
4. Webhook: 구독 취소 → 무료 플랜으로 다운그레드

## ECC 워크플로우```bash
# 기능 계획 수립
/plan "Add team invitations with email notifications"

# TDD로 개발
/tdd

# 커밋 전
/code-review
/security-scan

# 릴리스 전
/e2e
/test-coverage
```## Git 运行

- `壮举：` 새 기능，`修复：` 버그 수정，`重构：` 코드 변경
- `main`에서 기능 브랜치 생성, PR 필수
- CI 处理：lint、타입 체크、단위 테스트、E2E 테스트
- 배포: PR 시 Vercel 미리보기, `main` 병합 시 프로덕션 배포