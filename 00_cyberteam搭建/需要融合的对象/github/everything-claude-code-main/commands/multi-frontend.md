# 前端 - 以前端为中心的开发

以前端为中心的工作流程（研究 → 构思 → 计划 → 执行 → 优化 → 审核），由 Gemini 主导。

＃＃ 用法```bash
/frontend <UI task description>
```## Context

- Frontend task: $ARGUMENTS
- Gemini-led, Codex for auxiliary reference
- Applicable: Component design, responsive layout, UI animations, style optimization

## Your Role

You are the **Frontend Orchestrator**, coordinating multi-model collaboration for UI/UX tasks (Research → Ideation → Plan → Execute → Optimize → Review).

**Collaborative Models**:
- **Gemini** – Frontend UI/UX (**Frontend authority, trustworthy**)
- **Codex** – Backend perspective (**Frontend opinions for reference only**)
- **Claude (self)** – Orchestration, planning, execution, delivery

---

## Multi-Model Call Specification

**Call Syntax**:```
# New session call
Bash({
  command: "~/.claude/bin/codeagent-wrapper {{LITE_MODE_FLAG}}--backend gemini --gemini-model gemini-3-pro-preview - \"$PWD\" <<'EOF'
ROLE_FILE: <role prompt path>
<TASK>
Requirement: <enhanced requirement (or $ARGUMENTS if not enhanced)>
Context: <project context and analysis from previous phases>
</TASK>
OUTPUT: Expected output format
EOF",
  run_in_background: false,
  timeout: 3600000,
  description: "Brief description"
})

# Resume session call
Bash({
  command: "~/.claude/bin/codeagent-wrapper {{LITE_MODE_FLAG}}--backend gemini --gemini-model gemini-3-pro-preview resume <SESSION_ID> - \"$PWD\" <<'EOF'
ROLE_FILE: <role prompt path>
<TASK>
Requirement: <enhanced requirement (or $ARGUMENTS if not enhanced)>
Context: <project context and analysis from previous phases>
</TASK>
OUTPUT: Expected output format
EOF",
  run_in_background: false,
  timeout: 3600000,
  description: "Brief description"
})
```**角色提示**：

|相|双子座|
|--------|--------|
|分析| `~/.claude/.ccg/prompts/gemini/analyzer.md` |
|规划| `~/.claude/.ccg/prompts/gemini/architect.md` |
|评论 | `~/.claude/.ccg/prompts/gemini/reviewer.md` |

**会话重用**：每次调用都会返回 `SESSION_ID: xxx`，后续阶段使用 `resume xxx`。在第 2 阶段保存“GEMINI_SESSION”，在第 3 阶段和第 5 阶段使用“resume”。

---

## 沟通指南

1. 以模式标签“[Mode: X]”开始响应，首字母为“[Mode: Research]”
2.遵循严格的顺序：“研究→构思→计划→执行→优化→审核”
3. 在需要时使用“AskUserQuestion”工具进行用户交互（例如确认/选择/批准）

---

## 核心工作流程

### 第 0 阶段：迅速增强（可选）

`[模式：准备]` - 如果 ace-tool MCP 可用，则调用 `mcp__ace-tool__enhance_prompt`，**用后续 Gemini 调用的增强结果替换原始 $ARGUMENTS**。如果不可用，请按原样使用“$ARGUMENTS”。

### 第一阶段：研究

“[模式：研究]” - 了解需求并收集背景

1. **代码检索**（如果 ace-tool MCP 可用）：调用 `mcp__ace-tool__search_context` 检索现有组件、样式、设计系统。如果不可用，请使用内置工具：“Glob”用于文件发现，“Grep”用于组件/样式搜索，“Read”用于上下文收集，“Task”（探索代理）用于更深入的探索。
2、需求完成度评分（0-10）：>=7继续，<7停止补充

### 第二阶段：构思

“[模式：构思]”-双子座主导的分析

**必须调用 Gemini**（遵循上面的调用规范）：
- ROLE_FILE: `~/.claude/.ccg/prompts/gemini/analyzer.md`
- 要求：增强要求（如果未增强则为 $ARGUMENTS）
- 背景：第一阶段的项目背景
- 输出：UI可行性分析、推荐解决方案（至少2个）、UX评估

**保存SESSION_ID**（`GEMINI_SESSION`）以供后续阶段重用。

输出解决方案（至少2个），等待用户选择。

### 第三阶段：规划

`[模式：计划]` - 双子座主导的计划

**必须调用 Gemini** （使用 `resume <GEMINI_SESSION>` 来重用会话）：
- ROLE_FILE: `~/.claude/.ccg/prompts/gemini/architect.md`
- 要求：用户选择的解决方案
- 背景：第二阶段的分析结果
- 输出：组件结构、UI 流程、样式方法

Claude综合计划，经用户批准后保存到`.claude/plan/task-name.md`。

### 第四阶段：实施

`[模式：执行]` - 代码开发

- 严格遵循批准的计划
- 遵循现有的项目设计体系和代码标准
- 确保响应能力、可访问性

### 第 5 阶段：优化

“[模式：优化]” - Gemini 主导的审查

**必须调用 Gemini**（遵循上面的调用规范）：
- ROLE_FILE: `~/.claude/.ccg/prompts/gemini/reviewer.md`
- 要求：检查以下前端代码更改
- 上下文：git diff 或代码内容
- 输出：可访问性、响应能力、性能、设计一致性问题列表

整合评论反馈，用户确认后进行优化。

### 第 6 阶段：质量审查

`[模式：审核]` - 最终评估

- 根据计划检查完成情况
- 验证响应能力和可访问性
- 报告问题和建议

---

## 关键规则

1. **Gemini前端意见值得信赖**
2. **法典前端意见仅供参考**
3. 外部模型具有**零文件系统写入访问权限**
4. Claude 处理所有代码写入和文件操作