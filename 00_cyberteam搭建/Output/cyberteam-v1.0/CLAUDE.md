# CyberTeam 项目指南

## 项目概述

CyberTeam 是一个 AI 模拟公司协作系统，核心理念：**一句话交代，整个团队干活**。

## 目录结构

```
cyberteam/
├── CEO.md                    # CEO Agent（100思维框架 + 计划审核）
├── agents/                   # Agent 定义
│   ├── manager/             # 部门负责人
│   └── executor/            # 执行 Agent
├── skills/                  # Skill 定义
│   ├── goal-driven.md      # 目标驱动循环
│   ├── pua-supervisor.md  # PUA 监督
│   ├── office-hours.md    # 计划审核（YC 六问）
│   └── investigate.md     # 根因分析
├── system/                  # 系统实现
│   ├── core/               # 核心代码
│   ├── integration/        # ClawTeam 集成
│   └── tests/              # 测试
└── docs/                   # 文档
```

## 核心组件

### 1. CEO Agent

- **功能**：问题分析 + 任务分发 + 计划审核
- **能力**：5W1H + MECE + 100 思维框架

### 2. Skills

| Skill | 功能 |
|-------|------|
| goal-driven | 目标驱动循环，持续工作直到达成 |
| pua-supervisor | 监督 Agent，防止偷懒 |
| office-hours | YC 六问，计划审核 |
| investigate | 根因分析 |

## 使用流程

### 基本流程

```
用户输入 → CEO 分析 → 计划审核 → Agent 选择 → 执行 + PUA → 完成
```

### 详细流程

1. **用户输入业务目标**
2. **CEO 分析**（5W1H + MECE）
3. **计划审核**（Office Hours + 专家思维）
4. **Agent 选择**（从 Agent 库中自主选择）
5. **启动执行**（并行处理）
6. **PUA 监督**（监控进度，防止偷懒）
7. **Goal-Driven 循环**（持续工作直到达成）
8. **输出结果**

## 参考资源

- **ClawTeam**：多 Agent 协作框架
- **agency-agents**：150+ 专业 Agent 模板
- **gstack**：工作流技能设计
- **goal-driven-main**：目标驱动机制
- **思考天团 agents/**：100 个思维框架

## 注意事项

1. 所有专家参与：确保所有相关思维框架都参与分析
2. PUA 监督：在执行过程中监控进度
3. 持续工作：使用 goal-driven 循环直到目标达成
4. 结果聚合：汇总所有 Agent 的输出

---

*创建日期：2026-03-23*
