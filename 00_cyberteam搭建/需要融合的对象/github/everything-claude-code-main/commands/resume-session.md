# 恢复会话命令

在进行任何工作之前，加载上次保存的会话状态并完全定向。
该命令与“/save-session”相对应。

## 何时使用

- 开始新的会话以继续前一天的工作
- 由于上下文限制开始新会话后
- 从另一个源移交会话文件时（只需提供文件路径）
- 任何时候你有一个会话文件并希望克劳德在继续之前完全吸收它

## 用法```
/resume-session                                                      # loads most recent file in ~/.claude/sessions/
/resume-session 2024-01-15                                           # loads most recent session for that date
/resume-session ~/.claude/sessions/2024-01-15-session.tmp           # loads a specific legacy-format file
/resume-session ~/.claude/sessions/2024-01-15-abc123de-session.tmp  # loads a current short-id session file
```## 流程

### 第 1 步：找到会话文件

如果没有提供参数：

1.检查`~/.claude/sessions/`
2. 选择最近修改的`*-session.tmp`文件
3. 如果该文件夹不存在或没有匹配的文件，则告诉用户：```
   No session files found in ~/.claude/sessions/
   Run /save-session at the end of a session to create one.
   ```然后停下来。

如果提供参数：

- 如果它看起来像日期（“YYYY-MM-DD”），请搜索“~/.claude/sessions/”以查找匹配的文件
  `YYYY-MM-DD-session.tmp`（旧格式）或 `YYYY-MM-DD-<shortid>-session.tmp`（当前格式）
  并加载该日期最近修改的变体
- 如果它看起来像一个文件路径，则直接读取该文件
- 如果没有发现，请明确报告并停止

### 步骤 2：读取整个会话文件

阅读完整的文件。还不总结一下。

### 第 3 步：确认理解

按照以下格式进行结构化简报回应：```
SESSION LOADED: [actual resolved path to the file]
════════════════════════════════════════════════

PROJECT: [project name / topic from file]

WHAT WE'RE BUILDING:
[2-3 sentence summary in your own words]

CURRENT STATE:
✅ Working: [count] items confirmed
🔄 In Progress: [list files that are in progress]
🗒️ Not Started: [list planned but untouched]

WHAT NOT TO RETRY:
[list every failed approach with its reason — this is critical]

OPEN QUESTIONS / BLOCKERS:
[list any blockers or unanswered questions]

NEXT STEP:
[exact next step if defined in the file]
[if not defined: "No next step defined — recommend reviewing 'What Has NOT Been Tried Yet' together before starting"]

════════════════════════════════════════════════
Ready to continue. What would you like to do?
```### 第 4 步：等待用户

不要自动开始工作。请勿触摸任何文件。等待用户说出下一步该做什么。

如果会话文件中明确定义了下一步，并且用户说“继续”或“是”或类似内容 - 继续执行下一步。

如果没有定义下一步 - 询问用户从哪里开始，并可选择从“尚未尝试过的内容”部分建议一种方法。

---

## 边缘情况

**同一日期的多个会话**（`2024-01-15-session.tmp`、`2024-01-15-abc123de-session.tmp`）：
加载该日期最近修改的匹配文件，无论它使用旧版 no-id 格式还是当前的短 id 格式。

**会话文件引用不再存在的文件：**
在简报中请注意这一点 - “⚠️ `path/to/file.ts` 在会话中引用，但在磁盘上找不到。”

**会话文件来自 7 天多前：**
注意差距——“⚠️这个会话是N天前的（阈值：7天）。事情可能已经改变了。” ——然后正常进行。

**用户直接提供文件路径（例如，从队友转发）：**
阅读它并遵循相同的简报流程——无论来源如何，格式都是相同的。

**会话文件为空或格式错误：**
报告：“找到会话文件，但显示为空或无法读取。您可能需要使用 /save-session 创建一个新文件。”

---

## 输出示例```
SESSION LOADED: /Users/you/.claude/sessions/2024-01-15-abc123de-session.tmp
════════════════════════════════════════════════

PROJECT: my-app — JWT Authentication

WHAT WE'RE BUILDING:
User authentication with JWT tokens stored in httpOnly cookies.
Register and login endpoints are partially done. Route protection
via middleware hasn't been started yet.

CURRENT STATE:
✅ Working: 3 items (register endpoint, JWT generation, password hashing)
🔄 In Progress: app/api/auth/login/route.ts (token works, cookie not set yet)
🗒️ Not Started: middleware.ts, app/login/page.tsx

WHAT NOT TO RETRY:
❌ Next-Auth — conflicts with custom Prisma adapter, threw adapter error on every request
❌ localStorage for JWT — causes SSR hydration mismatch, incompatible with Next.js

OPEN QUESTIONS / BLOCKERS:
- Does cookies().set() work inside a Route Handler or only Server Actions?

NEXT STEP:
In app/api/auth/login/route.ts — set the JWT as an httpOnly cookie using
cookies().set('token', jwt, { httpOnly: true, secure: true, sameSite: 'strict' })
then test with Postman for a Set-Cookie header in the response.

════════════════════════════════════════════════
Ready to continue. What would you like to do?
```---

## 注释

- 加载会话文件时切勿修改它——它是只读历史记录
- 简报格式是固定的——即使是空的部分也不要跳过
- 必须始终显示“不要重试的内容”，即使它只是说“无”——这太重要了，不容错过
- 恢复后，用户可能希望在新会话结束时再次运行“/save-session”以创建新的日期文件