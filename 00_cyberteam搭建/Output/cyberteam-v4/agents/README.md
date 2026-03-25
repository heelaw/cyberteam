# CyberTeam V4 Agents 目录

## 目录结构

```
agents/
├── ceo/              # CEO 角色定义
├── strategy/         # 策略专家
├── pm/               # 项目经理
├── department/       # 部门总监
├── middle-tier/      # 中台服务
│   ├── thinking/    # 思维注入
│   ├── communication/ # 通信协作
│   ├── memory/     # 记忆存储
│   ├── monitoring/ # 监控
│   └── assets/     # 资产库
└── bg/              # 业务BG
    ├── growth/     # 增长BG
    ├── product/     # 产品BG
    ├── tech/        # 技术BG
    └── ceo-officer/ # 总经办
```

## Agent 定义说明

每个 Agent 是一个角色定义文件（AGENT.md），包含：

- **身份**: 角色名称、背景、核心能力
- **触发条件**: 何时调用此 Agent
- **工作流程**: 如何执行任务
- **输出格式**: 标准化的输出结构
- **Handoff协议**: 与其他 Agent 的交接规范

## Agent 层级

```
CEO (总指挥)
    │
    ├── Strategy (策略)
    ├── PM (项目管理)
    ├── Department (部门)
    │   ├── Growth BG (增长)
    │   ├── Product BG (产品)
    │   ├── Tech BG (技术)
    │   └── CEO Officer (总经办)
    └── Middle-tier (中台服务)
        ├── Thinking (思维注入)
        ├── Communication (通信)
        ├── Memory (记忆)
        ├── Monitoring (监控)
        └── Assets (资产)
```

## 角色定义规范

1. **文件名**: `AGENT.md`
2. **位置**: 按角色分类到对应目录
3. **格式**: Markdown，包含完整的角色定义

---

*更新: 2026-03-25*
