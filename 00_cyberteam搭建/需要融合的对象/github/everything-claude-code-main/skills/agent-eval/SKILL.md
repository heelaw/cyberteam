# 特工评估技能

一个轻量级 CLI 工具，用于在可重复任务上对编码代理进行正面比较。每个“哪种编码剂最好？”比较基于共鸣——这个工具将其系统化。

## 何时激活

- 在您自己的代码库上比较编码代理（Claude Code、Aider、Codex 等）
- 在采用新工具或模型之前衡量代理绩效
- 当代理更新其模型或工具时运行回归检查
- 为团队制定有数据支持的代理选择决策

## 安装```bash
# pinned to v0.1.0 — latest stable commit
pip install git+https://github.com/joaquinhuigomez/agent-eval.git@6d062a2f5cda6ea443bf5d458d361892c04e749b
```## 核心概念

### YAML 任务定义

以声明方式定义任务。每个任务指定要做什么、要接触哪些文件以及如何判断成功：```yaml
name: add-retry-logic
description: Add exponential backoff retry to the HTTP client
repo: ./my-project
files:
  - src/http_client.py
prompt: |
  Add retry logic with exponential backoff to all HTTP requests.
  Max 3 retries. Initial delay 1s, max delay 30s.
judge:
  - type: pytest
    command: pytest tests/test_http_client.py -v
  - type: grep
    pattern: "exponential_backoff|retry"
    files: src/http_client.py
commit: "abc1234"  # pin to specific commit for reproducibility
```### Git 工作树隔离

每个代理运行都有自己的 git 工作树——不需要 Docker。这提供了可重复性隔离，因此代理不能互相干扰或损坏基础存储库。

### 收集的指标

|公制|它测量什么 |
|--------|-----------------|
|通过率|代理生成的代码是否通过了评审？ |
|成本|每个任务的 API 支出（如果可用）|
|时间 |挂钟数秒完成 |
|一致性|重复运行的通过率（例如，3/3 = 100%）|

## 工作流程

### 1. 定义任务

使用 YAML 文件创建一个 `tasks/` 目录，每个任务一个：```bash
mkdir tasks
# Write task definitions (see template above)
```### 2. 运行代理

针对您的任务执行代理：```bash
agent-eval run --task tasks/add-retry-logic.yaml --agent claude-code --agent aider --runs 3
```每次运行：
1. 从指定的提交创建一个新的 git 工作树
2. 将提示交给代理
3.运行评判标准
4. 记录通过/失败、成本和时间

### 3. 比较结果

生成比较报告：```bash
agent-eval report --format table
``````
Task: add-retry-logic (3 runs each)
┌──────────────┬───────────┬────────┬────────┬─────────────┐
│ Agent        │ Pass Rate │ Cost   │ Time   │ Consistency │
├──────────────┼───────────┼────────┼────────┼─────────────┤
│ claude-code  │ 3/3       │ $0.12  │ 45s    │ 100%        │
│ aider        │ 2/3       │ $0.08  │ 38s    │  67%        │
└──────────────┴───────────┴────────┴────────┴─────────────┘
```## 法官类型

### 基于代码（确定性）```yaml
judge:
  - type: pytest
    command: pytest tests/ -v
  - type: command
    command: npm run build
```### 基于模式```yaml
judge:
  - type: grep
    pattern: "class.*Retry"
    files: src/**/*.py
```### 基于模型（法学硕士作为法官）```yaml
judge:
  - type: llm
    prompt: |
      Does this implementation correctly handle exponential backoff?
      Check for: max retries, increasing delays, jitter.
```## 最佳实践

- **从 3-5 个任务开始**，这些任务代表您的实际工作量，而不是玩具示例
- **每个代理至少运行 3 次试验**以捕获方差 - 代理是不确定的
- **将提交固定在任务 YAML 中，以便结果可以在几天/几周内重现
- **每项任务至少包括一名确定性法官**（测试、构建）——LLM 法官会增加噪音
- **跟踪成本和通过率** — 95% 的代理以 10 倍的成本可能不是正确的选择
- **版本化您的任务定义** - 它们是测试装置，将它们视为代码

## 链接

- 存储库：[github.com/joaquinhuigomez/agent-eval](https://github.com/joaquinhuigomez/agent-eval)