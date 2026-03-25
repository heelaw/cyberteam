# CyberTeam V4 Backend

CyberTeam V4 版本的后端 API 服务。

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 运行服务

```bash
# 开发模式
uvicorn app.main:app --reload --port 8080

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### 3. 验证服务

```bash
# 健康检查
curl http://localhost:8080/health

# API 根路径
curl http://localhost:8080/
```

## API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/tasks` | GET | 获取任务列表 |
| `/api/tasks` | POST | 创建新任务 |
| `/api/tasks/{task_id}` | GET | 获取任务详情 |
| `/api/tasks/{task_id}` | DELETE | 删除任务 |
| `/api/tasks/{task_id}/transition` | POST | 任务状态流转 |
| `/api/tasks/stats` | GET | 任务统计 |
| `/api/agents` | GET | 获取 Agent 列表 |
| `/api/agents/{agent_id}` | GET | 获取指定 Agent 信息 |
| `/api/experts/classify` | POST | 意图分类 |
| `/api/experts/route` | POST | 专家路由 |
| `/api/debate/start` | POST | 启动辩论 |
| `/api/debate/progress` | POST | 更新辩论进度 |
| `/api/debate/converge-check` | POST | 检查收敛 |
| `/api/debate/end` | POST | 结束辩论 |
| `/api/debate/status/{task_id}` | GET | 获取辩论状态 |
| `/api/scoring/rate` | POST | 专家评分 |
| `/api/scoring/gate` | POST | 质量门禁检查 |
| `/api/scoring/aggregate` | POST | 聚合评分 |
| `/api/scoring/weights` | GET | 获取评分权重 |

## 配置

通过环境变量配置：

| 变量 | 默认值 | 描述 |
|------|--------|------|
| `PORT` | 8080 | 服务端口 |
| `HOST` | 0.0.0.0 | 服务地址 |
| `DEBUG` | false | 调试模式 |
| `DATABASE_URL` | sqlite+aiosqlite:///./cyberteam.db | 数据库连接 |
| `EXPERT_TIMEOUT` | 120 | 专家超时时间(秒) |
| `DEBATE_ROUNDS` | 5 | 辩论轮次 |
| `CONVERGENCE_THRESHOLD` | 0.3 | 收敛阈值 |
| `SCORE_THRESHOLD` | 50 | 通过分数阈值 |
| `QUALITY_GATE_L1` | 70 | L1 门禁分数 |
| `QUALITY_GATE_L3` | 70 | L3 门禁分数 |
| `QUALITY_GATE_L4` | 75 | L4 门禁分数 |

## 数据库

使用 SQLite 存储数据：
- `tasks` - 任务表
- `expert_outputs` - 专家输出表
- `debate_rounds` - 辩论轮次表
- `department_outputs` - 部门输出表
- `final_reports` - 最终报告表

## 六维评分体系

| 维度 | 权重 | 描述 |
|------|------|------|
| 完整性 | 25% | 核心观点+分析+建议+风险 |
| 专业性 | 25% | 框架关键词+准确应用 |
| 实用性 | 20% | 可执行+具体+可落地 |
| 逻辑性 | 15% | 结构+因果+结论 |
| 创新性 | 10% | 独特视角+新见解 |
| 安全性 | 5% | 风险提示+注意事项 |

## 质量门禁

| 级别 | 名称 | 通过条件 |
|------|------|----------|
| L0 | 输入校验 | 无错误 |
| L1 | 计划审批 | ≥70分 |
| L2 | 过程检查 | 正常/警告 |
| L3 | 结果评审 | ≥70分 |
| L4 | 交付终审 | ≥75分+中低风险 |