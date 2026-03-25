# CyberTeam V4 目录架构重构计划

## 当前问题分析

### 问题1: AGENT.md 分散
```
当前: 分散在 30+ 个位置
- 中台/各中台/AGENT.md
- 增长BG/BG-LEADER/AGENT.md
- 技术BG/研发部/AGENT.md
- skills/v3-agents/...
- CEO总指挥/AGENT.md
```

### 问题2: 空目录
```
agents/ - 空目录
```

### 问题3: 旧版本残留
```
v3/           - 旧版本残留
v3-agents/    - 旧版本残留
cyberteam-extensions/ - 疑似重复
```

### 问题4: skills/ 混杂
```
skills/
├── agency-agents/  - 第三方
├── baoyu/         - 第三方
├── gstack/        - 第三方
├── superpowers/   - 第三方
├── pua-skill/     - 第三方
├── v3/           - 旧版本
└── v3-agents/    - 旧版本
```

## 目标架构

```
CyberTeam V4/
├── agents/               # 角色定义（统一）
│   ├── ceo/             - CEO角色
│   ├── strategy/         - 策略专家
│   ├── pm/              - 项目经理
│   ├── department/       - 部门总监
│   ├── middle-tier/     - 中台服务
│   │   ├── thinking/    - 思维注入
│   │   ├── communication/ - 通信协作
│   │   ├── memory/     - 记忆存储
│   │   ├── monitoring/ - 监控
│   │   └── assets/     - 资产库
│   └── bg/             - 业务BG
│       ├── growth/      - 增长BG
│       ├── product/    - 产品BG
│       ├── tech/       - 技术BG
│       └── ceo-officer/- 总经办
├── engine/               # 核心引擎
│   ├── ceo/            - CEO路由
│   ├── pm/             - 项目管理
│   ├── department/     - 部门调度
│   ├── strategy/       - 策略设计
│   ├── debate/         - 辩论引擎
│   └── thinking/        - 思维注入
├── cyberteam/            # 底层能力（来自ClawTeam）
│   ├── team/
│   ├── spawn/
│   ├── workspace/
│   ├── transport/
│   ├── board/
│   ├── cli/
│   ├── mcp/
│   └── skills/
├── skills/               # 扩展工具
│   ├── third-party/    # 第三方Skills
│   │   ├── baoyu/
│   │   ├── gstack/
│   │   ├── superpowers/
│   │   ├── agency/
│   │   └── pua/
│   └── custom/         # 自定义Skills
│       └── [future]
├── 中台/                  # 共享服务
│   ├── thinking/        - 思维注入服务
│   ├── communication/  - 通信协作
│   ├── memory/         - 记忆存储
│   ├── monitoring/     - 监控
│   └── assets/         - 资产库
├── docs/                 # 文档
├── tests/                # 测试
└── [BG业务目录]          # 业务BG（保持结构，含AGENT.md）
```

## 执行计划

### Phase 1: 清理旧版本
- [ ] 删除 v3/ 目录
- [ ] 删除 v3-agents/ 目录
- [ ] 删除 cyberteam-extensions/ 目录

### Phase 2: 重组 skills/
- [ ] 创建 skills/third-party/
- [ ] 移动第三方Skills到third-party/
- [ ] 创建 skills/custom/
- [ ] 更新 skills/README.md

### Phase 3: 迁移 AGENT.md
- [ ] 创建 agents/ 目录结构
- [ ] 迁移 CEO总指挥/AGENT.md → agents/ceo/
- [ ] 迁移 中台/各中台/AGENT.md → agents/middle-tier/
- [ ] 迁移 BG/BG-LEADER/AGENT.md → agents/bg/
- [ ] 清理空的原AGENT.md位置

### Phase 4: 拆分 engine/
- [ ] 创建 engine/ceo/, engine/pm/, engine/department/, engine/strategy/, engine/debate/
- [ ] 移动 ceo.py → engine/ceo/
- [ ] 移动 pm.py → engine/pm/
- [ ] 移动 department.py → engine/department/
- [ ] 移动 strategy.py → engine/strategy/
- [ ] 移动 debate_engine.py → engine/debate/
- [ ] 更新所有导入路径

### Phase 5: 重组中台/
- [ ] 重组中台目录结构
- [ ] 清理空的子目录
- [ ] 确保中台服务完整

### Phase 6: 验证
- [ ] 运行测试
- [ ] 验证导入
- [ ] 更新文档

---

*创建: 2026-03-25*
