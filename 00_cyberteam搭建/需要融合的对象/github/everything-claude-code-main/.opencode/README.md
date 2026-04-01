# OpenCode ECC Plugin

> ⚠️ This README is specific to OpenCode usage.  
> If you installed ECC via npm (e.g. `npm install opencode-ecc`), refer to the root README instead.

Everything Claude Code (ECC) plugin for OpenCode - agents, commands, hooks, and skills.

## Installation

## Installation Overview

There are two ways to use Everything Claude Code (ECC):

1. **npm package (recommended for most users)**  
   Install via npm/bun/yarn and use the `ecc-install` CLI to set up rules and agents.

2. **Direct clone / plugin mode**  
   Clone the repository and run OpenCode directly inside it.

Choose the method that matches your workflow below.

### Option 1: npm Package```bash
npm install ecc-universal
```添加到您的“opencode.json”：```json
{
  "plugin": ["ecc-universal"]
}
```这将从 npm 加载 ECC OpenCode 插件模块：
- 挂钩/事件集成
- 插件导出的捆绑自定义工具

它**不会**在项目配置中自动注册完整的 ECC 命令/代理/指令目录。对于完整的 OpenCode 设置，可以：
- 在此存储库中运行 OpenCode，或者
- 将相关的`.opencode/commands/`、`.opencode/prompts/`、`.opencode/instructions/`以及`instructions`、`agent`和`command`配置条目复制到您自己的项目中

安装后，`ecc-install` CLI 也可用：```bash
npx ecc-install typescript
```### 选项 2：直接使用

在存储库中克隆并运行 OpenCode：```bash
git clone https://github.com/affaan-m/everything-claude-code
cd everything-claude-code
opencode
```## 特点

### 特工 (12)

|代理|描述 |
|--------|-------------|
|策划师|实施规划|
|建筑师 |系统设计|
|代码审查员 |代码审查 |
|安全审查员 |证券分析|
| TDD 指南 |测试驱动开发 |
|构建错误解析器 |构建错误修复 |
| e2e-跑步者 |端到端测试|
|文档更新程序 |文档 |
|重构清理器 |死代码清理 |
|去评论家 |进行代码审查 |
|去构建解析器 |去构建错误|
|数据库审阅者 |数据库优化 |

### 命令 (31)

|命令 |描述 |
|---------|-------------|
| `/计划` |制定实施计划 |
| `/tdd` | TDD 工作流程 |
| `/代码审查` |查看代码更改 |
| `/安全` |安全审查|
| `/构建修复` |修复构建错误 |
| `/e2e` |端到端测试 |
| `/refactor-clean` |删除死代码 |
| `/编排` |多代理工作流程 |
| `/学习` |提取模式 |
| `/检查点` |保存进度 |
| `/验证` |验证循环|
| `/评估` |评价|
| `/更新文档` |更新文档 |
| `/更新代码映射` |更新代码图 |
| `/测试覆盖率` |覆盖率分析|
| `/setup-pm` |包管理器 |
| `/去评论` |进行代码审查 |
| `/去测试` |进行 TDD |
| `/go-build` |去构建修复|
| `/技能创建` |生成技能 |
| `/本能状态` |查看本能 |
| `/本能导入` |进口本能|
| `/本能导出` |出口本能|
| `/进化` |集群本能|
| `/推广` |促进项目本能|
| `/项目` |列出已知项目 |
| `/harness-audit` |审核线束可靠性和评估准备情况|
| `/循环开始` |启动受控代理循环 |
| `/循环状态` |检查循环状态和检查点 |
| `/质量门` |在文件/存储库范围上运行质量关 |
| `/模型路线` |按模型和预算安排任务|

### 插件挂钩

|钩|活动 |目的|
|------|--------|---------|
|更漂亮 | `文件.编辑` |自动格式化 JS/TS |
|打字稿 | `工具.执行后` |检查类型错误 |
|控制台日志 | `文件.编辑` |关于调试语句的警告 |
|通知 | `会话.空闲` |桌面通知 |
|安全| `工具.执行.之前` |检查秘密 |

### 自定义工具

|工具|描述 |
|------|-------------|
|运行测试 |使用选项运行测试套件 |
|检查覆盖率|分析测试覆盖率 |
|安全审计 |安全漏洞扫描 |

## 钩子事件映射

OpenCode 的插件系统映射到 Claude Code hooks：

|克劳德·代码 |开放代码 |
|----------|----------|
|预工具使用 | `工具.执行.之前` |
|发布工具使用 | `工具.执行后` |
|停止| `会话.空闲` |
|会话开始 | `会话.创建` |
|会议结束 | `会话.已删除` |

OpenCode 有 20 多个 Claude Code 中没有的附加事件。

### 挂钩运行时控件

OpenCode 插件挂钩遵循 Claude Code/Cursor 使用的相同运行时控件：```bash
export ECC_HOOK_PROFILE=standard
export ECC_DISABLED_HOOKS="pre:bash:tmux-reminder,post:edit:typecheck"
```- `ECC_HOOK_PROFILE`：`最小`、`标准`（默认）、`严格`
- `ECC_DISABLED_HOOKS`：要禁用的以逗号分隔的挂钩 ID

## 技能

默认 OpenCode 配置通过“instructions”数组加载 11 个精选的 ECC 技能：

- 编码标准
- 后端模式
- 前端模式
- 前端幻灯片
- 安全审查
- TDD工作流程
- 战略紧凑
- 评估线束
- 验证循环
- api设计
- e2e测试

其他专业技能在“skills/”中提供，但默认情况下不加载，以保持 OpenCode 会话的精简：

- 文章写作
- 内容引擎
- 市场研究
- 投资者材料
- 投资者外展

## 配置

`opencode.json` 中的完整配置：```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-5",
  "small_model": "anthropic/claude-haiku-4-5",
  "plugin": ["./plugins"],
  "instructions": [
    "skills/tdd-workflow/SKILL.md",
    "skills/security-review/SKILL.md"
  ],
  "agent": { /* 12 agents */ },
  "command": { /* 24 commands */ }
}
```## 许可证

麻省理工学院