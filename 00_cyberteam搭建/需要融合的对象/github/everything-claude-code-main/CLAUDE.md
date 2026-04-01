# 克劳德.md

此文件为 Claude Code (claude.ai/code) 提供使用此存储库中的代码时的指导。

## 项目概述

这是一个 **Claude Code 插件** - 生产就绪代理、技能、挂钩、命令、规则和 MCP 配置的集合。该项目为使用 Claude Code 的软件开发提供了经过实战检验的工作流程。

## 运行测试```bash
# Run all tests
node tests/run-all.js

# Run individual test files
node tests/lib/utils.test.js
node tests/lib/package-manager.test.js
node tests/hooks/hooks.test.js
```## 架构

该项目分为几个核心组件：

- **agents/** - 用于授权的专门子代理（规划者、代码审查者、tdd 指南等）
- **技能/** - 工作流程定义和领域知识（编码标准、模式、测试）
- **commands/** - 用户调用的斜杠命令（/tdd、/plan、/e2e 等）
- **hooks/** - 基于触发器的自动化（会话持久性、工具前/后工具挂钩）
- **规则/** - 始终遵循准则（安全性、编码风格、测试要求）
- **mcp-configs/** - 用于外部集成的 MCP 服务器配置
- **scripts/** - 用于挂钩和设置的跨平台 Node.js 实用程序
- **tests/** - 脚本和实用程序的测试套件

## 按键命令

- `/tdd` - 测试驱动的开发工作流程
- `/plan` - 实施计划
- `/e2e` - 生成并运行 E2E 测试
- `/code-review` - 质量审核
- `/build-fix` - 修复构建错误
- `/learn` - 从会话中提取模式
- `/skill-create` - 从 git 历史记录生成技能

## 开发笔记

- 包管理器检测：npm、pnpm、yarn、bun（可通过“CLAUDE_PACKAGE_MANAGER”环境变量或项目配置进行配置）
- 跨平台：通过 Node.js 脚本支持 Windows、macOS、Linux
- 代理格式：带有 YAML frontmatter 的 Markdown（名称、描述、工具、模型）
- 技能格式：Markdown，其中包含清晰的部分，说明何时使用、如何工作、示例
- 挂钩格式：带有匹配器条件和命令/通知挂钩的 JSON

## 贡献

遵循 CONTRIBUTING.md 中的格式：
- 代理：带有 frontmatter 的 Markdown（名称、描述、工具、型号）
- 技能：清晰的部分（何时使用、如何工作、示例）
- 命令：带有描述 frontmatter 的 Markdown
- Hooks：带有匹配器和 hooks 数组的 JSON

文件命名：小写字母加连字符（例如“python-reviewer.md”、“tdd-workflow.md”）