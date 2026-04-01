# 持续学习 v2.1 - 本能
基于架构

先进的学习系统，通过原子“本能”将您的克劳德代码课程转化为可重用的知识 - 具有信心评分的小学习行为。

**v2.1** 添加了**项目范围的本能** - React 模式保留在您的 React 项目中，Python 约定保留在您的 Python 项目中，并且通用模式（例如“始终验证输入”）在全球范围内共享。

## 何时激活

- 设置从克劳德代码会话自动学习
- 通过钩子配置基于本能的行为提取
- 调整学习行为的置信度阈值
- 审查、导出或导入本能库
- 将本能进化为完整的技能、命令或代理
- 管理项目范围与全球本能
- 将本能从项目提升到全球范围

## v2.1 中的新增功能

|特色 | v2.0 | v2.1 |
|---------|------|------|
|存储|全局 (~/.claude/homunculus/) |项目范围 (projects/<hash>/) |
|范围 |所有本能都适用于任何地方 |项目范围+全球|
|检测|无 | git 远程 URL / 仓库路径 |
|促销|不适用 |项目 → 在 2 个以上项目中看到时为全局 |
|命令 | 4（状态/演变/导出/导入）| 6（+推广/项目）|
|跨项目|污染风险 |默认隔离|

## v2 中的新增功能（相对于 v1）

|特色 | v1 | v2 |
|---------|----|----|
|观察|停止钩子（会话结束）| PreToolUse/PostToolUse（100% 可靠）|
|分析|主要背景|背景特工（俳句）|
|粒度|技能全 |原子“本能”|
|信心|无 | 0.3-0.9 加权 |
|进化|直接技能 |本能 -> 集群 -> 技能/命令/代理 |
|分享|无 |出口/进口本能 |

## 本能模型

本能是一种小的习得行为：```yaml
---
id: prefer-functional-style
trigger: "when writing new functions"
confidence: 0.7
domain: "code-style"
source: "session-observation"
scope: project
project_id: "a1b2c3d4e5f6"
project_name: "my-react-app"
---

# Prefer Functional Style

## Action
Use functional patterns over classes when appropriate.

## Evidence
- Observed 5 instances of functional pattern preference
- User corrected class-based approach to functional on 2025-01-15
```**特性：**
- **原子** -- 一次触发，一次操作
- **置信度加权** -- 0.3 = 暂定，0.9 = 接近确定
- **域标记** -- 代码风格、测试、git、调试、工作流程等。
- **有证据支持** -- 追踪观察结果产生的结果
- **范围感知** -- `project`（默认）或`global`

## 它是如何工作的```
Session Activity (in a git repo)
      |
      | Hooks capture prompts + tool use (100% reliable)
      | + detect project context (git remote / repo path)
      v
+---------------------------------------------+
|  projects/<project-hash>/observations.jsonl  |
|   (prompts, tool calls, outcomes, project)   |
+---------------------------------------------+
      |
      | Observer agent reads (background, Haiku)
      v
+---------------------------------------------+
|          PATTERN DETECTION                   |
|   * User corrections -> instinct             |
|   * Error resolutions -> instinct            |
|   * Repeated workflows -> instinct           |
|   * Scope decision: project or global?       |
+---------------------------------------------+
      |
      | Creates/updates
      v
+---------------------------------------------+
|  projects/<project-hash>/instincts/personal/ |
|   * prefer-functional.yaml (0.7) [project]   |
|   * use-react-hooks.yaml (0.9) [project]     |
+---------------------------------------------+
|  instincts/personal/  (GLOBAL)               |
|   * always-validate-input.yaml (0.85) [global]|
|   * grep-before-edit.yaml (0.6) [global]     |
+---------------------------------------------+
      |
      | /evolve clusters + /promote
      v
+---------------------------------------------+
|  projects/<hash>/evolved/ (project-scoped)   |
|  evolved/ (global)                           |
|   * commands/new-feature.md                  |
|   * skills/testing-workflow.md               |
|   * agents/refactor-specialist.md            |
+---------------------------------------------+
```## 项目检测

系统自动检测您当前的项目：

1. **`CLAUDE_PROJECT_DIR` 环境变量**（最高优先级）
2. **`git remote get-url origin`** -- 散列以创建可移植的项目 ID（不同机器上的相同存储库获得相同的 ID）
3. **`git rev-parse --show-toplevel`** -- 使用 repo 路径进行回退（特定于机器）
4. **全局回退**——如果没有检测到项目，本能就会进入全局范围

每个项目都有一个 12 个字符的哈希 ID（例如“a1b2c3d4e5f6”）。 `~/.claude/homunculus/projects.json` 中的注册表文件将 ID 映射到人类可读的名称。

## 快速入门

### 1.启用观察钩子

添加到您的“~/.claude/settings.json”。

**如果作为插件安装**（推荐）：```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning-v2/hooks/observe.sh"
      }]
    }],
    "PostToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning-v2/hooks/observe.sh"
      }]
    }]
  }
}
```**如果手动安装**到`~/.claude/skills`：```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/skills/continuous-learning-v2/hooks/observe.sh"
      }]
    }],
    "PostToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/skills/continuous-learning-v2/hooks/observe.sh"
      }]
    }]
  }
}
```### 2.初始化目录结构

系统在第一次使用时自动创建目录，但您也可以手动创建它们：```bash
# Global directories
mkdir -p ~/.claude/homunculus/{instincts/{personal,inherited},evolved/{agents,skills,commands},projects}

# Project directories are auto-created when the hook first runs in a git repo
```### 3. 使用本能命令```bash
/instinct-status     # Show learned instincts (project + global)
/evolve              # Cluster related instincts into skills/commands
/instinct-export     # Export instincts to file
/instinct-import     # Import instincts from others
/promote             # Promote project instincts to global scope
/projects            # List all known projects and their instinct counts
```## 命令

|命令 |描述 |
|---------|-------------|
| `/本能状态` |自信地展现所有本能（项目范围+全球）|
| `/进化` |将相关直觉聚集到技能/命令中，提出晋升建议 |
| `/本能导出` |导出本能（可按范围/域过滤）|
| `/instinct-import <文件>` |通过范围控制导入本能 |
| `/推广 [id]` |将项目本能提升到全球范围 |
| `/项目` |列出所有已知项目及其本能计数 |

## 配置

编辑`config.json`来控制后台观察者：```json
{
  "version": "2.1",
  "observer": {
    "enabled": false,
    "run_interval_minutes": 5,
    "min_observations_to_analyze": 20
  }
}
```|关键|默认 |描述 |
|-----|---------|-------------|
| `观察者.启用` | `假` |启用后台观察代理 |
| `observer.run_interval_分钟` | `5` |观察者多久分析一次观察结果？
| `observer.min_observations_to_analyze` | `20` |分析运行前的最少观测值 |

其他行为（观察捕获、本能阈值、项目范围、升级标准）通过“instinct-cli.py”和“observe.sh”中的代码默认值进行配置。

## 文件结构```
~/.claude/homunculus/
+-- identity.json           # Your profile, technical level
+-- projects.json           # Registry: project hash -> name/path/remote
+-- observations.jsonl      # Global observations (fallback)
+-- instincts/
|   +-- personal/           # Global auto-learned instincts
|   +-- inherited/          # Global imported instincts
+-- evolved/
|   +-- agents/             # Global generated agents
|   +-- skills/             # Global generated skills
|   +-- commands/           # Global generated commands
+-- projects/
    +-- a1b2c3d4e5f6/       # Project hash (from git remote URL)
    |   +-- project.json    # Per-project metadata mirror (id/name/root/remote)
    |   +-- observations.jsonl
    |   +-- observations.archive/
    |   +-- instincts/
    |   |   +-- personal/   # Project-specific auto-learned
    |   |   +-- inherited/  # Project-specific imported
    |   +-- evolved/
    |       +-- skills/
    |       +-- commands/
    |       +-- agents/
    +-- f6e5d4c3b2a1/       # Another project
        +-- ...
```## 范围决策指南

|图案类型|范围 |示例 |
|------------|--------|---------|
|语言/框架约定| **项目** | “使用 React hooks”、“遵循 Django REST 模式”|
|文件结构首选项 | **项目** | “测试在`__tests__`/”，“组件在src/components/” |
|代码风格| **项目** | “使用函数式风格”、“首选数据类” |
|错误处理策略| **项目** | “对错误使用结果类型”|
|安全实践| **全球** | “验证用户输入”、“清理 SQL”|
|一般最佳实践 | **全球** | “首先编写测试”，“始终处理错误” |
|工具工作流程首选项 | **全球** | “编辑前的 Grep”、“写入前的读取”|
| Git 实践 | **全球** | “常规提交”、“小型集中提交”|

## 本能推广（项目 -> 全球）

当相同的本能以高度信心出现在多个项目中时，它就是晋升到全球范围的候选者。

**自动晋升标准：**
- 2个以上项目中有相同的本能ID
- 平均置信度 >= 0.8

**如何推广：**```bash
# Promote a specific instinct
python3 instinct-cli.py promote prefer-explicit-errors

# Auto-promote all qualifying instincts
python3 instinct-cli.py promote

# Preview without changes
python3 instinct-cli.py promote --dry-run
````/evolve` 命令还建议晋升候选人。

## 置信度评分

信心随着时间的推移而变化：

|分数 |意义|行为 |
|--------|---------|----------|
| 0.3 | 0.3暂定|建议但不强制执行 |
| 0.5 | 0.5中等|相关时应用 |
| 0.7 | 0.7强|自动批准申请 |
| 0.9 | 0.9几乎确定|核心行为|

**在以下情况下信心会增加**：
- 重复观察模式
- 用户没有纠正建议的行为
- 其他来源的类似直觉也同意

**在以下情况下信心会降低**：
- 用户明确纠正行为
- 长时间未观察到模式
- 出现矛盾的证据

## 为什么要使用 Hooks 与观察技能？

> “v1 依靠技能来观察。技能是概率性的——根据克劳德的判断，它们大约有 50-80% 的时间会触发。”

Hooks 确定性地**100% 的时间**触发。这意味着：
- 观察每个工具调用
- 没有任何图案被遗漏
- 学习内容全面

## 向后兼容性

v2.1 与 v2.0 和 v1 完全兼容：
- `~/.claude/homunculus/instincts/` 中现有的全局本能仍然作为全局本能起作用
- v1 中现有的 `~/.claude/skills/learned/` 技能仍然有效
- Stop hook 仍然运行（但现在也输入到 v2 中）
- 逐步迁移：并行运行

## 隐私

- 观察结果保留在您的机器上**本地**
- 项目范围内的本能是按项目隔离的
- 只能导出**本能**（模式）——不能导出原始观察结果
- 没有共享实际代码或对话内容
- 您可以控制导出和推广的内容

## 相关

- [技能创建者](https://skill-creator.app) - 从存储库历史记录中生成本能
- Homunculus - 启发 v2 基于本能的架构的社区项目（原子观察、置信度评分、本能进化管道）
- [长篇指南](https://x.com/affaanmustafa/status/2014040193557471352) - 持续学习部分

---

*基于本能的学习：教克劳德你的模式，一次一个项目。*