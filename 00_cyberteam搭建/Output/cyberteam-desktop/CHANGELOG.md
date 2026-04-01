# Changelog

所有值得注意的变更都会记录在这个文件中。

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/) 规范。

## [0.1.0-alpha] - 2026-03-31

### 初始化

- 初始架构设计文档 (ARCHITECTURE.md)
- 项目路线图 (ROADMAP.md)
- 技术验证报告 (VERIFICATION.md)

### 技术决策

- 采用 **Electron 40** 作为桌面应用框架（替代 Tauri）
- 采用 **React 19 + Vite** 作为前端框架
- 采用 **better-sqlite3** 作为本地数据库
- 采用 **@anthropic-ai/claude-agent-sdk** 集成 Claude Code CLI

### 参考项目

- [CodePilot](https://github.com/heidarboie/Copilot) - Electron + Claude SDK 集成参考
- [Magic](https://github.com/heidarboie/Magic) - Agent 市场 + 多 Agent 协作参考
- [CyberTeam V4](https://github.com/heelaw/cyberteam) - CEO 路由 + 三省六部架构

### 功能模块设计

- [ ] Phase 0: 项目初始化
- [ ] Phase 1: 设置 + Provider 管理
- [ ] Phase 2: 项目 + 目录管理
- [ ] Phase 3: 对话核心
- [ ] Phase 4: 聊天界面（微信风格）
- [ ] Phase 5: 部门 + Agent 市场
- [ ] Phase 6: Skill 管理
- [ ] Phase 7: 多 Agent 协作 + CEO 审核
- [ ] Phase 8: Playground + 会议纪要
- [ ] Phase 9: 打包发布

---

## 版本说明

版本格式：`MAJOR.MINOR.PATCH`

- **MAJOR**: 不兼容的 API 变更
- **MINOR**: 向后兼容的新功能
- **PATCH**: 向后兼容的 Bug 修复

预发布版本：
- `alpha` - 内部测试版
- `beta` - 公开测试版
- `rc` - 候选发布版
