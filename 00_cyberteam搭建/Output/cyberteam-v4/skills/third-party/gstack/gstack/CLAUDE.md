# gstack开发

## 命令

```bash
bun install          # 安装依赖
bun test             # 运行免费测试(browse + snapshot + skill验证)
bun run test:evals   # 运行付费评估:LLM评判 + E2E(基于diff,最多~$4/次)
bun run test:evals:all  # 运行所有付费评估,不管diff
bun run test:e2e     # 仅运行E2E测试(基于diff,最多~$3.85/次)
bun run test:e2e:all # 不管diff运行所有E2E测试
bun run eval:select  # 显示基于当前diff会运行哪些测试
bun run dev <cmd>    # 在dev模式下运行CLI,例如 bun run dev goto https://example.com
bun run build        # 生成文档 + 编译二进制文件
bun run gen:skill-docs  # 从模板重新生成SKILL.md文件
bun run skill:check  # 所有技能的健康仪表板
bun run dev:skill    # 观察模式:自动重新生成 + 变更时验证
bun run eval:list    # 列出所有eval运行从~/.gstack-dev/evals/
bun run eval:compare # 比较两个eval运行(自动选择最新的)
bun run eval:summary # 跨所有eval运行聚合统计
```

`test:evals` 需要 `ANTHROPIC_API_KEY`。E2E测试通过 `--output-format stream-json --verbose` 流式传输实时进度(按工具调用)。结果持久化到 `~/.gstack-dev/evals/` 并与前一次运行自动比较。

**基于diff的测试选择:** `test:evals` 和 `test:e2e` 基于与基础分支的 `git diff` 自动选择测试。每个测试在 `test/helpers/touchfiles.ts` 中声明其文件依赖。更改全局touchfiles(session-runner、eval-store、llm-judge、gen-skill-docs)触发所有测试。使用 `EVALS_ALL=1` 或 `:all` 脚本变体强制运行所有测试。运行 `eval:select` 预览会运行哪些测试。

## 测试

```bash
bun test             # 每次提交前运行——免费,<2s
bun run test:evals   # 发布前运行——付费,基于diff(最多~$4/次)
```

`bun test` 运行技能验证、gen-skill-docs质量检查和browse集成测试。`bun run test:evals` 运行LLM评判质量评估和通过 `claude -p` 的E2E测试。两者都必须在创建PR前通过。

## 项目结构

```
gstack/
├── browse/          # 无头浏览器CLI(Playwright)
│   ├── src/         # CLI + 服务器 + 命令
│   │   ├── commands.ts  # 命令注册表(单一真相来源)
│   │   └── snapshot.ts  # SNAPSHOT_FLAGS元数据数组
│   ├── test/        # 集成测试 + fixtures
│   └── dist/        # 编译的二进制文件
├── scripts/         # 构建 + DX工具
│   ├── gen-skill-docs.ts  # 模板 → SKILL.md生成器
│   ├── skill-check.ts     # 健康仪表板
│   └── dev-skill.ts       # 观察模式
├── test/            # 技能验证 + 评估测试
│   ├── helpers/     # skill-parser.ts、session-runner.ts、llm-judge.ts、eval-store.ts
│   ├── fixtures/    # Ground truth JSON、植入bug fixtures、评估基线
│   ├── skill-validation.test.ts  # 第1层:静态验证(免费,<1s)
│   ├── gen-skill-docs.test.ts    # 第1层:生成器质量(免费,<1s)
│   ├── skill-llm-eval.test.ts   # 第3层:LLM-as-judge(~$0.15/次)
│   └── skill-e2e.test.ts         # 第2层:通过claude -p的E2E(~$3.85/次)
├── qa-only/         # /qa-only技能(仅报告QA,无修复)
├── plan-design-review/  # /plan-design-review技能(仅报告设计审计)
├── design-review/    # /design-review技能(设计审计 + 修复循环)
├── ship/            # Ship工作流技能
├── review/          # PR审查技能
├── plan-ceo-review/ # /plan-ceo-review技能
├── plan-eng-review/ # /plan-eng-review技能
├── office-hours/    # /office-hours技能(YC办公时间——创业诊断 + 构建者头脑风暴)
├── investigate/     # /investigate技能(系统性根本原因调试)
├── retro/           # 回顾技能
├── document-release/ # /document-release技能(发布后文档更新)
├── setup            # 一次性设置:构建二进制 + symlink技能
├── SKILL.md         # 从SKILL.md.tmpl生成(不要直接编辑)
├── SKILL.md.tmpl    # 模板:编辑这个,运行gen:skill-docs
└── package.json     # 浏览器的构建脚本
```

## SKILL.md工作流

SKILL.md文件 **从 `.tmpl` 模板生成**。更新文档:

1. 编辑 `.tmpl` 文件(例如 `SKILL.md.tmpl` 或 `browse/SKILL.md.tmpl`)
2. 运行 `bun run gen:skill-docs`(或 `bun run build` 自动执行此操作)
3. 提交 `.tmpl` 和生成的 `.md` 文件

添加新的browse命令:添加到 `browse/src/commands.ts` 并重新构建。
添加snapshot标志:添加到 `browse/src/snapshot.ts` 中的 `SNAPSHOT_FLAGS` 并重新构建。

## 平台无关设计

技能绝不能硬编码特定框架的命令、文件模式或目录结构。相反:

1. **读取CLAUDE.md** 获取项目特定配置(测试命令、评估命令等)
2. **如果缺失,AskUserQuestion** —— 让用户告诉你或让gstack搜索仓库
3. **将答案持久化到CLAUDE.md** 这样我们永远不必再问

这适用于测试命令、评估命令、部署命令和任何其他特定项目的行为。项目拥有其配置;gstack读取它。

## 编写SKILL模板

SKILL.md.tmpl文件是 **由Claude读取的提示模板**,不是bash脚本。每个bash代码块在单独的shell中运行——变量不在块之间持久化。

规则:
- **对逻辑和状态使用自然语言。** 不要使用shell变量在代码块之间传递状态。相反,告诉Claude要记住什么并在散文中的引用(例如,"步骤0中检测到的基础分支")。
- **不要硬编码分支名称。** 通过 `gh pr view` 或 `gh repo view` 动态检测 `main`/`master`/etc。对PR定位技能使用 `{{BASE_BRANCH_DETECT}}`。在散文中使用"基础分支",在代码块占位符中使用 `<base>`。
- **保持bash块自包含。** 每个代码块应该独立工作。如果块需要前一步的上下文,在上面的散文中重新陈述它。
- **用英语表达条件。** 不要在bash中嵌套 `if/elif/else`,写编号决策步骤:"1. 如果X,做Y。2. 否则,做Z。"

## 浏览器交互

当你需要与浏览器交互时(QA、dogfooding、cookie设置),使用 `/browse` 技能或直接通过 `$B <command>` 运行browse二进制文件。永远不要使用 `mcp__claude-in-chrome__*` 工具——它们慢、不可靠,不是这个项目使用的。

## Vendored symlink感知

开发gstack时,`.claude/skills/gstack` 可能是一个symlink回到这个工作目录(gitignored)。这意味着技能更改 **立即生效** —— 适合快速迭代,在大型重构期间有风险,那时半写好的技能可能破坏同时使用gstack的其他Claude Code会话。

**每会话检查一次:** 运行 `ls -la .claude/skills/gstack` 看它是一个symlink还是一个真实副本。如果它是一个symlink回到你的工作目录,请注意:
- 模板更改 + `bun run gen:skill-docs` 立即影响所有gstack调用
- 对SKILL.md.tmpl文件的破坏性更改可以破坏并发的gstack会话
- 在大型重构期间,删除symlink(`rm .claude/skills/gstack`),这样使用 `~/.claude/skills/gstack/` 中的全局安装

**对于计划审查:** 审查修改技能模板或gen-skill-docs管道的计划时,考虑是否应该在隔离中测试更改然后上线(特别是如果用户在其他窗口中积极使用gstack)。

## 提交风格

**总是bisect提交。** 每个提交应该是一个单一的逻辑更改。当你做了多个更改时(例如重命名 + 重写 + 新测试),将它们分成单独的提交再推送。每个提交应该可以独立理解和回滚。

良好bisection的例子:
- 重命名/移动与行为更改分开
- 测试基础设施(touchfiles、helpers)与测试实现分开
- 模板更改与生成文件重新生成分开
- 机械重构与新功能分开

当用户说"bisect commit"或"bisect and push"时,将staged/unstaged更改分成逻辑提交并推送。

## CHANGELOG风格

CHANGELOG.md是 **给用户的**,不是贡献者。像产品发布说明一样写:

- 以用户现在可以 **做** 以前不能做的事情为首。不要谈论实现细节。"你现在可以..."而不是"重构了..."。
- **永远不要提及TODOS.md、内部跟踪、评估基础设施或贡献者面向的细节。** 这些对用户不可见,对他们没有意义。
- 将贡献者/内部更改放在底部单独的"For contributors"部分。
- 每个条目都应该让人认为"哦,不错,我想试试那个。"
- 不要用术语:说"每个问题现在告诉你你在哪个项目和分支"而不是"通过前导码解析器在技能模板间标准化了AskUserQuestion格式。"

## AI工作量压缩

在估算或讨论工作量时,总是同时显示人工团队和CC+gstack时间:

| 任务类型 | 人工团队 | CC+gstack | 压缩 |
|---------|---------|-----------|------|
| 样板/脚手架 | 2天 | 15分钟 | ~100倍 |
| 测试编写 | 1天 | 15分钟 | ~50倍 |
| 功能实现 | 1周 | 30分钟 | ~30倍 |
| Bug修复 + 回归测试 | 4小时 | 15分钟 | ~20倍 |
| 架构/设计 | 2天 | 4小时 | ~5倍 |
| 研究/探索 | 1天 | 3小时 | ~3倍 |

完整性是廉价的。当完整实现是一个"湖"(可实现的)而不是"海洋"(多季度迁移)时,不建议走捷径。参见技能前导码中的完整性原则以获取完整理念。

## 本地计划

贡献者可以将长期愿景文档和设计文档存储在 `~/.gstack-dev/plans/` 中。这些是本地唯一的(不检查)。在审查TODOS.md时,检查 `plans/` 中可能准备好提升到TODOs或实现的候选。

## E2E评估失败归因协议

当E2E评估在任何工作流中失败时, `/ship` 或其他, **永远不要在未经证明的情况下声称"与我们的更改无关"。** 这些系统有看不见的耦合——前导码文本更改影响代理行为,新helper更改时间,重新生成的SKILL.md移动提示上下文。

**归因于"预先存在"之前的要求:**
1. 在main上运行相同的评估(或基础分支)并显示它在那里也失败
2. 如果它在main上通过但在分支上失败——那是你的更改。追踪归因。
3. 如果你不能在main上运行,说"未验证——可能相关也可能不相关"并在PR正文中标记为风险

没有receipt的"预先存在"是懒惰的声称。证明它,或者不要说它。

## 部署到活动技能

活动技能位于 `~/.claude/skills/gstack/`。进行更改后:

1. 推送你的分支
2. 在技能目录中获取并重置: `cd ~/.claude/skills/gstack && git fetch origin && git reset --hard origin/main`
3. 重新构建: `cd ~/.claude/skills/gstack && bun run build`

或直接复制二进制文件: `cp browse/dist/browse ~/.claude/skills/gstack/browse/dist/browse`
