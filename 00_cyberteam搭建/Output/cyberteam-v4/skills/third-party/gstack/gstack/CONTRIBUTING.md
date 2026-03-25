# 为gstack做贡献

感谢您想让gstack变得更好。无论您是在修复技能提示中的拼写错误还是构建全新的工作流,本指南都将帮助您快速启动。

## 快速开始

gstack技能是Claude Code从 `skills/` 目录发现的Markdown文件。通常它们位于 `~/.claude/skills/gstack/` (您的全局安装)。但当您开发gstack本身时,您希望Claude Code使用您工作树中的技能 —— 这样编辑立即生效,无需复制或部署任何东西。

这就是dev模式的作用。它symlink您的仓库到本地 `.claude/skills/` 目录,以便Claude Code直接从您的checkout读取技能。

```bash
git clone <repo> && cd gstack
bun install                    # 安装依赖
bin/dev-setup                  # 激活dev模式
```

现在编辑任何 `SKILL.md`,在Claude Code中调用它(例如 `/review`),并实时查看您的更改。开发完成时:

```bash
bin/dev-teardown               # 停用 —— 返回您的全局安装
```

## 贡献者模式

贡献者模式将gstack变成一个自我改进的工具。启用它,Claude Code将定期反思其gstack体验——在每个主要工作流步骤结束时对其进行0-10评分。当某事不是10时,它会思考原因并向 `~/.gstack/contributor-logs/` 提交一份报告,说明发生了什么、重现步骤以及如何改进。

```bash
~/.claude/skills/gstack/bin/gstack-config set gstack_contributor true
```

日志是 **给您看的**。当某事困扰您到需要修复时,报告已经写好了。Fork gstack,将您的fork symlink到您遇到问题的项目中,修复它,然后打开PR。

### 贡献者工作流

1. **正常使用gstack** —— 贡献者模式自动反思并记录问题
2. **检查您的日志:** `ls ~/.gstack/contributor-logs/`
3. **Fork并克隆gstack**(如果您还没有)
4. **将您的fork symlink到您遇到bug的项目:**
   ```bash
   # 在您的核心项目中(gstack让您烦恼的那个)
   ln -sfn /path/to/your/gstack-fork .claude/skills/gstack
   cd .claude/skills/gstack && bun install && bun run build
   ```
5. **修复问题** —— 您的更改在该项目中立即生效
6. **通过实际使用gstack来测试** —— 做让您烦恼的事情,验证它已修复
7. **从您的fork打开PR**

这是贡献的最佳方式:在做真实工作的同时修复gstack,在您实际感受到痛点的项目中。

### 会话感知

当您同时打开3+个gstack会话时,每个问题都会告诉您是哪个项目、哪个分支以及发生了什么。不再盯着问题思考"等等,这是哪个窗口?"格式在所有15个技能中保持一致。

## 在gstack仓库内使用gstack

当您编辑gstack技能并想通过在实际项目中使用gstack来测试它们时,`bin/dev-setup` 会进行连接。它创建 `.claude/skills/` symlinks(gitignored)指向您的工作树,因此Claude Code使用您的本地编辑而不是全局安装。

```
gstack/                          <- 您的工作树
├── .claude/skills/              <- 由dev-setup创建(gitignored)
│   ├── gstack -> ../../         <- symlink回仓库根
│   ├── review -> gstack/review
│   ├── ship -> gstack/ship
│   └── ...                      <- 每个技能一个symlink
├── review/
│   └── SKILL.md                 <- 编辑这个,用/review测试
├── ship/
│   └── SKILL.md
├── browse/
│   ├── src/                     <- TypeScript源
│   └── dist/                    <- 编译的二进制文件(gitignored)
└── ...
```

## 日常工作流

```bash
# 1. 进入dev模式
bin/dev-setup

# 2. 编辑技能
vim review/SKILL.md

# 3. 在Claude Code中测试 —— 更改是实时的
#    > /review

# 4. 编辑browse源代码?重新构建二进制文件
bun run build

# 5. 一天结束?拆除
bin/dev-teardown
```

## 测试与评估

### 设置

```bash
# 1. 复制.env.example并添加您的API密钥
cp .env.example .env
# 编辑.env → 设置ANTHROPIC_API_KEY=sk-ant-...

# 2. 安装依赖(如果您还没有)
bun install
```

Bun自动加载 `.env` —— 无需额外配置。Conductor工作空间从主工作树自动继承 `.env`(见下面的"Conductor工作空间")。

### 测试层

| 层 | 命令 | 成本 | 它测试什么 |
|------|---------|------|------------|
| 1 — 静态 | `bun test` | 免费 | 命令验证、快照标志、SKILL.md正确性、TODOS-format.md引用、观察性单元测试 |
| 2 — E2E | `bun run test:e2e` | ~$3.85 | 通过 `claude -p` 子进程的完整技能执行 |
| 3 — LLM评估 | `bun run test:evals` | ~$0.15 独立 | LLM-as-judge对生成的SKILL.md文档评分 |
| 2+3 | `bun run test:evals` | ~$4 组合 | E2E + LLM-as-judge(两者都运行) |

```bash
bun test                     # 仅第1层(每次提交运行,<5s)
bun run test:e2e             # 第2层:仅E2E(需要EVALS=1,不能在Claude Code内运行)
bun run test:evals           # 第2 + 3层组合(~$4/次)
```

### 第1层:静态验证(免费)

随 `bun test` 自动运行。无需API密钥。

- **技能解析器测试** (`test/skill-parser.test.ts`) —— 从SKILL.md bash代码块中提取每个 `$B` 命令,并对照 `browse/src/commands.ts` 中的命令注册表验证。捕捉拼写错误、已删除的命令和无效的快照标志。
- **技能验证测试** (`test/skill-validation.test.ts`) —— 验证SKILL.md文件仅引用真实命令和标志,以及命令描述符合质量阈值。
- **生成器测试** (`test/gen-skill-docs.test.ts`) —— 测试模板系统:验证占位符正确解析,输出为标志包含值提示(例如 `-d <N>` 而不是只是 `-d`),为关键命令添加丰富描述(例如 `is` 列出有效状态,`press` 列出关键示例)。

### 第2层:通过 `claude -p` 的E2E(~$3.85/次)

生成 `claude -p` 作为子进程,使用 `--output-format stream-json --verbose`,流式传输NDJSON以获取实时进度,并扫描浏览错误。这是"这个技能实际上端到端工作吗?"的最接近的方式。

```bash
# 必须从普通终端运行 —— 不能嵌套在Claude Code或Conductor内
EVALS=1 bun test test/skill-e2e.test.ts
```

- 由 `EVALS=1` env var门禁(防止意外昂贵运行)
- 如果在Claude Code内运行则自动跳过(`claude -p` 不能嵌套)
- API连接预检查 —— 在消耗预算前快速失败ConnectionRefused
- 实时进度到stderr: `[Ns] turn T tool #C: Name(...)`
- 保存完整NDJSON转录和失败JSON用于调试
- 测试位于 `test/skill-e2e.test.ts`,运行器逻辑位于 `test/helpers/session-runner.ts`

### E2E观察性

当E2E测试运行时,它们在 `~/.gstack-dev/` 中生成机器可读的artifacts:

| Artifact | 路径 | 用途 |
|----------|------|------|
| Heartbeat | `e2e-live.json` | 当前测试状态(每个工具调用更新) |
| Partial results | `evals/_partial-e2e.json` | 完成的测试(生存kills) |
| Progress log | `e2e-runs/{runId}/progress.log` | 仅追加文本日志 |
| NDJSON transcripts | `e2e-runs/{runId}/{test}.ndjson` | 每个测试的原始 `claude -p` 输出 |
| Failure JSON | `e2e-runs/{runId}/{test}-failure.json` | 失败时的诊断数据 |

**实时仪表板:** 在第二个终端运行 `bun run eval:watch` 以查看显示已完成测试、当前运行测试和成本的实时仪表板。使用 `--tail` 也显示progress.log的最后10行。

**评估历史工具:**

```bash
bun run eval:list            # 列出所有eval运行(轮次、持续时间、每次运行的成本)
bun run eval:compare         # 比较两个运行 —— 显示每个测试的delta + Takeaway评论
bun run eval:summary         # 跨运行聚合统计 + 每个测试效率平均
```

**评估比较评论:** `eval:compare` 生成解释两个运行之间变化的专业语言Takeaway部分 —— 标记回归、注明改进、指出效率提升(更少轮次、更快、更便宜),并产生整体总结。这由 `eval-store.ts` 中的 `generateCommentary()` 驱动。

Artifacts永远不清理 —— 它们在 `~/.gstack-dev/` 中积累用于事后调试和趋势分析。

### 第3层:LLM-as-judge(~$0.15/次)

使用Claude Sonnet对生成的SKILL.md文档在三个维度上评分:

- **清晰度** —— AI代理能否理解指令而没有歧义?
- **完整性** —— 所有命令、标志和使用模式都记录了吗?
- **可操作性** —— 代理能否仅使用文档中的信息执行任务?

每个维度评分1-5。阈值:每个维度必须评分 **≥ 4**。还有一个回归测试,将生成的文档与 `origin/main` 的手动维护基线进行比较 —— 生成的必须评分相等或更高。

```bash
# 需要.env中的ANTHROPIC_API_KEY —— 包含在bun run test:evals中
```

- 使用 `claude-sonnet-4-6` 以获得评分稳定性
- 测试位于 `test/skill-llm-eval.test.ts`
- 直接调用Anthropic API(不是 `claude -p`),所以它可以从任何地方运行,包括Claude Code内

### CI

GitHub Action(`.github/workflows/skill-docs.yml`)在每次push和PR时运行 `bun run gen:skill-docs --dry-run`。如果生成的SKILL.md文件与已提交的不同,CI失败。这在合并前捕捉过时的文档。

测试直接针对browse二进制文件运行 —— 不需要dev模式。

## 编辑SKILL.md文件

SKILL.md文件是 **从 `.tmpl` 模板生成的**。不要直接编辑 `.md` —— 您的更改将在下次构建时被覆盖。

```bash
# 1. 编辑模板
vim SKILL.md.tmpl              # 或browse/SKILL.md.tmpl

# 2. 重新生成
bun run gen:skill-docs

# 3. 检查健康
bun run skill:check

# 或使用观察模式 —— 保存时自动重新生成
bun run dev:skill
```

对于模板编写最佳实践(自然语言优于bash-ism、动态分支检测、`{{BASE_BRANCH_DETECT}}` 用法),请参阅CLAUDE.md的"编写SKILL模板"部分。

要添加browse命令,添加到 `browse/src/commands.ts`。要添加快照标志,添加到 `browse/src/snapshot.ts` 中的 `SNAPSHOT_FLAGS`。然后重新构建。

## Conductor工作空间

如果您使用[Conductor](https://conductor.build)并行运行多个Claude Code会话,`conductor.json` 自动连接工作空间生命周期:

| Hook | 脚本 | 它做什么 |
|------|------|----------|
| `setup` | `bin/dev-setup` | 从主工作树复制 `.env`,安装依赖,symlink技能 |
| `archive` | `bin/dev-teardown` | 移除技能symlinks,清理 `.claude/` 目录 |

当Conductor创建新工作空间时,`bin/dev-setup` 自动运行。它检测主工作树(via `git worktree list`),复制您的 `.env` 以便API密钥可以延续,并设置dev模式 —— 无需手动步骤。

**首次设置:** 将您的 `ANTHROPIC_API_KEY` 放在主仓库的 `.env` 中(见 `.env.example`)。每个Conductor工作空间自动继承它。

## 需要知道的事情

- **SKILL.md文件是生成的。** 编辑 `.tmpl` 模板,而不是 `.md`。运行 `bun run gen:skill-docs` 重新生成。
- **TODOS.md是统一的待办事项列表。** 按技能/组件组织,带P0-P4优先级。`/ship` 自动检测完成的项目。所有规划/审查/回顾技能都读取它以获取上下文。
- **浏览源代码更改需要重新构建。** 如果您触摸 `browse/src/*.ts`,运行 `bun run build`。
- **Dev模式会影响您的全局安装。** 项目本地技能优先于 `~/.claude/skills/gstack`。`bin/dev-teardown` 恢复全局安装。
- **Conductor工作空间是独立的。** 每个工作空间是自己的git工作树。`bin/dev-setup` 通过 `conductor.json` 自动运行。
- **`.env` 在工作树间传播。** 在主仓库中设置一次,所有Conductor工作空间都会获得它。
- **`.claude/skills/` 是gitignored。** symlinks永远不会被提交。

## 在真实项目中测试您的更改

**这是推荐的方式开发gstack。** 将您的gstack checkout symlink到您实际使用它的项目中,这样您的更改在您做真实工作时是实时的:

```bash
# 在您的核心项目中
ln -sfn /path/to/your/gstack-checkout .claude/skills/gstack
cd .claude/skills/gstack && bun install && bun run build
```

现在在此项目中的每个gstack技能调用都使用您的工作树。编辑模板,运行 `bun run gen:skill-docs`,下一次 `/review` 或 `/qa` 调用立即获取它。

**要返回稳定的全局安装**,只需移除symlink:

```bash
rm .claude/skills/gstack
```

Claude Code自动回退到 `~/.claude/skills/gstack/`。

### 替代:将您的全局安装指向一个分支

如果您不想要每个项目的symlinks,可以切换全局安装:

```bash
cd ~/.claude/skills/gstack
git fetch origin
git checkout origin/<branch>
bun install && bun run build
```

这会影响所有项目。要还原: `git checkout main && git pull && bun run build`。

## 发布您的更改

当您对技能编辑满意时:

```bash
/ship
```

这运行测试,审查diff,分类Greptile评论(带2层升级),管理TODOS.md,更新版本,并打开PR。见 `ship/SKILL.md` 获取完整工作流。
