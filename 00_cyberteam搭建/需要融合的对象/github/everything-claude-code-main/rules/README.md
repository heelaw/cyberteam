# 规则
## 结构

规则被组织成**通用**层以及**特定语言**目录：```
rules/
├── common/          # Language-agnostic principles (always install)
│   ├── coding-style.md
│   ├── git-workflow.md
│   ├── testing.md
│   ├── performance.md
│   ├── patterns.md
│   ├── hooks.md
│   ├── agents.md
│   └── security.md
├── typescript/      # TypeScript/JavaScript specific
├── python/          # Python specific
├── golang/          # Go specific
├── swift/           # Swift specific
└── php/             # PHP specific
```- **common/** 包含通用原则 - 没有特定于语言的代码示例。
- **语言目录** 使用特定于框架的模式、工具和代码示例扩展通用规则。每个文件都引用其共同的对应文件。

## 安装

### 选项 1：安装脚本（推荐）```bash
# Install common + one or more language-specific rule sets
./install.sh typescript
./install.sh python
./install.sh golang
./install.sh swift
./install.sh php

# Install multiple languages at once
./install.sh typescript python
```### 选项 2：手动安装

> **重要提示：**复制整个目录 - 不要使用“/*”进行平展。
> 通用目录和特定语言目录包含同名文件。
> 将它们平铺到一个目录中会导致特定于语言的文件被覆盖
> 通用规则，并打破了使用的相对 `../common/` 引用
> 特定于语言的文件。```bash
# Install common rules (required for all projects)
cp -r rules/common ~/.claude/rules/common

# Install language-specific rules based on your project's tech stack
cp -r rules/typescript ~/.claude/rules/typescript
cp -r rules/python ~/.claude/rules/python
cp -r rules/golang ~/.claude/rules/golang
cp -r rules/swift ~/.claude/rules/swift
cp -r rules/php ~/.claude/rules/php

# Attention ! ! ! Configure according to your actual project requirements; the configuration here is for reference only.
```## 规则与技能

- **规则**定义了广泛适用的标准、约定和清单（例如，“80% 测试覆盖率”、“无硬编码秘密”）。
- **技能**（`skills/`目录）为特定任务提供深入的、可操作的参考材料（例如，`python-patterns`、`golang-testing`）。

特定于语言的规则文件在适当的情况下引用相关技能。规则告诉你“做什么”；技能告诉你“如何”去做。

## 添加新语言

添加对新语言的支持（例如“rust/”）：

1.创建`rules/rust/`目录
2. 添加扩展通用规则的文件：
   - `coding-style.md` — 格式化工具、习语、错误处理模式
   - `testing.md` — 测试框架、覆盖工具、测试组织
   - `patterns.md` — 特定于语言的设计模式
   - `hooks.md` — PostToolUse 用于格式化程序、linter、类型检查器的钩子
   - `security.md` — 秘密管理、安全扫描工具
3. 每个文件应以以下内容开头：```
   > This file extends [common/xxx.md](../common/xxx.md) with <Language> specific content.
   ```4. 参考现有技能（如果有），或在“技能/”下创建新技能。

## 规则优先级

当特定于语言的规则和通用规则发生冲突时，**特定于语言的规则优先**（特定于通用的规则）。这遵循标准的分层配置模式（类似于 CSS 特异性或“.gitignore”优先级）。

- `rules/common/` 定义适用于所有项目的通用默认值。
- `rules/golang/`、`rules/python/`、`rules/swift/`、`rules/php/`、`rules/typescript/` 等覆盖语言习语不同的默认值。

### 示例

`common/coding-style.md` 建议将不变性作为默认原则。特定于语言的 `golang/coding-style.md` 可以覆盖它：

> 惯用的 Go 使用指针接收器进行结构突变 - 请参阅 [common/coding-style.md](../common/coding-style.md) 了解一般原理，但这里首选 Go 惯用的突变。

### 带有覆盖注释的通用规则

`rules/common/` 中可能被特定于语言的文件覆盖的规则标记为：

> **语言注释**：对于此模式不惯用的语言，此规则可能会被特定于语言的规则覆盖。