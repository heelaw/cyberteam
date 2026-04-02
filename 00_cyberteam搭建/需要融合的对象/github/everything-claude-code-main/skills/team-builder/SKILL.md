# 团队建设者

用于按需浏览和组成代理团队的交互式菜单。适用于平面或域子目录代理集合。

## 何时使用

- 您有多个代理角色（Markdown 文件），并且想要选择用于任务的角色
- 您想组建一个来自不同领域的临时团队（例如，安全+搜索引擎优化+架构）
- 在决定之前您想浏览一下可用的代理

## 先决条件

代理文件必须是包含角色提示（身份、规则、工作流程、可交付成果）的 Markdown 文件。第一个“# Heading”用作代理名称，第一段用作描述。

支持平面布局和子目录布局：

**子目录布局** — 域是从文件夹名称推断出来的：```
agents/
├── engineering/
│   ├── security-engineer.md
│   └── software-architect.md
├── marketing/
│   └── seo-specialist.md
└── sales/
    └── discovery-coach.md
```**平面布局** — 从共享文件名前缀推断出的域。当 2 个以上文件共享某个前缀时，该前缀将被视为一个域。具有唯一前缀的文件转到“常规”。注意：算法在第一个“-”处分割，因此多字域（例如“产品管理”）应使用子目录布局：```
agents/
├── engineering-security-engineer.md
├── engineering-software-architect.md
├── marketing-seo-specialist.md
├── marketing-content-strategist.md
├── sales-discovery-coach.md
└── sales-outbound-strategist.md
```## 配置

按顺序探测代理目录并合并结果：

1. `./agents/**/*.md` + `./agents/*.md` — 项目本地代理（两个深度）
2. `~/.claude/agents/**/*.md` + `~/.claude/agents/*.md` — 全局代理（两个深度）

来自所有位置的结果均按代理名称进行合并和重复数据删除。项目本地代理优先于同名的全局代理。如果用户指定，则可以使用自定义路径。

## 它是如何工作的

### 第 1 步：发现可用的代理

使用上面的探测顺序的 Glob 代理目录。排除自述文件。对于找到的每个文件：
- **子目录布局：**从父文件夹名称中提取域
- **平面布局：**收集所有文件名前缀（第一个“-”之前的文本）。仅当前缀出现在 2 个或多个文件名中时，该前缀才有资格作为域（例如，“engineering-security-engineer.md”和“engineering-software-architect.md”均以“engineering”→ Engineering 域开头）。具有唯一前缀的文件（例如“code-reviewer.md”、“tdd-guide.md”）分组在“常规”下
- 从第一个“# Heading”中提取代理名称。如果未找到标题，则从文件名中获取名称（剥离“.md”，用空格替换连字符，标题大小写）
- 从标题后的第一段中提取单行摘要

如果在探测所有位置后未找到代理文件，请通知用户：“未找到代理文件。已检查：[列出探测到的路径]。预期：这些目录之一中的 markdown 文件。”然后停下来。

### 第 2 步：显示域菜单```
Available agent domains:
1. Engineering — Software Architect, Security Engineer
2. Marketing — SEO Specialist
3. Sales — Discovery Coach, Outbound Strategist

Pick domains or name specific agents (e.g., "1,3" or "security + seo"):
```- 跳过具有零代理的域（空目录）
- 显示每个域的代理计数

### 第 3 步：处理选择

接受灵活的输入：
- 数字：“1,3”选择来自工程和销售的所有代理
- 名称：“安全+搜索引擎优化”与已发现代理的模糊匹配
- “全部来自工程”选择该域中的每个代理

如果选择了 5 个以上的代理，则按字母顺序列出它们并要求用户缩小范围：“您选择了 N 个代理（最多 5 个）。选择要保留的代理，或者说‘前 5 个’以按字母顺序使用前 5 个代理。”

确认选择：```
Selected: Security Engineer + SEO Specialist
What should they work on? (describe the task):
```### 步骤 4：并行生成代理

1. 读取每个选定代理的markdown文件
2. 提示输入任务描述（如果尚未提供）
3. 使用 Agent 工具并行生成所有代理：
   - `subagent_type：“通用”`
   - `提示：“{代理文件内容}\n\n任务：{任务描述}”`
   - 每个代理独立运行——无需代理间通信
4. 如果代理失败（错误、超时或空输出），请内联记下失败（例如，“安全工程师：失败 - [原因]”）并继续使用成功代理的结果

### 步骤 5：综合结果

收集所有输出并提交统一报告：
- 按代理分组的结果
- 合成部分突出显示：
  - 代理之间的协议
  - 建议之间的冲突或紧张
  - 建议的后续步骤

如果仅选择 1 个代理，则跳过合成并直接呈现输出。

## 规则

- **仅限动态发现。**切勿对代理列表进行硬编码。目录中的新文件会自动出现在菜单中。
- **每个团队最多 5 名代理。** 超过 5 名代理会导致收益递减和代币使用过多。在选择时强制执行。
- **并行调度。** 所有代理同时运行 - 使用代理工具的并行调用模式。
- **并行代理调用，而不是 TeamCreate。**此技能使用并行代理工具调用来进行独立工作。仅当代理必须相互辩论或响应时才需要 TeamCreate（用于多代理对话的 Claude Code 工具）。

## 示例```
User: team builder

Claude:
Available agent domains:
1. Engineering (2) — Software Architect, Security Engineer
2. Marketing (1) — SEO Specialist
3. Sales (4) — Discovery Coach, Outbound Strategist, Proposal Strategist, Sales Engineer
4. Support (1) — Executive Summary

Pick domains or name specific agents:

User: security + seo

Claude:
Selected: Security Engineer + SEO Specialist
What should they work on?

User: Review my Next.js e-commerce site before launch

[Both agents spawn in parallel, each applying their specialty to the codebase]

Claude:
## Security Engineer Findings
- [findings...]

## SEO Specialist Findings
- [findings...]

## Synthesis
Both agents agree on: [...]
Tension: Security recommends CSP that blocks inline styles, SEO needs inline schema markup. Resolution: [...]
Next steps: [...]
```