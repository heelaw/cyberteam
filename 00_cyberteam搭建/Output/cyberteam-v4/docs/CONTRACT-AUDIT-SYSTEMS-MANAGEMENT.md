# 系统与管理 Agent 契约审查报告

> 审查者：system-patterns | 日期：2026-04-01 | 团队：insight-council-audit
> 方法：goal-driven pseudocode 循环分析

---

## 执行摘要

使用 `while unresolved { 找缺失步骤/停止条件/边界/模型库连接 → 形成最小 scaffold → 指出误用风险 → 验证是否能落地 → 继续补洞 }` 进行系统性审查。

**结论**：核心引擎层（Orchestrator、Socratic Questioner）契约扎实，但 BG 层（Finance、Product、Growth）和 Middle-Tier 存在系统性缺失，存在 **11 个高危缺口**，其中 **3 个可能导致系统性误用**。

---

## 现有缺口（按严重度排序）

### G1 [CRITICAL] Thinking Router 存在但 Orchestrator 不使用

**现状**：
- `engine/thinking/router.py` 有完整的 8 类意图→思维模型路由逻辑
- `engine/thinking/router.py:18` 定义了 INTENT_TRIGGER_RULES 映射（数据分析/内容运营/技术研发/安全合规/战略规划/人力资源/运营支持/财务投资）
- Orchestrator SKILL.md 完全没有提及 ThinkingRouter
- Orchestrator 的"任务复杂度评估"表只有 P0-P3 时间维，没有模型选择维度

**误用风险**：
```
风险：Orchestrator spawn 子 Agent 时不过 ThinkingRouter，
      导致 94 个思维模型被静默跳过。
      整个"思维注入"卖点变成装饰性文档。
```

**最小 scaffold**：
```python
# 在 Orchestrator SKILL.md 的 Step 1: 复杂度评估 后追加：

### Step 1.5: 思维模型路由（强制）

context = TaskContext(
    intent=classify_intent(user_task),  # 8 类意图
    complexity=assess_complexity(user_task),  # P0-P3
    task_description=user_task
)
routing_result = thinking_router.route(context)

# 必须在 spawn 时将 routing_result.combination 注入子 Agent 的 system prompt
for agent in selected_agents:
    agent.system_prompt += f"\n\n# 思维模型\n{routing_result.combination.to_prompt()}"
```

**最小改法**：
1. 在 `AGENTS/orchestrator/Orchestrator/SKILL.md` 的 Step 1 和 Step 2 之间增加 Step 1.5
2. 在 spawn 调用前，增加 `thinking_router.route()` 调用并注入结果

---

### G2 [CRITICAL] BG Agents 无 SKILL.md，只有 AGENT.md + SOUL.md

**现状**：
- Orchestrator：有 AGENT.md + SOUL.md + SKILL.md（三层完整）
- Socratic Questioner：有 AGENT.md + SOUL.md + 质疑清单（功能完整）
- Finance Agent：有 AGENT.md + SOUL.md，**无 SKILL.md**
- Product Agent：有 AGENT.md + SOUL.md，**无 SKILL.md**
- Growth Agent：有 AGENT.md + SOUL.md，**无 SKILL.md**

**后果**：
- Trap Log 机制只存在于 Orchestrator SKILL.md，BG Agents 没有记录陷阱的能力
- BG Agents 被 spawn 时没有"操作步骤"可循，只有角色定义

**最小 scaffold**（以 Finance 为例）：
```markdown
# SKILL.md - 财务模型Agent

## 触发条件
- 用户提到："UE模型"、"LTV"、"CAC"、"利润结构"、"财务报表"

## 标准操作步骤

### Step 1: 信息确认
□ 是否已获取收入数据？
□ 是否已获取成本数据？
□ 数据时间范围是否明确？

### Step 2: 分析选择
- UE模型 → 调用 UE_SKILL
- 利润结构 → 调用 PROFIT_SKILL
- 财务报表 → 调用 FS_SKILL

### Step 3: 输出标准
[见输出格式节]

## Trap Log
[空，待填充]
```

**最小改法**：
为每个 BG Agent 补充 SKILL.md，重点：
- 触发条件（哪些关键词激活此 Agent）
- 标准操作步骤（IMA 分层）
- 输出 schema
- Trap Log 起始节

---

### G3 [HIGH] Handoff Protocol 代码存在但 Agent 契约不声明

**现状**：
- `cyberteam/transport/handoff_protocol.py`：完整的 HandoffProtocol 类（状态机、7 种状态）
- `engine/department/handoff.py`：HandoffStateMachine（IDLE→PENDING→ACTIVE→COMPLETED）
- **但**：没有任何 Agent AGENT.md 声明"我使用 HandoffProtocol"
- Orchestrator SOUL.md 说"汇总产出"，没说"通过 HandoffProtocol 交接"

**后果**：
- 两个 Handoff 实现无人调用，实际是 dead code
- Agent 之间用非结构化消息传递，无交接保障

**最小 scaffold**：
在 Orchestrator AGENT.md 增加：
```markdown
## Handoff 声明

所有 Agent 间任务交接必须通过 HandoffProtocol：

- 发起方：调用 `handoff_protocol.initiate(from_agent, to_agent, task)`
- 接收方：调用 `handoff_protocol.accept(handoff_id)`
- 完成方：调用 `handoff_protocol.complete(handoff_id, result)`

禁止：直接通过消息传递任务而不走 HandoffProtocol。
```

---

### G4 [HIGH] Orchestrator 引用 sessions_spawn 但这是 pseudocode

**现状**：
- Orchestrator SKILL.md 的 spawn 示例使用 `sessions_spawn()`, `sessions_list()` 等
- 这些是 **文档级 pseudocode**，不是真实 tool name
- 实际代码在 `cyberteam/spawn/sessions.py` 但没有导出的统一接口

**后果**：
```
误用场景：开发者看到 SKILL.md 的 sessions_spawn 示例，
         以为这是可调用的 tool，复制使用后系统不响应。
```

**最小 scaffold**：
```markdown
## 工具调用说明

> ⚠️ 以下为 pseudocode 示例，实际 tool 调用通过 ClawTeam MCP 协议。

伪代码示例（不可直接使用）：
```python
sessions_spawn(...)  # 不是真实 tool
sessions_send(...)
sessions_list(...)
```

真实调用：通过 `clawteam spawn` CLI 命令或 Agent runtime API。
详见 `cyberteam/spawn/` 模块。
```

---

### G5 [HIGH] Middle-Tier Agents 全是 Placeholder

**现状**：
- `AGENTS/middle-tier/agent-test-3.md`：几乎所有字段为空
- `AGENTS/middle-tier/` 目录下无任何实现的 agent 代码
- 架构图将 middle-tier 列为独立层，但实际是空的

**后果**：
- 整个"中台服务"层是 phantom architecture
- Thinking/Memory/Monitoring/Communication 中台能力没有载体

**最小 scaffold**：
```
路径：AGENTS/middle-tier/

├── thinking/         # 思维注入中台
│   └── THOUGHT_MIDDLE.py   # 封装 engine/thinking 的 API
├── memory/           # 记忆存储中台
│   └── MEMORY_MIDDLE.py   # 标准化 memory 读写协议
├── monitoring/       # 监控中台
│   └── MONITOR_MIDDLE.py  # 进度/异常监控
└── communication/    # 通信中台
    └── COMM_MIDDLE.py     # Agent 间消息路由

每个 middle agent 必须有：
- AGENT.md（最小定义）
- SOUL.md（Voice 灵魂）
- PROTOCOL.md（暴露的接口契约）
```

---

### G6 [MEDIUM] Trap Log 写后不读

**现状**：
- Orchestrator SKILL.md 有详细的 TRAP-001 到 TRAP-005 记录
- 规则说"子 Agent 失败时记录到 SKILL.md → 子 Agent 重试时自动加载更新后的 SKILL.md"
- **但没有任何机制确保这一点**：
  - 没有验证脚本
  - 没有重试时读取 SKILL.md 的代码路径
  - Trap Log 条目没有编号递增规则

**后果**：
- Trap Log 变成 human-only备忘录，不是系统级 enforcement
- 同一错误会被重复犯，因为没有自动检查

**最小 scaffold**：
```python
# 在 spawn 前验证 trap 的检查点：
def check_traps_before_spawn(agent_id: str, task: str) -> list[str]:
    """读取 SKILL.md，返回需要规避的 trap 列表"""
    traps = parse_trap_log(f"AGENTS/{agent_id}/SKILL.md")
    active_traps = [t for t in traps if t.status == "active"]
    relevant = [t for t in active_traps if t.task_type in task]
    return relevant

# spawn 时必须传入：
spawn(agent_id, task, traps=check_traps_before_spawn(agent_id, task))
```

---

### G7 [MEDIUM] 输出 schema 不标准

**现状**：
- Orchestrator SOUL.md 定义了"合格输出"示例（带 ✅ 和 🔗 符号的格式）
- 但没有定义结构化 schema
- 每个 BG Agent 输出格式各异（Finance 用表格，Growth 用 Markdown 结构）

**后果**：
- Orchestrator 汇总时无法做结构化比对
- "有机关联"变成格式美化，不是语义关联

**最小 scaffold**：
```json
{
  "agent_output": {
    "agent_id": "string",
    "agent_type": "string",
    "findings": ["string"],
    "recommendations": ["string"],
    "risks": ["string"],
    "confidence": "float 0-1",
    "evidence": [{"source": "string", "quote": "string"}],
    "limitations": ["string"]
  }
}
```

---

### G8 [MEDIUM] 8 类意图 vs 94 个思维模型映射缺失文档

**现状**：
- `engine/thinking/router.py` 有 INTENT_TRIGGER_RULES（8 类意图）
- `engine/thinking/models.py` 声明有 94 个思维模型
- 意图到模型的映射规则存在于代码中，但没有在 Agent 契约中暴露

**后果**：
- Agent 不知道什么场景用什么思维模型
- 94 个模型变成数字游戏，不是可执行工具

---

### G9 [LOW] Orchestrator 决策树 fuzzy边界

**现状**：
- "迭代"和"复杂"任务边界模糊（都是多 Agent）
- "最多 3 轮后强制汇总"没有定义"轮"是什么（一次 spawn=1 轮？还是一次 send=1 轮？）
- "未知"任务类型没有明确识别标准

**后果**：
- 同一个任务可能被不同 Orchestrator 实例归类到不同分支
- "3 轮"限制可能轻易被绕过（不同轮次混合任务）

---

### G10 [LOW] RBAC 存在于 engine 但 Agent 不声明权限

**现状**：
- `engine/rbac.py` 存在
- Agent AGENT.md 没有声明自己的权限边界
- 没有 Agent 级别的权限矩阵

---

### G11 [LOW] Memory Layer 无 schema

**现状**：
- Orchestrator SKILL.md 说"必须记录到 memory/"
- "memory/" 目录存在但无 schema 定义
- 没有定义什么要记录、什么不要记录

---

## 最小改法优先级矩阵

| 优先级 | 缺口 | 改法 | 工作量 |
|--------|------|------|--------|
| P0 | G1 Thinking Router | Orchestrator SKILL.md 增加 Step 1.5 | 1 hr |
| P0 | G4 spawn pseudocode | AGENT.md 增加 tool 调用说明节 | 30 min |
| P1 | G2 BG Agents SKILL | 为 3 个 BG Agent 各补充 SKILL.md | 3 hr |
| P1 | G3 Handoff 集成 | Orchestrator AGENT.md 增加 Handoff 声明 | 1 hr |
| P1 | G5 Middle-Tier | 删除或补充 agent-test-3.md | 1 hr |
| P2 | G6 Trap 自动检查 | 在 spawn 逻辑中增加 trap 检查调用 | 2 hr |
| P2 | G7 输出 schema | 定义 JSON schema 并分发到所有 AGENT.md | 2 hr |

---

## 验证检查清单

- [ ] G1: ThinkingRouter.route() 在 spawn 前被调用
- [ ] G2: Finance/Product/Growth 都有 SKILL.md
- [ ] G3: HandoffProtocol.initiate() 在 Agent 间调用
- [ ] G4: SKILL.md 清楚标注 pseudocode vs real code
- [ ] G5: middle-tier/ 下无空 placeholder
- [ ] G6: Trap Log 在重试时被读取
- [ ] G7: Agent 输出符合标准 schema
