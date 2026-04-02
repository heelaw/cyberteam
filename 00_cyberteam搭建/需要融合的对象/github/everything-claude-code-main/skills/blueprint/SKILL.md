# 蓝图 — 施工计划生成器

将单行目标转变为任何编码代理都可以冷执行的分步构建计划。

## 何时使用

- 将一个大功能分解为多个具有明确依赖顺序的 PR
- 规划跨越多个会话的重构或迁移
- 协调子代理之间的并行工作流
- 会话之间上下文丢失会导致返工的任何任务

**不要将**用于可在单个 PR 中完成的任务、少于 3 次工具调用或当用户说“就做吧”时。

## 它是如何工作的

Blueprint 运行 5 阶段管道：

1. **研究** - 飞行前检查（git、gh auth、远程、默认分支），然后读取项目结构、现有计划和内存文件以收集上下文。
2. **设计** — 将目标分解为一个 PR 大小的步骤（通常为 3-12 个）。分配依赖边、并行/串行排序、模型层（最强与默认）以及每步的回滚策略。
3. **草稿** — 将独立的 Markdown 计划文件写入 `plans/`。每个步骤都包括上下文简介、任务列表、验证命令和退出标准，因此新代理可以执行任何步骤，而无需阅读先前的步骤。
4. **审查** - 将针对清单和反模式目录的对抗性审查委托给最强模型子代理（例如 Opus）。在最终确定之前修复所有关键发现。
5. **注册** — 保存计划、更新内存索引并向用户呈现步数和并行度摘要。

Blueprint 自动检测 git/gh 可用性。使用 git + GitHub CLI，它可以生成完整的分支/PR/CI 工作流程计划。如果没有它们，它将切换到直接模式（就地编辑，无分支）。

## 示例

### 基本用法```
/blueprint myapp "migrate database to PostgreSQL"
```生成 `plans/myapp-migrate-database-to-postgresql.md`，步骤如下：
- 第 1 步：添加 PostgreSQL 驱动程序和连接配置
- 第2步：为每个表创建迁移脚本
- 第 3 步：更新存储库层以使用新驱动程序
- 第 4 步：添加针对 PostgreSQL 的集成测试
- 第 5 步：删除旧的数据库代码和配置

### 多代理项目```
/blueprint chatbot "extract LLM providers into a plugin system"
```尽可能制定具有并行步骤的计划（例如，“实现 Anthropic 插件”和“实现 OpenAI 插件”在插件接口步骤完成后并行运行）、模型层分配（接口设计步骤最强，默认实现）以及每个步骤后验证的不变量（例如“所有现有测试都通过”、“核心中没有提供程序导入”）。

## 主要特点

- **冷启动执行** — 每个步骤都包含一个独立的上下文简介。无需先验背景。
- **对抗性审查门** - 每个计划都由最强模型子代理根据涵盖完整性、依赖性正确性和反模式检测的清单进行审查。
- **分支/PR/CI 工作流程** — 内置于每个步骤中。当 git/gh 不存在时，优雅地降级为直接模式。
- **并行步骤检测** - 依赖关系图识别没有共享文件或输出依赖关系的步骤。
- **计划突变协议** — 通过正式协议和审计跟踪，可以拆分、插入、跳过、重新排序或放弃步骤。
- **零运行时风险** - 纯粹的 Markdown 技能。整个存储库仅包含“.md”文件 - 没有钩子，没有 shell 脚本，没有可执行代码，没有“package.json”，没有构建步骤。除了 Claude Code 的本机 Markdown 技能加载器之外，安装或调用时不会运行任何内容。

## 安装

这项技能随 Everything Claude Code 一起提供。安装ECC时无需单独安装。

### 完整 ECC 安装

如果您通过 ECC 存储库签出进行工作，请通过以下方式验证该技能是否存在：```bash
test -f skills/blueprint/SKILL.md
```要稍后更新，请在更新前查看 ECC 差异：```bash
cd /path/to/everything-claude-code
git fetch origin main
git log --oneline HEAD..origin/main       # review new commits before updating
git checkout <reviewed-full-sha>          # pin to a specific reviewed commit
```### 提供的独立安装

如果您在完整 ECC 安装之外仅提供此技能，请将审阅的文件从 ECC 存储库复制到“~/.claude/skills/blueprint/SKILL.md”。供应的副本没有 git 远程，因此通过从审查的 ECC 提交中重新复制文件来更新它们，而不是运行“git pull”。

## 要求

- Claude Code（用于“/blueprint”斜线命令）
- Git + GitHub CLI（可选 - 启用完整的分支/PR/CI 工作流程；蓝图检测缺席并自动切换到直接模式）

## 来源

受到 antbotlab/blueprint — 上游项目和参考设计的启发。