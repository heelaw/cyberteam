# CyberTeam 自主任务规划系统 - 快速开始

## 🚀 一句话启动

```bash
cyberteam auto "你的需求描述"
```

## 📋 示例

### 简单任务
```bash
cyberteam auto "创建一个TODO应用原型"
```

输出:
```
[1/4] 📊 分析任务需求...
      ✓ 任务类型: 软件开发
      ✓ 复杂度: 简单
      ✓ 预估工期: 1-2天

[2/4] 👥 组建专家团队...
      ✓ 总人数: 2人

[3/4] 📋 分解任务...
      ✓ 子任务数: 3个
```

### 复杂项目
```bash
cyberteam auto "开发一个带用户认证的SaaS协作平台"
```

输出:
```
✓ 任务类型: 软件开发
✓ 复杂度: 复杂
✓ 团队规模: 6人
✓ 任务数量: 8个
✓ 预估工时: 72小时
```

## 🔧 核心能力

### 1. 任务分析（Task Analyzer）
- 识别任务类型：软件开发、数据分析、文档创作、研究调查
- 评估复杂度：简单、中等、复杂、超复杂
- 推荐技术栈
- 预估工期

### 2. 团队组合（Team Composer）
- 自动选择最优专家组合
- 支持15+专业角色
- 智能配置专家prompt

### 3. 任务分解（Task Decomposer）
- 智能分解为可执行子任务
- 设置任务依赖关系
- 定义验收标准
- 估算工时

## 📦 支持的专家角色

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

## 🎯 使用场景

### 场景1: 快速原型
```bash
cyberteam auto "创建一个TODO应用"
```
→ 2人团队，1-2天完成

### 场景2: 完整产品
```bash
cyberteam auto "开发一个企业级协作平台"
```
→ 6-8人团队，2-4周完成

### 场景3: 数据分析
```bash
cyberteam auto "分析销售数据并生成可视化报表"
```
→ 数据分析师团队

### 场景4: 技术调研
```bash
cyberteam auto "调研微服务架构方案"
```
→ 研究员团队

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
[用户确认]
    ↓
执行计划
    ↓
专家协同工作
    ↓
输出成果
```

## 📝 下一步功能

### Phase 2 (开发中)
- [ ] 自动执行计划（--execute参数）
- [ ] 动态创建专家
- [ ] 进度监控和阻塞检测

### Phase 3 (规划中)
- [ ] 智能资源调度
- [ ] 动态任务创建
- [ ] 多阶段迭代支持

## 💡 提示

1. **描述越清晰，规划越准确**
   - 好: "开发一个带用户认证的博客系统"
   - 差: "做一个博客"

2. **复杂度关键词影响团队规模**
   - 简单/原型 → 小团队
   - 复杂/超复杂 → 大团队

3. **可以指定项目名称**
   ```bash
   cyberteam auto "需求" --project "我的项目"
   ```

---

*更新日期: 2026-03-22*
*版本: v1.0*
