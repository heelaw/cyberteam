# Q3: Agent 与 Skill 的调用关系

**问题**: 那么他们做这些 Agent 的话，Agent 是否可以调用里边的，就 Agent 是否跟 Skill 可以存在着调用关系？就比如说 Agent 负责判断，负责逻辑处理，然后 Skill 负责具体的一些方法论，把它给处理，然后信息处理，然后 Agent 是作为一个编排。

---

## 一、核心结论：Agent 调用 Skill 是标准模式

**Agent 是"编排者"，Skill 是"执行者"**。这是 Multi-Agent 系统的标准分工：

```
┌─────────────────────────────────────────────────────┐
│                    Agent（编排者）                      │
│  ┌─────────────────────────────────────────────┐   │
│  │ 1. 理解任务意图（Intent Gate）                  │   │
│  │ 2. 规划执行路径                               │   │
│  │ 3. 判断调用哪个 Skill                          │   │
│  │ 4. 组装上下文                                 │   │
│  │ 5. 验证 Skill 输出质量                         │   │
│  └─────────────────────────────────────────────┘   │
│                         │                            │
│                    调用 Skill                        │
│                         ▼                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │ Skill A  │  │ Skill B  │  │ Skill C  │         │
│  │ 数据提取  │  │ 模板生成  │  │ 格式校验  │         │
│  └──────────┘  └──────────┘  └──────────┘         │
└─────────────────────────────────────────────────────┘
```

---

## 二、调用关系模式

### 模式1：Task 委托模式（oh-my-openagent-dev）

```typescript
// Agent 调用 Skill 的标准方式
task(category="visual-engineering", load_skills=["frontend-ui-ux"], prompt="...")

// Skill 提供领域知识
// Category 提供执行框架
// Agent 负责判断和组装
```

**流程**：
```
用户请求
    │
    ▼
Agent（意图理解）→ 确定需要的 Skill 组合
    │
    ├──▶ Skill A（数据提取）
    │         │
    │         ▼
    │    结果返回 Agent
    │
    ├──▶ Skill B（模板生成）
    │         │
    │         ▼
    │    结果返回 Agent
    │
    ▼
Agent（结果组装）→ 最终输出
```

---

### 模式2：Pipeline 模式（agency-agents）

```
PM Agent → Architect Agent → [Dev Agent ↔ QA Agent] → Release Agent
              │                    │
              │         ┌──────────┴──────────┐
              │         ▼                      ▼
              │    Skill A                 Skill B
              │   （详细设计）              （测试用例）
```

**特点**：
- 每个 Agent 调用特定领域的 Skill
- Agent 之间通过 Handoff 传递上下文
- Skill 是原子级执行单元

---

### 模式3：顺序编排模式（gstack）

```
/office-hours ──▶ 设计文档 ──▶ /plan-ceo-review ──▶ /plan-eng-review
                                                        │
                          /design-consultation ─────────┤
                                                        ▼
/review ◀── PR 准备 ◀── /qa ──────────────────────▶ /ship
     │              │                                    │
     │              ▼                                    ▼
     └─────── Bug 修复循环 ──────────────────────→ 测试通过 → 发布
```

**每个 Agent 实际调用了多个 Skill**：
- `/review` Agent 调用：代码审查 Skill、安全检查 Skill
- `/qa` Agent 调用：测试用例 Skill、回归测试 Skill
- `/ship` Agent 调用：部署 Skill、文档 Skill

---

### 模式4：工具注册模式（OpenViking）

```python
# Skill 被注册为 Agent 的工具
class ToolRegistry:
    register(skill)           # Skill 注册为工具
    execute(name, params)     # Agent 调用 Skill
    get_definitions()         # 导出 OpenAI 格式 schema
```

**Agent 的工具列表**：
```yaml
# Agent 定义中可以声明可用的 Skill/工具
---
name: viking-agent
tools:
  - read_file
  - write_file
  - ov-search-context    # Skill 作为工具
  - ov-add-data          # Skill 作为工具
---
```

---

## 三、Agent 调用 Skill 的实现方式

### 方式1：通过 load_skills 参数

```typescript
// oh-my-openagent-dev
task(
  category="deep",
  load_skills=["mvp-design", "user-research"],
  prompt="设计一个电商 MVP"
)
```

### 方式2：通过 Skill 路由表

```markdown
## Agent 内部路由

| 任务类型 | 调用的 Skill |
|----------|-------------|
| 需要数据提取 | `data-extraction-skill` |
| 需要文案生成 | `copywriting-skill` |
| 需要代码审查 | `code-review-skill` |
| 需要用户研究 | `user-research-skill` |
```

### 方式3：通过 MCP 协议

```yaml
# Skill 内嵌 MCP 配置
---
name: github-integration
mcp:
  - name: github-mcp
    type: stdio
    command: npx
    args: [-y, @modelcontextprotocol/server-github]
---

# Agent 通过 MCP 调用 Skill
```

---

## 四、Skill 在编排中的角色

### Skill 作为"方法论封装"

| 维度 | Agent 负责 | Skill 负责 |
|------|-----------|-----------|
| **判断** | ✅ 意图理解、路由决策 | ❌ |
| **规划** | ✅ 任务拆解、流程编排 | ❌ |
| **执行** | ❌ | ✅ 具体方法论实施 |
| **质量** | ✅ 结果验证、质量门禁 | ❌ |
| **记忆** | ✅ 跨 Skill 状态管理 | ❌ |

### Skill 的特征（适合被 Agent 调用）

1. **原子性** - 单一职责，可独立执行
2. **无状态** - 不依赖 Agent 的记忆
3. **标准化输入/输出** - 接口清晰
4. **可组合** - 多个 Skill 可串联执行

---

## 五、实际架构示例

### 示例：增长策略 Agent

```
┌─────────────────────────────────────────────────────────────┐
│              增长策略 Agent（编排者）                            │
│                                                              │
│  理解意图：用户想要"提升 DAU"                                    │
│                                                              │
│  规划路径：                                                   │
│    1. 先用 user-research-skill 了解用户画像                    │
│    2. 再用 aarrr-analysis-skill 做增长分析                     │
│    3. 然后用 ice-scoring-skill 排序解决方案                     │
│    4. 最后用 growth-plan-skill 生成具体计划                    │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ user-research │    │ aarrr-analysis│    │ ice-scoring  │
│ Skill         │    │ Skill         │    │ Skill        │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
    用户数据              增长漏斗              优先级排序
    报告                   报告                  列表
```

---

## 六、总结

| 问题 | 答案 |
|------|------|
| Agent 可以调用 Skill 吗？ | ✅ 是，这是标准架构模式 |
| Agent 和 Skill 的分工？ | Agent 负责判断/规划，Skill 负责执行 |
| Skill 是什么样的？ | 原子性、无状态、可组合的方法论单元 |
| Agent 如何知道调用哪个 Skill？ | 通过路由表、Category、或意图理解 |
| Skill 能调用 Agent 吗？ | 一般不，Skill 是执行单元，不是编排单元 |

**核心原则**：
- **Agent = 编排 + 判断 + 质量门禁**
- **Skill = 原子执行 + 方法论封装**
- **Agent 调用 Skill，Skill 不调用 Agent**

---

**研究日期**: 2026-03-20
**来源**: oh-my-openagent-dev, agency-agents, gstack, OpenViking
