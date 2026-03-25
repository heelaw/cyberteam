# CyberTeam 自主任务规划系统 - 完整使用指南

## 🚀 核心功能

一句话启动完整AI团队：
```bash
cyberteam auto "你的需求描述"
```

## 📊 系统架构

### 三大核心组件

**1. Task Analyzer（任务分析器）**
- 识别任务类型：软件开发、数据分析、文档创作、研究调查
- 评估复杂度：简单、中等、复杂、超复杂
- 推荐技术栈和所需角色
- 预估工期

**2. Team Composer（团队组合器）**
- 15+专业角色数据库
- 根据任务自动选择最优团队
- 智能生成专家prompt

**3. Task Decomposer（任务分解器）**
- 智能分解为可执行子任务
- 设置依赖关系
- 定义验收标准
- 估算工时

**4. Plan Executor（计划执行器）** ⭐ NEW
- 自动创建团队
- 批量创建专家
- 自动创建任务
- 让专家开始工作

## 🎯 使用方法

### 基础模式（仅规划）

```bash
cyberteam auto "创建一个博客系统"
```

输出：
```
[1/4] 📊 分析任务需求...
      ✓ 任务类型: 软件开发
      ✓ 复杂度: 中等
      ✓ 预估工期: 3-7天

[2/4] 👥 组建专家团队...
      ✓ 团队规模: 4人

[3/4] 📋 分解任务...
      ✓ 子任务数: 6个

[4/4] 📝 生成执行计划...
      ✓ 执行计划已生成

提示: 使用 --execute 参数来执行此计划
```

### 执行模式（自动执行）⭐

```bash
cyberteam auto "开发一个带用户认证的SaaS协作平台" --execute
```

输出：
```
[1/4] 创建团队...
      ✓ 团队已创建

[2/4] 创建专家...
      [1/6] 创建 系统架构师...
              ✓ 已启动
      [2/6] 创建 数据建模师...
              ✓ 已启动
      ...

[3/4] 创建任务...
      ✓ 系统架构设计 (ID: 330806bd)
      ✓ 数据模型设计 (ID: b47c000f)
      ...

[4/4] 通知专家开始工作...
      ✓ 已通知协调员

✓ 执行完成！
  团队: enterprise-collab
  创建专家: 7个
  创建任务: 6个
```

### 指定项目名称

```bash
cyberteam auto "需求描述" --project "my-project"
```

## 📦 支持的专家角色（15+）

### 研究类
- `requirement_analyst` - 需求分析师
- `tech_researcher` - 技术研究员

### 设计类
- `architect` - 系统架构师
- `ux_designer` - UX设计师
- `data_modeler` - 数据建模师

### 开发类
- `frontend_dev` - 前端开发
- `backend_dev` - 后端开发
- `fullstack_dev` - 全栈开发
- `mobile_dev` - 移动开发

### 质量类
- `tester` - 测试工程师
- `security_auditor` - 安全审计师
- `performance_optimizer` - 性能优化师

### 文档类
- `tech_writer` - 技术文档工程师
- `tutorial_creator` - 教程创作者

### 协调类
- `project_coordinator` - 项目协调员
- `code_reviewer` - 代码审查员

## 🎮 实际示例

### 示例1: 简单原型

```bash
$ cyberteam auto "创建一个TODO应用原型" --execute

团队规模: 2人
创建专家: 2个
创建任务: 3个
执行时间: 8秒

✓ 团队已就绪！
```

### 示例2: 复杂系统

```bash
$ cyberteam auto "开发一个超复杂的企业级协作平台，需要前后端分离、数据库设计、API开发、用户认证、实时通讯功能" --execute

团队规模: 8人
创建专家: 7个
创建任务: 6个
执行时间: 45秒

✓ 团队已就绪！
```

## 🔍 查看进度

### 查看团队状态
```bash
cyberteam team status <project-name>
```

### 查看任务列表
```bash
cyberteam task list <project-name>
```

### 启动 Web UI 监控
```bash
cyberteam board live <project-name>
```

### 附加到专家窗口
```bash
tmux attach -t cyberteam-<project-name>:<agent-name>
```

例如：
```bash
tmux attach -t cyberteam-enterprise-collab:architect
tmux attach -t cyberteam-enterprise-collab:project_coordinator
```

## 💡 提示

### 1. 需求描述越清晰，规划越准确

**好的描述：**
- "开发一个带用户认证的博客系统，支持Markdown编辑和评论功能"
- "创建一个数据分析仪表板，连接PostgreSQL数据库，使用Python"

**不够清晰的描述：**
- "做一个博客"
- "数据分析"

### 2. 复杂度关键词影响团队规模

包含以下关键词会增加复杂度：
- "简单"、"原型"、"demo" → 简单（1-2人）
- "中等"、"标准" → 中等（3-5人）
- "复杂"、"企业级"、"完整系统" → 复杂（6-10人）
- "超复杂"、"分布式"、"微服务" → 超复杂（10+人）

### 3. 自动处理 Workspace 问题

系统会自动处理 Git workspace 创建失败的情况：
- 首先尝试使用 tmux backend with workspace
- 如果失败，自动切换到 subprocess backend
- 确保专家能够成功启动

## 🔄 工作流程

```
用户输入需求
    ↓
Task Analyzer 分析任务
    ↓
Team Composer 组建团队
    ↓
Task Decomposer 分解任务
    ↓
Plan Executor 执行计划
    ↓
┌─────────────────┐
│  创建团队        │
│  创建专家        │
│  创建任务        │
│  通知协调员      │
└─────────────────┘
    ↓
专家协同工作
    ↓
输出成果
```

## 📊 成功案例

### 案例1: Calculator 应用
```bash
$ cyberteam auto "创建一个简单的计算器应用" --project calculator --execute

✓ 团队: calculator
✓ 专家: 1名 (fullstack_dev)
✓ 任务: 自动创建并执行
```

### 案例2: Enterprise 协作平台
```bash
$ cyberteam auto "开发一个超复杂的企业级协作平台" --project enterprise-collab --execute

✓ 团队: enterprise-collab
✓ 专家: 7名 (architect, data_modeler, backend_dev, tester, tech_writer, code_reviewer, project_coordinator)
✓ 任务: 6个 (系统架构、数据模型、后端API、数据库、功能测试、技术文档)
✓ 状态: 5个任务已进入 in_progress
```

## 🛠️ 高级功能（开发中）

### Phase 2 (部分已完成)
- ✅ 自动创建团队
- ✅ 批量创建专家
- ✅ 自动创建任务
- ✅ 进度监控
- 🔄 动态资源调度
- 🔄 智能阻塞检测

### Phase 3 (规划中)
- 动态任务创建（专家遇到问题时自动创建子任务）
- 多阶段迭代支持
- 风险预测和规避
- 自动代码审查流程

## 📝 故障排除

### 问题1: Git workspace 创建失败

**解决方案：** 系统会自动切换到 subprocess backend，无需手动处理

### 问题2: 专家启动失败

**检查：**
```bash
ps aux | grep claude | grep <project-name>
```

**手动启动：**
```bash
cyberteam spawn subprocess claude --team <project> --agent-name <name> --task "<task>" --no-workspace
```

### 问题3: 任务没有被领取

**通知协调员：**
```bash
cyberteam inbox send <project> project_coordinator "请分配任务给专家"
```

## 🎉 总结

CyberTeam 自主任务规划系统让你能够：

1. **一句话启动完整AI团队** - 无需手动配置
2. **智能任务分解** - 自动创建可执行的子任务
3. **自动执行** - 使用 `--execute` 参数一键启动
4. **实时监控** - 通过 Web UI 或命令行查看进度

开始使用：
```bash
cyberteam auto "你的项目需求" --execute
```

---

*更新日期: 2026-03-22*
*版本: v2.0 (支持 --execute)*
