# 旁白命令

在任务中提出问题，立即获得重点明确的答案，然后从上次停下的地方继续。当前任务、文件和上下文永远不会被修改。

## 何时使用

- 当克劳德工作时，你对某些事情感到好奇，并且不想失去动力
- 您需要对克劳德当前正在编辑的代码进行快速解释
- 您希望在不影响任务的情况下获得对决定的第二意见或澄清
- 在克劳德继续之前，你需要理解错误、概念或模式
- 您想询问与当前任务无关的问题而不开始新会话

## 用法```
/aside <your question>
/aside what does this function actually return?
/aside is this pattern thread-safe?
/aside why are we using X instead of Y here?
/aside what's the difference between foo() and bar()?
/aside should we be worried about the N+1 query we just added?
```## 流程

### 第 1 步：冻结当前任务状态

在回答任何问题之前，请先在心里记下：
- 当前的任务是什么？ （正在处理什么文件、功能或问题）
- 调用 `/aside` 时正在进行哪一步？
- 接下来会发生什么？

请勿在旁路期间触摸、编辑、创建或删除任何文件。

### 第2步：直接回答问题

以最简洁、完整且有用的形式回答问题。

- 以答案为主导，而不是推理
- 保持简短——如果需要完整的解释，请在任务完成后提供更深入的解释
- 如果问题是关于当前正在处理的文件或代码，请准确引用它（文件路径和行号，如果相关）
- 如果回答需要读取文件，请读取它 - 但只读，切勿写入

将响应格式化为：```
ASIDE: [restate the question briefly]

[Your answer here]

— Back to task: [one-line description of what was being done]
```### 第 3 步：恢复主要任务

给出答案后，立即从暂停的确切位置继续执行活动任务。不要请求恢复许可，除非旁边的答案揭示了阻碍因素或重新考虑当前方法的理由（请参阅边缘案例）。

---

## 边缘情况

**没有提供任何问题（`/aside` 后面没有任何内容）：**
回复：```
ASIDE: no question provided

What would you like to know? (ask your question and I'll answer without losing the current task context)

— Back to task: [one-line description of what was being done]
```**问题揭示了当前任务的潜在问题：**
在恢复之前明确标记它：```
ASIDE: [answer]

⚠️ Note: This answer suggests [issue] with the current approach. Want to address this before continuing, or proceed as planned?
```在恢复之前等待用户的决定。

**问题实际上是任务重定向（不是附带问题）：**
如果问题意味着更改正在构建的内容（例如“/aside 实际上，让我们使用 Redis”），请澄清：```
ASIDE: That sounds like a direction change, not just a side question.
Do you want to:
  (a) Answer this as information only and keep the current plan
  (b) Pause the current task and change approach
```等待用户的回答——不要做出假设。

**问题是关于当前打开的文件或代码：**
从实时上下文中回答。如果该文件是在会话的早期读取的，则直接引用它。如果没有，请立即阅读（只读）并使用 file:line 参考进行回答。

**没有活动任务（调用 `/aside` 时没有任何进展）：**
仍然使用标准包装器，以便响应形状保持一致：```
ASIDE: [restate the question briefly]

[Your answer here]

— Back to task: no active task to resume
```**问题需要很长的答案：**
简洁地给出基本答案，然后提供：```
That's the short version. Want a deeper explanation after we finish [current task]?
```**连续多个`/aside`问题：**
按顺序逐一回答。回答完最后一个问题后，继续主要任务。不要在一系列旁白中丢失任务状态。

**旁白答案意味着需要更改代码：**
记下所需的更改，但不要在旁白期间进行更改：```
ASIDE: [answer]

📝 Worth fixing: [what should be changed]. I'll flag this after the current task unless you want to address it now.
```**问题不明确或太模糊：**
提出一个澄清性问题——能够获得回答所需信息的最短问题。不要问多个问题。

---

## 输出示例```
User: /aside what does fetchWithRetry() actually do?

ASIDE: what does fetchWithRetry() do?

fetchWithRetry() (src/api/retry.ts:12) attempts the request up to 3 times with
exponential backoff (250ms → 500ms → 1s). It only retries on 5xx responses and
network errors — 4xx errors are treated as final and not retried.

— Back to task: refactoring the auth middleware in src/middleware/auth.ts
``````
User: /aside is the approach we're taking thread-safe?

ASIDE: is the current approach thread-safe?

No — the shared cache object in src/cache/store.ts:34 is mutated without locking.
Under concurrent requests this is a race condition. It's low risk in a single-process
Node.js server but would be a real problem with worker threads or clustering.

⚠️ Note: This could affect the feature we're building. Want to address this now or continue and fix it in a follow-up?
```---

## 注释

- 切勿在旁白期间修改文件 - 只读访问权限
- 旁白是对话暂停，而不是新任务 - 原始任务必须始终恢复
- 保持答案集中：目标是快速解锁用户，而不是进行讲座
- 如果旁白引发了更大的讨论，请先完成当前任务，除非旁白揭示了阻碍因素
- 旁白不会保存到会话文件中，除非与任务结果明确相关