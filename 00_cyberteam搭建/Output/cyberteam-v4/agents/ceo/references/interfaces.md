# interfaces - CEO 总指挥

**版本**: v2.0
**更新**: 2026-03-25
**状态**: 已集成项目资料库架构

---

## 一、输入接口（新）

### 1.1 用户任务输入

```yaml
type: user_task
version: "2.0"

# 任务基本信息
task:
  id: task_xxx              # 自动生成
  type: 新项目 | 已有项目追加 | 常规咨询
  description: 用户任务描述

# 项目关联（如果是已有项目追加）
project_id: proj_xxx         # 可选

# 上下文信息
context:
  user_background: 用户背景（行业/公司/职位）
  expected_delivery: 期望交付物
  deadline: 期望完成时间
  budget_constraint: 预算约束（可选）

# 约束条件
constraints:
  must_include: [强制包含内容]
  must_exclude: [禁止包含内容]
  prefer_methods: [推荐方法]
```

### 1.2 项目资料库读取

```yaml
# 启动时自动读取
project_id: proj_xxx
reading_sequence:
  - shared/business_data/          # 必读：标准业务数据
  - shared/templates/               # 必读：文档模板
  - projects/{project_id}/metadata.yaml  # 必读：项目元数据
  - projects/{project_id}/context/  # 业务背景
  - projects/{project_id}/decisions/ # 历史决策
  - projects/{project_id}/meetings/ # 历史会议记录
```

---

## 二、输出接口（新）

### 2.1 项目初始化

```yaml
# 如果用户提交新任务，CEO负责初始化项目
type: project_initialized
output:
  project_id: proj_xxx
  created_from: 用户任务描述
  routing_result:
    target: L2/L3A/L3B/L3C/SWARM
    intent: Intent
    complexity: 高/中/低
    reason: 路由原因
  agents_assigned:
    - agent_id: agent_xxx
      role: 角色
      responsibility: 职责
  next_action: 等待用户确认项目方向
```

### 2.2 路由决策输出

```yaml
type: routing_decision
version: "2.0"

routing_result:
  target: enum          # L2/L3A/L3B/L3C/SWARM
  intent: Intent         # 数据分析|内容运营|技术研发|安全合规|战略规划|人力资源|运营支持|未知
  complexity: Complexity # 高|中|低
  reason: string         # 路由原因说明
  swarm_id: string       # SWARM模式时返回
  agents: Agent[]        # 分配的Agent列表

# 项目文件更新
project_updates:
  - file: projects/{project_id}/context/routing_decision.md
    action: created
  - file: projects/{project_id}/meetings/meeting_001.md
    action: created_if_swarm
```

---

## 三、项目文件规范（新）

### 3.1 必须创建的文件

```
projects/{project_id}/
├── metadata.yaml           # 项目元数据（CEO创建）
├── context/
│   ├── user_task.md       # 用户原始需求
│   ├── business_context.md # 业务背景
│   └── constraints.md      # 约束条件
├── decisions/
│   └── routing_decision.md # 路由决策
└── meetings/
    └── meeting_001.md      # Swarm会议记录（SWARM模式）
```

### 3.2 文件读取优先级

| 优先级 | 文件 | 说明 |
|--------|------|------|
| P0 | `shared/business_data/` | 所有Agent必须先读标准业务数据 |
| P0 | `shared/templates/` | 必须遵循文档模板 |
| P1 | `projects/{id}/metadata.yaml` | 项目基本信息 |
| P1 | `projects/{id}/context/` | 业务背景 |
| P2 | `projects/{id}/decisions/` | 历史决策参考 |
| P2 | `projects/{id}/meetings/` | 历史会议参考 |

## 输出接口

| 接口 | 类型 | 说明 |
|------|------|------|
| `routing_result` | RoutingResult | 路由决策结果 |
| `intent` | Intent | 识别出的用户意图（8种） |
| `complexity` | Complexity | 复杂度评估（高/中/低） |
| `swarm_id` | string | Swarm团队ID（高复杂度时） |
| `agents` | Agent[] | 分配的Agent列表（可选） |

## RoutingResult 结构

```yaml
RoutingResult:
  target: enum          # L2/L3A/L3B/L3C/SWARM
  intent: Intent         # 数据分析|内容运营|技术研发|安全合规|战略规划|人力资源|运营支持|未知
  complexity: Complexity # 高|中|低
  reason: string         # 路由原因说明
  swarm_id: string       # SWARM模式时返回
  agents: Agent[]        # 分配的Agent列表
```

## 调用示例

```python
from engine.ceo import CEORouter

router = CEORouter()
result = router.route("用户任务描述")

# 返回示例
{
    "target": "SWARM",
    "intent": "战略规划",
    "complexity": "高",
    "reason": "高复杂度+多领域+战略类型",
    "swarm_id": "ceo-strategy-xxx-uuid",
    "agents": ["researcher-1", "researcher-2", "executor-1", "executor-2", "qa"]
}
```

## 意图识别映射

| 意图 | 触发关键词 |
|------|------------|
| 数据分析 | 增长, 数据, 分析, 财务, ROI, 转化率, GMV, DAU, 留存, LTV |
| 内容运营 | 内容, 文案, 创作, 文章, 发布, 公众号, 小红书, 抖音, 营销, 推广 |
| 技术研发 | 开发, 代码, 功能, 实现, 修复, Bug, 架构, 测试, 部署, API |
| 安全合规 | 安全, 审计, 合规, 隐私, 漏洞, 渗透 |
| 战略规划 | 战略, 规划, 方案, 决策, 竞争, 市场, 进入 |
| 人力资源 | 招聘, 绩效, 团队, 人力, OKR |
| 运营支持 | 运营, 活动, 用户, 社群, 增长黑客 |

## 路由目标映射

| 目标 | 说明 | 触发条件 |
|------|------|----------|
| L2 | PM + Strategy 协调层 | 高/中复杂度 |
| L3A | CyberTeam 部门 | 默认路由 |
| L3B | Gstack Skills | 技术研发/代码审查 |
| L3C | 独立 Agents | 通用功能开发 |
| SWARM | Swarm 群体智能 | 高复杂度+多领域+明确要求 |

---

## 四、项目工作流程（新）

### 4.1 完整流程

```
1. 用户提交任务
         ↓
2. CEO读取 shared/business_data/ 和 shared/templates/
         ↓
3. CEO判断：
   - 新任务 → 创建项目 projects/proj_xxx/
   - 已有项目追加 → 读取 projects/{id}/context/
         ↓
4. 路由决策 + 项目初始化
         ↓
5. 分配Agent团队
         ↓
6. Agent工作 → 产出存入 projects/{id}/
         ↓
7. 会议记录 → meetings/meeting_*.md
         ↓
8. 方案产出 → decisions/options.md
         ↓
9. 知识沉淀 → 重要内容 → shared/knowledge_base/
```

### 4.2 项目归档规则

| 类型 | 存储位置 | 说明 |
|------|----------|------|
| 用户原始需求 | `context/user_task.md` | 不变 |
| 业务背景 | `context/business_context.md` | 可更新 |
| 会议记录 | `meetings/meeting_*.md` | 每次会议新建 |
| 方案选项 | `decisions/options.md` | 方案文档 |
| 最终决策 | `decisions/decision.md` | 决策结果 |
| 知识沉淀 | `shared/knowledge_base/` | 重要洞察 |

---

## 五、版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-25 | 初始版本（基础路由接口） |
| v2.0 | 2026-03-25 | 集成项目资料库架构、输入/输出标准化 |

---

*CEO接口版本: v2.0 | 最后更新: 2026-03-25*
