# 保存会话命令

捕获本次会话中发生的所有事情 - 构建了什么、有效的、失败的、剩下的 - 并将其写入一个注明日期的文件，以便下一个会话可以准确地从本次会话结束的地方继续。

## 何时使用

- 在关闭克劳德代码之前结束工作会话
- 在达到上下文限制之前（首先运行此命令，然后开始新的会话）
- 解决了一个你想要记住的复杂问题后
- 任何时候您需要将上下文移交给未来的会话

## 流程

### 第 1 步：收集背景信息

在写入文件之前，收集：

- 读取本次会话期间修改的所有文件（使用 git diff 或从对话中调用）
- 回顾讨论、尝试和决定的内容
- 记录遇到的任何错误以及如何解决（或未解决）
- 检查当前测试/构建状态（如果相关）

### 步骤2：如果sessions文件夹不存在则创建它

在用户的 Claude 主目录中创建规范会话文件夹：```bash
mkdir -p ~/.claude/sessions
```### 第三步：写入会话文件

创建“~/.claude/sessions/YYYY-MM-DD-<short-id>-session.tmp”，使用今天的实际日期和满足“session-manager.js”中“SESSION_FILENAME_REGEX”强制执行的规则的短ID：

- 允许的字符：小写“a-z”、数字“0-9”、连字符“-”
- 最小长度：8 个字符
- 没有大写字母，没有下划线，没有空格

有效示例：`abc123de`、`a1b2c3d4`、`frontend-worktree-1`
无效示例：“ABC123de”（大写）、“short”（8 个字符以下）、“test_id1”（下划线）

完整有效的文件名示例：`2024-01-15-abc123de-session.tmp`

旧文件名“YYYY-MM-DD-session.tmp”仍然有效，但新会话文件应该更喜欢短 ID 形式以避免当天冲突。

### 步骤 4：使用以下所有部分填充文件

诚实地写每个部分。不要跳过某些部分——如果某个部分确实没有内容，请写“还没有”或“N/A”。不完整的文件比诚实的空部分更糟糕。

### 步骤 5：向用户显示文件

写完后，显示完整内容并询问：```
Session saved to [actual resolved path to the session file]

Does this look accurate? Anything to correct or add before we close?
```等待确认。根据要求进行编辑。

---

## 会话文件格式```markdown
# Session: YYYY-MM-DD

**Started:** [approximate time if known]
**Last Updated:** [current time]
**Project:** [project name or path]
**Topic:** [one-line summary of what this session was about]

---

## What We Are Building

[1-3 paragraphs describing the feature, bug fix, or task. Include enough
context that someone with zero memory of this session can understand the goal.
Include: what it does, why it's needed, how it fits into the larger system.]

---

## What WORKED (with evidence)

[List only things that are confirmed working. For each item include WHY you
know it works — test passed, ran in browser, Postman returned 200, etc.
Without evidence, move it to "Not Tried Yet" instead.]

- **[thing that works]** — confirmed by: [specific evidence]
- **[thing that works]** — confirmed by: [specific evidence]

If nothing is confirmed working yet: "Nothing confirmed working yet — all approaches still in progress or untested."

---

## What Did NOT Work (and why)

[This is the most important section. List every approach tried that failed.
For each failure write the EXACT reason so the next session doesn't retry it.
Be specific: "threw X error because Y" is useful. "didn't work" is not.]

- **[approach tried]** — failed because: [exact reason / error message]
- **[approach tried]** — failed because: [exact reason / error message]

If nothing failed: "No failed approaches yet."

---

## What Has NOT Been Tried Yet

[Approaches that seem promising but haven't been attempted. Ideas from the
conversation. Alternative solutions worth exploring. Be specific enough that
the next session knows exactly what to try.]

- [approach / idea]
- [approach / idea]

If nothing is queued: "No specific untried approaches identified."

---

## Current State of Files

[Every file touched this session. Be precise about what state each file is in.]

| File              | Status         | Notes                      |
| ----------------- | -------------- | -------------------------- |
| `path/to/file.ts` | ✅ Complete    | [what it does]             |
| `path/to/file.ts` | 🔄 In Progress | [what's done, what's left] |
| `path/to/file.ts` | ❌ Broken      | [what's wrong]             |
| `path/to/file.ts` | 🗒️ Not Started | [planned but not touched]  |

If no files were touched: "No files modified this session."

---

## Decisions Made

[Architecture choices, tradeoffs accepted, approaches chosen and why.
These prevent the next session from relitigating settled decisions.]

- **[decision]** — reason: [why this was chosen over alternatives]

If no significant decisions: "No major decisions made this session."

---

## Blockers & Open Questions

[Anything unresolved that the next session needs to address or investigate.
Questions that came up but weren't answered. External dependencies waiting on.]

- [blocker / open question]

If none: "No active blockers."

---

## Exact Next Step

[If known: The single most important thing to do when resuming. Be precise
enough that resuming requires zero thinking about where to start.]

[If not known: "Next step not determined — review 'What Has NOT Been Tried Yet'
and 'Blockers' sections to decide on direction before starting."]

---

## Environment & Setup Notes

[Only fill this if relevant — commands needed to run the project, env vars
required, services that need to be running, etc. Skip if standard setup.]

[If none: omit this section entirely.]
```---

## 输出示例```markdown
# Session: 2024-01-15

**Started:** ~2pm
**Last Updated:** 5:30pm
**Project:** my-app
**Topic:** Building JWT authentication with httpOnly cookies

---

## What We Are Building

User authentication system for the Next.js app. Users register with email/password,
receive a JWT stored in an httpOnly cookie (not localStorage), and protected routes
check for a valid token via middleware. The goal is session persistence across browser
refreshes without exposing the token to JavaScript.

---

## What WORKED (with evidence)

- **`/api/auth/register` endpoint** — confirmed by: Postman POST returns 200 with user
  object, row visible in Supabase dashboard, bcrypt hash stored correctly
- **JWT generation in `lib/auth.ts`** — confirmed by: unit test passes
  (`npm test -- auth.test.ts`), decoded token at jwt.io shows correct payload
- **Password hashing** — confirmed by: `bcrypt.compare()` returns true in test

---

## What Did NOT Work (and why)

- **Next-Auth library** — failed because: conflicts with our custom Prisma adapter,
  threw "Cannot use adapter with credentials provider in this configuration" on every
  request. Not worth debugging — too opinionated for our setup.
- **Storing JWT in localStorage** — failed because: SSR renders happen before
  localStorage is available, caused React hydration mismatch error on every page load.
  This approach is fundamentally incompatible with Next.js SSR.

---

## What Has NOT Been Tried Yet

- Store JWT as httpOnly cookie in the login route response (most likely solution)
- Use `cookies()` from `next/headers` to read token in server components
- Write middleware.ts to protect routes by checking cookie existence

---

## Current State of Files

| File                             | Status         | Notes                                           |
| -------------------------------- | -------------- | ----------------------------------------------- |
| `app/api/auth/register/route.ts` | ✅ Complete    | Works, tested                                   |
| `app/api/auth/login/route.ts`    | 🔄 In Progress | Token generates but not setting cookie yet      |
| `lib/auth.ts`                    | ✅ Complete    | JWT helpers, all tested                         |
| `middleware.ts`                  | 🗒️ Not Started | Route protection, needs cookie read logic first |
| `app/login/page.tsx`             | 🗒️ Not Started | UI not started                                  |

---

## Decisions Made

- **httpOnly cookie over localStorage** — reason: prevents XSS token theft, works with SSR
- **Custom auth over Next-Auth** — reason: Next-Auth conflicts with our Prisma setup, not worth the fight

---

## Blockers & Open Questions

- Does `cookies().set()` work inside a Route Handler or only in Server Actions? Need to verify.

---

## Exact Next Step

In `app/api/auth/login/route.ts`, after generating the JWT, set it as an httpOnly
cookie using `cookies().set('token', jwt, { httpOnly: true, secure: true, sameSite: 'strict' })`.
Then test with Postman — the response should include a `Set-Cookie` header.
```---

## 注释

- 每个会话都有自己的文件 - 永远不会附加到前一个会话的文件
- “什么不起作用”部分是最关键的——如果没有它，未来的会议将盲目地重试失败的方法
- 如果用户要求在会话中保存（而不仅仅是在结束时），请保存到目前为止已知的内容并清楚地标记正在进行的项目
- 该文件旨在由克劳德在下一个会话开始时通过“/resume-session”读取
- 使用规范的全局会话存储：`~/.claude/sessions/`
- 对于任何新会话文件，首选短 ID 文件名形式 (`YYYY-MM-DD-<short-id>-session.tmp`)