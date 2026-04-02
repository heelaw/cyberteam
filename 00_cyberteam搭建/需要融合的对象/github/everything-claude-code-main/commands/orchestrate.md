# 编排命令

复杂任务的顺序代理工作流程。

## 用法

`/orchestrate [工作流程类型] [任务描述]`

## 工作流程类型

### 功能
全功能实施流程：```
planner -> tdd-guide -> code-reviewer -> security-reviewer
```### 错误修复
错误调查和修复工作流程：```
planner -> tdd-guide -> code-reviewer
```### 重构
安全重构工作流程：```
architect -> code-reviewer -> tdd-guide
```### 安全
以安全为重点的审查：```
security-reviewer -> code-reviewer -> architect
```## 执行模式

对于工作流程中的每个代理：

1. **使用前一个代理的上下文调用代理**
2. **收集输出**作为结构化移交文档
3. **传递给链中的下一个代理**
4. **将结果汇总**到最终报告中

## 移交文档格式

在代理之间，创建移交文档：```markdown
## HANDOFF: [previous-agent] -> [next-agent]

### Context
[Summary of what was done]

### Findings
[Key discoveries or decisions]

### Files Modified
[List of files touched]

### Open Questions
[Unresolved items for next agent]

### Recommendations
[Suggested next steps]
```## 示例：功能工作流程```
/orchestrate feature "Add user authentication"
```执行：

1. **规划代理**
   - 分析需求
   - 制定实施计划
   - 识别依赖关系
   - 输出：`HANDOFF：规划器 -> tdd-guide`

2. **TDD指导代理**
   - 阅读计划者交接
   - 首先编写测试
   - 实施以通过测试
   - 输出：`HANDOFF：tdd-guide -> code-reviewer`

3. **代码审查代理**
   - 审查实施情况
   - 检查问题
   - 提出改进建议
   - 输出：`HANDOFF：代码审查者 -> 安全审查者`

4. **安全审查代理**
   - 安全审计
   - 漏洞检查
   - 最终批准
   - 输出：最终报告

## 最终报告格式```
ORCHESTRATION REPORT
====================
Workflow: feature
Task: Add user authentication
Agents: planner -> tdd-guide -> code-reviewer -> security-reviewer

SUMMARY
-------
[One paragraph summary]

AGENT OUTPUTS
-------------
Planner: [summary]
TDD Guide: [summary]
Code Reviewer: [summary]
Security Reviewer: [summary]

FILES CHANGED
-------------
[List all files modified]

TEST RESULTS
------------
[Test pass/fail summary]

SECURITY STATUS
---------------
[Security findings]

RECOMMENDATION
--------------
[SHIP / NEEDS WORK / BLOCKED]
```## 并行执行

对于独立检查，并行运行代理：```markdown
### Parallel Phase
Run simultaneously:
- code-reviewer (quality)
- security-reviewer (security)
- architect (design)

### Merge Results
Combine outputs into single report
```对于具有单独 git 工作树的外部 tmux-pane 工作人员，请使用 `node script/orchestrate-worktrees.js plan.json --execute`。内置的编排模式保持在进程中；该助手用于长时间运行或跨线束会话。

当工作人员需要从主结账中查看脏的或未跟踪的本地文件时，请将“seedPaths”添加到计划文件中。 ECC 在“git worktree add”之后仅将那些选定的路径覆盖到每个工作人员工作树中，这使分支保持隔离，同时仍然公开运行中的本地脚本、计划或文档。```json
{
  "sessionName": "workflow-e2e",
  "seedPaths": [
    "scripts/orchestrate-worktrees.js",
    "scripts/lib/tmux-worktree-orchestrator.js",
    ".claude/plan/workflow-e2e-test.json"
  ],
  "workers": [
    { "name": "docs", "task": "Update orchestration docs." }
  ]
}
```要导出实时 tmux/worktree 会话的控制平面快照，请运行：```bash
node scripts/orchestration-status.js .claude/plan/workflow-visual-proof.json
```快照包括会话活动、tmux 窗格元数据、工作状态、目标、种子覆盖以及 JSON 形式的最近切换摘要。

## 操作员指挥中心切换

当工作流程跨越多个会话、工作树或 tmux 窗格时，将控制平面块附加到最终切换：```markdown
CONTROL PLANE
-------------
Sessions:
- active session ID or alias
- branch + worktree path for each active worker
- tmux pane or detached session name when applicable

Diffs:
- git status summary
- git diff --stat for touched files
- merge/conflict risk notes

Approvals:
- pending user approvals
- blocked steps awaiting confirmation

Telemetry:
- last activity timestamp or idle signal
- estimated token or cost drift
- policy events raised by hooks or reviewers
```这使得计划者、实施者、审核者和循环工作人员在操作员界面上清晰可见。

## 参数

$参数：
- `feature <description>` - 完整功能工作流程
- `bugfix <描述>` - 错误修复工作流程
- `refactor <description>` - 重构工作流程
- `security <description>` - 安全审核工作流程
- `custom <agents> <description>` - 自定义代理序列

## 自定义工作流程示例```
/orchestrate custom "architect,tdd-guide,code-reviewer" "Redesign caching layer"
```## 提示

1. **从规划器开始**复杂的功能
2. **在合并之前始终包含代码审查者**
3. **使用安全审核器**进行身份验证/付款/PII
4. **保持交接简洁** - 关注下一个座席的需求
5. **如果需要，在代理之间运行验证**