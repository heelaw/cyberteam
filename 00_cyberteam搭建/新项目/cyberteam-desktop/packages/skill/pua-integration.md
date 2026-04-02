# PUA Integration

## 定位

PUA 不是 CyberTeam 的主线功能，而是一个可选的持续执行 / 动机 / 反馈闭环增强模块。它只作为 CyberTeam 的扩展能力存在，不进入 MVP 主链路。

## 接入目标

- 为 Agent 提供持续推进机制
- 为长任务提供反馈闭环
- 为执行节奏提供提醒与触发机制
- 为循环任务提供 hook / command 扩展
- 作为后续增强的可插拔模块

## 建议接入层

### 1. packages/core
负责把 PUA 作为可选的 loop enhancer / persistence enhancer / motivation enhancer 挂入团队编排层。

### 2. packages/claude
负责把 PUA 与 Claude Code 的命令、hook、会话状态联动。

### 3. packages/skill
将 PUA 视为一种 Skill 或能力包，而不是主业务系统。

## 第一版不做的事

- 不把 PUA 作为 CyberTeam 主卖点
- 不把所有 hook 机制一次性做满
- 不把复杂的动机系统塞进 MVP 主链路

## 建议预留能力

- loop controller
- session restore
- failure detector
- trigger command registry
- feedback event bus
- 对 Claude Code command / hook / session 状态联动的接口