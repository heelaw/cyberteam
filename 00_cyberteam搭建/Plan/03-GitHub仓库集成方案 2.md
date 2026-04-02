# GitHub仓库集成方案

**版本**: v1.0
**日期**: 2026-03-23
**输出目录**: `/Users/cyberwiz/Documents/01_Project/02_Skill研发/cyberteam搭建/【项目组2】/`

---

## 仓库清单

| # | 仓库 | 本地路径 | Stars | 核心功能 |
|---|------|----------|-------|----------|
| 1 | ClawTeam | ~/github_stars/ClawTeam | 2,897 | Agent协调框架 |
| 2 | agency-agents | ~/github_stars/agency-agents | 59,702 | 多Agent协作 |
| 3 | agency-agents-zh | ~/github_stars/agency-agents-zh | 1,992 | 中文版Agent |
| 4 | autoresearch-master | ~/github_stars/autoresearch-master | 469 | 自动研究 |
| 5 | everything-claude-code | ~/github_stars/everything-claude-code | 98,576 | Claude Code优化 |
| 6 | goal-driven-main | ~/github_stars/goal-driven-main | 545 | 目标驱动模式 |
| 7 | gstack | ~/github_stars/gstack | 38,683 | 虚拟工程团队 |
| 8 | OpenViking | ~/github_stars/OpenViking | 18,027 | 上下文数据库 |
| 9 | paperclip | ~/github_stars/paperclip | 31,692 | 工作流编排 |
| 10 | pua-main | ~/github_stars/pua-main | 10,173 | 激励模式 |
| 11 | superpowers-main | ~/github_stars/superpowers-main | - | 超能力集 |

---

## 集成矩阵

### 1. ClawTeam - 底层框架

**集成层级**: P0 - 底层框架

```yaml
clawteam:
  purpose: "Agent协调和团队管理"

  core_features:
    - tmux会话管理
    - Agent spawn和管理
    - 消息传递系统
    - 任务管理
    - 团队协作

  integration_points:
    ceo_layer:
      - CEO通过clawteam spawn部门Agent
      - 消息传递给各部门

    management_layer:
      - 部门Agent通过clawteam通信
      - 任务通过clawteam分发

    execution_layer:
      - 执行Agent通过clawteam协调
      - 进度汇报到CEO

  install_location: "~/.clawteam/"
```

### 2. agency-agents - 部门Agent模板

**集成层级**: P0 - 部门模板

```yaml
agency_agents:
  purpose: "多部门Agent协作模板"

  departments:
    engineering:
      - frontend-developer
      - backend-architect
      - security-engineer
      - devops-automator
      - data-engineer
      - mobile-app-builder

    design:
      - ui-designer
      - ux-researcher
      - visual-storyteller
      - brand-guardian
      - whimsy-injector

    marketing:
      - douyin-strategist
      - xiaohongshu-specialist
      - tiktok-strategist
      - seo-specialist
      - growth-hacker

  integration_points:
    - 复制agents/*.md到~/.claude/agents/
    - 部门前缀映射到CyberTeam部门
    - 思维注入到各Agent

  install_command: |
    cp -r ~/github_stars/agency-agents/engineering/*.md ~/.claude/agents/
    cp -r ~/github_stars/agency-agents/design/*.md ~/.claude/agents/
    cp -r ~/github_stars/agency-agents/marketing/*.md ~/.claude/agents/
```

### 3. agency-agents-zh - 本地化

**集成层级**: P1 - 本地化

```yaml
agency_agents_zh:
  purpose: "中文版Agent"

  features:
    - 中文提示词
    - 本土化案例
    - 中文输出格式

  integration_points:
    - 覆盖英文agent提示词
    - 提供中文模板
    - 保留英文原版作为参考
```

### 4. autoresearch-master - 自动研究

**集成层级**: P1 - CEO工具

```yaml
autoresearch:
  purpose: "自动网络研究和信息收集"

  features:
    - 自动搜索相关资料
    - 信息聚合和分析
    - 研究报告生成

  integration_points:
    ceo_layer:
      - CEO在拆解问题时调用autoresearch
      - 获取行业信息、市场数据、竞品分析

    thinking_experts:
      - 思维专家需要数据支撑时调用
      - 验证假设时调用

  install_location: "~/.claude/skills/autoresearch/"
```

### 5. everything-claude-code - 性能优化

**集成层级**: P1 - 性能层

```yaml
everything_claude_code:
  purpose: "Claude Code性能和效率优化"

  features:
    - hooks系统
    - commands命令
    - instincts本能
    - memory优化
    - 安全扫描

  integration_points:
    all_layers:
      - CEO层: 高效意图理解
      - 管理层: 快速部门讨论
      - 执行层: 高效代码实现

    specific:
      - hooks: 上下文压缩
      - commands: 常用操作快捷化
      - instincts: 模式匹配自动化

  install_location: "~/.claude/"
```

### 6. goal-driven - 目标驱动

**集成层级**: P2 - 执行模式

```yaml
goal_driven:
  purpose: "长任务自动续跑"

  features:
    - Master Agent + Subagent模式
    - 目标-标准-检查循环
    - 自动恢复机制
    - 长时间运行支持

  integration_points:
    execution_layer:
      - 复杂任务自动续跑
      - 中断后自动恢复
      - 目标达成验证

    ceo_layer:
      - 大型项目自动分阶段
      - 里程碑检查点

  install_location: "~/.claude/skills/goal-driven/"
```

### 7. gstack - 工程命令

**集成层级**: P1 - 工程命令

```yaml
gstack:
  purpose: "虚拟工程团队slash commands"

  commands:
    office-hours: "战略讨论"
    plan-ceo-review: "CEO视角审核"
    plan-eng-review: "工程视角审核"
    design-review: "设计审核"
    review: "代码审查"
    qa: "测试验证"
    ship: "部署发布"
    retro: "复盘"

  integration_points:
    management_layer:
      - 部门会议讨论
      - 方案审核

    execution_layer:
      - 代码审查
      - 测试验证
      - 部署发布

  install_location: "~/.claude/skills/gstack/"
```

### 8. OpenViking - 上下文管理

**集成层级**: P2 - 记忆系统

```yaml
openviking:
  purpose: "AI Agent上下文数据库"

  features:
    - 文件系统范式管理context
    - 层级化context交付
    - 自进化memory系统

  integration_points:
    ceo_layer:
      - 跨会话记忆
      - 用户偏好记忆
      - 项目历史记忆

    thinking_experts:
      - 专家知识积累
      - 经验复用

    all_layers:
      - 上下文压缩和恢复
```

### 9. paperclip - 工作流编排

**集成层级**: P2 - 任务编排

```yaml
paperclip:
  purpose: "AI工作流编排系统"

  features:
    - 多步骤任务自动化
    - 工作流模板
    - 零人力公司编排

  integration_points:
    execution_layer:
      - 复杂任务分解执行
      - 部门协作流程编排
      - 自动测试部署

    ceo_layer:
      - 大型项目分阶段执行
```

### 10. pua - 激励模式

**集成层级**: P1 - 能动性驱动

```yaml
pua:
  purpose: "强制高能动性，不放弃"

  features:
    - L1-L4压力升级
    - 味道切换 (阿里/字节/华为...)
    - 失败计数持久化
    - 自动触发机制

  integration_points:
    all_layers:
      - CEO层: 高标准要求
      - 管理层: 压力传导
      - 执行层: 不放弃精神

    triggers:
      - 重复失败2次+
      - 被动等待
      - 推卸责任

  install_location: "~/.claude/skills/pua/"
```

### 11. superpowers - 能力扩展

**集成层级**: P3 - 能力扩展

```yaml
superpowers:
  purpose: "增强Agent特殊能力"

  categories:
    - 超级记忆
    - 超级搜索
    - 超级调试
    - 超级测试

  integration_points:
    按需调用:
      - 需要特殊能力时
      - 能力补强时
```

---

## 集成检查清单

### Phase 1: 底层框架 (Week 1)

- [ ] 集成ClawTeam
  - [ ] 配置tmux会话
  - [ ] 设置spawn命令
  - [ ] 配置消息传递
  - [ ] 测试Agent spawn

- [ ] 集成agency-agents
  - [ ] 复制engineering agents
  - [ ] 复制design agents
  - [ ] 复制marketing agents
  - [ ] 映射到CyberTeam部门

### Phase 2: 核心工具 (Week 2)

- [ ] 集成gstack
  - [ ] 安装所有commands
  - [ ] 配置快捷键
  - [ ] 测试主要功能

- [ ] 集成pua
  - [ ] 安装skill
  - [ ] 配置自动触发
  - [ ] 设置味道偏好

- [ ] 集成everything-claude-code
  - [ ] 安装hooks
  - [ ] 配置commands
  - [ ] 优化memory

### Phase 3: 扩展工具 (Week 3)

- [ ] 集成autoresearch
  - [ ] 安装skill
  - [ ] 配置搜索参数
  - [ ] 测试研究能力

- [ ] 集成goal-driven
  - [ ] 安装skill
  - [ ] 配置长任务模式
  - [ ] 测试自动续跑

- [ ] 集成paperclip
  - [ ] 安装CLI
  - [ ] 配置工作流
  - [ ] 测试任务编排

### Phase 4: 辅助工具 (Week 4)

- [ ] 集成OpenViking
  - [ ] 安装上下文系统
  - [ ] 配置记忆管理
  - [ ] 测试跨会话

- [ ] 集成superpowers
  - [ ] 安装能力扩展
  - [ ] 配置按需调用

- [ ] 集成agency-agents-zh
  - [ ] 本地化提示词
  - [ ] 中文模板

---

## 验证测试

### 集成验证清单

```yaml
integration_tests:
  clawteam:
    - [ ] 能spawn新Agent
    - [ ] Agent间能消息传递
    - [ ] 任务能分发和跟踪

  agency_agents:
    - [ ] 所有部门agent可调用
    - [ ] 思维注入生效
    - [ ] 输出格式统一

  gstack:
    - [ ] /office-hours可用
    - [ ] /review可用
    - [ ] /qa可用

  pua:
    - [ ] 失败触发L1
    - [ ] 多次失败升级L3
    - [ ] 味道可切换

  everything_claude_code:
    - [ ] hooks生效
    - [ ] memory优化生效

  autoresearch:
    - [ ] 能自动搜索
    - [ ] 能聚合信息

  goal_driven:
    - [ ] 长任务自动续跑
    - [ ] 中断后恢复

  paperclip:
    - [ ] 工作流可编排
    - [ ] 模板可用

  openviking:
    - [ ] 上下文持久化
    - [ ] 跨会话记忆

  superpowers:
    - [ ] 特殊能力可用
```

---

**文档状态**: 设计中
**创建日期**: 2026-03-23
