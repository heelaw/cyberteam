# 架构决策记录

捕获编码会话期间发生的架构决策。这项技能不再只存在于 Slack 线程、PR 评论或某人的记忆中，而是生成与代码一起存在的结构化 ADR 文档。

## 何时激活

- 用户明确地说“让我们记录这个决定”或“ADR 这个”
- 用户在重要的替代方案（框架、库、模式、数据库、API 设计）之间进行选择
- 用户说“我们决定……”或“我们做 X 而不是 Y 的原因是……”
- 用户问“为什么我们选择 X？” （阅读现有的 ADR）
- 在规划阶段讨论架构权衡

## ADR 格式

使用 Michael Nygard 提出的轻量级 ADR 格式，适用于人工智能辅助开发：```markdown
# ADR-NNNN: [Decision Title]

**Date**: YYYY-MM-DD
**Status**: proposed | accepted | deprecated | superseded by ADR-NNNN
**Deciders**: [who was involved]

## Context

What is the issue that we're seeing that is motivating this decision or change?

[2-5 sentences describing the situation, constraints, and forces at play]

## Decision

What is the change that we're proposing and/or doing?

[1-3 sentences stating the decision clearly]

## Alternatives Considered

### Alternative 1: [Name]
- **Pros**: [benefits]
- **Cons**: [drawbacks]
- **Why not**: [specific reason this was rejected]

### Alternative 2: [Name]
- **Pros**: [benefits]
- **Cons**: [drawbacks]
- **Why not**: [specific reason this was rejected]

## Consequences

What becomes easier or more difficult to do because of this change?

### Positive
- [benefit 1]
- [benefit 2]

### Negative
- [trade-off 1]
- [trade-off 2]

### Risks
- [risk and mitigation]
```## 工作流程

### 捕获新的 ADR

当检测到决策时刻时：

1. **初始化（仅限第一次）** — 如果 `docs/adr/` 不存在，请在创建目录之前要求用户确认，创建一个包含索引表头的 `README.md`（请参阅下面的 ADR 索引格式），以及一个用于手动使用的空白 `template.md`。未经明确同意，请勿创建文件。
2. **确定决策** — 提取正在做出的核心架构选择
3. **收集背景** — 是什么问题导致了这个？存在哪些限制？
4. **记录替代方案** — 还考虑了哪些其他选项？他们为什么被拒绝？
5. **国家后果**——权衡是什么？什么变得更容易/更难？
6. **分配一个号码** — 扫描 `docs/adr/` 中的现有 ADR 并递增
7. **确认并撰写** — 将 ADR 草案提交给用户审核。仅在明确批准后才写入“docs/adr/NNNN-decision-title.md”。如果用户拒绝，则丢弃草稿而不写入任何文件。
8. **更新索引** — 附加到 `docs/adr/README.md`

### 阅读现有的 ADR

当用户问“为什么我们选择 X？”时：

1. 检查 `docs/adr/` 是否存在 - 如果不存在，请回答：“此项目中未找到 ADR。您想开始记录架构决策吗？”
2. 如果存在，则扫描 `docs/adr/README.md` 索引以查找相关条目
3. 阅读匹配的 ADR 文件并呈现上下文和决策部分
4. 如果未找到匹配项，请回复：“未找到该决定的 ADR。您想现在记录一个吗？”

### ADR 目录结构```
docs/
└── adr/
    ├── README.md              ← index of all ADRs
    ├── 0001-use-nextjs.md
    ├── 0002-postgres-over-mongo.md
    ├── 0003-rest-over-graphql.md
    └── template.md            ← blank template for manual use
```### ADR 指数格式```markdown
# Architecture Decision Records

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [0001](0001-use-nextjs.md) | Use Next.js as frontend framework | accepted | 2026-01-15 |
| [0002](0002-postgres-over-mongo.md) | PostgreSQL over MongoDB for primary datastore | accepted | 2026-01-20 |
| [0003](0003-rest-over-graphql.md) | REST API over GraphQL | accepted | 2026-02-01 |
```## Decision Detection Signals

Watch for these patterns in conversation that indicate an architectural decision:

**Explicit signals**
- "Let's go with X"
- "We should use X instead of Y"
- "The trade-off is worth it because..."
- "Record this as an ADR"

**Implicit signals** (suggest recording an ADR — do not auto-create without user confirmation)
- Comparing two frameworks or libraries and reaching a conclusion
- Making a database schema design choice with stated rationale
- Choosing between architectural patterns (monolith vs microservices, REST vs GraphQL)
- Deciding on authentication/authorization strategy
- Selecting deployment infrastructure after evaluating alternatives

## What Makes a Good ADR

### Do
- **Be specific** — "Use Prisma ORM" not "use an ORM"
- **Record the why** — the rationale matters more than the what
- **Include rejected alternatives** — future developers need to know what was considered
- **State consequences honestly** — every decision has trade-offs
- **Keep it short** — an ADR should be readable in 2 minutes
- **Use present tense** — "We use X" not "We will use X"

### Don't
- Record trivial decisions — variable naming or formatting choices don't need ADRs
- Write essays — if the context section exceeds 10 lines, it's too long
- Omit alternatives — "we just picked it" is not a valid rationale
- Backfill without marking it — if recording a past decision, note the original date
- Let ADRs go stale — superseded decisions should reference their replacement

## ADR Lifecycle```
proposed → accepted → [deprecated | superseded by ADR-NNNN]
```- **提议**：决定正在讨论中，尚未提交
- **接受**：决定生效并得到遵循
- **已弃用**：决策不再相关（例如，功能已删除）
- **被取代**：较新的 ADR 取代了该 ADR（始终链接替代品）

## 值得记录的决策类别

|类别 |示例 |
|----------|---------|
| **技术选择** |框架、语言、数据库、云提供商|
| **架构模式** |单体应用 vs 微服务、事件驱动、CQRS |
| **API设计** | REST 与 GraphQL、版本控制策略、身份验证机制 |
| **数据建模** |架构设计、规范化决策、缓存策略 |
| **基础设施** |部署模型、CI/CD 管道、监控堆栈 |
| **安全** |认证策略、加密方法、秘密管理 |
| **测试** |测试框架、覆盖目标、E2E 与集成平衡 |
| **流程** |分支策略、审核流程、发布节奏 |

## 与其他技能的整合

- **规划者代理**：当规划者提出架构变更时，建议创建ADR
- **代码审查代理**：标记引入架构更改但没有相应 ADR 的 PR