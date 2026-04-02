# Agents 使用说明

## 位置说明

本目录存放所有项目共用的 Agent 配置。

## 当前 Agent 清单（21 个）

### 🎖️ Agent审查团（2 个 + 细致审查子系统 + 自我进化子系统）
- `Agent审查团.md` - 审查团入口，统筹协调，含自我进化系统

**细致审查子系统**（细致审查/ 目录，13 个）：
- `00审查总负责.md` - 统筹协调，审核报告
- `00汇总整合.md` - 收集整理，生成报告
- `01架构完整性审查.md` - Frontmatter + 8章节
- `02通信协议审查.md` - 消息格式/上下文/状态/错误
- `03调用机制审查.md` - triggers/调用/权限/生命周期
- `04交接协议审查.md` - 移交文档/质量期望/接收确认
- `05质量门禁审查.md` - 五级门禁/守门人
- `06交付物质量审查.md` - 代码/模板/指标
- `07DevQA循环审查.md` - 反馈/重试/升级/终止
- `08独特个性审查.md` - Voice/禁止词/语气
- `09编排集成审查.md` - 上下游/接口/依赖
- `10证据充分性审查.md` - 引用/来源/数据/逻辑
- `11Skill配套审查.md` - SKILL.md/ trigger/功能

### Cyberwiz 核心 Agent（2 个）
- `cyberwiz.md` - Cyberwiz 主 Agent
- `cyber-digital-army.md` - Cyber 数字军团

### 专业顾问 Agent（7 个）
- `technical-advisor.md` - 技术顾问
- `product-advisor.md` - 产品顾问
- `growth-advisor.md` - 增长顾问
- `strategy-advisor.md` - 战略顾问
- `planning-department.md` - 计划部门
- `discussion-coordinator.md` - 讨论协调员
- `hr-department.md` - HR 部门

### 功能型 Agent（10 个）
- `bug-analyzer.md` - Bug 分析专家
- `code-reviewer.md` - 代码审查专家
- `skill-auditor.md` - Skill 审核专家
- `knowledge-orchestrator.md` - 知识编排器
- `information-department.md` - 信息部
- `ui-sketcher.md` - UI 草图工程师
- `proposal-generator.md` - 技术方案生成器
- `proposal-reviewer.md` - 技术方案审查员
- `story-generator.md` - 故事生成器
- `dev-planner.md` - 开发规划师

### 质量管控 Agent（2 个）
- `reality-checker.md` - 质量关卡检查员
- `todo-enforcer.md` - 任务执行监控专家

## 迁移记录

**迁移日期**: 2026-03-11
**来源**: `~/.claude/agents/`
**目标**: `01 项目（Projects）/.claude/agents/`
**状态**: ✅ 已完成 - 所有 Cyberwiz Agent 已复制到全局配置层

## 与相关目录的关系

```
【Agent 三层架构】

~/.claude/agents/              01 项目（Projects）/.claude/agents/
     ↓                                ↓
【运行位置】                    【配置位置】
Claude Code 实际调用            项目级共用配置（本目录）
     ↑                                ↑
     └────── 00_基础研发/01_Agent 研发/Agents/ ──────┘
                    ↓
              【研发位置】
              草稿和迭代开发
```

## 使用方法

### 添加新 Agent

1. 在 `00_基础研发/01_Agent 研发/Agents/` 中开发
2. 测试通过后：
   - 复制到 `~/.claude/agents/`（运行位置）
   - 复制到本目录（配置位置，便于 Git 管理）
   - 在 `02 领域/01_专业能力建设/02_Agents/` 创建文档索引

### 删除 Agent

1. 从 `~/.claude/agents/` 删除（运行位置）
2. 从本目录删除（配置位置）
3. 在 `02 领域/01_专业能力建设/02_Agents/` 更新索引

### 修改 Agent

1. 在 `00_基础研发/01_Agent 研发/Agents/` 中修改
2. 测试通过后同步到：
   - `~/.claude/agents/`
   - 本目录

## 命名规范

- 文件名：`Agent 名称.md`
- 内容：符合 CyberWiz Agent 体系规范

## 相关文件

- `../CLAUDE.md` - 全局配置说明
- `02 领域/01_专业能力建设/02_Agents/_README.md` - 领域 Agents 索引

---
*创建日期：2026-03-11*
