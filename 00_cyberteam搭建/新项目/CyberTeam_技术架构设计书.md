# CyberTeam 技术架构设计书

## 版本
v0.2

## 1. 架构总览

CyberTeam 采用桌面端 + 本地数据 + Claude Code 引擎 + AI 军团编排层 的四层架构。它的核心是把 Claude Code 作为底层执行引擎，把 CyberTeam 作为组织与协作系统。

```text
┌──────────────────────────────────────────┐
│              Electron 桌面壳              │
│   macOS 原生窗口、菜单、文件、系统能力     │
└──────────────────────────┬───────────────┘
                           │
┌──────────────────────────▼───────────────┐
│        Next.js / React 前端界面层          │
│  聊天 / 组织架构 / 市场 / Playground / 设置 │
└──────────────────────────┬───────────────┘
                           │ IPC / API
┌──────────────────────────▼───────────────┐
│          CyberTeam 业务编排层              │
│ Team / Department / Agent / Skill / Chat  │
│ MessageRouter / SessionManager / Review    │
└──────────────────────────┬───────────────┘
                           │
┌──────────────────────────▼───────────────┐
│           Claude Code 执行引擎层            │
│ Claude Agent SDK / 本地 Claude Code / SSE   │
└──────────────────────────┬───────────────┘
                           │
┌──────────────────────────▼───────────────┐
│            SQLite 本地数据层                │
│  公司 / 部门 / Agent / 会话 / 消息 / 文档   │
└──────────────────────────────────────────┘
```

## 2. 设计原则

### 2.1 Claude Code 为底座
CyberTeam 不自己造 AI 引擎，而是使用用户本地 Claude Code，复用最新能力，作为 GUI + 编排 + 组织管理层。

### 2.2 CyberTeam 为组织系统
重点不是模型，而是组织结构、Agent 编排、部门协作、群聊讨论、结果沉淀、CEO 审核。

### 2.3 本地优先
先做 macOS 桌面端，本地 SQLite 存储，本地 Claude Code 连接，尽量避免云依赖。

### 2.4 结果导向
所有对话都尽量沉淀为成果，输出可复用、可导出、可审核。

### 2.5 可扩展但不臃肿
第一版只保留最小闭环，但所有模块都要为未来的市场、模板、外部集成和 PUA 增强预留接口。

## 3. 技术选型

- Electron
- Next.js + React + TypeScript
- Tailwind CSS + Radix UI
- Zustand
- SQLite + better-sqlite3
- Claude Code / Claude Agent SDK

## 4. 核心模块划分

### 4.1 Desktop Shell 模块
负责主窗口、菜单栏、启动检测、系统文件访问、安装和更新、系统通知。

### 4.2 Chat 模块
负责私聊、群聊、消息流、消息持久化、@提及、Agent 回复展示。

### 4.3 Organization 模块
负责公司、部门、团队、Agent 结构、组织树编辑、绑定关系。

### 4.4 Agent Runtime 模块
负责 Agent 生命周期、启动、会话、状态、prompt 编译、Skill 绑定。

### 4.5 Team Orchestration 模块
负责团队管理、群聊协同、讨论调度、发言顺序、CEO 汇总、冲突处理。

### 4.6 Skill System 模块
负责 Skill 定义、市场、安装、绑定 Agent、绑定部门。

### 4.7 Playground 模块
负责会议记录、摘要、任务结果、CEO 审核、文档输出、版本存档。

### 4.8 Market 模块
负责 Agent 模板、Skill 模板、部门模板、公司模板、一键安装/试用。

### 4.9 Claude Integration 模块
负责 Claude Code 检测、连接、流式请求、最新命令、用户本地环境。

## 5. 核心数据模型

- Company
- Department
- Agent
- Skill
- ChatConversation
- ChatMessage
- PlaygroundDocument
- ReviewRecord

## 6. 对话与协作机制

### 6.1 私聊机制
用户与单个 Agent 单独对话，流式回复，保存历史，可转 Playground。

### 6.2 群聊机制
用户创建群聊，可添加任意 Agent，可拉整个部门，可动态增减成员，可切换群聊主题。

### 6.3 @任务机制
在群聊里 @某 Agent / @某部门 / @某专家 / @CEO 触发任务，获得上下文并回应。

### 6.4 自动讨论机制
任务进入群聊后，CEO 接单、部门讨论、专家补充、CEO 汇总、生成总结。

### 6.5 CEO 审核机制
适用于高风险任务、文档定稿、市场发布、方案决策。

## 7. 前端页面设计

### 7.1 Chat 页面
左侧会话列表，中间聊天窗口，右侧成员/上下文/状态栏。

### 7.2 Organization 页面
公司树、部门树、Agent 节点、可拖拽编辑、节点绑定关系。

### 7.3 Market 页面
Agent 市场、Skill 市场、模板市场、一键安装。

### 7.4 Playground 页面
会话摘要、会议纪要、审核流程、导出按钮、历史版本。

### 7.5 Settings 页面
Claude Code 配置、模型设置、路径检测、本地数据目录、外观设置、快捷键设置。

## 8. 从 V4 复用
- TeamManager 思路
- Mailbox 机制
- MessageRouter 逻辑
- Session 持久化
- Agent 编排思想
- Thinking modules
- State machine
- Debate / Department / Swarm 概念
- Playground 输出和审核思路
- 组织树和部门层级抽象

## 9. 从 Magic 复用
- 数字员工市场
- 成果交付导向
- 审核与安全机制
- 部门化表达
- 企业感 UI 语言
- 专家 Agent 的产品表达
- 输出成品化的思路
## 10. 从 CodePilot 复用
- Electron + Next.js 结构
- Claude Code 底座接入方式
- SQLite 本地存储
- 流式输出
- Bridge 架构思路
- 设置中心结构
- 桌面端安装/检测/启动流程
- 本地会话与 UI 组合方式
## 11. 建议目录结构

```bash
cyberteam/
├── apps/
│   ├── desktop/
│   └── renderer/
├── packages/
│   ├── core/
│   ├── claude/
│   ├── team/
│   ├── chat/
│   ├── skill/
│   ├── playground/
│   ├── market/
│   ├── db/
│   └── ui/
├── resources/
├── docs/
├── tests/
└── package.json
```

## 12. MVP 建议

第一版必须做：macOS 桌面端、Claude Code 检测、连接本地 Claude Code、一个聊天页、一个组织页、一个 Agent、一个部门、一个群聊、一个 Playground。

## 13. 最终架构结论

CyberTeam 采用 Electron + Next.js 的 macOS 桌面架构，以用户本地 Claude Code 作为执行引擎，以 SQLite 作为本地数据层，以 Team / Agent / Department / Skill 为组织模型，以 Chat / Group / Playground 为协作与输出界面，构建一个 AI 军团操作系统。
