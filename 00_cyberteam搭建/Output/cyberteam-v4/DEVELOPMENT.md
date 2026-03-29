# CyberTeam V4 开发者指南

## 目录

1. [快速开始](#快速开始)
2. [项目结构](#项目结构)
3. [核心概念](#核心概念)
4. [开发工作流](#开发工作流)
5. [测试指南](#测试指南)
6. [扩展开发](#扩展开发)

---

## 快速开始

### 安装

```bash
# 克隆项目
cd /path/to/cyberteam-v4

# 安装依赖
pip3 install -e .

# 验证安装
./demo.sh
```

### 运行测试

```bash
# 运行全部测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_core.py::TestCEORouter -v
```

---

## 项目结构

```
cyberteam-v4/
├── cyberteam/              # 核心 Swarm 框架
│   ├── team/              # 团队管理 (12 文件)
│   ├── spawn/             # Agent 生成 (13 文件)
│   ├── workspace/         # Git Worktree (7 文件)
│   ├── transport/         # 消息传递 (6 文件)
│   ├── board/             # 仪表盘 (6 文件)
│   └── cli/               # 命令行工具
│
├── engine/                # 垂直行业引擎
│   ├── ceo.py            # CEO 路由引擎
│   ├── strategy.py       # 策略三角
│   ├── department.py     # 部门管理
│   └── debate_engine.py  # 辩论引擎
│
├── integration/           # 外部集成
│   └── cyberteam_adapter.py
│
├── swarm_orchestrator.py  # 群体智能编排器
├── backend/              # FastAPI 后端
├── tests/                # 测试套件
└── docs/                 # 文档
```

---

## 核心概念

### 1. Swarm Intelligence (群体智能)

CyberTeam 的核心是让 AI Agent 自主组建团队、协同工作：

```python
from swarm_orchestrator import SwarmOrchestrator

# 创建 Swarm
swarm = SwarmOrchestrator("my-team", "完成项目")

# 创建子 Agent (独立 Worktree + tmux)
swarm.create_agent("researcher", "研究员", command="claude --goal '...'")

# 分配任务 (支持依赖链)
task1 = swarm.assign_task("researcher", "收集数据")
task2 = swarm.assign_task("writer", "撰写报告", blocked_by=[task1.task_id])

# 完成任务 (自动解除下游阻塞)
swarm.complete_task(task1.task_id, "数据已收集")
```

### 2. CEO 路由引擎

自动判断任务复杂度并路由：

```python
from engine.ceo import CEORouter

router = CEORouter()
result = router.route("分析市场并制定战略")

# result.target: "DIRECT" | "L3A" | "L3C" | "SWARM"
# result.intent: "数据分析" | "战略规划" | ...
# result.complexity: 0-1
```

### 3. 任务依赖链

支持 DAG 任务图：

```
task1 (收集数据)
  ↓
task2 (分析数据)
  ↓
task3 (撰写报告)

task1 完成后，task2 自动解除阻塞
task2 完成后，task3 自动解除阻塞
```

---

## 开发工作流

### 1. 创建新功能

```bash
# 创建功能分支
git checkout -b feature/my-feature

# 开发
vim cyberteam/...

# 测试
pytest tests/ -v

# 提交
git add .
git commit -m "feat: 添加我的功能"
```

### 2. 代码风格

- 使用 Python 3.9+ 兼容语法
- 类型注解使用 `typing` 模块
- 遵循 PEP 8 规范

### 3. 提交规范

```
feat: 新功能
fix: 修复 bug
docs: 文档更新
test: 测试相关
refactor: 重构
```

---

## 测试指南

### 单元测试

```python
# tests/test_my_feature.py
import pytest

def test_basic_functionality():
    """测试基本功能"""
    from cyberteam.team import TeamManager
    tm = TeamManager()
    assert tm is not None

def test_edge_cases():
    """测试边界情况"""
    with pytest.raises(ValueError):
        # 应该抛出异常的代码
        pass
```

### 集成测试

```python
def test_full_workflow():
    """测试完整工作流"""
    swarm = SwarmOrchestrator("test", "测试")
    swarm.create_agent("agent1", "测试员", command="echo", workspace=False)
    task = swarm.assign_task("agent1", "测试任务")
    assert task.status == "pending"
```

---

## 扩展开发

### 添加新的 Spawn Backend

```python
# cyberteam/spawn/my_backend.py
from cyberteam.spawn.base import SpawnBackend

class MyBackend(SpawnBackend):
    def spawn(self, command: str, **kwargs):
        # 实现 spawn 逻辑
        pass

    def is_alive(self, agent_id: str) -> bool:
        # 实现存活检查
        pass
```

### 扩展 CEO 路由

```python
# engine/ceo.py
class CEORouter:
    def route(self, user_input: str) -> RoutingResult:
        # 添加新的路由逻辑
        if "特殊场景" in user_input:
            return RoutingResult(target="CUSTOM", ...)
```

### 自定义团队模板

```python
# cyberteam/team/presets.py
CUSTOM_PRESET = {
    "name": "custom",
    "agents": [
        {"role": "专家", "count": 3},
        {"role": "审核", "count": 1},
    ],
    "workflow": "custom_workflow"
}
```

---

## 常见问题

### Q: 如何调试 Agent 通信？

```bash
# 查看 tmux session
tmux attach -t cyberteam-my-team:agent-name

# 查看消息日志
cat ~/.cyberteam/teams/my-team/inbox/*/*
```

### Q: 如何清理测试数据？

```bash
# 删除所有 team
rm -rf ~/.cyberteam/teams/*

# 删除所有 workspaces
rm -rf ~/.cyberteam/workspaces/*

# 关闭所有 tmux sessions
tmux ls | grep cyberteam | awk '{print $1}' | xargs -I {} tmux kill-session -t {}
```

### Q: 如何添加新的专家 Agent？

1. 在 `engine/experts/` 创建专家定义
2. 在 `engine/ceo.py` 注册专家
3. 添加测试用例

---

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 编写测试
4. 提交 PR

---

*最后更新: 2026-03-25*
