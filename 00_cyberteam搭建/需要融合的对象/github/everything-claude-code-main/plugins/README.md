# 插件和市场

插件通过新的工具和功能扩展了 Claude Code。本指南仅涵盖安装 - 请参阅[完整文章](https://x.com/affaanmustafa/status/2012378465664745795)了解何时以及为何使用它们。

---

## 市场

市场是可安装插件的存储库。

### 添加市场```bash
# Add official Anthropic marketplace
claude plugin marketplace add https://github.com/anthropics/claude-plugins-official

# Add community marketplaces (mgrep by @mixedbread-ai)
claude plugin marketplace add https://github.com/mixedbread-ai/mgrep
```### 推荐市场

|市场|来源 |
|-------------|--------|
|克劳德插件官方 | `anthropics/claude-plugins-official` |
|克劳德代码插件 | `人类学/克劳德代码` |
| Mixedbread-Grep (@mixedbread-ai) | `mixedbread-ai/mgrep` |

---

## 安装插件```bash
# Open plugins browser
/plugins

# Or install directly
claude plugin install typescript-lsp@claude-plugins-official
```### 推荐插件

**发展：**
- `typescript-lsp` - TypeScript 智能
- `pyright-lsp` - Python 类型检查
- `hookify` - 以对话方式创建钩子
- `代码简化器` - 重构代码

**代码质量：**
- `代码审查` - 代码审查
- `公关审查工具包` - 公关自动化
- `安全指导` - 安全检查

**搜索：**
- `mgrep` - 增强搜索（比 ripgrep 更好）
- `context7` - 实时文档查找

**工作流程：**
- `commit-commands` - Git 工作流程
- `前端设计` - UI 模式
- `feature-dev` - 功能开发

---

## 快速设置```bash
# Add marketplaces
claude plugin marketplace add https://github.com/anthropics/claude-plugins-official
claude plugin marketplace add https://github.com/mixedbread-ai/mgrep

# Open /plugins and install what you need
```---

## 插件文件位置```
~/.claude/plugins/
|-- cache/                    # Downloaded plugins
|-- installed_plugins.json    # Installed list
|-- known_marketplaces.json   # Added marketplaces
|-- marketplaces/             # Marketplace data
```