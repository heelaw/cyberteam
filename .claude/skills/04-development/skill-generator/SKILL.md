---
description: Skill 生成器 - 将知识体系转化为 Claude Code Skill
---

# skill-generator

Skill 生成器 - 将知识体系转化为 Claude Code Skill

## 触发词

- "生成 Skill"
- "创建技能"
- "转化为 Skill"

## 功能

### generate_skill

将知识文档转化为标准的 Skill 结构

```yaml
输入:
  source_documents: ["文档路径1", "文档路径2"]
  skill_name: "技能名称"
  description: "技能描述"

输出:
  - SKILL.md 文件
  - 实现代码（如需要）
  - 测试用例
```

## Skill 结构模板

```
skill-name/
├── SKILL.md          # 必需：技能定义
├── impl/             # 可选：实现代码
│   ├── main.py
│   └── utils.py
├── tests/            # 可选：测试用例
│   └── test_*.py
└── README.md         # 可选：使用说明
```

## SKILL.md 模板

```yaml
---
description: 简短描述（一句话）
---

# skill-name

技能标题

## 触发词

- "触发词1"
- "触发词2"

## 功能

### 功能1名称

功能描述

```yaml
输入:
  参数名: 参数说明

输出:
  输出说明
```

## MCP 工具

- `tool:name` - 工具说明

## 使用示例

```
用户输入
Agent 输出
```
```

## 输出位置

- 生成的 Skills: `02_Area/01_专业能力建设/01_Skills/`
- 临时草稿: `01_Project/00_基础研发/`

## 验证清单

- [ ] SKILL.md 格式正确
- [ ] 触发词清晰有效
- [ ] MCP 工具调用正确
- [ ] 有使用示例
- [ ] 通过测试
```

## MCP 工具

- `obsidian:read_multiple_notes` - 批量读取笔记
- `filesystem:write_file` - 写入文件
- `filesystem:create_directory` - 创建目录
