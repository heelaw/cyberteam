# Plan - 多模型协同规划

多模型协同规划——上下文检索+双模型分析→生成分步实施计划。

$参数

---

## 核心协议

- **语言协议**：与工具/模型交互时使用**英语**，用用户的语言与用户交流
- **强制并行**：Codex/Gemini 调用必须使用 `run_in_background: true` （包括单个模型调用，以避免阻塞主线程）
- **代码主权**：外部模型具有**零文件系统写入访问权限**，所有修改均由 Claude 进行
- **止损机制**：在验证当前阶段输出之前不要继续下一阶段
- **仅计划**：此命令允许读取上下文并写入`.claude/plan/*`计划文件，但**永远不要修改生产代码**

---

## 多模型调用规范

**调用语法**（并行：使用 `run_in_background: true`）：```
Bash({
  command: "~/.claude/bin/codeagent-wrapper {{LITE_MODE_FLAG}}--backend <codex|gemini> {{GEMINI_MODEL_FLAG}}- \"$PWD\" <<'EOF'
ROLE_FILE: <role prompt path>
<TASK>
Requirement: <enhanced requirement>
Context: <retrieved project context>
</TASK>
OUTPUT: Step-by-step implementation plan with pseudo-code. DO NOT modify any files.
EOF",
  run_in_background: true,
  timeout: 3600000,
  description: "Brief description"
})
```**型号参数备注**：
- `{{GEMINI_MODEL_FLAG}}`：使用`--backend gemini`时，替换为`--gemini-model gemini-3-pro-preview`（注意尾随空格）；使用空字符串作为法典

**角色提示**：

|相|法典|双子座|
|--------|--------|--------|
|分析| `~/.claude/.ccg/prompts/codex/analyzer.md` | `~/.claude/.ccg/prompts/gemini/analyzer.md` |
|规划| `~/.claude/.ccg/prompts/codex/architect.md` | `~/.claude/.ccg/prompts/gemini/architect.md` |

**会话重用**：每次调用都会返回`SESSION_ID: xxx`（通常由包装器输出），**必须保存**以供后续`/ccg:execute`使用。

**等待后台任务**（最大超时 600000 毫秒 = 10 分钟）：```
TaskOutput({ task_id: "<task_id>", block: true, timeout: 600000 })
```**重要**：
- 必须指定`timeout: 600000`，否则默认30秒会导致过早超时
- 如果 10 分钟后仍未完成，请继续使用“TaskOutput”进行轮询，**切勿终止进程**
- 如果由于超时而跳过等待，**必须调用`AskUserQuestion`来询问用户是否继续等待或终止任务**

---

## 执行工作流程

**规划任务**：$ARGUMENTS

### 第 1 阶段：完整上下文检索

`[模式：研究]`

#### 1.1 提示增强（必须先执行）

**如果 ace-tool MCP 可用**，调用 `mcp__ace-tool__enhance_prompt` 工具：```
mcp__ace-tool__enhance_prompt({
  prompt: "$ARGUMENTS",
  conversation_history: "<last 5-10 conversation turns>",
  project_root_path: "$PWD"
})
```等待增强提示，**将原始 $ARGUMENTS 替换为增强结果**以用于所有后续阶段。

**如果 ace-tool MCP 不可用**：跳过此步骤并在所有后续阶段按原样使用原始的“$ARGUMENTS”。

#### 1.2 上下文检索

**如果 ace-tool MCP 可用**，调用 `mcp__ace-tool__search_context` 工具：```
mcp__ace-tool__search_context({
  query: "<semantic query based on enhanced requirement>",
  project_root_path: "$PWD"
})
```- 使用自然语言构建语义查询（哪里/什么/如何）
- **永远不要基于假设回答**

**如果 ace-tool MCP 不可用**，请使用 Claude Code 内置工具作为后备：
1. **Glob**：按模式查找相关文件（例如`Glob("**/*.ts")`、`Glob("src/**/*.py")`）
2. **Grep**：搜索关键符号、函数名称、类定义（例如 `Grep("className|functionName")`）
3. **读取**：读取发现的文件以收集完整的上下文
4. **任务（探索代理）**：要进行更深入的探索，请使用“Task”和“subagent_type: "Explore"”在整个代码库中进行搜索

#### 1.3 完整性检查

- 必须获得相关类、函数、变量的**完整定义和签名**
- 如果上下文不足，触发**递归检索**
- 优先输出：入口文件+行号+关键符号名称；仅在必要时添加最少的代码片段以解决歧义

#### 1.4 需求调整

- 如果需求仍然不明确，**必须**为用户输出指导性问题
- 直到需求边界清晰（无遗漏、无冗余）

### 第二阶段：多模型协同分析

`[模式：分析]`

#### 2.1 分配输入

**并行调用** Codex 和 Gemini (`run_in_background: true`)：

将**原始需求**（无预设意见）分发给两个模型：

1. **法典后端分析**：
   - ROLE_FILE: `~/.claude/.ccg/prompts/codex/analyzer.md`
   - 重点：技术可行性、架构影响、性能考虑、潜在风险
   - 输出：多视角解决方案+优缺点分析

2. **Gemini前端分析**：
   - ROLE_FILE: `~/.claude/.ccg/prompts/gemini/analyzer.md`
   - 重点：UI/UX 影响、用户体验、视觉设计
   - 输出：多视角解决方案+优缺点分析

使用“TaskOutput”等待两个模型的完整结果。 **保存SESSION_ID**（`CODEX_SESSION`和`GEMINI_SESSION`）。

#### 2.2 交叉验证

整合视角并迭代优化：

1. **确定共识**（强信号）
2. **识别背离**（需要权衡）
3. **优势互补**：后端逻辑遵循Codex，前端设计遵循Gemini
4. **逻辑推理**：消除解决方案中的逻辑差距

#### 2.3（可选但推荐）双模型计划草案

为了减少克劳德综合计划中遗漏的风险，可以并行让两个模型输出“计划草案”（仍然**不允许**修改文件）：

1. **法典计划草案**（后端权威）：
   - ROLE_FILE: `~/.claude/.ccg/prompts/codex/architect.md`
   - 输出：分步计划+伪代码（重点：数据流/边缘情况/错误处理/测试策略）

2. **Gemini计划草案**（前端权威）：
   - ROLE_FILE: `~/.claude/.ccg/prompts/gemini/architect.md`
   - 输出：分步计划+伪代码（重点：信息架构/交互/可访问性/视觉一致性）

使用“TaskOutput”等待两个模型的完整结果，记录其建议中的关键差异。

#### 2.4 生成实施计划（克劳德最终版本）

综合这两种分析，生成**分步实施计划**：```markdown
## Implementation Plan: <Task Name>

### Task Type
- [ ] Frontend (→ Gemini)
- [ ] Backend (→ Codex)
- [ ] Fullstack (→ Parallel)

### Technical Solution
<Optimal solution synthesized from Codex + Gemini analysis>

### Implementation Steps
1. <Step 1> - Expected deliverable
2. <Step 2> - Expected deliverable
...

### Key Files
| File | Operation | Description |
|------|-----------|-------------|
| path/to/file.ts:L10-L50 | Modify | Description |

### Risks and Mitigation
| Risk | Mitigation |
|------|------------|

### SESSION_ID (for /ccg:execute use)
- CODEX_SESSION: <session_id>
- GEMINI_SESSION: <session_id>
```### 第 2 阶段结束：计划交付（而非执行）

**`/ccg:plan` 职责到此结束，必须执行以下操作**：

1. 向用户呈现完整的实施方案（包括伪代码）
2. 将计划保存到`.claude/plan/<feature-name>.md`（从需求中提取功能名称，例如`user-auth`、` payment-module`）
3.以**粗体文本**输出提示（必须使用实际保存的文件路径）：

   ---
   **生成计划并保存到 `.claude/plan/actual-feature-name.md`**

   **请查看上面的计划。您可以：**
   - **修改计划**：告诉我哪些需要调整，我会更新计划
   - **执行计划**：将以下命令复制到新会话中```
   /ccg:execute .claude/plan/actual-feature-name.md
   ```---

   **注意**：上面的 `actual-feature-name.md` 必须替换为实际保存的文件名！

4. **立即终止当前响应**（在此停止。不再调用工具。）

**绝对禁止**：
- 询问用户“Y/N”然后自动执行（执行是`/ccg:execute`的责任）
- 对生产代码的任何写入操作
- 自动调用 `/ccg:execute` 或任何执行操作
- 当用户未明确请求修改时继续触发模型调用

---

## 计划储蓄

计划完成后，将计划保存到：

- **第一次规划**：`.claude/plan/<feature-name>.md`
- **迭代版本**：`.claude/plan/<feature-name>-v2.md`、`.claude/plan/<feature-name>-v3.md`...

计划文件写入应在向用户呈现计划之前完成。

---

## 计划修改流程

如果用户请求修改计划：

1.根据用户反馈调整计划内容
2. 更新 `.claude/plan/<feature-name>.md` 文件
3.重新提出修改后的计划
4.提示用户重新查看或执行

---

## 后续步骤

用户批准后，**手动**执行：```bash
/ccg:execute .claude/plan/<feature-name>.md
```---

## 关键规则

1. **仅计划，无实施** – 该命令不执行任何代码更改
2. **无 Y/N 提示** – 仅呈现计划，让用户决定下一步
3. **信任规则** – 后端遵循 Codex，前端遵循 Gemini
4. 外部模型具有**零文件系统写入访问权限**
5. **SESSION_ID Handoff** – 计划必须在末尾包含 `CODEX_SESSION` / `GEMINI_SESSION` （供 `/ccg:executeresume <SESSION_ID>` 使用）