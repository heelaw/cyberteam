# 执行-多模型协同执行

多模型协同执行——从计划中获取原型→Claude重构并实现→多模型审核和交付。

$参数

---

## 核心协议

- **语言协议**：与工具/模型交互时使用**英语**，用用户的语言与用户交流
- **代码主权**：外部模型具有**零文件系统写入访问权限**，所有修改均由 Claude 进行
- **脏原型重构**：将 Codex/Gemini Unified Diff 视为“脏原型”，必须重构为生产级代码
- **止损机制**：在验证当前阶段输出之前不要继续下一阶段
- **先决条件**：仅在用户明确回复“Y”到`/ccg:plan`输出后执行（如果缺少，必须首先确认）

---

## 多模型调用规范

**调用语法**（并行：使用 `run_in_background: true`）：```
# Resume session call (recommended) - Implementation Prototype
Bash({
  command: "~/.claude/bin/codeagent-wrapper {{LITE_MODE_FLAG}}--backend <codex|gemini> {{GEMINI_MODEL_FLAG}}resume <SESSION_ID> - \"$PWD\" <<'EOF'
ROLE_FILE: <role prompt path>
<TASK>
Requirement: <task description>
Context: <plan content + target files>
</TASK>
OUTPUT: Unified Diff Patch ONLY. Strictly prohibit any actual modifications.
EOF",
  run_in_background: true,
  timeout: 3600000,
  description: "Brief description"
})

# New session call - Implementation Prototype
Bash({
  command: "~/.claude/bin/codeagent-wrapper {{LITE_MODE_FLAG}}--backend <codex|gemini> {{GEMINI_MODEL_FLAG}}- \"$PWD\" <<'EOF'
ROLE_FILE: <role prompt path>
<TASK>
Requirement: <task description>
Context: <plan content + target files>
</TASK>
OUTPUT: Unified Diff Patch ONLY. Strictly prohibit any actual modifications.
EOF",
  run_in_background: true,
  timeout: 3600000,
  description: "Brief description"
})
```**审计调用语法**（代码审查/审计）：```
Bash({
  command: "~/.claude/bin/codeagent-wrapper {{LITE_MODE_FLAG}}--backend <codex|gemini> {{GEMINI_MODEL_FLAG}}resume <SESSION_ID> - \"$PWD\" <<'EOF'
ROLE_FILE: <role prompt path>
<TASK>
Scope: Audit the final code changes.
Inputs:
- The applied patch (git diff / final unified diff)
- The touched files (relevant excerpts if needed)
Constraints:
- Do NOT modify any files.
- Do NOT output tool commands that assume filesystem access.
</TASK>
OUTPUT:
1) A prioritized list of issues (severity, file, rationale)
2) Concrete fixes; if code changes are needed, include a Unified Diff Patch in a fenced code block.
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
|实施 | `~/.claude/.ccg/prompts/codex/architect.md` | `~/.claude/.ccg/prompts/gemini/frontend.md` |
|评论 | `~/.claude/.ccg/prompts/codex/reviewer.md` | `~/.claude/.ccg/prompts/gemini/reviewer.md` |

**会话重用**：如果 `/ccg:plan` 提供了 SESSION_ID，请使用 `resume <SESSION_ID>` 来重用上下文。

**等待后台任务**（最大超时 600000 毫秒 = 10 分钟）：```
TaskOutput({ task_id: "<task_id>", block: true, timeout: 600000 })
```**重要**：
- 必须指定`timeout: 600000`，否则默认30秒会导致过早超时
- 如果 10 分钟后仍未完成，请继续使用“TaskOutput”进行轮询，**切勿终止进程**
- 如果由于超时而跳过等待，**必须调用`AskUserQuestion`来询问用户是否继续等待或终止任务**

---

## 执行工作流程

**执行任务**：$ARGUMENTS

### 第 0 阶段：阅读计划

`[模式：准备]`

1. **识别输入类型**：
   - 计划文件路径（例如`.claude/plan/xxx.md`）
   - 直接的任务描述

2. **阅读计划内容**：
   - 如果提供了计划文件路径，则读取并解析
   - 摘录：任务类型、实施步骤、关键文件、SESSION_ID

3. **执行前确认**：
   - 如果输入是“直接任务描述”或计划缺少`SESSION_ID`/关键文件：首先与用户确认
   - 如果无法确认用户对计划回答“Y”：必须再次确认才能继续

4. **任务类型路由**：

   |任务类型 |检测|路线 |
   |------------|------------|--------|
   | **前端** |页面、组件、UI、样式、布局 |双子座|
   | **后端** | API、接口、数据库、逻辑、算法 |法典|
   | **全栈** |包含前端和后端 | Codex ∥ 双子座并行 |

---

### 第 1 阶段：快速上下文检索

`[模式：检索]`

**如果 ace-tool MCP 可用**，请使用它进行快速上下文检索：

根据计划中的“关键文件”列表，调用`mcp__ace-tool__search_context`：```
mcp__ace-tool__search_context({
  query: "<semantic query based on plan content, including key files, modules, function names>",
  project_root_path: "$PWD"
})
```**检索策略**：
- 从计划的“关键文件”表中提取目标路径
- 构建语义查询，涵盖：入口文件、依赖模块、相关类型定义
- 如果结果不够，添加1-2次递归检索

**如果 ace-tool MCP 不可用**，请使用 Claude Code 内置工具作为后备：
1. **Glob**：从计划的“关键文件”表中查找目标文件（例如 `Glob("src/components/**/*.tsx")`）
2. **Grep**：在代码库中搜索关键符号、函数名称、类型定义
3. **读取**：读取发现的文件以收集完整的上下文
4. **任务（探索代理）**：要进行更广泛的探索，请使用“任务”和“subagent_type：“探索””

**检索后**：
- 组织检索到的代码片段
- 确认实施的完整背景
- 进入第三阶段

---

### 第 3 阶段：原型获取

`[模式：原型]`

**基于任务类型的路线**：

#### 路线 A：前端/UI/样式 → Gemini

**限制**：上下文 < 32k 令牌

1.调用Gemini（使用`~/.claude/.ccg/prompts/gemini/frontend.md`）
2. 输入：计划内容+检索上下文+目标文件
3. 输出：`仅统一差异补丁。严格禁止任何实际修改。`
4. **Gemini是前端设计权威，其CSS/React/Vue原型是最终的视觉基线**
5. **警告**：忽略Gemini的后端逻辑建议
6. 如果计划包含`GEMINI_SESSION`：更喜欢`resume <GEMINI_SESSION>`

#### 路线 B：后端/逻辑/算法 → Codex

1.调用Codex（使用`~/.claude/.ccg/prompts/codex/architect.md`）
2. 输入：计划内容+检索上下文+目标文件
3. 输出：`仅统一差异补丁。严格禁止任何实际修改。`
4. **Codex是后端逻辑权威，发挥其逻辑推理和调试能力**
5. 如果计划包含`CODEX_SESSION`：更喜欢`resume <CODEX_SESSION>`

#### 路线 C：全栈 → 并行调用

1. **并行调用** (`run_in_background: true`):
   - Gemini：处理前端部分
   - Codex：处理后端部分
2. 使用 `TaskOutput` 等待两个模型的完整结果
3. 每个都使用“resume”计划中相应的“SESSION_ID”（如果丢失，则创建新会话）

**遵循上面“多模型调用规范”中的“重要”说明**

---

### 第 4 阶段：代码实施

`[模式：实施]`

**克劳德作为代码主权执行以下步骤**：

1. **读取 Diff**：解析 Codex/Gemini 返回的统一 Diff 补丁

2. **心理沙箱**：
   - 模拟将 Diff 应用于目标文件
   - 检查逻辑一致性
   - 识别潜在的冲突或副作用

3. **重构和清理**：
   - 将“脏原型”重构为**可读、可维护的企业级代码**
   - 删除多余代码
   - 确保符合项目现有的代码标准
   - **除非必要，否则不要生成注释/文档**，代码应该是不言自明的

4. **最小范围**：
   - 更改仅限于要求范围
   - **副作用的强制审查**
   - 进行有针对性的修正

5. **应用更改**：
   - 使用编辑/写入工具执行实际修改
   - **仅修改必要的代码**，绝不影响用户其他现有功能

6. **自我验证**（强烈推荐）：
   - 运行项目现有的 lint / 类型检查 / 测试（优先考虑最小相关范围）
   - 如果失败：首先修复回归，然后进入第 5 阶段

---

### 第 5 阶段：审核和交付

`[模式：审核]`

#### 5.1 自动审核

**更改生效后，必须立即并行调用** Codex 和 Gemini 进行代码审查：

1. **法典审查**（`run_in_background：true`）：
   - ROLE_FILE: `~/.claude/.ccg/prompts/codex/reviewer.md`
   - 输入：更改 Diff + 目标文件
   - 重点：安全性、性能、错误处理、逻辑正确性

2. **双子座评论** (`run_in_background: true`):
   - ROLE_FILE: `~/.claude/.ccg/prompts/gemini/reviewer.md`
   - 输入：更改 Diff + 目标文件
   - 重点：可访问性、设计一致性、用户体验

使用“TaskOutput”等待两个模型的完整审核结果。为了上下文一致性，最好重用第 3 阶段会话（`resume <SESSION_ID>`）。

#### 5.2 集成和修复

1.综合Codex+Gemini审稿反馈
2. 按信任规则衡量：后端遵循 Codex，前端遵循 Gemini
3. 执行必要的修复
4. 根据需要重复阶段 5.1（直到风险可接受）

#### 5.3 交货确认

审核通过后，向用户报告：```markdown
## Execution Complete

### Change Summary
| File | Operation | Description |
|------|-----------|-------------|
| path/to/file.ts | Modified | Description |

### Audit Results
- Codex: <Passed/Found N issues>
- Gemini: <Passed/Found N issues>

### Recommendations
1. [ ] <Suggested test steps>
2. [ ] <Suggested verification steps>
```---

## 关键规则

1. **代码主权** – Claude 修改的所有文件，外部模型的写入权限为零
2. **脏原型重构** – Codex/Gemini 输出被视为草稿，必须重构
3. **信任规则** – 后端遵循 Codex，前端遵循 Gemini
4. **Minimum Changes** – 仅修改必要的代码，无副作用
5. **强制审计** – 更改后必须执行多模型代码审查

---

## 用法```bash
# Execute plan file
/ccg:execute .claude/plan/feature-name.md

# Execute task directly (for plans already discussed in context)
/ccg:execute implement user authentication based on previous plan
```---

## 与 /ccg:plan 的关系

1.`/ccg:plan`生成计划+SESSION_ID
2. 用户按“Y”确认
3.`/ccg:execute`读取计划，重用SESSION_ID，执行实现