# SaaS 应用程序 — 项目 CLAUDE.md

> Next.js + Supabase + Stripe SaaS 应用程序的真实示例。
> 将其复制到您的项目根目录并针对您的堆栈进行自定义。

## 项目概述

**堆栈：** Next.js 15（应用程序路由器）、TypeScript、Supabase（身份验证 + DB）、Stripe（计费）、Tailwind CSS、Playwright（E2E）

**架构：**默认服务器组件。客户端组件仅用于交互。 Webhook 的 API 路由和突变的服务器操作。

## 关键规则

### 数据库

- 所有查询均使用启用了 RLS 的 Supabase 客户端 — 切勿绕过 RLS
- `supabase/migrations/` 中的迁移 — 切勿直接修改数据库
- 使用具有显式列列表的“select()”，而不是“select('*')”
- 所有面向用户的查询必须包含 `.limit()` 以防止结果不受限制

### 身份验证

- 在服务器组件中使用来自“@supabase/ssr”的“createServerClient()”
- 在客户端组件中使用来自“@supabase/ssr”的“createBrowserClient()”
- 受保护的路由检查 `getUser()` — 永远不要单独信任 `getSession()` 进行身份验证
- `middleware.ts` 中的中间件会根据每个请求刷新身份验证令牌

### 计费

- `app/api/webhooks/stripe/route.ts` 中的 Stripe webhook 处理程序
- 永远不要相信客户端价格数据 — 始终从 Stripe 服务器端获取
- 通过“subscription_status”列检查订阅状态，通过 webhook 同步
- 免费层用户：3 个项目，每天 100 次 API 调用

### 代码风格

- 代码或注释中没有表情符号
- 仅不可变模式 - 扩展运算符，永不变异
- 服务器组件：没有“use client”指令，没有“useState”/“useEffect”
- 客户端组件：“使用客户端”位于顶部，最小 — 将逻辑提取到钩子
- 首选 Zod 模式进行所有输入验证（API 路由、表单、环境变量）

## 文件结构```
src/
  app/
    (auth)/          # Auth pages (login, signup, forgot-password)
    (dashboard)/     # Protected dashboard pages
    api/
      webhooks/      # Stripe, Supabase webhooks
    layout.tsx       # Root layout with providers
  components/
    ui/              # Shadcn/ui components
    forms/           # Form components with validation
    dashboard/       # Dashboard-specific components
  hooks/             # Custom React hooks
  lib/
    supabase/        # Supabase client factories
    stripe/          # Stripe client and helpers
    utils.ts         # General utilities
  types/             # Shared TypeScript types
supabase/
  migrations/        # Database migrations
  seed.sql           # Development seed data
```## 关键模式

### API 响应格式```typescript
type ApiResponse<T> =
  | { success: true; data: T }
  | { success: false; error: string; code?: string }
```### 服务器操作模式```typescript
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
```## 环境变量```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=     # Server-only, never expose to client

# Stripe
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=

# App
NEXT_PUBLIC_APP_URL=http://localhost:3000
```## 测试策略```bash
/tdd                    # Unit + integration tests for new features
/e2e                    # Playwright tests for auth flow, billing, dashboard
/test-coverage          # Verify 80%+ coverage
```### 关键的端到端流程

1. 注册→邮箱验证→第一个项目创建
2.登录→仪表板→CRUD操作
3.升级计划→Stripe结账→订阅激活
4. Webhook：订阅取消→降级为免费套餐

## ECC 工作流程```bash
# Planning a feature
/plan "Add team invitations with email notifications"

# Developing with TDD
/tdd

# Before committing
/code-review
/security-scan

# Before release
/e2e
/test-coverage
```## Git 工作流程

- `feat:` 新功能、`fix:` 错误修复、`refactor:` 代码更改
- 来自“main”的功能分支，需要 PR
- CI 运行：lint、类型检查、单元测试、E2E 测试
- 部署：PR 上的 Vercel 预览，合并到“main”上的生产