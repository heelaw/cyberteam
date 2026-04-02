# 反重力设置和使用指南

Google 的 [Antigravity](https://antigravity.dev) 是一个 AI 编码 IDE，它使用 `.agent/` 目录约定进行配置。 ECC 通过其选择性安装系统为 Antigravity 提供一流的支持。

## 快速入门```bash
# Install ECC with Antigravity target
./install.sh --target antigravity typescript

# Or with multiple language modules
./install.sh --target antigravity typescript python go
```这会将 ECC 组件安装到项目的“.agent/”目录中，为 Antigravity 做好准备。

## 安装映射如何工作

ECC 重新映射其组件结构以匹配 Antigravity 的预期布局：

| ECC 来源 |反重力目的地|它包含什么 |
|------------|------------------------------------|--------------------|
| `规则/` | `.agent/rules/` |语言规则和编码标准（扁平化）|
| `命令/` | `.agent/workflows/` | Slash 命令成为反重力工作流程 |
| `代理/` | `.agent/skills/` |特工定义成为反重力技能|

> **关于 `.agents/` 与 `.agent/` 与 `agents/` 的注意事项**：安装程序仅显式处理三个源路径：`rules` → `.agent/rules/`、`commands` → `.agent/workflows/` 和 `agents`（无点前缀）→ `.agent/skills/`。 ECC 存储库中的点前缀“.agents/”目录是 Codex/反重力技能定义和“openai.yaml”配置的“静态布局”——它不是由安装程序直接映射的。任何“.agents/”路径都会进入默认的脚手架操作。如果您希望“.agents/skills/”内容在反重力运行时可用，则必须手动将其复制到“.agent/skills/”。

### 与 Claude Code 的主要区别

- **规则被扁平化**：Claude Code 将规则嵌套在子目录下（`rules/common/`、`rules/typescript/`）。 Antigravity 需要一个扁平的“rules/”目录——安装程序会自动处理这个目录。
- **命令成为工作流程**：ECC 的 `/command` 文件位于 `.agent/workflows/` 中，这相当于反重力的斜杠命令。
- **代理成为技能**：ECC 代理定义映射到 `.agent/skills/`，Antigravity 在其中查找技能配置。

## 安装后的目录结构```
your-project/
├── .agent/
│   ├── rules/
│   │   ├── coding-standards.md
│   │   ├── testing.md
│   │   ├── security.md
│   │   └── typescript.md          # language-specific rules
│   ├── workflows/
│   │   ├── plan.md
│   │   ├── code-review.md
│   │   ├── tdd.md
│   │   └── ...
│   ├── skills/
│   │   ├── planner.md
│   │   ├── code-reviewer.md
│   │   ├── tdd-guide.md
│   │   └── ...
│   └── ecc-install-state.json     # tracks what ECC installed
```## The `openai.yaml` Agent Config

Each skill directory under `.agents/skills/` contains an `agents/openai.yaml` file at the path `.agents/skills/<skill-name>/agents/openai.yaml` that configures the skill for Antigravity:```yaml
interface:
  display_name: "API Design"
  short_description: "REST API design patterns and best practices"
  brand_color: "#F97316"
  default_prompt: "Design REST API: resources, status codes, pagination"
policy:
  allow_implicit_invocation: true
```|领域|目的|
|--------|---------|
| `显示名称` | Antigravity 的 UI 中显示人类可读的名称 |
| `简短描述` |简要描述该技能的作用 |
| `品牌颜色` |技能视觉徽章的十六进制颜色 |
| `默认提示` |手动调用技能时的建议提示 |
| `允许隐式调用` |当“true”时，反重力可以根据上下文自动激活技能 |

## 管理您的安装

### 检查已安装的内容```bash
node scripts/list-installed.js --target antigravity
```### 修复损坏的安装```bash
# First, diagnose what's wrong
node scripts/doctor.js --target antigravity

# Then, restore missing or drifted files
node scripts/repair.js --target antigravity
```### 卸载```bash
node scripts/uninstall.js --target antigravity
```### 安装状态

安装程序会写入“.agent/ecc-install-state.json”来跟踪 ECC 拥有哪些文件。这可以实现安全卸载和修复 — ECC 永远不会触及不是它创建的文件。

## 添加反重力自定义技能

如果您正在贡献一项新技能并希望在反重力上使用它：

1. 像往常一样在`skills/your-skill-name/SKILL.md`下创建技能
2. 在 `agents/your-skill-name.md` 添加代理定义 — 这是安装程序在运行时映射到 `.agent/skills/` 的路径，使您的技能可以在反重力工具中使用
3. 在 `.agents/skills/your-skill-name/agents/openai.yaml` 添加 Antigravity 代理配置 — 这是 Codex 用于隐式调用元数据的静态存储库布局
4. 将 `SKILL.md` 内容镜像到 `.agents/skills/your-skill-name/SKILL.md` — 此静态副本由 Codex 使用，并作为 Antigravity 的参考
5. 在您的 PR 中提及您添加了反重力支持

> **关键区别**：安装程序部署 `agents/` （无点）→ `.agent/skills/` — 这就是使技能在运行时可用的原因。 `.agents/` （点前缀）目录是 Codex `openai.yaml` 配置的单独静态布局，安装程序不会自动部署。

请参阅 [CONTRIBUTING.md](../CONTRIBUTING.md) 了解完整的贡献指南。

## 与其他目标的比较

|特色 |克劳德·代码 |光标|法典|反重力|
|--------|-------------|--------|--------|-------------|
|安装目标|克劳德之家 | `光标项目` | `法典主页` | `反重力` |
|配置根目录| `~/.claude/` | `.cursor/` | `~/.codex/` | `.agent/` |
|范围 |用户级|项目级|用户级|项目级|
|规则格式|嵌套目录 |平|平|平|
|命令 | `命令/` |不适用 |不适用 | `工作流程/` |
|特工/技能 | `代理/` |不适用 |不适用 | `技能/` |
|安装状态 | `ecc-install-state.json` | `ecc-install-state.json` | `ecc-install-state.json` | `ecc-install-state.json` |

## 故障排除

### 反重力技能未加载

- 验证项目根目录（而不是主目录）中是否存在“.agent/”目录
- 检查是否创建了“ecc-install-state.json” - 如果丢失，请重新运行安装程序
- 确保文件具有“.md”扩展名和有效的 frontmatter

### 规则不适用

- 规则必须位于`.agent/rules/`中，不能嵌套在子目录中
- 运行 `node script/doctor.js --target antigravity` 来验证安装

### 工作流程不可用

- Antigravity 在 `.agent/workflows/` 中查找工作流程，而不是在 `commands/` 中
- 如果您手动复制了 ECC 命令，请重命名该目录

## 相关资源

- [选择性安装架构](./SELECTIVE-INSTALL-ARCHITECTURE.md) — 安装系统如何在幕后工作
- [选择性安装设计](./SELECTIVE-INSTALL-DESIGN.md) — 设计决策和目标适配器合同
- [CONTRIBUTING.md](../CONTRIBUTING.md) — 如何贡献技能、代理和命令