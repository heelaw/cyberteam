# 自主循环技能

> 兼容性说明 (v1.8.0)：`autonomous-loops` 保留在一个版本中。
> 规范技能名称现在为“连续代理循环”。新循环指导
> 应在那里创作，而此技能仍然可以避免
> 打破现有的工作流程。

用于在循环中自主运行 Claude Code 的模式、架构和参考实现。涵盖从简单的“claude -p”管道到完整的 RFC 驱动的多代理 DAG 编排的一切。

## 何时使用

- 设置无需人工干预即可运行的自主开发工作流程
- 为您的问题选择正确的循环架构（简单与复杂）
- 构建CI/CD式的持续开发管道
- 通过合并协调运行并行代理
- 跨循环迭代实现上下文持久化
- 将质量门和清理通道添加到自主工作流程中

## 循环模式频谱

从最简单到最复杂：

|图案|复杂性 |最适合 |
|--------|------------|----------|
| [顺序管道](#1-sequential-pipeline-claude--p) |低|每日开发步骤、脚本化工作流程 |
| [NanoClaw REPL](#2-nanoclaw-repl) |低|交互式持久会话|
| [无限代理循环](#3-无限代理循环) |中等|并行内容生成，规范驱动的工作 |
| [连续克劳德 PR 循环](#4-连续-克劳德-PR-循环) |中等|使用 CI 门的多日迭代项目 |
| [去马虎模式](#5-去马虎模式) |附加组件 |任何实施者步骤之后的质量清理 |
| [Ralphinho / RFC 驱动的 DAG](#6-ralphinho--rfc-driven-dag-orchestration) |高|大特征，多单元并行工作与合并队列 |

---

## 1. 顺序管道 (`claude -p`)

**最简单的循环。** 将日常开发分解为一系列非交互式“claude -p”调用。每次通话都是一个有明确提示的重点步骤。

### 核心洞察

> 如果你无法找出这样的循环，则意味着你甚至无法驱动 LLM 在交互模式下修复你的代码。

`claude -p` 标志以非交互方式运行 Claude Code，并有提示，完成后退出。链式调用构建管道：```bash
#!/bin/bash
# daily-dev.sh — Sequential pipeline for a feature branch

set -e

# Step 1: Implement the feature
claude -p "Read the spec in docs/auth-spec.md. Implement OAuth2 login in src/auth/. Write tests first (TDD). Do NOT create any new documentation files."

# Step 2: De-sloppify (cleanup pass)
claude -p "Review all files changed by the previous commit. Remove any unnecessary type tests, overly defensive checks, or testing of language features (e.g., testing that TypeScript generics work). Keep real business logic tests. Run the test suite after cleanup."

# Step 3: Verify
claude -p "Run the full build, lint, type check, and test suite. Fix any failures. Do not add new features."

# Step 4: Commit
claude -p "Create a conventional commit for all staged changes. Use 'feat: add OAuth2 login flow' as the message."
```### 关键设计原则

1. **每个步骤都是隔离的** — 每个“claude -p”调用都有一个新的上下文窗口，意味着步骤之间不会出现上下文流失。
2. **顺序很重要** — 步骤按顺序执行。每个都建立在前一个留下的文件系统状态之上。
3. **负面指令是危险的** — 不要说“不要测试类型系统”。相反，添加一个单独的清理步骤（请参阅[De-Sloppify 模式](#5-the-de-sloppify-pattern)）。
4. **退出代码传播** — `set -e` 在失败时停止管道。

### 变化

**使用模型路由：**```bash
# Research with Opus (deep reasoning)
claude -p --model opus "Analyze the codebase architecture and write a plan for adding caching..."

# Implement with Sonnet (fast, capable)
claude -p "Implement the caching layer according to the plan in docs/caching-plan.md..."

# Review with Opus (thorough)
claude -p --model opus "Review all changes for security issues, race conditions, and edge cases..."
```**具有环境上下文：**```bash
# Pass context via files, not prompt length
echo "Focus areas: auth module, API rate limiting" > .claude-context.md
claude -p "Read .claude-context.md for priorities. Work through them in order."
rm .claude-context.md
```**使用 `--allowedTools` 限制：**```bash
# Read-only analysis pass
claude -p --allowedTools "Read,Grep,Glob" "Audit this codebase for security vulnerabilities..."

# Write-only implementation pass
claude -p --allowedTools "Read,Write,Edit,Bash" "Implement the fixes from security-audit.md..."
```---

## 2. NanoClaw REPL

**ECC 的内置持久循环。** 会话感知 REPL，可与完整对话历史记录同步调用“claude -p”。```bash
# Start the default session
node scripts/claw.js

# Named session with skill context
CLAW_SESSION=my-project CLAW_SKILLS=tdd-workflow,security-review node scripts/claw.js
```### 它是如何运作的

1. 从 `~/.claude/claw/{session}.md` 加载对话历史记录
2. 每条用户消息都会发送到“claude -p”，并以完整历史记录作为上下文
3. 响应被附加到会话文件中（Markdown-as-database）
4. 会话在重新启动后仍然存在

### 当 NanoClaw 与顺序管道时

|使用案例|纳米爪 |顺序管道|
|----------|----------|--------------------|
|互动探索 |是的 |没有 |
|脚本化自动化|没有 |是的 |
|会话保持 |内置|手册|
|语境积累|每回合成长 |每一步都清新 |
| CI/CD 集成 |可怜|优秀|

有关完整详细信息，请参阅“/claw”命令文档。

---

## 3.无限代理循环

**两个提示系统**，协调并行子代理以进行规范驱动的生成。由 disler 开发（来源：@disler）。

### 架构：两个提示系统```
PROMPT 1 (Orchestrator)              PROMPT 2 (Sub-Agents)
┌─────────────────────┐             ┌──────────────────────┐
│ Parse spec file      │             │ Receive full context  │
│ Scan output dir      │  deploys   │ Read assigned number  │
│ Plan iteration       │────────────│ Follow spec exactly   │
│ Assign creative dirs │  N agents  │ Generate unique output │
│ Manage waves         │             │ Save to output dir    │
└─────────────────────┘             └──────────────────────┘
```### 模式

1. **规范分析** — Orchestrator 读取定义要生成的内容的规范文件 (Markdown)
2. **Directory Recon** — 扫描现有输出以查找最高迭代数
3. **并行部署** — 启动 N 个子代理，每个子代理具有：
   - 完整规格
   - 独特的创作方向
   - 特定的迭代次数（无冲突）
   - 现有迭代的快照（为了唯一性）
4. **Wave Management** — 对于无限模式，部署 3-5 个代理的 Wave，直到上下文耗尽

### 通过 Claude 代码命令实现

创建 `.claude/commands/infinite.md`：```markdown
Parse the following arguments from $ARGUMENTS:
1. spec_file — path to the specification markdown
2. output_dir — where iterations are saved
3. count — integer 1-N or "infinite"

PHASE 1: Read and deeply understand the specification.
PHASE 2: List output_dir, find highest iteration number. Start at N+1.
PHASE 3: Plan creative directions — each agent gets a DIFFERENT theme/approach.
PHASE 4: Deploy sub-agents in parallel (Task tool). Each receives:
  - Full spec text
  - Current directory snapshot
  - Their assigned iteration number
  - Their unique creative direction
PHASE 5 (infinite mode): Loop in waves of 3-5 until context is low.
```**调用：**```bash
/project:infinite specs/component-spec.md src/ 5
/project:infinite specs/component-spec.md src/ infinite
```### 批处理策略

|计数 |战略|
|--------|----------|
| 1-5 | 1-5所有代理同时进行|
| 6-20 | 5 个批次 |
|无限| 3-5波，渐进复杂|

### 关键见解：通过分配实现唯一性

不要依赖代理商进行自我差异化。协调器为每个代理分配特定的创意方向和迭代编号。这可以防止并行代理之间出现重复的概念。

---

## 4. 连续的克劳德 PR 循环

**生产级 shell 脚本**，在连续循环中运行 Claude Code，创建 PR，等待 CI，并自动合并。由 AnandChowdhary 创建（来源：@AnandChowdhary）。

### 核心循环```
┌─────────────────────────────────────────────────────┐
│  CONTINUOUS CLAUDE ITERATION                        │
│                                                     │
│  1. Create branch (continuous-claude/iteration-N)   │
│  2. Run claude -p with enhanced prompt              │
│  3. (Optional) Reviewer pass — separate claude -p   │
│  4. Commit changes (claude generates message)       │
│  5. Push + create PR (gh pr create)                 │
│  6. Wait for CI checks (poll gh pr checks)          │
│  7. CI failure? → Auto-fix pass (claude -p)         │
│  8. Merge PR (squash/merge/rebase)                  │
│  9. Return to main → repeat                         │
│                                                     │
│  Limit by: --max-runs N | --max-cost $X             │
│            --max-duration 2h | completion signal     │
└─────────────────────────────────────────────────────┘
```＃＃＃ 安装```bash
curl -fsSL https://raw.githubusercontent.com/AnandChowdhary/continuous-claude/HEAD/install.sh | bash
```＃＃＃ 用法```bash
# Basic: 10 iterations
continuous-claude --prompt "Add unit tests for all untested functions" --max-runs 10

# Cost-limited
continuous-claude --prompt "Fix all linter errors" --max-cost 5.00

# Time-boxed
continuous-claude --prompt "Improve test coverage" --max-duration 8h

# With code review pass
continuous-claude \
  --prompt "Add authentication feature" \
  --max-runs 10 \
  --review-prompt "Run npm test && npm run lint, fix any failures"

# Parallel via worktrees
continuous-claude --prompt "Add tests" --max-runs 5 --worktree tests-worker &
continuous-claude --prompt "Refactor code" --max-runs 5 --worktree refactor-worker &
wait
```### 交叉迭代上下文：SHARED_TASK_NOTES.md

关键的创新：“SHARED_TASK_NOTES.md”文件在迭代中持续存在：```markdown
## Progress
- [x] Added tests for auth module (iteration 1)
- [x] Fixed edge case in token refresh (iteration 2)
- [ ] Still need: rate limiting tests, error boundary tests

## Next Steps
- Focus on rate limiting module next
- The mock setup in tests/helpers.ts can be reused
```Claude 在迭代开始时读取此文件并在迭代结束时更新它。这弥合了独立的“claude -p”调用之间的上下文差距。

### CI 故障恢复

当 PR 检查失败时，连续克劳德会自动：
1.通过`gh run list`获取失败的运行ID
2. 生成一个带有 CI 修复上下文的新“claude -p”
3. Claude 通过 `gh run view` 检查日志，修复代码，提交，推送
4. 重新等待检查（最多尝试“--ci-retry-max”）

### 完成信号

克劳德可以通过输出一个神奇的短语来表示“我完成了”：```bash
continuous-claude \
  --prompt "Fix all bugs in the issue tracker" \
  --completion-signal "CONTINUOUS_CLAUDE_PROJECT_COMPLETE" \
  --completion-threshold 3  # Stops after 3 consecutive signals
```三个连续的迭代信号完成会停止循环，从而防止浪费运行已完成的工作。

### 关键配置

|旗帜|目的|
|------|---------|
| `--max-runs N` | N次成功迭代后停止 |
| `--最大成本 $X` |花费 X 美元后停止 |
| `--最大持续时间 2h` |时间过去后停止 |
| `--合并策略挤压` |压缩、合并或变基 |
| `--worktree <名称>` |通过 git worktrees 并行执行 |
| `--disable-commits` |空运行模式（无 git 操作）|
| `--审阅提示“...”` |每次迭代添加审阅者通过 |
| `--ci-retry-max N` |自动修复 CI 故障（默认值：1） |

---

## 5. 去马虎模式

**适用于任何循环的附加模式。** 在每个实施者步骤之后添加专用的清理/重构步骤。

### 问题

当你要求法学硕士使用 TDD 来实现时，它太字面地理解了“编写测试”：
- 验证 TypeScript 类型系统是否正常工作的测试（测试 `typeof x === 'string'`）
- 对类型系统已经保证的事情进行过度防御性的运行时检查
- 测试框架行为而不是业务逻辑
- 过多的错误处理掩盖了实际的代码

### 为什么不是负面指令？

在实施者提示中添加“不要测试类型系统”或“不要添加不必要的检查”会产生下游影响：
- 模型对所有测试变得犹豫不决
- 它跳过合法的边缘情况测试
- 质量不可预测地下降

### 解决方案：单独传递

不要限制实施者，而要彻底。然后添加集中清理剂：```bash
# Step 1: Implement (let it be thorough)
claude -p "Implement the feature with full TDD. Be thorough with tests."

# Step 2: De-sloppify (separate context, focused cleanup)
claude -p "Review all changes in the working tree. Remove:
- Tests that verify language/framework behavior rather than business logic
- Redundant type checks that the type system already enforces
- Over-defensive error handling for impossible states
- Console.log statements
- Commented-out code

Keep all business logic tests. Run the test suite after cleanup to ensure nothing breaks."
```### 在循环上下文中```bash
for feature in "${features[@]}"; do
  # Implement
  claude -p "Implement $feature with TDD."

  # De-sloppify
  claude -p "Cleanup pass: review changes, remove test/code slop, run tests."

  # Verify
  claude -p "Run build + lint + tests. Fix any failures."

  # Commit
  claude -p "Commit with message: feat: add $feature"
done
```### 关键见解

> 添加单独的 de-sloppify 通道，而不是添加对下游质量有影响的负面指令。两名专注的智能体胜过一名受限的智能体。

---

## 6. Ralphinho / RFC 驱动的 DAG 编排

**最复杂的模式。** RFC 驱动的多代理管道，将规范分解为依赖 DAG，通过分层质量管道运行每个单元，并通过代理驱动的合并队列将它们着陆。由 enitrat 创建（来源：@enitrat）。

### 架构概述```
RFC/PRD Document
       │
       ▼
  DECOMPOSITION (AI)
  Break RFC into work units with dependency DAG
       │
       ▼
┌──────────────────────────────────────────────────────┐
│  RALPH LOOP (up to 3 passes)                         │
│                                                      │
│  For each DAG layer (sequential, by dependency):     │
│                                                      │
│  ┌── Quality Pipelines (parallel per unit) ───────┐  │
│  │  Each unit in its own worktree:                │  │
│  │  Research → Plan → Implement → Test → Review   │  │
│  │  (depth varies by complexity tier)             │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  ┌── Merge Queue ─────────────────────────────────┐  │
│  │  Rebase onto main → Run tests → Land or evict │  │
│  │  Evicted units re-enter with conflict context  │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
└──────────────────────────────────────────────────────┘
```### RFC分解

AI 读取 RFC 并生成工作单元：```typescript
interface WorkUnit {
  id: string;              // kebab-case identifier
  name: string;            // Human-readable name
  rfcSections: string[];   // Which RFC sections this addresses
  description: string;     // Detailed description
  deps: string[];          // Dependencies (other unit IDs)
  acceptance: string[];    // Concrete acceptance criteria
  tier: "trivial" | "small" | "medium" | "large";
}
```**分解规则：**
- 喜欢较少的、有凝聚力的单元（最小化合并风险）
- 最小化跨单元文件重叠（避免冲突）
- 保持测试与实现（永远不要分开“实现 X”+“测试 X”）
- 仅在存在实际代码依赖关系的情况下才存在依赖关系

依赖DAG决定执行顺序：```
Layer 0: [unit-a, unit-b]     ← no deps, run in parallel
Layer 1: [unit-c]             ← depends on unit-a
Layer 2: [unit-d, unit-e]     ← depend on unit-c
```### 复杂度等级

不同的层有不同的管道深度：

|等级 |管道阶段|
|------|----------------|
| **微不足道** |实施→测试|
| **小** |实施→测试→代码审查|
| **中** |研究→计划→实施→测试→PRD审查+代码审查→审查修复|
| **大** |研究→计划→实施→测试→PRD审查+代码审查→审查修复→最终审查|

这可以防止对简单更改进行昂贵的操作，同时确保架构更改得到彻底的审查。

### 单独的上下文窗口（作者偏见消除）

每个阶段都在自己的代理进程中运行，并具有自己的上下文窗口：

|舞台|型号|目的|
|--------|--------|---------|
|研究|十四行诗|阅读代码库 + RFC，生成上下文文档 |
|计划|作品|设计实施步骤|
|实施 |法典|按照计划编写代码 |
|测试|十四行诗|运行构建+测试套件|
|珠三角评论 |十四行诗|规格合规性检查 |
|代码审查 |作品|品质+安全检查|
|审查修复|法典|解决审核问题 |
|最终审查|作品|质量门（仅限大层）|

**关键设计：** 审阅者从未编写过其审阅的代码。这消除了作者偏见——这是自我审查中遗漏问题的最常见原因。

### 合并队列与驱逐

质量管道完成后，单元进入合并队列：```
Unit branch
    │
    ├─ Rebase onto main
    │   └─ Conflict? → EVICT (capture conflict context)
    │
    ├─ Run build + tests
    │   └─ Fail? → EVICT (capture test output)
    │
    └─ Pass → Fast-forward main, push, delete branch
```**文件重叠智能：**
- 非重叠单位投机地并行登陆
- 重叠的单位一一落地，每次都重新定位

**驱逐恢复：**
当被驱逐时，完整的上下文被捕获（冲突文件、差异、测试输出）并在下一个 Ralph 传递中反馈给实现者：```markdown
## MERGE CONFLICT — RESOLVE BEFORE NEXT LANDING

Your previous implementation conflicted with another unit that landed first.
Restructure your changes to avoid the conflicting files/lines below.

{full eviction context with diffs}
```### 阶段之间的数据流```
research.contextFilePath ──────────────────→ plan
plan.implementationSteps ──────────────────→ implement
implement.{filesCreated, whatWasDone} ─────→ test, reviews
test.failingSummary ───────────────────────→ reviews, implement (next pass)
reviews.{feedback, issues} ────────────────→ review-fix → implement (next pass)
final-review.reasoning ────────────────────→ implement (next pass)
evictionContext ───────────────────────────→ implement (after merge conflict)
```### 工作树隔离

每个单元都在一个独立的工作树中运行（使用 jj/Jujutsu，而不是 git）：```
/tmp/workflow-wt-{unit-id}/
```同一单元的管道阶段**共享**工作树，在研究→计划→实施→测试→审查之间保留状态（上下文文件、计划文件、代码更改）。

### 关键设计原则

1. **确定性执行** - 预先分解锁定并行性和顺序
2. **杠杆点的人工审查** — 工作计划是单一最高杠杆干预点
3. **单独的关注点** - 每个阶段都在一个单独的上下文窗口中，具有单独的代理
4. **与上下文的冲突恢复** - 完全驱逐上下文可以实现智能重新运行，而不是盲目重试
5. **层级驱动的深度**——琐碎的改变跳过研究/审查；大的变化得到最大程度的审查
6. **可恢复工作流程** — 完整状态保存到 SQLite；从任意点恢复

### 何时使用 Ralphinho 与更简单的模式

|信号|使用拉尔菲尼奥 |使用更简单的模式 |
|--------|--------------|--------------------|
|多个相互依赖的工作单位|是的 |没有 |
|需要并行实施 |是的 |没有 |
|可能发生合并冲突 |是的 |否（顺序即可）|
|单文件更改 |没有 |是（顺序管道）|
|多日项目 |是的 |也许（连续克劳德）|
|规范/RFC 已编写 |是的 |也许|
|快速迭代一件事 |没有 |是（NanoClaw 或管道）|

---

## 选择正确的模式

### 决策矩阵```
Is the task a single focused change?
├─ Yes → Sequential Pipeline or NanoClaw
└─ No → Is there a written spec/RFC?
         ├─ Yes → Do you need parallel implementation?
         │        ├─ Yes → Ralphinho (DAG orchestration)
         │        └─ No → Continuous Claude (iterative PR loop)
         └─ No → Do you need many variations of the same thing?
                  ├─ Yes → Infinite Agentic Loop (spec-driven generation)
                  └─ No → Sequential Pipeline with de-sloppify
```### 组合模式

这些模式组合得很好：

1. **顺序流水线 + De-Sloppify** — 最常见的组合。每个实施步骤都会获得清理通行证。

2. **连续 Claude + De-Sloppify** — 在每次迭代中添加带有 de-sloppify 指令的 `--review-prompt`。

3. **任意循环 + 验证** — 使用 ECC 的 `/verify` 命令或 `verification-loop` 技能作为提交之前的关卡。

4. **Ralphinho 在更简单循环中的分层方法** — 即使在顺序管道中，您也可以将简单任务路由到 Haiku，将复杂任务路由到 Opus：```bash
   # Simple formatting fix
   claude -p --model haiku "Fix the import ordering in src/utils.ts"

   # Complex architectural change
   claude -p --model opus "Refactor the auth module to use the strategy pattern"
   ```---

## 反模式

### 常见错误

1. **无退出条件的无限循环** — 始终具有最大运行次数、最大成本、最大持续时间或完成信号。

2. **迭代之间没有上下文桥梁** — 每个“claude -p”调用都是全新开始的。使用“SHARED_TASK_NOTES.md”或文件系统状态来桥接上下文。

3. **重试相同的失败** — 如果迭代失败，不要只是重试。捕获错误上下文并将其提供给下一次尝试。

4. **用否定指令代替清理通行证** — 不要说“不要做 X”。添加一个单独的通道来删除 X。

5. **一个上下文窗口中的所有代理** — 对于复杂的工作流程，将关注点分离到不同的代理进程中。审稿人永远不应该是作者。

6. **忽略并行工作中的文件重叠** — 如果两个并行代理可能编辑同一个文件，则需要合并策略（顺序登陆、变基或冲突解决）。

---

## 参考文献

|项目|作者 |链接 |
|---------|--------|------|
|拉尔菲尼奥 |埃尼特拉特 |信用：@enitrat |
|无限代理循环 |迪斯勒 |信用：@disler |
|连续克劳德|阿南德·乔杜里 |信用：@AnandChowdhary |
|纳米爪 | ECC |此存储库中的“/claw”命令 |
|验证循环| ECC |此存储库中的“技能/验证循环/” |