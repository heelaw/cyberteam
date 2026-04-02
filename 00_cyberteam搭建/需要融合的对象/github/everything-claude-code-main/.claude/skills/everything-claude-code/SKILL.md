# 一切克劳德代码

在“everything-claude-code”存储库中工作时使用此技能，并且您需要存储库特定的指导而不是通用的编码建议。

对于使用“Continous-learning-v2”的团队，可选的同伴本能位于“.claude/homunculus/instincts/inherited/everything-claude-code-instincts.yaml”。

## 何时使用

当任务触及以下一个或多个区域时激活此技能：
- Claude Code、Cursor、Codex 和 OpenCode 之间的跨平台奇偶校验
- 挂钩脚本、挂钩文档或挂钩测试
- 必须跨表面保持同步的技能、命令、代理或规则
- 发布工作，例如版本升级、变更日志更新或插件元数据更新
- 此存储库内的持续学习或本能工作流程

## 它是如何工作的

### 1.遵循回购协议的开发合同

- 使用常规提交，例如“feat:”、“fix:”、“docs:”、“test:”、“chore:”。
- 保持提交主题简洁并接近大约 70 个字符的存储库规范。
- JavaScript 和 TypeScript 模块文件名首选驼峰命名法。
- 使用短横线命名技能目录和命令文件名。
- 将测试文件保留在现有的“*.test.js”模式上。

### 2. 将根存储库视为事实来源

从根实现开始，然后将更改镜像到有意发布的位置。

典型的镜像目标：
- `.cursor/`
- `.codex/`
- `.opencode/`
- `.agents/`

不要假设每个“.claude/”工件都需要跨平台副本。仅镜像属于所提供的多平台表面一部分的文件。

### 3. 使用测试和文档一起更新钩子

更改钩子行为时：
1.更新 `hooks/hooks.json` 或 `scripts/hooks/` 中的相关脚本
2.更新 `tests/hooks/` 或 `tests/integration/` 中的匹配测试
3. 如果行为或配置发生变化，请更新 `hooks/README.md`
4. 验证 `.cursor/hooks/` 和 `.opencode/plugins/` 的奇偶性（如果适用）

### 4. 保持发布元数据同步

准备发布时，请验证同一版本是否反映在其出现的任何位置：
- `package.json`
- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `.opencode/package.json`
- 发布流程需要时发布说明或变更日志条目

### 5. 明确持续学习的变化

如果任务涉及“技能/持续学习-v2/”或导入的本能：
- 与自动生成的批量输出相比，更喜欢准确、低噪音的本能
- 保持本能文件可通过“instinct-cli.py”导入
- 消除重复或矛盾的本能，而不是在顶部分层更多指导

## 示例

### 命名示例```text
skills/continuous-learning-v2/SKILL.md
commands/update-docs.md
scripts/hooks/session-start.js
tests/hooks/hooks.test.js
```### 提交示例```text
fix: harden session summary extraction on Stop hook
docs: align Codex config examples with current schema
test: cover Windows formatter fallback behavior
```### 技能更新清单```text
1. Update the root skill or command.
2. Mirror it only where that surface is shipped.
3. Run targeted tests first, then the broader suite if behavior changed.
4. Review docs and release notes for user-visible changes.
```### 发布清单```text
1. Bump package and plugin versions.
2. Run npm test.
3. Verify platform-specific manifests.
4. Publish the release notes with a human-readable summary.
```