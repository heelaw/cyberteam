# CyberTeam MVP 范围定义

## 版本
v0.2

## 1. MVP 的目标

MVP 不是把所有想法做出来，而是验证 CyberTeam 这个方向到底是不是对的。

MVP 只验证 4 件事：
1. 用户能不能接受“AI 军团”这个概念
2. 用户能不能在软件里搭出自己的组织
3. 用户能不能和 Agent 顺畅协作
4. 输出能不能从聊天变成成果

## 2. MVP 设计原则

- 只做一个完整闭环
- 只做最小组织结构
- 只做一个桌面平台
- 只做 Claude Code 底座接入
- 只做能感知价值的功能

## 3. MVP 必须有的功能

### 3.1 基础安装与启动
- macOS 桌面端
- 软件启动
- 本地数据目录初始化
- Claude Code 检测
- Claude Code 接入状态提示
- Claude Code 本地会话连接

### 3.2 公司创建
- 创建公司
- 设置公司名
- 设置公司头像
- 设置公司描述

### 3.3 组织结构
- CEO 节点
- 讨论部门
- 执行部门
- Agent 节点
- 节点绑定 Agent
- 最小组织树编辑

### 3.4 Agent 创建
- 创建 Agent
- 设置头像
- 设置岗位
- 设置名称
- 设置职责
- 设置技能标签

### 3.5 私聊
- 与单个 Agent 对话
- 流式输出
- 历史记录
- 消息持久化

### 3.6 群聊
- 创建群聊
- 拉入多个 Agent
- 拉入整个部门
- 群聊消息流式输出
- @Agent
- 群聊中 Agent 互相补充

### 3.7 Playground
- 从群聊生成会议记录
- 生成摘要
- 生成任务清单
- CEO 审核
- 导出 Markdown
- 保存版本历史

## 4. MVP 必须砍掉的东西

- 100+ 思维专家
- 25 个 Agent 全量系统
- 复杂市场系统
- 企业级多租户
- 云端同步
- 跨平台支持
- 大而全权限系统
- 复杂审批编排

## 5. MVP 最小结构建议

### 公司结构
- CEO
- 讨论层
- 执行层

### Agent 数量
第一版只做 3 到 5 个 Agent。

### Skill 数量
第一版只做 3 到 5 个基础 Skill。

## 6. MVP 页面范围

- 首页 / Dashboard
- Chat 页面
- Organization 页面
- Playground 页面
- Settings 页面

## 7. MVP 用户流程

### 流程 A：首次进入
安装并打开软件 → 检测 Claude Code → 创建公司 → 创建 CEO 和基础 Agent → 进入聊天。

### 流程 B：发起任务
在群聊里提需求 → @几个 Agent → Agent 讨论 → CEO 总结 → 生成 Playground 结果。

### 流程 C：导出成果
在 Playground 看结果 → CEO 审核 → 用户导出 Markdown。

## 8. MVP 成功标准

- 5 分钟内创建组织
- 1 分钟内发起群聊
- 能看到 Agent 之间的协作
- 能生成像样的 Playground 产物
- 用户会觉得“这个比普通聊天有组织感”

## 9. MVP 技术优先级

### P0
桌面壳、Claude Code 接入、数据存储、聊天、组织结构、Agent 创建、最小群聊。

### P1
群聊、@机制、Agent 讨论、Playground、审核流。
### P2
Skill 市场、模板市场、更丰富的组织控制。

## 10. MVP 的一句话定义

CyberTeam MVP 是一个 macOS 桌面端 AI 军团雏形，用户可以创建公司、组织部门、配置 Agent、在群聊里 @Agent 协作，并把讨论结果沉淀到 Playground。
