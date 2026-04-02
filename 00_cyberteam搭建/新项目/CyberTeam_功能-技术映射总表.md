# CyberTeam 功能-技术映射总表

## 1. 总体原则

- 桌面端优先：Electron
- 前端优先：Next.js + React
- 数据本地化：SQLite
- AI 底座：Claude Code / Claude Agent SDK
- 组织编排：Team / Department / Agent
- 协作中心：Chat / Group / Playground

## 2. 功能到技术映射

### 2.1 公司创建
- 功能：创建公司、命名、头像、描述、版本
- 技术：React 表单 + SQLite companies 表 + Zustand 状态

### 2.2 部门管理
- 功能：创建部门、树结构、父子层级、颜色、职责
- 技术：React 树组件 + SQLite departments 表 + 组织树状态

### 2.3 Agent 管理
- 功能：创建 Agent、编辑岗位、头像、技能、状态
- 技术：React 编辑器 + SQLite agents 表 + agent_skills 关联表

### 2.4 Skill 系统
- 功能：创建/安装/绑定 Skill
- 技术：Markdown/JSON Skill 文件 + SQLite skills 表 + Skill 市场页面

### 2.5 私聊
- 功能：用户与单个 Agent 聊天
- 技术：Claude Code 会话 + SSE 流 + messages 表 + Chat 页面

### 2.6 群聊
- 功能：多人协作、拉部门、拉 Agent、@Agent
- 技术：MessageRouter + conversation_participants 表 + 群聊 UI

### 2.7 Agent 讨论
- 功能：Agent 之间自动补充、轮流发言、互相讨论
- 技术：任务状态机 + 路由策略 + CEO 汇总规则

### 2.8 Playground
- 功能：会议纪要、摘要、任务清单、审核、导出
- 技术：Markdown 生成器 + playground_documents 表 + review_records 表

### 2.9 CEO 审核
- 功能：对高风险任务和最终文档进行审核
- 技术：审核流程状态机 + ReviewRecord + 确认弹窗

### 2.10 市场
- 功能：Agent 模板、Skill 模板、部门模板
- 技术：模板元数据 + React 卡片列表 + 一键安装

### 2.11 Claude Code 检测
- 功能：检测本地是否安装 Claude Code
- 技术：Electron 主进程检测 + 设置页提示

### 2.12 本地会话与消息流
- 功能：流式输出、历史记录、恢复对话
- 技术：Claude Agent SDK + SSE + SQLite messages 表

### 2.13 PUA 增强
- 功能：持续执行、动机、反馈闭环
- 技术：可选 skill 包 + hook/command 联动 + feedback event bus

## 3. 第一版优先级

### P0
- 公司创建
- 部门创建
- Agent 创建
- 私聊
- 基础群聊
- Claude Code 接入

### P1
- @Agent
- Agent 讨论
- Playground
- CEO 审核

### P2
- Skill 市场
- Agent 市场
- 模板市场
- PUA 增强

## 4. 复用来源

- CodePilot：Electron、Claude Code、SQLite、流式输出、设置中心
- Magic：市场、数字员工、成果交付、审核机制
- V4：组织树、MessageRouter、Mailbox、Playground、协作模型
