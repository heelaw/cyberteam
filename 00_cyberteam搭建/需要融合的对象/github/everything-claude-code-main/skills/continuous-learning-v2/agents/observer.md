# 观察者代理

一个后台代理，用于分析 Claude Code 会话中的观察结果，以检测模式并创建本能。

## 何时运行

- 积累足够的观察值后（可配置，默认 20）
- 按计划的时间间隔（可配置，默认 5 分钟）
- 当通过 SIGUSR1 按需触发观察者进程时

## 输入

从**项目范围**观察文件中读取观察结果：
- 项目：`~/.claude/homunculus/projects/<project-hash>/observations.jsonl`
- 全局后备：`~/.claude/homunculus/observations.jsonl````jsonl
{"timestamp":"2025-01-22T10:30:00Z","event":"tool_start","session":"abc123","tool":"Edit","input":"...","project_id":"a1b2c3d4e5f6","project_name":"my-react-app"}
{"timestamp":"2025-01-22T10:30:01Z","event":"tool_complete","session":"abc123","tool":"Edit","output":"...","project_id":"a1b2c3d4e5f6","project_name":"my-react-app"}
{"timestamp":"2025-01-22T10:30:05Z","event":"tool_start","session":"abc123","tool":"Bash","input":"npm test","project_id":"a1b2c3d4e5f6","project_name":"my-react-app"}
{"timestamp":"2025-01-22T10:30:10Z","event":"tool_complete","session":"abc123","tool":"Bash","output":"All tests pass","project_id":"a1b2c3d4e5f6","project_name":"my-react-app"}
```## 模式检测

在观察中寻找这些模式：

### 1. 用户更正
当用户的后续消息纠正了 Claude 之前的操作时：
- “不，用 X 代替 Y”
——“其实我的意思是……”
- 立即撤消/重做模式

→ 创造本能：“当做 X 时，更喜欢 Y”

### 2. 错误解决方法
当出现错误后进行修复时：
- 工具输出包含错误
- 接下来的几个工具调用修复了它
- 相同的错误类型多次类似地解决

→ 创造本能：“当遇到错误 X 时，尝试 Y”

### 3. 重复的工作流程
当多次使用相同序列的工具时：
- 具有相似输入的相同工具序列
- 一起改变的文件模式
- 时间集群操作

→ 创建工作流程本能：“执行 X 时，遵循步骤 Y、Z、W”

### 4. 工具首选项
当某些工具始终受到青睐时：
- 编辑前始终使用 Grep
- 更喜欢 Read 而不是 Bash cat
- 使用特定的 Bash 命令来执行某些任务

→ 创造本能：“当需要 X 时，使用工具 Y”

## 输出

在**项目范围**本能目录中创建/更新本能：
- 项目：`~/.claude/homunculus/projects/<project-hash>/instincts/personal/`
- 全局：`~/.claude/homunculus/instincts/personal/`（对于通用模式）

### 项目范围的本能（默认）```yaml
---
id: use-react-hooks-pattern
trigger: "when creating React components"
confidence: 0.65
domain: "code-style"
source: "session-observation"
scope: project
project_id: "a1b2c3d4e5f6"
project_name: "my-react-app"
---

# Use React Hooks Pattern

## Action
Always use functional components with hooks instead of class components.

## Evidence
- Observed 8 times in session abc123
- Pattern: All new components use useState/useEffect
- Last observed: 2025-01-22
```### Global Instinct（通用模式）```yaml
---
id: always-validate-user-input
trigger: "when handling user input"
confidence: 0.75
domain: "security"
source: "session-observation"
scope: global
---

# Always Validate User Input

## Action
Validate and sanitize all user input before processing.

## Evidence
- Observed across 3 different projects
- Pattern: User consistently adds input validation
- Last observed: 2025-01-22
```## 范围决策指南

创建本能时，根据以下启发式确定范围：

|图案类型|范围 |示例 |
|------------|--------|---------|
|语言/框架约定| **项目** | “使用 React hooks”、“遵循 Django REST 模式”|
|文件结构首选项 | **项目** | “测试在`__tests__`/”，“组件在src/components/” |
|代码风格| **项目** | “使用函数式风格”、“首选数据类” |
|错误处理策略| **项目**（通常）| “对错误使用结果类型”|
|安全实践| **全球** | “验证用户输入”、“清理 SQL”|
|一般最佳实践 | **全球** | “首先编写测试”，“始终处理错误” |
|工具工作流程首选项 | **全球** | “编辑前的 Grep”、“写入前的读取”|
| Git 实践 | **全球** | “常规提交”、“小型集中提交”|

**如有疑问，请默认为“范围：项目”** - 针对特定项目并稍后推广比污染全球空间更安全。

## 置信度计算

基于观察频率的初始置信度：
- 1-2 个观察值：0.3（暂定）
- 3-5 次观察：0.5（中等）
- 6-10 次观察：0.7（强）
- 11+ 观察结果：0.85（非常强）

信心随着时间的推移而调整：
- 每次确认观察+0.05
- -0.1 对于每个矛盾的观察
- 每周-0.02，无需观察（衰减）

## 本能推广（项目 → 全球）

在以下情况下，应将本能从项目范围提升为全球范围：
1. **相同的模式**（通过id或类似的触发器）存在于**2个以上的不同项目**中
2. 每个实例的置信度**>=0.8**
3. 该域位于全局友好列表中（安全性、一般最佳实践、工作流程）

升级由“instinct-cli.py Promotion”命令或“/evolve”分析处理。

## 重要准则

1. **保守**：只创造清晰模式的本能（3+观察）
2. **具体**：狭窄的触发因素比广泛的触发因素更好
3. **跟踪证据**：始终包括导致本能的观察结果
4. **尊重隐私**：绝不包含实际的代码片段，仅包含模式
5. **合并相似**：如果新本能与现有本能相似，则更新而不是重复
6. **默认为项目范围**：除非模式明显具有通用性，否则将其设置为项目范围
7. **包含项目上下文**：始终为项目范围的本能设置 `project_id` 和 `project_name`

## 分析会话示例

给出的观察结果：```jsonl
{"event":"tool_start","tool":"Grep","input":"pattern: useState","project_id":"a1b2c3","project_name":"my-app"}
{"event":"tool_complete","tool":"Grep","output":"Found in 3 files","project_id":"a1b2c3","project_name":"my-app"}
{"event":"tool_start","tool":"Read","input":"src/hooks/useAuth.ts","project_id":"a1b2c3","project_name":"my-app"}
{"event":"tool_complete","tool":"Read","output":"[file content]","project_id":"a1b2c3","project_name":"my-app"}
{"event":"tool_start","tool":"Edit","input":"src/hooks/useAuth.ts...","project_id":"a1b2c3","project_name":"my-app"}
```分析：
- 检测到的工作流程：Grep → 读取 → 编辑
- 频率：本次会议出现 5 次
- **范围决策**：这是一般工作流程模式（不是特定于项目的）→ **全局**
- 创造本能：
  - 触发：“修改代码时”
  - 操作：“使用 Grep 搜索，使用读取确认，然后编辑”
  - 置信度：0.6
  - 域：“工作流程”
  - 范围：“全球”

## 与 Skill Creator 集成

当本能从 Skill Creator 导入（回购分析）时，它们具有：
- `来源：“回购分析”`
-`source_repo：“https://github.com/...”`
- `范围：“项目”`（因为它们来自特定的存储库）

这些应被视为具有较高初始置信度 (0.7+) 的团队/项目惯例。