# 克劳德代码的详细指南

![标题：克劳德代码的详细指南](./assets/images/longform/01-header.png)

---

> **先决条件**：本指南建立在[克劳德代码的速记指南](./the-shortform-guide.md) 的基础上。如果您尚未设置技能、挂钩、子代理、MCP 和插件，请先阅读该内容。

![速记指南参考](./assets/images/longform/02-shortform-reference.png)
*速记指南 - 首先阅读它*

在速记指南中，我介绍了基本设置：技能和命令、挂钩、子代理、MCP、插件以及构成有效 Claude Code 工作流程支柱的配置模式。这就是设置指南和基础设施。

这份长篇指南探讨了区分富有成效的会议和浪费的会议的技术。如果您还没有阅读速记指南，请先返回并设置您的配置。接下来的内容假设您拥有已配置且正在运行的技能、代理、挂钩和 MCP。

这里的主题：代币经济学、内存持久性、验证模式、并行化策略以及构建可重用工作流程的复合效应。这些是我在 10 多个月的日常使用中改进的模式，这些模式使得在第一个小时内受到上下文腐烂的困扰与在数小时内保持高效会话之间存在差异。

速记和长格式指南中涵盖的所有内容均可在 GitHub 上找到：`github.com/affaan-m/everything-claude-code`

---

## 提示和技巧

### 一些 MCP 是可替换的并且会释放您的上下文窗口

对于版本控制 (GitHub)、数据库 (Supabase)、部署（Vercel、Railway）等 MCP，大多数平台已经拥有强大的 CLI，MCP 本质上只是对其进行了包装。 MCP 是一个很好的包装器，但它是有代价的。

要使 CLI 功能更像 MCP，而不实际使用 MCP（以及随之而来的减少的上下文窗口），请考虑将功能捆绑到技能和命令中。去掉 MCP 公开的使事情变得简单的工具，并将其转化为命令。

示例：创建一个 `/gh-pr` 命令，用您的首选选项包装 `gh pr create`，而不是始终加载 GitHub MCP。创建直接使用 Supabase CLI 的技能，而不是 Supabase MCP 饮食环境。

通过延迟加载，上下文窗口问题基本上得到解决。但代币的使用和成本并不是以同样的方式解决的。 CLI+技能的方式仍然是一种token优化方式。

---

## 重要的事情

### 上下文和内存管理

为了跨会话共享内存，最好的选择是总结和检查进度的技能或命令，然后将其保存到“.claude”文件夹中的“.tmp”文件中，并附加到该文件，直到会话结束。第二天，它可以使用它作为上下文，并从您上次停下的地方继续，为每个会话创建一个新文件，这样您就不会将旧的上下文污染到新的工作中。

![会话存储文件树](./assets/images/longform/03-session-storage.png)
*会话存储示例 -> <https://github.com/affaan-m/everything-claude-code/tree/main/examples/sessions>*

克劳德创建一个总结当前状态的文件。检查它，如果需要的话要求编辑，然后重新开始。对于新对话，只需提供文件路径。当您遇到上下文限制并需要继续复杂的工作时特别有用。这些文件应包含：
- 哪些方法有效（有证据可验证）
- 尝试过哪些方法但没有奏效
- 哪些方法尚未尝试以及还需要做什么

**战略性地清理背景：**

一旦您设置了计划并清除了上下文（现在克劳德代码中计划模式的默认选项），您就可以按照计划进行工作。当您积累了大量与执行不再相关的探索上下文时，这非常有用。对于策略性压缩，请禁用自动压缩。按逻辑间隔手动压缩或创建一项可以为您执行此操作的技能。

**高级：动态系统提示注射**

我选择的一种模式是：不要将所有内容都放在加载每个会话的 CLAUDE.md（用户范围）或“.claude/rules/”（项目范围）中，而是使用 CLI 标志动态注入上下文。```bash
claude --system-prompt "$(cat memory.md)"
```这让您可以更加精确地了解何时加载什么上下文。系统提示内容的权限高于用户消息，用户消息的权限高于工具结果。

**实际设置：**```bash
# Daily development
alias claude-dev='claude --system-prompt "$(cat ~/.claude/contexts/dev.md)"'

# PR review mode
alias claude-review='claude --system-prompt "$(cat ~/.claude/contexts/review.md)"'

# Research/exploration mode
alias claude-research='claude --system-prompt "$(cat ~/.claude/contexts/research.md)"'
```**高级：内存持久挂钩**

大多数人不知道一些有助于记忆的技巧：

- **PreCompact Hook**：在上下文压缩发生之前，将重要状态保存到文件中
- **停止挂钩（会话结束）**：在会话结束时，将学习内容保存到文件中
- **SessionStart Hook**：在新会话中，自动加载以前的上下文

我已经构建了这些钩子，它们位于`github.com/affaan-m/everything-claude-code/tree/main/hooks/memory-persistence`的存储库中

---

### 持续学习/记忆

如果您必须多次重复提示，而克劳德遇到了同样的问题，或者给了您以前听过的答复 - 这些模式必须附加到技能中。

**问题：** 浪费令牌，浪费上下文，浪费时间。

**解决方案：** 当 Claude Code 发现一些不平凡的东西（调试技术、解决方法、一些特定于项目的模式）时，它会将这些知识保存为新技能。下次出现类似问题时，该技能会自动加载。

我已经建立了一种持续学习技能来做到这一点：`github.com/affaan-m/everything-claude-code/tree/main/skills/continuous-learning`

**为什么停止 Hook（不是 UserPromptSubmit）：**

关键的设计决策是使用 **Stop hook** 而不是 UserPromptSubmit。 UserPromptSubmit 在每条消息上运行 - 增加每个提示的延迟。在训练结束时停止运行一次 - 轻量级，不会在训练期间减慢您的速度。

---

### 代币优化

**主要策略：子代理架构**

优化您使用的工具和子代理架构，旨在委托足以完成任务的最便宜的模型。

**选型快速参考：**

![模型选择表](./assets/images/longform/04-model-selection.png)
*针对各种常见任务的子代理的假设设置以及选择背后的推理*

|任务类型|型号|为什么 |
| ---------------------------------- | ------ | ------------------------------------------------------ |
|探索/搜索 |俳句 |快速、便宜、足以查找文件 |
|简单编辑|俳句 |单文件修改，指令清晰|
|多文件实现 |十四行诗|编码的最佳平衡 |
|复杂的建筑|作品|需要深刻的推理 |
|公关评论 |十四行诗|理解上下文，捕捉细微差别 |
|证券分析|作品|不能错过漏洞|
|撰写文档 |俳句 |结构简单|
|调试复杂的错误|作品|需要牢记整个系统|

90% 的编码任务默认使用 Sonnet。当第一次尝试失败、任务跨越 5 个以上文件、架构决策或安全关键代码时升级到 Opus。

**定价参考：**

![克劳德模型定价](./assets/images/longform/05-pricing-table.png)
*来源：<https://platform.claude.com/docs/en/about-claude/pricing>*

**特定于工具的优化：**

将 grep 替换为 mgrep - 与传统 grep 或 ripgrep 相比，平均减少约 50% 的标记：

![mgrep 基准](./assets/images/longform/06-mgrep-benchmark.png)
*在我们的 50 项任务基准测试中，mgrep + Claude Code 使用的标记比基于 grep 的工作流程少约 2 倍，且质量相似或更好。来源：@mixedbread-ai* 的 mgrep

**模块化代码库的好处：**

拥有一个更加模块化的代码库，其中主文件由数百行而不是数千行组成，有助于降低令牌优化成本，并在第一次尝试时就正确完成任务。

---

### 验证循环和评估

**基准测试工作流程：**

比较有技能和没有技能要求相同的事情并检查输出差异：

分叉对话，在没有技能的情况下在其中一个中启动一个新的工作树，最后拉出差异，查看记录的内容。

**评估模式类型：**

- **基于检查点的评估**：设置显式检查点，根据定义的标准进行验证，在继续之前修复
- **连续评估**：每 N 分钟或重大更改后运行一次，完整的测试套件 + lint

**关键指标：**```
pass@k: At least ONE of k attempts succeeds
        k=1: 70%  k=3: 91%  k=5: 97%

pass^k: ALL k attempts must succeed
        k=1: 70%  k=3: 34%  k=5: 17%
```当您只需要它工作时，请使用 **pass@k**。当一致性至关重要时使用 **pass^k**。

---

## 并行化

在多 Claude 终端设置中分叉对话时，请确保分叉和原始对话中的操作的范围已明确定义。在代码更改方面力求尽量减少重叠。

**我喜欢的图案：**

主要讨论代码更改，分叉询问有关代码库及其当前状态的问题，或研究外部服务。

**关于任意终端计数：**

![并行终端上的鲍里斯](./assets/images/longform/07-boris-parallel.png)
*Boris (Anthropic) 运行多个 Claude 实例*

鲍里斯有关于并行化的技巧。他建议在本地运行 5 个 Claude 实例，在上游运行 5 个实例。我建议不要设置任意的终端金额。添加终端应该是出于真正的需要。

您的目标应该是：**使用最小可行的并行化量可以完成多少工作。**

**并行实例的 Git 工作树：**```bash
# Create worktrees for parallel work
git worktree add ../project-feature-a feature-a
git worktree add ../project-feature-b feature-b
git worktree add ../project-refactor refactor-branch

# Each worktree gets its own Claude instance
cd ../project-feature-a && claude
```如果您要开始扩展实例，并且您有多个 Claude 实例正在处理彼此重叠的代码，那么您必须使用 git 工作树，并为每个实例制定一个非常明确的计划。使用“/rename <此处的名称>”来命名所有聊天。

![双终端设置](./assets/images/longform/08-two-terminals.png)
*开始设置：左侧终端用于编码，右侧终端用于提问 - 使用 /rename 和 /fork*

**级联方法：**

当运行多个 Claude Code 实例时，请使用“级联”模式进行组织：

- 在右侧的新选项卡中打开新任务
- 从左到右滑动，从最旧到最新
- 一次最多专注 3-4 项任务

---

## 基础工作

**两个实例启动模式：**

对于我自己的工作流程管理，我喜欢启动一个包含 2 个打开的 Claude 实例的空存储库。

**实例1：脚手架代理**
- 铺设脚手架和地基
- 创建项目结构
- 设置配置（CLAUDE.md、规则、代理）

**实例2：深度研究代理**
- 连接到您的所有服务、网络搜索
- 创建详细的 PRD
- 创建建筑美人鱼图
- 将参考文献与实际文档剪辑一起编译

**llms.txt 模式：**

如果可用，您可以在到达文档页面后对许多文档参考执行“/llms.txt”操作，从而在许多文档参考中找到“llms.txt”。这为您提供了一个干净的、经过 LLM 优化的文档版本。

**理念：构建可重用的模式**

来自@omarsar0：“早期，我花时间构建可重用的工作流程/模式。构建起来很乏味，但随着模型和代理工具的改进，这产生了巨大的复合效应。”

**投资什么：**

- 子代理
- 技能
- 命令
- 规划模式
- MCP工具
- 上下文工程模式

---

## 代理和子代理的最佳实践

**子代理上下文问题：**

子代理的存在是为了通过返回摘要而不是转储所有内容来保存上下文。但协调器具有子代理所缺乏的语义上下文。子代理只知道文字查询，而不知道请求背后的目的。

**迭代检索模式：**

1. Orchestrator评估每个子代理的回报
2. 接受之前提出后续问题
3. 子代理返回源，获取答案，返回
4. 循环直到足够（最多 3 个循环）

**关键：** 传递客观上下文，而不仅仅是查询。

**具有连续阶段的编排器：**```markdown
Phase 1: RESEARCH (use Explore agent) → research-summary.md
Phase 2: PLAN (use planner agent) → plan.md
Phase 3: IMPLEMENT (use tdd-guide agent) → code changes
Phase 4: REVIEW (use code-reviewer agent) → review-comments.md
Phase 5: VERIFY (use build-error-resolver if needed) → done or loop back
```**关键规则：**

1. 每个智能体获得一个明确的输入并产生一个明确的输出
2. 输出成为下一阶段的输入
3. 切勿跳过阶段
4.代理之间使用`/clear`
5. 将中间输出存储在文件中

---

## 有趣的东西/不重要只是有趣的提示

### 自定义状态行

你可以使用“/statusline”来设置它 - 然后克劳德会说你没有，但可以为你设置它并询问你想要什么。

另请参阅：ccstatusline（自定义 Claude 代码状态行的社区项目）

### 语音转录

用你的声音与克劳德·科德交谈。对很多人来说比打字还要快。

- Mac 上的 superwhisper、MacWhisper
- 即使存在转录错误，克劳德也能理解意图

### 终端别名```bash
alias c='claude'
alias gb='github'
alias co='code'
alias q='cd ~/Desktop/projects'
```---

## 里程碑

![25k+ GitHub Stars](./assets/images/longform/09-25k-stars.png)
*不到一周就有超过 25,000 个 GitHub star*

---

## 资源

**代理编排：**

- claude-flow — 社区构建的企业编排平台，拥有超过 54 个专业代理

**自我提高记忆力：**

- 请参阅此存储库中的“技能/持续学习/”
- rlancemartin.github.io/2025/12/01/claude_diary/ - 会话反射模式

**系统提示参考：**

- system-prompts-and-models-of-ai-tools — AI 系统提示的社区合集（110k+ 星）

**官方：**

- 人类学院：anthropic.skilljar.com

---

## 参考文献

- [Anthropic：揭秘人工智能代理的评估](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [YK：32 个克劳德代码提示](https://agenticcoding.substack.com/p/32-claude-code-tips-from-basics-to)
- [RLanceMartin：会话反射模式](https://rlancemartin.github.io/2025/12/01/claude_diary/)
- @PerceptualPeak：子代理上下文协商
- @menhguin：代理抽象层级列表
- @omarsar0：复合效应哲学

---

*这两个指南中涵盖的所有内容都可以在 GitHub 上找到：[everything-claude-code](https://github.com/affaan-m/everything-claude-code)*