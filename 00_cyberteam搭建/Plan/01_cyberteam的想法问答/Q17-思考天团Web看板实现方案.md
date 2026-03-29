# Q17: 思考天团Web看板实现方案

**问题**: ClawTeam怎么安装配置？能否变成Web Dashboard实时交互？具体步骤和技术栈是什么？

---

## 一、ClawTeam安装方式

### 1.1 安装要求

```bash
# 环境要求
- Python 3.10+
- tmux
- Claude Code / Codex / OpenClaw 等CLI Agent
```

### 1.2 安装命令

```bash
# 方式1: 直接安装（推荐）
pip install cyberteam

# 方式2: 从源码安装
git clone https://github.com/HKUDS/ClawTeam.git
cd ClawTeam
pip install -e .

# 可选：P2P传输
pip install -e ".[p2p]"
```

### 1.3 依赖检查

```bash
# 运行前检查
tmux -V              # tmux版本
cyberteam --help      # CLI可用
claude --version     # Agent可用
```

---

## 二、完整实现方案

### 2.1 可以变成Web Dashboard吗？

**答案：完全可以！**

```
当前：思考天团MVP
└─ 用户输入问题 → 等待 → 最终报告

实现后：思考天团v2.0 + Web看板
└─ 用户输入问题 → 实时看板 → 每个专家进度 → 最终报告
        ↑
    浏览器访问 http://localhost:8080
```

---

### 2.2 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                   思考天团 Web看板架构                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐     ┌──────────────┐                  │
│  │  用户浏览器  │────▶│  Web服务器   │                  │
│  │  (Dashboard) │◀────│  (Flask/FastAPI)              │
│  └──────────────┘     └──────┬───────┘                  │
│                               │                              │
│  ┌──────────────┐            │                              │
│  │ 任务状态文件 │◀───────────┤                              │
│  │ tasks.json   │            │                              │
│  └──────────────┘            │                              │
│                               │                              │
│  ┌──────────────┐            │                              │
│  │  思考天团    │◀───────────┘                              │
│  │ 主系统       │                                         │
│  └──────────────┘                                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### 2.3 技术栈

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| **Web框架** | FastAPI / Flask | 轻量级Web服务 |
| **前端** | HTML+Vue3 / React | 看板界面 |
| **实时通信** | WebSocket / SSE | 实时推送进度 |
| **状态存储** | JSON文件 / SQLite | 任务状态持久化 |
| **Agent集成** | subprocess / tmux | 调用Claude Code |

---

## 三、需要从ClawTeam移植什么

### 3.1 可以直接用的

| 模块 | 来源 | 可直接用 |
|------|------|----------|
| **任务状态管理** | ClawTeam | ✅ 核心逻辑可用 |
| **Board CLI** | ClawTeam | ✅ 参考实现 |
| **Inbox消息** | ClawTeam | ✅ 通信机制 |
| **TOML配置解析** | ClawTeam | ✅ 模板定义 |
| **依赖管理** | ClawTeam | ✅ 任务链 |

### 3.2 需要自己写的

| 模块 | 说明 |
|------|------|
| **Web服务器** | 提供HTTP服务 |
| **Dashboard前端** | 看板界面 |
| **实时推送** | WebSocket/SSE |
| **思考天团集成** | 对接14个专家Agent |

---

## 四、具体实现步骤

### 步骤1：搭建基础结构（1天）

```python
# 项目结构
thinking-team-board/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI入口
│   ├── models.py            # 数据模型
│   ├── routes.py            # API路由
│   └── websocket.py         # WebSocket
├── frontend/
│   ├── index.html          # 看板页面
│   ├── app.js               # Vue/React前端
│   └── styles.css           # 样式
├── config/
│   ├── thinking-team.toml   # 专家配置
│   └── settings.py          # 设置
└── requirements.txt
```

### 步骤2：实现任务状态管理（1天）

```python
# models.py
from pydantic import BaseModel
from enum import Enum
from datetime import datetime

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ExpertTask(BaseModel):
    id: str
    expert_name: str          # Kahneman, FirstPrinciple等
    status: TaskStatus
    progress: int = 0          # 0-100
    output: str = ""           # 实时输出
    started_at: datetime = None
    completed_at: datetime = None
    error: str = None

class BoardState(BaseModel):
    tasks: List[ExpertTask]
    total_progress: int
    current_phase: str         # 分析中/辩论中/整合中
```

### 步骤3：实现Web API（1天）

```python
# routes.py
from fastapi import APIRouter, WebSocket
from typing import List

router = APIRouter()

@router.get("/api/board")
async def get_board_state():
    """获取看板状态"""
    return board_state

@router.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    """获取单个任务"""
    return get_task_by_id(task_id)

@router.websocket("/ws/board")
async def websocket_board(websocket: WebSocket):
    """WebSocket实时推送"""
    await websocket.accept()
    while True:
        state = get_board_state()
        await websocket.send_json(state)
        await asyncio.sleep(2)  # 每2秒推送
```

### 步骤4：实现前端看板（1天）

```html
<!-- frontend/index.html -->
<div id="app">
  <!-- 头部 -->
  <header>
    <h1>🧠 思考天团</h1>
    <div class="progress">{{ totalProgress }}%</div>
  </header>

  <!-- 任务看板 -->
  <div class="board">
    <div v-for="task in tasks" :class="task.status">
      <div class="expert">{{ task.expert_name }}</div>
      <div class="status">{{ task.status }}</div>
      <div class="progress-bar">
        <div :style="{width: task.progress + '%'}"></div>
      </div>
      <div class="output">{{ task.output }}</div>
    </div>
  </div>
</div>
```

### 步骤5：集成思考天团（1天）

```python
# integration.py
class ThinkingTeamIntegration:
    """思考天团集成"""

    def __init__(self):
        self.board = BoardState()
        self.experts = load_experts("thinking-team.toml")

    async def start_analysis(self, question: str):
        # 1. 意图识别
        routing = await self.route(question)

        # 2. 创建任务
        for expert in routing.experts:
            task = self.board.create_task(expert)

        # 3. 启动执行
        asyncio.create_task(self.run_expert(task, expert, question))

    async def run_expert(self, task, expert, question):
        task.status = "running"
        # 调用Claude Code执行专家分析
        result = await call_claude_code(expert.prompt, question)

        # 实时更新输出
        for chunk in result.stream():
            task.output += chunk
            task.progress = estimate_progress(chunk)

        task.status = "completed"
```

---

## 五、完整文件清单

### 5.1 需要创建的文件

```
thinking-team-board/
├── requirements.txt              # 依赖
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI主入口 (50行)
│   ├── models.py                # 数据模型 (30行)
│   ├── routes.py                # API路由 (80行)
│   ├── websocket.py             # WebSocket (40行)
│   ├── board.py                 # 看板逻辑 (100行)
│   ├── tasks.py                 # 任务管理 (80行)
│   └── integration.py            # 思考天团集成 (100行)
├── templates/
│   └── board.html               # 看板页面 (150行)
├── config/
│   └── thinking-team.toml        # 专家配置
└── README.md
```

### 5.2 核心代码量

| 文件 | 代码量 | 说明 |
|------|--------|------|
| main.py | ~50行 | Web服务入口 |
| models.py | ~30行 | 数据模型 |
| routes.py | ~80行 | API接口 |
| websocket.py | ~40行 | 实时推送 |
| board.py | ~100行 | 看板状态管理 |
| tasks.py | ~80行 | 任务管理 |
| integration.py | ~100行 | 思考天团集成 |
| board.html | ~150行 | 前端界面 |
| **总计** | **~630行** | 完整可运行 |

---

## 六、Web看板功能预览

### 6.1 主界面

```
╔══════════════════════════════════════════════════════════════════╗
║                    🧠 思考天团 - 实时看板                    ║
╠══════════════════════════════════════════════════════════════════╣
║ 问题: 如何提升DAU 10%？                                    ║
║ 状态: 🔄 分析中                        进度: 40%           ║
╠══════════════════════════════════════════════════════════════════╣
║                                                          ║
║  ┌─────────────────────────────────────────────────────┐  ║
║  │ 🧠 Kahneman (卡尼曼)                               │  ║
║  │ 状态: ✅ 完成    进度: 100%   耗时: 2m30s        │  ║
║  │ 输出: 识别到3个认知偏差：锚定效应、确认偏差...     │  ║
║  └─────────────────────────────────────────────────────┘  ║
║                                                          ║
║  ┌─────────────────────────────────────────────────────┐  ║
║  │ 💡 FirstPrinciple (第一性原理)                     │  ║
║  │ 状态: 🔄 进行中  进度: 75%   耗时: 1m45s        │  ║
║  │ 输出: 正在重构成本结构...                          │  ║
║  └─────────────────────────────────────────────────────┘  ║
║                                                          ║
║  ┌─────────────────────────────────────────────────────┐  ║
║  │ 🎩 SixHats (六顶思考帽)                            │  ║
║  │ 状态: ⏳ 等待中   进度: 0%    耗时: -            │  ║
║  │ 输出: -                                            │  ║
║  └─────────────────────────────────────────────────────┘  ║
║                                                          ║
╚══════════════════════════════════════════════════════════════════╝
```

### 6.2 实时消息流

```
【消息】Kahneman → FirstPrinciple
> 我发现这个决策存在锚定效应，建议重新评估成本假设...

【消息】FirstPrinciple → SixHats
> 同意，我正在从本质重构方案，需要你补充蓝色思考帽视角...
```

---

## 七、总结

### 技术栈

| 层级 | 技术 |
|------|------|
| Web框架 | FastAPI |
| 前端 | Vue3 + Vite |
| 实时 | WebSocket |
| 状态 | JSON/SQLite |
| Agent调用 | subprocess |

### 实现难度

| 模块 | 难度 | 预估时间 |
|------|------|----------|
| 任务状态管理 | ⭐ | 1天 |
| Web API | ⭐ | 1天 |
| 前端看板 | ⭐⭐ | 1天 |
| 实时推送 | ⭐⭐ | 1天 |
| 思考天团集成 | ⭐⭐ | 1天 |

### 能否变成Web Dashboard

**完全可以！** 核心功能：
- ✅ 实时任务看板
- ✅ 每个专家进度显示
- ✅ 实时输出流
- ✅ 消息记录
- ✅ Web浏览器访问

---

**实现总时间：约5天**

---

**研究日期**: 2026-03-20
**来源**: ClawTeam仓库分析
