# gstack

你好,我是 [Garry Tan](https://x.com/garrytan)。我是 [Y Combinator](https://www.ycombinator.com/) 的总裁兼CEO,在这里我与数千家初创公司合作过,包括Coinbase、Instacart和Rippling——在他们还只是一两个人在车库里创业的时候——现在这些公司价值数百亿美元。在加入YC之前,我设计了Palantir的标志,是那里最早的工程经理/产品经理/设计师之一。我共同创立了Posterious,一个博客平台,后来卖给了Twitter。我还在2013年建立了YC的内部社交网络Bookface。我作为设计师、产品经理和工程经理长期从事产品开发。

而现在,我正处于一个全新的时代。

在过去60天里,我写了 **超过60万行生产代码** —— 35%是测试 —— 而且我在履行YC CEO所有职责的同时,每天还能完成 **10,000到20,000行可用代码**。这不是笔误。我上一次 `/retro`(过去7天的开发者统计)在3个项目中的情况: **140,751行新增,362次提交,约11.5万净代码行**。模型每周都在显著变得更好。我们正站在一个新时代的黎明——一个人以曾经需要一个二十人团队才能达到的规模交付产品。

**2026年 — 1,237次贡献且还在继续:**

![GitHub贡献2026 — 1,237次贡献,1月到3月大幅加速](docs/images/github-2026.png)

**2013年 — 我在YC建立Bookface时(772次贡献):**

![GitHub贡献2013 — 在YC建立Bookface的772次贡献](docs/images/github-2013.png)

同一个人。不同的时代。区别在于工具。

**gstack就是我的方法。** 这是我的开源软件工厂。它将Claude Code变成一个你真正在管理的虚拟工程团队——一位重新思考产品的CEO,一位锁定架构的工程经理,一位捕捉AI垃圾的设计师,一位发现生产bug的偏执审查者,一位打开真实浏览器并点击你的应用的QA负责人,以及一位发布PR的发布工程师。十五位专家和六个强力工具,全部作为斜杠命令,全部是Markdown, **全部免费,MIT许可证,现在可用。**

我正在学习如何发挥截至2026年3月代理系统的能力,这是我的实时实验。我分享它是因为我希望全世界都能与我一起踏上这段旅程。

Fork它。改进它。让它成为你的。不要玩家仇恨,要欣赏。

**这是给谁的:**
- **创始人和CEO** —— 特别是仍然想要交付的技术创始人。这是像二十人团队一样构建的方法。
- **首次使用Claude Code的用户** —— gstack是最佳起点。结构化角色替代空白提示。
- **技术负责人和高级工程师** —— 为每个PR带来严格的审查、QA和发布自动化

## 快速开始:你的前10分钟

1. 安装gstack(30秒——见下文)
2. 运行 `/office-hours` —— 描述你正在构建的东西。它会在你写一行代码之前重新定义问题。
3. 在任何功能想法上运行 `/plan-ceo-review`
4. 在任何有更改的分支上运行 `/review`
5. 在你的预发布URL上运行 `/qa`
6. 到这里就停。你会知道这是否适合你。

在任何已有测试设置的仓库上,预期前5分钟内有第一个有用的运行。

**如果你只再读一个部分,就读这个。**

## 安装 —— 需要30秒

**要求:** [Claude Code](https://docs.anthropic.com/en/docs/claude-code)、[Git](https://git-scm.com/)、[Bun](https://bun.sh/) v1.0+

### 步骤1:在你的机器上安装

打开Claude Code并粘贴这个。Claude会完成剩下的工作。

> 安装gstack:运行 **`git clone https://github.com/garrytan/gstack.git ~/.claude/skills/gstack && cd ~/.claude/skills/gstack && ./setup`** 然后在CLAUDE.md中添加一个"gstack"部分,说明对所有网页浏览使用gstack的/browse技能,永远不要使用mcp\_\_claude-in-chrome\_\_\*工具,并列出可用的技能:/office-hours、/plan-ceo-review、/plan-eng-review、/plan-design-review、/design-consultation、/review、/ship、/browse、/qa、/qa-only、/design-review、/setup-browser-cookies、/retro、/investigate、/document-release、/codex、/careful、/freeze、/guard、/unfreeze、/gstack-upgrade。然后问用户他们是否也想将gstack添加到当前项目,以便队友也能使用它。

### 步骤2:添加到你的仓库,以便队友也能使用(可选)

> 添加gstack到该项目:运行 **`cp -Rf ~/.claude/skills/gstack .claude/skills/gstack && rm -rf .claude/skills/gstack/.git && cd .claude/skills/gstack && ./setup`** 然后在该项目的CLAUDE.md中添加一个"gstack"部分,说明对所有网页浏览使用gstack的/browse技能,永远不要使用mcp\_\_claude-in-chrome\_\_\*工具,列出可用的技能:/office-hours、/plan-ceo-review、/plan-eng-review、/plan-design-review、/design-consultation、/review、/ship、/browse、/qa、/qa-only、/design-review、/setup-browser-cookies、/retro、/investigate、/document-release、/codex、/careful、/freeze、/guard、/unfreeze、/gstack-upgrade,并告诉Claude如果gstack技能不工作,运行 `cd .claude/skills/gstack && ./setup` 来构建二进制文件并注册技能。

真实的文件会被提交到你的仓库(不是子模块),所以 `git clone` 就能工作。一切都在 `.claude/` 里面。没有任何东西接触你的PATH或后台运行。

## 看它如何工作

```
你:    我想为我的日历构建一个每日简报应用。
你:    /office-hours
Claude: [询问痛点——具体例子,不是假设]

你:    多个Google日历,信息陈旧,位置错误。
        准备要很长时间而且结果不够好...

Claude: 我要反驳这个框架。你说"每日简报应用。"
        但你实际描述的是一个个人首席助手AI。
        [提取你没有意识到的5个能力]
        [挑战4个前提——你同意、不同意或调整]
        [生成3个带有工作量估算的实施方法]
        建议:明天交付最窄的楔子,从真实使用中学习。
        完整愿景是一个3个月的项目——从真正有效的每日简报开始。
        [编写设计文档 → 自动输入下游技能]

你:    /plan-ceo-review
        [阅读设计文档,挑战范围,运行10节审查]

你:    /plan-eng-review
        [ASCII图表用于数据流、状态机、错误路径]
        [测试矩阵、故障模式、安全问题]

你:    批准计划。退出计划模式。
        [在11个文件中编写2,400行。约8分钟。]

你:    /review
        [自动修复] 2个问题。[询问] 竞态条件 → 你批准修复。

你:    /qa https://staging.myapp.com
        [打开真实浏览器,点击流程,发现并修复一个bug]

你:    /ship
        测试: 42 → 51 (+9个新)。PR: github.com/you/app/pull/42
```

你说"每日简报应用。"代理说"你正在构建一个首席助手AI"——因为它倾听了你的痛点,而不是你的功能请求。然后它挑战你的前提,生成三种方法,建议最窄的楔子,并编写了输入到每个下游技能的设计文档。八个命令。那不是copilot。那是一个团队。

## 冲刺

gstack是一个过程,不是工具集合。技能的排列方式就像冲刺运行的方式:

**思考 → 计划 → 构建 → 审查 → 测试 → 发布 → 反思**

每个技能都输入到下一个。`/office-hours` 编写的设计文档被 `/plan-ceo-review` 读取。`/plan-eng-review` 编写的测试计划被 `/qa` 获取。`/review` 发现的bug被 `/ship` 验证已修复。没有什么会漏掉,因为每一步都知道之前发生了什么。

一次冲刺,一个人,一个功能——用gstack大约需要30分钟。但改变一切的是:你可以并行运行10-15个这样的冲刺。不同的功能,不同的分支,不同的代理——同时进行。这就是我在做实际工作的同时每天交付10,000+行生产代码的方式。

| 技能 | 你的专家 | 他们做什么 |
|------|----------|------------|
| `/office-hours` | **YC办公时间** | 从这里开始。六个强制性问题,在你写代码之前重新定义你的产品。反驳你的框架,挑战前提,生成实施替代方案。设计文档输入到每个下游技能。 |
| `/plan-ceo-review` | **CEO/创始人** | 重新思考问题。找到隐藏在请求中的10星产品。四种模式:扩展、选择性扩展、保持范围、缩减。 |
| `/plan-eng-review` | **工程经理** | 锁定架构、数据流、图表、边缘情况和测试。将隐藏的假设暴露出来。 |
| `/plan-design-review` | **高级设计师** | 每个设计维度从0-10评分,解释10是什么样的,然后编辑计划以达到那里。AI垃圾检测。交互式——每个设计选择一次AskUserQuestion。 |
| `/design-consultation` | **设计伙伴** | 从头构建完整的设计系统。了解领域,提出安全的创意风险,生成现实的产品模型。在所有其他阶段的核心进行设计。 |
| `/review` | **高级工程师** | 发现通过CI但会在生产中爆发的bug。自动修复明显的问题。标记完整性差距。 |
| `/investigate` | **调试员** | 系统性根本原因调试。铁律:没有调查就没有修复。追踪数据流,测试假设,3次修复失败后停止。 |
| `/design-review` | **会编码的设计师** | 与/plan-design-review相同的审计,然后修复它发现的问题。原子提交,前后截图。 |
| `/qa` | **QA负责人** | 测试你的应用,发现bug,用原子提交修复它们,重新验证。为每个修复自动生成回归测试。 |
| `/qa-only` | **QA报告者** | 与/qa相同的方法但只报告。当你想要纯粹的bug报告而不需要代码更改时使用。 |
| `/ship` | **发布工程师** | 同步main,运行测试,审计覆盖率,推送,打开PR。如果你没有测试框架则引导测试框架。一个命令。 |
| `/document-release` | **技术作家** | 更新所有项目文档以匹配你刚刚发布的内容。自动捕捉过时的README。 |
| `/retro` | **工程经理** | 团队感知的每周回顾。每个人分解,交付 streaks,测试健康趋势,成长机会。 |
| `/browse` | **QA工程师** | 给代理眼睛。真实Chromium浏览器,真实点击,真实截图。每命令约100ms。 |
| `/setup-browser-cookies` | **会话管理器** | 从你的真实浏览器(Chrome、Arc、Brave、Edge)导入cookie到无头会话。测试认证页面。 |

### 强力工具

| 技能 | 它做什么 |
|------|----------|
| `/codex` | **第二意见** —— 来自OpenAI Codex CLI的独立代码审查。三种模式:审查(通过/失败门)、对抗性挑战和开放咨询。当 /review 和 /codex 都运行过同一分支时,进行跨模型分析。 |
| `/careful` | **安全护栏** —— 在破坏性命令之前警告(rm -rf、DROP TABLE、force-push)。说"小心"来激活。覆盖任何警告。 |
| `/freeze` | **编辑锁** —— 将文件编辑限制在一个目录。在调试时防止意外的更改超出范围。 |
| `/guard` | **完全安全** —— `/careful` + `/freeze` 一个命令。对生产工作最大安全。 |
| `/unfreeze` | **解锁** —— 移除 `/freeze` 边界。 |
| `/gstack-upgrade` | **自我更新器** —— 升级gstack到最新。检测全局与 vendored 安装,同步两者,显示更改了什么。 |

**[每个技能的深度挖掘与示例和理念 →](docs/skills.md)**

## 什么是新的以及为什么重要

**`/office-hours` 在你写代码之前重新定义你的产品。** 你说"每日简报应用。"它倾听你实际的痛点,反驳框架,告诉你实际上在构建一个个人首席助手AI,挑战你的前提,并生成三个带有工作量估算的实施方法。它编写的设计文档直接输入到 `/plan-ceo-review` 和 `/plan-eng-review` —— 所以每个下游技能从真正的清晰开始,而不是模糊的功能请求。

**设计在核心。** `/design-consultation` 不只是选字体。它研究你的领域里有什么,提出安全的选择和创意风险,生成你实际产品的现实模型,并编写 `DESIGN.md` —— 然后 `/design-review` 和 `/plan-eng-review` 读取你的选择。设计决策流经整个系统。

**`/qa` 是一个巨大的突破。** 它让我从6个并行工作者增加到12个。Claude Code说 *"我看到问题了"* 然后实际修复它,生成一个回归测试,并验证修复——这改变了我工作的方式。代理现在有眼睛了。

**智能审查路由。** 就像在一个运行良好的初创公司一样:CEO不需要看基础设施bug修复,设计审查不需要后端更改。gstack跟踪运行了什么审查,找出什么是合适的,然后做智能的事情。审查准备仪表板告诉你发布前你的位置。

**测试一切。** `/ship` 如果你的项目没有测试框架则从头引导测试框架。每次 `/ship` 运行都会产生覆盖率审计。每个 `/qa` bug修复都会生成一个回归测试。100%测试覆盖率是目标——测试使vibe coding安全而不是yolo coding。

**`/document-release` 是你从未有过的工程师。** 它读取你项目中的每个文档文件,交叉引用diff,并更新所有漂移的东西。README、ARCHITECTURE、CONTRIBUTING、CLAUDE.md、TODOS——所有都自动保持最新。现在 `/ship` 自动调用它——文档保持最新而无需额外命令。

**当AI卡住时浏览器交接。** 遇到CAPTCHA、认证墙或MFA提示? `$B handoff` 在完全相同的页面打开可见的Chrome,保留所有cookie和标签页。解决问题,告诉Claude你完成了,`$B resume` 从中断的地方继续。代理甚至在3次连续失败后自动建议它。

**多AI第二意见。** `/codex` 从OpenAI的Codex CLI获得独立审查——一个完全不同的AI看相同的diff。三种模式:带通过/失败门的代码审查,积极尝试打破你的代码的对抗性挑战,以及带会话连续性的开放咨询。当 `/review`(Claude)和 `/codex`(OpenAI)都审查了同一分支时,你获得跨模型分析,显示哪些发现重叠,哪些是每个独有的。

**按需安全护栏。** 说"小心"和 `/careful` 在任何破坏性命令之前警告——rm -rf、DROP TABLE、force-push、git reset --hard。`/freeze` 在调试时将编辑锁定到一个目录,这样Claude不会意外"修复"不相关的代码。`/guard` 同时激活两者。`/investigate` 自动冻结到正在调查的模块。

**主动技能建议。** gstack注意到你在哪个阶段——头脑风暴、审查、调试、测试——并建议正确的技能。不喜欢?说"停止建议",它会在会话中记住。

## 10-15个并行冲刺

gstack在一个冲刺中很强大。在同时运行十个时是变革性的。

[Conductor](https://conductor.build) 并行运行多个Claude Code会话——每个都在自己的隔离工作空间中。一个会话在 `/office-hours` 上处理一个新想法,另一个在PR上做 `/review`,第三个实现一个功能,第四个在预发布上运行 `/qa`,还有六个在其他分支上。同时进行。我经常运行10-15个并行冲刺——这是目前实际的最大值。

冲刺结构是并行工作正常运作的原因。没有过程,十个代理是十个混乱源。有了过程——思考、计划、构建、审查、测试、发布——每个代理确切地知道做什么和何时停止。你管理它们就像CEO管理团队一样:检查重要决定,让其余的运行。

---

## 来乘风破浪

这是 **免费、MIT许可、开源、现在可用。** 没有高级层。没有等待名单。没有附加条件。

我开源了我如何做开发,我在这里积极升级我自己的软件工厂。你可以fork它并使其成为你自己的。这就是重点。我希望每个人都在这段旅程中。

相同的工具,不同的结果——因为gstack给你结构化的角色和审查门,而不是通用的代理混乱。那种治理是快速交付和鲁莽交付之间的区别。

模型正在快速变得更好。现在弄清楚如何与它们一起工作的人——真正地工作,而不只是浅尝辄止——将获得巨大优势。这就是那个窗口。让我们开始。

十五位专家和六个强力工具。全部斜杠命令。全部Markdown。全部免费。 **[github.com/garrytan/gstack](https://github.com/garrytan/gstack)** —— MIT许可证

> **我们正在招聘。** 想每天交付10K+代码行并帮助强化gstack?
> 来YC工作 —— [ycombinator.com/software](https://ycombinator.com/software)
> 非常有竞争力的薪水和股权。旧金山Dogpatch区。

## 文档

| 文档 | 它涵盖什么 |
|------|------------|
| [技能深度挖掘](docs/skills.md) | 每个技能的理念、示例和工作流(包括Greptile集成) |
| [架构](ARCHITECTURE.md) | 设计决策和系统内部结构 |
| [浏览器参考](BROWSER.md) | `/browse` 的完整命令参考 |
| [贡献](CONTRIBUTING.md) | 开发设置、测试、贡献者模式和开发模式 |
| [变更日志](CHANGELOG.md) | 每个版本的新内容 |

## 故障排除

**技能没有显示?** `cd ~/.claude/skills/gstack && ./setup`

**`/browse` 失败?** `cd ~/.claude/skills/gstack && bun install && bun run build`

**安装过时?** 运行 `/gstack-upgrade` —— 或在 `~/.gstack/config.yaml` 中设置 `auto_upgrade: true`

**Claude说看不到技能?** 确保你项目的 `CLAUDE.md` 有gstack部分。添加这个:

```
## gstack
对所有网页浏览使用gstack的/browse。永远不要使用mcp__claude-in-chrome__*工具。
可用技能: /office-hours、/plan-ceo-review、/plan-eng-review、/plan-design-review、
/design-consultation、/review、/ship、/browse、/qa、/qa-only、/design-review、
/setup-browser-cookies、/retro、/investigate、/document-release、/codex、/careful、
/freeze、/guard、/unfreeze、/gstack-upgrade。
```

## 许可证

MIT。永远免费。去构建点什么吧。
