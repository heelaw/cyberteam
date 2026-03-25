# CyberTeam V4 技术规格说明书

> 版本: 4.0.0
> 更新日期: 2026-03-25

---

## 1. 系统概述

### 1.1 项目定位

CyberTeam V4 是一个企业级 AI Agent 协作系统，模拟真实公司运作，实现：
- **自动团队组建**: CEO 路由引擎自动分析需求，组建合适的 Agent 团队
- **多专家协作**: 14个思维专家 + 6个执行部门协同工作
- **质量保障**: 六维评分 + 五级质量门禁
- **外部集成**: ClawTeam 多Agent编排

### 1.2 架构概览

```
用户输入 → CEO路由(L1) → 策略层(L2) → 专家层(L3) → 评分门禁
                ↓
          ClawTeam Agent团队
```

---

## 2. 核心模块

### 2.1 CEO 路由引擎 (`engine/ceo.py`)

**职责**: 需求分拣、意图识别、复杂度评估、路由决策、Swarm 智能编排

**输入**: 用户任务描述
**输出**: 路由结果 (target, intent, complexity)

| 方法 | 说明 |
|------|------|
| `is_simple_consultation()` | 判断是否为简单咨询 |
| `recognize_intent()` | 识别8种意图类型 |
| `evaluate_complexity()` | 评估高/中/低复杂度 |
| `should_use_swarm()` | 判断是否需要 Swarm 群体智能 |
| `route()` | 执行路由决策 |
| `create_swarm_team()` | 创建 Swarm 团队 |
| `execute_swarm()` | 执行 Swarm 任务 |
| `get_swarm_status()` | 获取 Swarm 状态 |

**路由目标**:
- `L2`: PM + Strategy 协调层
- `L3A`: CyberTeam 部门
- `L3B`: Gstack Skills
- `L3C`: 独立 Agents
- `SWARM`: Swarm 群体智能 (新!)

**Swarm 触发条件**:
- 高复杂度任务 (字符数 > 100)
- 多领域任务 (含 "并且", "以及", "还有" 等连接词)
- 战略/分析类任务 (含 "战略", "分析", "规划" 等关键词)
- 明确要求团队协作 (含 "团队", "分工", "并行" 等关键词)

### 2.2 策略引擎 (`engine/strategy.py`)

**职责**: 方案设计、框架选择、资源规划

**核心类**: `StrategyEngine`, `ExecutionPlan`

### 2.3 项目管理 (`engine/pm.py`)

**职责**: 任务拆解、进度跟踪、风险管理

**执行模式**: `SERIAL` (串行) / `PARALLEL` (并行) / `HYBRID` (混合)

### 2.4 部门执行 (`engine/department.py`)

**6个执行部门**:
- 产品部 (product)
- 技术部 (engineering)
- 设计部 (design)
- 运营部 (operations)
- 财务部 (finance)
- 人力部 (hr)

### 2.5 辩论引擎 (`engine/debate_engine.py`)

**支持功能**:
- 多专家辩论
- 观点陈述与反驳
- 收敛判断
- 共识聚合

**状态机**: `PREPARING` → `IN_PROGRESS` → `CONVERGED`/`DEADLOCKED` → `COMPLETED`

### 2.6 ClawTeam 适配器 (`integration/clawteam_adapter.py`)

**功能**:
- 团队创建与管理
- Agent Spawn
- 任务分配
- 消息广播

**模板**: `dev` / `research` / `content` / `fullstack` / `swarm`

### 2.7 Swarm Intelligence (`swarm_orchestrator.py`)

**群体智能核心功能** (完整实现):

| 功能 | 状态 | 说明 |
|------|------|------|
| Leader 创建子 Agent | ✅ | `create_agent()` |
| 独立 Git Worktree | ✅ | `WorkspaceManager` |
| 独立 tmux 会话 | ✅ | `TmuxBackend` |
| 任务分配 + 依赖链 | ✅ | `TaskStore` + blocked_by |
| 完成后自动解除阻塞 | ✅ | `_resolve_dependents_unlocked()` |
| 向任意 Agent 发送消息 | ✅ | `MailboxManager` |
| 监控进度看板 | ✅ | `monitor_progress()` |
| 终止 + 重新分配 | ✅ | `terminate_and_respawn()` |
| 结果汇聚 | ✅ | `get_result()` |
| 合并 Worktree | ✅ | `merge_all_workspaces()` |

**协作模式**:
```
用户输入 → CEO 路由 → 高复杂度? → 是 → 自动组建 Swarm
                                              ↓
                                           分配任务
                                              ↓
                        ┌────────────────────┼────────────────────┐
                        ↓                    ↓                    ↓
                   researcher-1          researcher-2          executor-1
                        ↓                    ↓                    ↓
                        └────────────────────┼────────────────────┘
                                              ↓
                                        任务汇聚 + 收敛
                                              ↓
                                        最终方案输出
```

### 2.8 工作区管理 (`workspace/`)

**功能**:
- Git Worktree 创建与删除
- 分支管理
- 自动提交
- Workspace 合并

**目录结构**:
```
~/.cyberteam/workspaces/{team_name}/
├── {agent-1}/      # 独立 Worktree
├── {agent-2}/
└── ...
```

### 2.9 Spawn 系统 (`spawn/`)

**功能**:
- tmux 会话管理
- Agent 注册与存活检查
- 命令执行

### 2.10 团队协作 (`team/`)

**功能**:
- TaskStore: 任务依赖链管理
- MailboxManager: Agent 间消息传递
- 消息类型: MESSAGE / BROADCAST / TASK_UPDATE / RESULT

---

## 3. API 接口

### 3.1 任务管理

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/tasks` | GET | 任务列表 |
| `/api/tasks` | POST | 创建任务 |
| `/api/tasks/{task_id}` | GET | 任务详情 |
| `/api/tasks/{task_id}` | DELETE | 删除任务 |
| `/api/tasks/{task_id}/transition` | POST | 状态流转 |
| `/api/tasks/stats` | GET | 任务统计 |

### 3.2 Agent 管理

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/agents` | GET | Agent 列表 |
| `/api/agents/{agent_id}` | GET | Agent 详情 |

### 3.3 专家系统

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/experts/classify` | POST | 意图分类 |
| `/api/experts/route` | POST | 专家路由 |

### 3.4 辩论系统

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/debate/start` | POST | 启动辩论 |
| `/api/debate/progress` | POST | 更新进度 |
| `/api/debate/converge-check` | POST | 检查收敛 |
| `/api/debate/end` | POST | 结束辩论 |
| `/api/debate/status/{task_id}` | GET | 辩论状态 |

### 3.5 评分系统

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/scoring/rate` | POST | 专家评分 |
| `/api/scoring/gate` | POST | 质量门禁 |
| `/api/scoring/aggregate` | POST | 聚合评分 |
| `/api/scoring/weights` | GET | 评分权重 |

---

## 4. 数据模型

### 4.1 任务 (Task)

```python
{
    "task_id": str,
    "trace_id": str,
    "title": str,
    "description": str,
    "user_input": str,
    "state": "pending" | "running" | "completed" | "failed",
    "priority": "高" | "中" | "低",
    "creator": str,
    "tags": List[str],
    "score": float,
    "created_at": datetime,
    "updated_at": datetime,
    "completed_at": datetime
}
```

### 4.2 专家 (Expert)

```python
{
    "agent_id": str,
    "name": str,
    "type": "expert" | "department",
    "framework": str,
    "description": str,
    "keywords": List[str]
}
```

### 4.3 评分 (Score)

| 维度 | 权重 |
|------|------|
| 完整性 | 25% |
| 专业性 | 25% |
| 实用性 | 20% |
| 逻辑性 | 15% |
| 创新性 | 10% |
| 安全性 | 5% |

---

## 5. 质量门禁

| 级别 | 名称 | 通过条件 |
|------|------|----------|
| L0 | 输入校验 | 无错误 |
| L1 | 计划审批 | ≥70分 |
| L2 | 过程检查 | 正常/警告 |
| L3 | 结果评审 | ≥70分 |
| L4 | 交付终审 | ≥75分+中低风险 |

---

## 6. 部署

### 6.1 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

### 6.2 前端

```bash
cd frontend
python3 -m http.server 8081
# 访问 http://localhost:8081
```

### 6.3 Docker

```bash
docker build -t cyberteam-v4 .
docker run -p 8080:8080 cyberteam-v4
```

---

## 7. 测试

```bash
python tests/run_tests.py
```

---

## 8. 扩展点

- [x] Swarm Intelligence (已完成)
- [ ] gstack 集成
- [ ] 更丰富的专家框架
- [ ] WebSocket 实时通信
- [ ] 数据库迁移 (SQLite → PostgreSQL)
- [ ] 认证与授权
