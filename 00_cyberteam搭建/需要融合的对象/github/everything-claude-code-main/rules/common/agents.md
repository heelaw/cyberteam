# 代理编排

## 可用代理

位于`~/.claude/agents/`：

|代理|目的|何时使用 |
|--------|---------|-------------|
|策划师|实施规划|复杂功能，重构|
|建筑师 |系统设计|架构决策 |
| TDD 指南 |测试驱动开发 |新功能、错误修复 |
|代码审查员 |代码审查 |写完代码后|
|安全审查员 |证券分析|提交之前 |
|构建错误解析器 |修复构建错误 |当构建失败时 |
| e2e-跑步者 |端到端测试|关键用户流量|
|重构清理器 |死代码清理 |代码维护 |
|文档更新程序 |文档 |更新文档 |
| Rust 评论家 | Rust 代码审查 | Rust 项目 |

## 立即使用代理

无需用户提示：
1. 复杂的功能请求 - 使用 **planner** 代理
2. 刚刚编写/修改的代码 - 使用 **code-reviewer** 代理
3. Bug 修复或新功能 - 使用 **tdd-guide** 代理
4. 架构决策 - 使用 **architect** 代理

## 并行任务执行

始终使用并行任务执行来进行独立操作：```markdown
# GOOD: Parallel execution
Launch 3 agents in parallel:
1. Agent 1: Security analysis of auth module
2. Agent 2: Performance review of cache system
3. Agent 3: Type checking of utilities

# BAD: Sequential when unnecessary
First agent 1, then agent 2, then agent 3
```## 多视角分析

对于复杂问题，使用分割角色子代理：
- 事实审稿人
- 高级工程师
- 安全专家
- 一致性审核员
- 冗余检查器