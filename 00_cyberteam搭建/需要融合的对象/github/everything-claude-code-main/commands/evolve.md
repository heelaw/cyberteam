# 进化命令

## 实施

使用插件根路径运行本能 CLI：```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning-v2/scripts/instinct-cli.py" evolve [--generate]
```或者如果未设置“CLAUDE_PLUGIN_ROOT”（手动安装）：```bash
python3 ~/.claude/skills/continuous-learning-v2/scripts/instinct-cli.py evolve [--generate]
```分析本能并将相关的本能聚类到更高层次的结构中：
- **命令**：当本能描述用户调用的操作时
- **技能**：当本能描述自动触发的行为时
- **代理**：当本能描述复杂的多步骤过程时

## 用法```
/evolve                    # Analyze all instincts and suggest evolutions
/evolve --generate         # Also generate files under evolved/{skills,commands,agents}
```## 进化规则

### → 命令（用户调用）
当本能描述用户会明确请求的操作时：
- 关于“当用户要求......”时的多种本能
- 具有触发器的本能，例如“创建新的 X 时”
- 遵循可重复序列的本能

示例：
- `new-table-step1`: "添加数据库表时，创建迁移"
- `new-table-step2`：“添加数据库表时，更新架构”
- `new-table-step3`：“添加数据库表时，重新生成类型”

→ 创建：**new-table** 命令

### → 技能（自动触发）
当本能描述应该自动发生的行为时：
- 模式匹配触发器
- 错误处理响应
- 代码风格强制执行

示例：
- `prefer-function`：“编写函数时，更喜欢函数式风格”
- `use-immutable`：“修改状态时，使用不可变模式”
- `avoid-classes`：“设计模块时，避免基于类的设计”

→ 创建：“功能模式”技能

### → 特工（需要深度/隔离）
当本能描述受益于隔离的复杂、多步骤过程时：
- 调试工作流程
- 重构序列
- 研究任务

示例：
- `debug-step1`: “调试时，首先检查日志”
- `debug-step2`：“调试时，隔离失败的组件”
- `debug-step3`：“调试时，创建最小再现”
- `debug-step4`：“调试时，通过测试验证修复”

→ 创建：**调试器**代理

## 做什么

1. 检测当前项目上下文
2.读取项目+全局本能（ID冲突时项目优先）
3. 按触发/域模式对本能进行分组
4. 识别：
   - 候选技能（具有 2 个以上本能的触发集群）
   - 命令候选人（高可信度的工作流程本能）
   - 候选代理（更大、高置信度的集群）
5. 在适用时显示晋升候选人（项目 -> 全球）
6. 如果传递了`--generate`，则将文件写入：
   - 项目范围：`~/.claude/homunculus/projects/<project-id>/evolved/`
   - 全局后备：`~/.claude/homunculus/evolved/`

## 输出格式```
============================================================
  EVOLVE ANALYSIS - 12 instincts
  Project: my-app (a1b2c3d4e5f6)
  Project-scoped: 8 | Global: 4
============================================================

High confidence instincts (>=80%): 5

## SKILL CANDIDATES
1. Cluster: "adding tests"
   Instincts: 3
   Avg confidence: 82%
   Domains: testing
   Scopes: project

## COMMAND CANDIDATES (2)
  /adding-tests
    From: test-first-workflow [project]
    Confidence: 84%

## AGENT CANDIDATES (1)
  adding-tests-agent
    Covers 3 instincts
    Avg confidence: 82%
```## 旗帜

- `--generate`：除了分析输出之外还生成进化文件

## 生成的文件格式

### 命令```markdown
---
name: new-table
description: Create a new database table with migration, schema update, and type generation
command: /new-table
evolved_from:
  - new-table-migration
  - update-schema
  - regenerate-types
---

# New Table Command

[Generated content based on clustered instincts]

## Steps
1. ...
2. ...
```### Skill```markdown
---
name: functional-patterns
description: Enforce functional programming patterns
evolved_from:
  - prefer-functional
  - use-immutable
  - avoid-classes
---

# Functional Patterns Skill

[Generated content based on clustered instincts]
```＃＃＃ 代理人```markdown
---
name: debugger
description: Systematic debugging agent
model: sonnet
evolved_from:
  - debug-check-logs
  - debug-isolate
  - debug-reproduce
---

# Debugger Agent

[Generated content based on clustered instincts]
```