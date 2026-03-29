# Changelog

All notable changes to CyberTeam V4 will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [v4.1.0] - 2026-03-28

### Added
- **engine/state_machine.py** - Edict 三省六部状态机模块
  - 11个状态定义 (PENDING → TAIZI → ZHONGSHU → MENXIA → ASSIGNED → DOING → REVIEW → DONE)
  - CyberTeam 八节点映射
  - 状态转换规则校验
  - 转换历史记录 + 回调钩子

- **engine/rbac.py** - RBAC 权限矩阵模块
  - 22个 Agent 角色定义
  - Edict allowAgents 白名单机制
  - 双向权限校验（通信 + 调度）
  - BFS 路由路径计算

### Changed
- engine/__init__.py 集成新模块

## [v4.0.0] - 2026-03-27

### Added
- 完整 CyberTeam V4 架构
- CEO/COO/PM 三层管理架构
- 八节点流程引擎
- Mailbox 消息机制
- SkillLoader 技能加载系统
- 11个部门执行器
- ClawTeam 集成适配器
- gstack 集成适配器
- 后端 RESTful API (FastAPI)
- 前端 WebUI
- Docker 部署支持
- CI/CD 流水线

### Features
- 40+ 工程专家 Agent
- 20+ 设计专家 Agent
- 30+ 营销专家 Agent
- 50+ Skills 技能库
- 七层架构设计
- 多 Agent 并行处理
- 群体智能协作

---

## 版本规范 (Versioning Specification)

### 版本命名规则
```
v主版本.次版本.修订版本

v4.0.0 - 重大架构版本
v4.1.0 - 新功能版本（新增功能，向后兼容）
v4.0.1 - 修订版本（Bug修复，向后兼容）
v4.1.0-beta - 预发布版本
```

### Git Tag 规则
```bash
# 标记正式版本
git tag -a v4.1.0 -m "Release v4.1.0"
git push origin v4.1.0

# 标记预发布
git tag -a v4.2.0-beta -m "Beta release v4.2.0"
```

### Commit Message 规范
```
feat:     新功能
fix:      Bug 修复
docs:     文档更新
style:    代码格式（不影响功能）
refactor: 重构（不影响功能）
test:     测试相关
chore:    构建/工具相关
perf:     性能优化
ci:       CI/CD 相关
```

### 版本发布流程
1. 更新 CHANGELOG.md
2. 更新 _version.py 版本号
3. 创建 git tag
4. 提交并推送
5. GitHub Release (可选)

### 模块版本对应

| 模块 | 当前版本 | 说明 |
|------|----------|------|
| cyberteam | 4.0.0 | 核心包 |
| engine | 4.1.0 | 引擎模块 |
| state_machine | 1.0.0 | 状态机 |
| rbac | 1.0.0 | 权限矩阵 |
