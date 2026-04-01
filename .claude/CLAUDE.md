# 01_Project/.claude/ - 全局配置层

## 定位

这是所有项目共用的全局配置层，存放跨项目复用的 Agent 和 Skill 配置。

## 目录结构

```
.claude/
├── agents/          ← 所有项目共用的 Agents
│   └── _README.md   ← Agents 使用说明
└── skills/          ← 所有项目共用的 Skills
    └── _README.md   ← Skills 使用说明
```

## 与三层架构的关系

| 层级 | 位置 | 用途 |
|------|------|------|
| **全局配置层** | `01_Project/.claude/` | 所有项目共用的 Agent/Skill 配置 |
| **研发层** | `00_基础研发/` | 正在进行中的 Agent/Skill 研发 |
| **应用层** | `01_Project/X/` | 具体业务项目 |
| **归档层** | `02_Area（Area）/01_专业能力建设/` | 成品文档索引和归档 |

## 与 ~/.claude/ 的关系

**v2.0 完全迁移后**:

| 位置 | 用途 | 说明 |
|------|------|------|
| `01_Project/.claude/` | **唯一存储位置** | Cyberwiz Agent/Skill 的唯一存储位置 |
| `~/.claude/skills/` | **第三方 Skill** | 仅保留第三方 Skill 和 Anthropic 官方 Skill |
| `~/.claude/agents/` | **空目录** | Cyberwiz Agent 已完全移出 |

**使用方式**:
- 在项目根目录创建 `.claude/settings.local.json` 引用本目录
- 或通过符号链接关联到本目录

## 使用规范

### 新增共用 Agent/Skill

1. 在 `00_基础研发/` 中进行研发
2. 测试通过后放入 `01_Project/.claude/`（唯一存储位置）
3. 在 `02_Area（Area）/01_专业能力建设/` 创建文档索引
4. 纳入 Git 管理

### 项目引用

应用层项目可以通过以下方式引用全局配置：
- 直接在项目中配置引用路径
- 通过符号链接关联到全局配置

## 相关文件

- `agents/_README.md` - Agents 详细使用说明（含完整清单）
- `skills/_README.md` - Skills 详细使用说明（含完整清单）
- `../../02_Area（Area）/02_CODE 管理体系/output/Cyberwiz Agent-Skill 迁移报告.md` - 迁移报告

---
*创建日期：2026-03-11 | 版本：v2.0（完全迁移）*
