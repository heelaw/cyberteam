# Q4: Agent 的调用机制与精确路由

**问题**: 那么 Agent 平常都是怎么被调用的呢？然后怎么才能确保它的调用是精确的呢？详细地跟我说一下，这些 GitHub 仓库上的这些 Agent，他们的体系里边到底都是怎样一个调用逻辑？

---

## 一、Agent 调用的核心机制

### 1.1 三种调用方式

| 方式 | 触发 | 代表 |
|------|------|------|
| **Slash Command** | `/agent-name` | gstack, agency-agents |
| **Intent Routing** | 自然语言意图分析 | oh-my-openagent-dev (Intent Gate) |
| **Category Delegation** | `task(category, prompt)` | oh-my-openagent-dev |

---

## 二、精确路由的四大机制

### 机制1：Intent Gate（意图门控）

**来源**: oh-my-openagent-dev (Sisyphus Agent)

```markdown
## Phase 0 - Intent Gate（每个消息都执行）

| Surface Form    | True Intent     | Your Routing        |
|-----------------|-----------------|---------------------|
| "explain X"     | Research        | explore/librarian   |
| "implement X"   | Implementation  | plan → delegate     |
| "fix Y"         | Fix needed      | diagnose → fix      |
| "review PR #42" | Review          | /review             |
| "test this"     | QA needed       | /qa                 |
```

**工作原理**：
1. 用户输入 → Intent Gate 分析真实意图
2. 意图 → 路由表 → 选择合适的 Agent
3. **避免字面执行**，而是理解背后意图

---

### 机制2：Trigger Keywords（触发关键词）

**来源**: claude-skills, awesome-claude-skills

```yaml
---
name: code-review
description: Use when encountering errors or unexpected behavior
triggers: debug, error, bug, exception, traceback, troubleshoot
---
```

**触发逻辑**：
```python
# 伪代码
if user_prompt contains any(trigger_keywords):
    activate_skill()
```

**精确性保证**：
- 关键词精确匹配
- 多关键词组合（OR 逻辑）
- 关键词按场景分组（debug/error/bug 是同一类）

---

### 机制3：Category + Skill 委托

**来源**: oh-my-openagent-dev

```typescript
// Category 定义（语义分类，而非具体模型）
const DEFAULT_CATEGORIES = {
  "visual-engineering": {
    model: "google/gemini-3.1-pro",
    variant: "high",
    prompt_append: "<Category_Context>你是视觉工程师...</Category_Context>"
  },
  "ultrabrain": {
    model: "openai/gpt-5.3-codex",
    variant: "xhigh"
  },
  "deep": { model: "openai/gpt-5.3-codex", variant: "medium" },
  "quick": { model: "anthropic/claude-haiku-4-5" }
}

// Agent 调用
task(
  category="visual-engineering",  // 语义路由
  load_skills=["frontend-ui-ux"],
  prompt="设计一个登录页面"
)
```

**精确性保证**：
- Category 是语义级别（视觉/深度/快速）
- Skill 是领域级别（前端UI/后端架构）
- 两者组合实现精确路由

---

### 机制4：Multi-Agent Orchestrator

**来源**: agency-agents (agents-orchestrator.md)

```markdown
# Orchestrator 路由决策

## 任务类型识别
1. 产品需求 → PM Agent
2. 架构设计 → Architect Agent
3. 开发实现 → Dev Agent
4. 测试验证 → QA Agent
5. 发布部署 → Release Agent

## 质量门禁
- [ ] PM → Architect（需求清晰度检查）
- [ ] Architect → Dev（架构完整性检查）
- [ ] Dev → QA（代码完整性检查）
- [ ] QA → Release（测试通过检查）
```

**精确性保证**：
- 每个阶段有明确的进入/退出标准
- 不满足标准则回退或修复
- 强制质量门禁防止错误传递

---

## 三、调用链路全景图

```
用户输入
    │
    ▼
┌─────────────────────────────────────────────────────┐
│                  Layer 1: Intent Gate                 │
│  理解真实意图（而非字面意思）                            │
│  - "解释X" → Research                                 │
│  - "实现X" → Implementation                           │
│  - "修复Y" → Fix                                      │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│                  Layer 2: Skill Matching              │
│  匹配触发关键词                                         │
│  - triggers: debug/error/bug → code-review-skill      │
│  - triggers: test/qa → testing-skill                 │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│                  Layer 3: Category Routing            │
│  语义分类路由                                           │
│  - visual-engineering → 前端Agent                    │
│  - deep → 深度推理Agent                               │
│  - quick → 快速响应Agent                              │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│                  Layer 4: Agent Selection             │
│  精确选择目标Agent                                      │
│  - Architect Agent（架构设计）                        │
│  - Dev Agent（开发实现）                               │
│  - QA Agent（测试验证）                               │
└─────────────────────────────────────────────────────┘
    │
    ▼
目标 Agent 执行
```

---

## 四、确保精确路由的关键设计

### 4.1 分层路由（防止误触发）

```python
# 多层过滤确保精确
def route_agent(user_input):
    # Layer 1: 关键词快速过滤
    if not has_trigger_keywords(user_input):
        return default_agent

    # Layer 2: 意图理解
    intent = analyze_intent(user_input)
    if intent == "research":
        return research_agent

    # Layer 3: 上下文确认
    if not has_required_context(user_input):
        return ask_for_clarification()

    # Layer 4: 最终路由
    return target_agent
```

---

### 4.2 置信度评分（gstack 模式）

```python
# 计算路由置信度
def calculate_confidence(user_input, agent_triggers):
    score = 0

    # 关键词匹配权重
    if any(keyword in user_input for keyword in agent_triggers):
        score += 0.3

    # 语义相似度权重
    similarity = semantic_similarity(user_input, agent_description)
    score += similarity * 0.5

    # 上下文匹配权重
    if has_relevant_context(user_input, agent_context):
        score += 0.2

    # 低于阈值则询问确认
    if score < 0.7:
        return ask_user_confirmation()

    return agent
```

---

### 4.3 Fallback 机制（防止无响应）

```python
# 路由失败时的降级策略
def route_with_fallback(user_input):
    try:
        # 尝试精确路由
        agent = intent_gate(user_input)
        if agent:
            return agent
    except Exception as e:
        log_error(e)

    # 降级到通用路由
    general_agent = route_by_keywords(user_input)
    if general_agent:
        return general_agent

    # 最终降级到默认 Agent
    return default_agent
```

---

### 4.4 主动确认机制（关键决策）

```markdown
# 当路由不确定时主动询问
## 不确定的情况
- 多个 Agent 置信度相近（差值 < 0.15）
- 缺少必要上下文
- 可能造成破坏性操作

## 询问格式
> 我检测到你想要 [操作]，但这可能涉及 [风险]。
>
> 请确认：
> 1. 使用 [Agent A] - [描述]
> 2. 使用 [Agent B] - [描述]
> 3. 让我自主决定
```

---

## 五、各仓库的调用体系对比

| 仓库 | 调用方式 | 精确性保证 | 适用场景 |
|------|----------|-----------|----------|
| **oh-my-openagent-dev** | Intent Gate + Category | 4层过滤（意图→关键词→语义→Agent） | 复杂任务编排 |
| **gstack** | Slash Command + 置信度 | 分数阈值 + 主动确认 | CLI 工具链 |
| **claude-skills** | Trigger Keywords | 多关键词组合 + 领域分类 | 技能自动激活 |
| **agency-agents** | Orchestrator | 质量门禁 + Handoff 标签 | 多 Agent 流水线 |
| **OpenViking** | Skill Loader | L0/L1/L2 渐进式加载 | 聊天机器人 |

---

## 六、最佳实践总结

### 确保精确路由的 5 条规则

1. **永远不要只依赖关键词** - 关键词 + 意图理解 + 上下文
2. **设置置信度阈值** - 低于阈值主动询问确认
3. **提供清晰的错误回退** - 路由失败时有明确的降级路径
4. **使用分层路由** - 从快速过滤到精确路由，节省计算
5. **记录路由决策** - 便于调试和优化路由规则

---

## 七、实际调用流程示例

### 示例：用户说 "我的登录有问题"

```
输入: "我的登录有问题"
    │
    ▼
Intent Gate 分析
    ├─ 表面形式: "有问题"
    ├─ 真实意图: 需要诊断和修复
    └─ 路由决策: diagnose → fix
    │
    ▼
关键词匹配
    ├─ "问题" → problem/troubleshoot
    ├─ "登录" → auth/login
    └─ 匹配 Skill: authentication-debug
    │
    ▼
Category 分类
    └─ 需要诊断 → category="deep"
    │
    ▼
Agent 选择
    └─ Backend Architect（有认证调试能力）
    │
    ▼
执行流程
    1. Backend Architect 调用 authentication-debug Skill
    2. 收集日志和错误信息
    3. 诊断根因
    4. 生成修复方案
    5. 返回用户
```

---

## 八、总结

| 问题 | 答案 |
|------|------|
| Agent 怎么被调用？ | Slash Command、Intent Routing、Category Delegation |
| 如何确保精确？ | Intent Gate + 关键词 + Category + 置信度评分 |
| 调用失败怎么办？ | Fallback 机制 + 主动确认 |
| 最多几层路由？ | 通常 4 层：意图→关键词→语义→Agent |
| 哪种机制最精确？ | Intent Gate（oh-my-openagent-dev） |

**核心原则**：
- **永远不要猜测用户意图** - 不确定就问
- **多层过滤优于单一判断** - 逐级精确化
- **置信度阈值防止误触发** - 低于阈值主动确认

---

**研究日期**: 2026-03-20
**来源**: oh-my-openagent-dev, gstack, claude-skills, agency-agents, OpenViking
