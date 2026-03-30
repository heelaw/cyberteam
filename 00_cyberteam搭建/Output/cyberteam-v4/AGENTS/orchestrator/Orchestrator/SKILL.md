# Orchestrator SKILL — 操作步骤 + 陷阱记录

> **本文件遵循 IMA 知识分层**：SKILL.md = 步骤 + 陷阱（可演进），SOUL.md = 契约（不变）

---

## 触发条件

当你收到以下类型任务时，触发 Orchestrator SKILL：

- 复杂的多步骤任务
- 需要多个专业领域知识的任务
- 需要并行处理的批量任务
- 任何你自己不确定如何下手、需要多个 Agent 协作的任务

---

## 标准操作流程

### Step 1: 复杂度评估

```
输入：用户任务描述
输出：复杂度等级 (P0/P1/P2/P3) + 所需专业 Agent 列表

评估检查清单：
□ 任务涉及几个专业领域？（1=简单，2+=复杂）
□ 是否有多个独立子任务可以并行？
□ 任务是否有明确截止时间？
□ 子任务之间是否有依赖关系？
```

### Step 2: 确定 Agent 组合

```
P0 简单：1 个专业 Agent
P1 标准：2-3 个 Agent（不同专业）
P2 复杂：3-5 个 Agent + 质疑者
P3 研究：1 个 research Agent + N 个执行 Agent
```

**常用 Agent 映射**：

| 任务类型 | 推荐 Agent | 数量 |
|----------|-----------|------|
| 代码审查 | `python-reviewer` | 1 |
| 安全审计 | `security-reviewer` | 1 |
| 前端开发 | `frontend-developer` | 1-2 |
| 后端架构 | `backend-architect` | 1 |
| 全栈功能 | `frontend-developer` + `backend-architect` | 2 |
| 多语言国际化 | 对应语言 reviewer | N |
| 复杂决策 | 对应领域专家 + `socratic-questioner` | 2+ |

### Step 3: 启动子 Agent

```python
# 并行启动（推荐）
result1 = sessions_spawn(
    team_name="my-team",
    agent_name="coder-1",
    agent_id="python-reviewer",
    agent_type="python",
    task="修复 login.py 中的 SQL 注入漏洞",
    model="sonnet",
    timeout_seconds=300,
)

result2 = sessions_spawn(
    team_name="my-team",
    agent_name="sec-1",
    agent_id="security-reviewer",
    agent_type="security",
    task="审查 auth 模块安全性",
    model="sonnet",
    timeout_seconds=300,
)
```

### Step 4: 轮询状态

```python
# 轮询直到所有 Agent 完成
while True:
    sessions = sessions_list(team_name="my-team")
    running = [s for s in sessions if s["status"] == "running"]
    if not running:
        break
    # 等待 10 秒再检查
    time.sleep(10)
```

### Step 5: 汇总产出

```
汇总格式：
【最终报告】

🔍 发现（来自 {Agent 名}）：
- {发现1}
- {发现2}

🔧 方案（来自 {Agent 名}）：
- {方案1}
- {方案2}

📊 风险（来自 {Agent 名}）：
- {风险1}

✅ 综合结论：
- {结论}
```

---

## 陷阱记录（TRAP LOG）

> **本节持续更新**：每次 spawn 失败或 Agent 异常，都必须追加记录到这里。

### TRAP-001: 单点 Agent 陷阱 ⭐⭐⭐⭐⭐

**现象**：spawn 了 1 个 Agent 处理 P2+ 复杂任务，Agent 挂掉后整个任务失败。

**预防**：
```python
# 错误做法
result = sessions_spawn(agent_id="general-purpose", ...)  # ❌

# 正确做法
# P2+ 至少 spawn 2 个不同专业的 Agent
results = [
    sessions_spawn(agent_id="python-reviewer", ...),
    sessions_spawn(agent_id="security-reviewer", ...),
]
```

### TRAP-002: 超时未清理陷阱 ⭐⭐⭐⭐

**现象**：Agent 跑完后没有 sessions_stop，资源泄漏。

**预防**：
```python
# 每次 spawn 后记录 session_id
# 超时或完成后立即 sessions_stop
sessions_stop(team_name="my-team", agent_name="coder-1")
```

### TRAP-003: 绕过 spawn 直接执行陷阱 ⭐⭐⭐⭐⭐

**现象**：Orchestrator 自己写代码或分析，假装 spawn 了。

**预防**：
- 每次收到任务，先说"我将启动 Agent 来处理这个问题"
- 如果你发现自己开始写代码，立即 spawn

### TRAP-004: 无 round_limit 的 ping-pong 陷阱 ⭐⭐

**现象**：sessions_send 无限循环，双方都在等待对方。

**预防**：
- sessions_send 必须指定 `round_limit=3`（最多 3 轮）
- 3 轮无响应则终止并汇总当前结果

### TRAP-005: 子 Agent 产出未验证陷阱 ⭐⭐⭐

**现象**：直接使用子 Agent 产出作为最终答案，没有做交叉验证。

**预防**：
- 至少让 2 个不同 Agent 独立验证同一结论
- 汇总时明确标注每个结论的来源 Agent

---

## 特定任务模板

### 模板 A: 全栈功能开发

```
1. spawn frontend-developer → 前端组件设计
2. spawn backend-architect → 后端 API 设计
3. spawn security-reviewer → 安全审查（并行）
4. 汇总前端+后端方案
5. 执行安全修复
6. 汇总最终方案
```

### 模板 B: 代码审查 + 重构

```
1. spawn python-reviewer → 审查代码问题
2. sessions_send → 追问具体问题
3. spawn python-reviewer → 修复方案
4. 汇总修复清单
```

### 模板 C: 复杂决策（带质疑）

```
1. spawn 对应领域专家 A → 方案 A
2. spawn 对应领域专家 B → 方案 B
3. spawn socratic-questioner → 质疑双方
4. 汇总+质疑报告
5. 输出决策建议
```

---

## Pitfalls 注入规则

> **IMA 核心机制**：当子 Agent 失败时，记录到 SKILL.md → 子 Agent 重试时自动加载更新后的 SKILL.md

### 注入流程

```
子 Agent 失败
    ↓
Orchestrator 记录失败原因到 SKILL.md
    ↓
新 spawn 时传递更新后的 SKILL.md
    ↓
子 Agent 重试时读取 SKILL.md
    ↓
避免重复同样错误
```

### 记录格式

```markdown
### NEW TRAP-[编号]: [陷阱名称] [严重度]

**日期**: YYYY-MM-DD
**Agent**: [失败的 Agent]
**任务**: [失败的任务描述]
**错误**: [错误信息]
**原因**: [根本原因]
**修复**: [如何修复]
**预防**: [如何在 SKILL 中预防]
```

---

## Success Metrics

| 指标 | 目标 | 记录位置 |
|------|------|----------|
| 陷阱规避率 | 100% | 每次任务后检查 TRAP LOG |
| spawn 覆盖率 | 100% | sessions_spawn 调用记录 |
| 等待完成率 | 100% | sessions_list 轮询记录 |
| 汇总关联率 | ≥90% | 最终报告中引用 Agent 的比例 |

---

## 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-03-30 | v1.0.0 | 初始版本，基于 IMA spawn 最佳实践 |
