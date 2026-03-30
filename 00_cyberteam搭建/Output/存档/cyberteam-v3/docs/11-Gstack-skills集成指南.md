# Gstack Skills 集成指南

> **版本**: v3.1 | **创建日期**: 2026-03-24 | **更新日期**: 2026-03-24 | **定位**: 工程技能调用手册
>
> 本文档定义了 Gstack (43个工程技能) 的集成方式、调用边界、协作流程。
>
> **v3.1 更新**: 整合到 L3B 技术实现层，明确与 CyberTeam 协作流程。

---

## 目录

1. [Gstack 概述](#一gstack概述)
2. [技能分类与清单](#二技能分类与清单)
3. [调用机制](#三调用机制)
4. [使用场景](#四使用场景)
5. [集成协议](#五集成协议)
6. [最佳实践](#六最佳实践)

---

## 一、Gstack 概述

### 1.1 什么是 Gstack

```yaml
定义:
  Gstack 是一套工程技能集合，
  包含 43 个实用技能，覆盖代码开发、
  测试部署、项目管理等场景。

核心价值:
  - 技术实现: 代码编写、测试、部署
  - 工程化: CI/CD、监控、运维
  - 质量保证: 代码审查、安全审计
  - 团队协作: 项目管理、沟通协调

提供者:
  gstack (第三方工程技能集合)
```

### 1.2 架构定位

```
┌─────────────────────────────────────────────────────────────┐
│                    CyberTeam v3 架构                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  技术研发部 (主要使用者)                                     │
│    ↓                                                        │
│  PM 协调                                                    │
│    ↓                                                        │
│  L3B: Gstack Skills (43个)                                 │
│    ├── 代码开发 (codex)                                     │
│    ├── 代码审查 (review)                                    │
│    ├── QA测试 (qa)                                          │
│    ├── 部署发布 (ship)                                      │
│    ├── 监控运维 (canary)                                    │
│    └── ... (更多)                                           │
│    ↓                                                        │
│  返回技术实现结果                                            │
│    ↓                                                        │
│  整合到最终交付物                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 职责边界

```yaml
CyberTeam 负责:
  - 业务逻辑分析
  - 需求理解和拆解
  - 业务决策
  - 多部门协调

Gstack 负责:
  - 技术实现
  - 代码编写
  - 测试验证
  - 部署发布

协作流程:
  1. CyberTeam 部门分析业务需求
  2. CyberTeam PM 识别技术实现需求
  3. CyberTeam PM 调用 Gstack skills
  4. Gstack 返回技术实现结果
  5. CyberTeam 部门整合业务和技术结果
  6. CyberTeam PM 返回最终交付物
```

---

## 二、技能分类与清单

### 2.1 代码开发类

#### /codex

```yaml
功能: OpenAI Codex CLI 包装器
支持三种模式:
  1. 代码审查: 独立 diff 审查
  2. 挑战模式: 对抗性模式
  3. 咨询模式: 会话连续性

调用格式:
  /codex [mode] [args]

模式:
  review: 代码审查
    /codex review path/to/file.js

  challenge: 挑战代码
    /codex challenge "这段代码有问题吗？"

  consult: 咨询问题
    /codex consult "如何实现用户登录？"

使用场景:
  - 代码审查
  - 技术咨询
  - 代码挑战

触发条件:
  - 技术研发部识别需要编码任务
  - PM 识别需要代码审查
```

### 2.2 代码审查类

#### /review

```yaml
功能: PR 预审查

调用格式:
  /review path/to/file.js

输出:
  - 审查报告
  - 问题清单
  - 改进建议

使用场景:
  - 提交 PR 前审查
  - 代码质量检查
  - 安全性审查

触发条件:
  - 提交 PR 时
  - 代码合并前
```

### 2.3 QA 测试类

#### /qa

```yaml
功能: QA 测试 + 修复

调用格式:
  /qa path/to/test.spec.js

工作流程:
  1. 运行 QA 测试
  2. 识别问题
  3. 修复问题
  4. 重新验证

输出:
  - 测试报告
  - 问题修复记录
  - 最终验证结果

使用场景:
  - 功能测试
  - 回归测试
  - 集成测试

触发条件:
  - 需要测试功能
  - 发布前验证
```

#### /qa-only

```yaml
功能: 仅报告 QA 测试 (不修复)

调用格式:
  /qa-only path/to/test.spec.js

输出:
  - 测试报告
  - 问题清单
  - 健康评分

使用场景:
  - 只需要测试报告
  - 不需要自动修复

触发条件:
  - 用户明确只要报告
```

### 2.4 部署发布类

#### /ship

```yaml
功能: 发布工作流

调用格式:
  /ship

工作流程:
  1. 检测 + 合并基础分支
  2. 运行测试
  3. 审查 diff
  4. 更新版本号
  5. 更新 CHANGELOG
  6. 提交、推送、创建 PR

输出:
  - PR 链接
  - 发布状态

使用场景:
  - 准备发布
  - 创建 PR
  - 合并部署

触发条件:
  - 用户说 "ship"
  - 用户说 "deploy"
  - 用户说 "push to main"
```

#### /land-and-deploy

```yaml
功能: 合并部署工作流

调用格式:
  /land-and-deploy

工作流程:
  1. 合并 PR
  2. 等待 CI 和部署
  3. 验证生产健康

输出:
  - 部署状态
  - 生产健康检查

使用场景:
  - 合并 PR 后部署
  - 验证生产环境

触发条件:
  - PR 已批准
  - 准备合并部署
```

#### /canary

```yaml
功能: 金丝雀监控

调用格式:
  /canary

功能:
  - 监控生产环境
  - 检查控制台错误
  - 性能回归检测
  - 页面失败检测
  - 定期截图对比
  - 异常告警

使用场景:
  - 发布后监控
  - 生产环境监控
  - 金丝雀部署

触发条件:
  - 发布后
  - 用户要求监控
```

### 2.5 安全审计类

#### /cso

```yaml
功能: CSO 安全官模式

调用格式:
  /cso

审计内容:
  - OWASP Top 10 审计
  - STRIDE 威胁建模
  - 攻击面分析
  - 认证流程验证
  - 秘密检测
  - 依赖 CVE 扫描
  - 供应链风险评估
  - 数据分类审查

使用场景:
  - 安全审计
  - 威胁建模
  - 合规审查

触发条件:
  - 用户要求安全审计
  - 生产环境部署前
```

#### /guard

```yaml
功能: 安全警告 (破坏性操作)

调用格式:
  /guard

警告场景:
  - rm -rf
  - DROP TABLE
  - force-push
  - git reset --hard
  - kubectl delete

使用场景:
  - 触摸生产环境
  - 危险操作

触发条件:
  - 执行破坏性命令
  - 修改生产数据
```

#### /careful

```yaml
功能: 警告确认

调用格式:
  /careful [command]

功能:
  - 破坏性命令前警告
  - 用户确认后执行

使用场景:
  - 危险命令
  - 生产操作

触发条件:
  - 用户执行危险命令
```

### 2.6 调试诊断类

#### /investigate

```yaml
功能: 系统化调试

调用格式:
  /investigate "问题描述"

四个阶段:
  1. investigate: 调查问题
  2. analyze: 分析根因
  3. hypothesize: 提出假设
  4. implement: 实施修复

铁律: 没有根因不修复

使用场景:
  - 调试 Bug
  - 根因分析
  - 问题诊断

触发条件:
  - 用户说 "debug this"
  - 用户说 "fix this bug"
```

### 2.7 战略决策类

#### /office-hours

```yaml
功能: YC Office Hours

两种模式:
  1. Startup 模式: 六个强制问题
     - 需求现实
     - 现状
     - 绝对 specificity
     - 最窄楔子
     - 观察
     - 未来适配

  2. Builder 模式: 设计思维头脑风暴

调用格式:
  /office-hours [startup|builder]

使用场景:
  - 战略决策讨论
  - 创业问题分析
  - 产品设计

触发条件:
  - CEO 需要战略讨论
  - 重要决策前
```

### 2.8 其他技能

```yaml
规划相关:
  /plan-ceo-review: CEO/创始人模式计划审查
  /plan-eng-review: 工程经理模式计划审查
  /plan-design-review: 设计师眼计划审查

设计相关:
  /design-consultation: 设计咨询
  /design-review: 设计师眼 QA

文档相关:
  /document-release: 发布后文档更新

团队相关:
  /retro: 每周工程回顾

性能相关:
  /benchmark: 性能回归检测

浏览器相关:
  /browse: 无头浏览器 (QA 测试)
  /gstack: 快速无头浏览器

其他:
  /freeze: 限制编辑范围
  /unfreeze: 取消限制
  /setup-deploy: 配置部署设置
```

---

## 三、调用机制

### 3.1 调用方式

#### 方式1: 直接调用

```yaml
调用格式:
  /{skill-name} [args]

示例:
  /codex review path/to/file.js
  /qa path/to/test.spec.js
  /ship

执行流程:
  1. PM 决策调用技能
  2. 执行技能调用
  3. 获取执行结果
  4. 返回给 PM
```

#### 方式2: 通过 PM 调用

```yaml
调用流程:
  1. 用户需求
  2. CEO 路由到技术研发部
  3. 技术研发部分析需求
  4. PM 识别技术实现需求
  5. PM 调用 Gstack skills
  6. 获取执行结果
  7. 整合到交付物

示例:
  用户: "实现用户登录功能"
  → CEO 路由到技术研发部
  → 技术研发部分析需求
  → PM 调用:
      /codex "实现用户登录功能"
      /review src/auth.js
      /qa test/auth.spec.js
      /ship
  → 整合结果
  → 返回交付物
```

#### 方式3: 批量调用

```yaml
批量场景:
  - 完整开发流程
  - CI/CD 流水线
  - 发布流程

调用方式:
  顺序执行多个技能

示例:
  完整开发流程:
    /codex "实现功能"
    /review src/feature.js
    /qa test/feature.spec.js
    /ship

  输出: 完整交付物
```

### 3.2 调用协议

```yaml
输入格式:
  {
    "skill": "/codex",
    "mode": "review",
    "args": "path/to/file.js"
  }

输出格式:
  {
    "skill": "/codex",
    "status": "success",
    "result": {
      "output": "执行结果",
      "artifacts": ["产出物"]
    },
    "error": null
  }

错误处理:
  if 调用失败:
    - 记录错误日志
    - 返回错误信息
    - 降级到备用方案
    - 通知 PM
```

### 3.3 调用权限

```yaml
权限级别:
  L1 (CEO):
    - /office-hours: 完全权限
    - 其他: 只读

  L2 (PM):
    - 所有技能: 协调权限
    - 可以调用但不能直接执行

  L3 (技术研发部):
    - 所有技能: 完全权限
    - 可以调用和执行

调用原则:
  - PM 协调，部门执行
  - PM 不能绕过部门直接调用
  - 部门可以建议 PM 调用
```

---

## 四、使用场景

### 4.1 功能开发场景

```yaml
场景: 开发用户登录功能

流程:
  Step 1: 技术研发部分析需求
  Step 2: PM 协调
  Step 3: 调用 Gstack skills
  Step 4: 整合结果

调用序列:
  /codex "实现用户登录功能，使用 React + Node.js + JWT"
  → 生成代码

  /review src/auth.js
  → 审查代码

  /qa test/auth.spec.js
  → 测试功能

  /ship
  → 创建 PR

预期产出:
  - 功能代码
  - 审查报告
  - 测试报告
  - PR 链接
```

### 4.2 代码审查场景

```yaml
场景: 审查代码 PR

流程:
  Step 1: 提交 PR
  Step 2: 调用 /review 预审查
  Step 3: 调用 /cso 安全审查
  Step 4: 整合审查意见

调用序列:
  /review path/to/pr/file.js
  /cso

预期产出:
  - 代码审查报告
  - 安全审查报告
  - 改进建议
```

### 4.3 部署发布场景

```yaml
场景: 发布新功能

流程:
  Step 1: 准备发布
  Step 2: 调用 /ship
  Step 3: 合并 PR
  Step 4: 调用 /land-and-deploy
  Step 5: 调用 /canary 监控

调用序列:
  /ship
  → 创建 PR

  /land-and-deploy
  → 合并部署

  /canary
  → 监控生产

预期产出:
  - PR 链接
  - 部署状态
  - 生产监控报告
```

### 4.4 问题调试场景

```yaml
场景: 调试生产问题

流程:
  Step 1: 识别问题
  Step 2: 调用 /investigate
  Step 3: 根因分析
  Step 4: 实施修复
  Step 5: 验证修复

调用序列:
  /investigate "生产环境用户无法登录"
  → 根因分析

  /codex "修复认证问题"
  → 修复代码

  /qa test/auth.spec.js
  → 验证修复

  /ship
  → 部署修复

预期产出:
  - 根因分析报告
  - 修复代码
  - 验证报告
```

---

## 五、集成协议

### 5.1 与技术研发部集成

```yaml
集成方式:
  Gstack 作为技术研发部的标准工具集

调用流程:
  1. 用户需求 → CEO
  2. CEO 路由到技术研发部
  3. 技术研发部分析需求
  4. PM 协调
  5. 调用 Gstack skills
  6. 整合结果
  7. 返回交付物

调用权限:
  - 技术研发部: 所有技能完全权限
  - PM: 协调权限
  - 其他部门: 通过 PM 请求
```

### 5.2 与其他部门集成

```yaml
数据分析部:
  偶尔使用:
    - /codex: 数据处理脚本
    - /review: 审查数据代码
    - /qa: 测试数据管道

内容运营部:
  偶尔使用:
    - /codex: 自动化脚本
    - /review: 审查发布代码

安全合规部:
  主要使用:
    - /cso: 安全审计
    - /review: 安全审查
    - /investigate: 安全问题调查
```

### 5.3 调用边界

```yaml
CyberTeam 负责:
  - 业务需求分析
  - 技术方案设计
  - 结果整合验证

Gstack 负责:
  - 技术实现
  - 代码编写
  - 测试部署

不调用场景:
  - 纯业务问题 (不涉及技术实现)
  - 创意设计问题
  - 市场分析问题

必须调用场景:
  - 代码编写
  - 代码审查
  - 功能测试
  - 部署发布
```

---

## 六、最佳实践

### 6.1 开发流程

```yaml
最佳实践:
  1. 需求明确
     - 技术研发部分析需求
     - PM 确认技术方案

  2. 代码实现
     - 使用 /codex 生成代码
     - 人工审核关键部分

  3. 代码审查
     - 使用 /review 预审查
     - 使用 /cso 安全审查

  4. 测试验证
     - 使用 /qa 测试
     - 修复发现的问题

  5. 部署发布
     - 使用 /ship 创建 PR
     - 使用 /land-and-deploy 合并
     - 使用 /canary 监控
```

### 6.2 安全实践

```yaml
最佳实践:
  1. 代码审查
     - 提交前使用 /review
     - 重要代码使用 /cso

  2. 危险操作
     - 使用 /guard 保护
     - 使用 /careful 确认

  3. 生产环境
     - 使用 /freeze 限制范围
     - 使用 /canary 监控
```

### 6.3 调试实践

```yaml
最佳实践:
  1. 系统化调试
     - 使用 /investigate 调试
     - 遵循铁律: 没有根因不修复

  2. 问题跟踪
     - 记录问题
     - 分析根因
     - 验证修复

  3. 知识积累
     - 记录解决方案
     - 更新文档
```

---

## 七、附录

### 7.1 技能速查表

| 类别 | 技能 | 功能 |
|------|------|------|
| 代码开发 | codex | 代码生成与咨询 |
| 代码审查 | review | PR 预审查 |
| QA测试 | qa | 测试 + 修复 |
| QA测试 | qa-only | 仅测试报告 |
| 部署发布 | ship | 发布工作流 |
| 部署发布 | land-and-deploy | 合并部署 |
| 监控运维 | canary | 金丝雀监控 |
| 安全审计 | cso | CSO 安全官模式 |
| 安全审计 | guard | 安全警告 |
| 安全审计 | careful | 警告确认 |
| 调试诊断 | investigate | 系统化调试 |
| 战略决策 | office-hours | YC Office Hours |
| 浏览器 | browse | 无头浏览器 |
| 浏览器 | gstack | 快速无头浏览器 |

### 7.2 安装指南

```yaml
前提条件:
  - Claude Code CLI 已安装
  - Node.js 18+ (用于某些技能)
  - Git (用于版本控制)

安装方式:

方式1: 使用官方安装脚本 (推荐)

  Step 1: 克隆 Gstack 仓库
    git clone https://github.com/your-repo/gstack.git ~/.claude/skills/gstack

  Step 2: 运行安装脚本
    cd ~/.claude/skills/gstack
    ./setup

  Step 3: 验证安装
    /codex --help
    /review --help
    /qa --help

方式2: 手动安装

  Step 1: 创建技能目录
    mkdir -p ~/.claude/skills/gstack

  Step 2: 下载技能文件
    将各技能的 SKILL.md 文件放入对应目录

  Step 3: 配置依赖
    # 安装 Node.js 依赖 (如需要)
    cd ~/.claude/skills/gstack
    npm install

  Step 4: 验证安装
    ls ~/.claude/skills/gstack/

常用技能验证:

  # 代码审查
  /review path/to/file.js

  # QA 测试
  /qa test/file.spec.js

  # 发布
  /ship

升级 Gstack:

  # 使用升级技能
  /gstack-upgrade

  # 或手动拉取
  cd ~/.claude/skills/gstack
  git pull
```

### 7.3 相关文档

- [00-分层集成架构设计.md](./00-分层集成架构设计.md)
- [01-公司架构与人员配置.md](./01-公司架构与人员配置.md)
- [07-用户执行指南.md](./07-用户执行指南.md)

---

**文档版本**: v3.1
**创建日期**: 2026-03-24
**最后更新**: 2026-03-24

---

*本文档定义了 Gstack (43个工程技能) 的集成方式、调用边界、协作流程。*
