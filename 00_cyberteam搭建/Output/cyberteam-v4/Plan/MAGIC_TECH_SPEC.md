# Magic → CyberTeam v4 技术抄作业清单

> 创建日期：2026-03-28
> 竞品：Magic (超级麦吉) 开源项目
> 目标：全方位抄作业，同时保留 CyberTeam 的三省六部 + Swarm 特色

---

## 一、前端重构（最大差距）

### 1.1 技术栈（完全抄 Magic）

| 技术 | 版本 | 用途 |
|------|------|------|
| React | 18.x | 核心 UI 框架 |
| TypeScript | 5.x | 类型系统 |
| Vite | 6.x | 构建工具 |
| Ant Design | 5.x | PC 端组件库 |
| shadcn/ui (Radix UI) | latest | 新组件开发基础 |
| Tailwind CSS | 3.x | 原子化 CSS |
| Zustand | 4.x | 组件级状态管理 |
| SWR | 2.x | 服务端数据缓存 |
| TipTap | 3.x | 富文本编辑器 |
| i18next | latest | 国际化 |
| Framer Motion | latest | 动画 |

### 1.2 目录结构

```
frontend/
├── src/
│   ├── apis/                    # API 层
│   │   ├── clients/
│   │   │   ├── cyberteam.ts     # HTTP 客户端 (axios)
│   │   │   └── websocket.ts     # WebSocket 客户端
│   │   └── modules/
│   │       ├── chat.ts
│   │       ├── agents.ts
│   │       ├── tasks.ts
│   │       ├── projects.ts
│   │       └── skills.ts
│   ├── components/
│   │   ├── base/                # 基础组件 (MagicButton, MagicInput...)
│   │   ├── business/            # 业务组件 (AgentCard, TaskBoard...)
│   │   └── shadcn-ui/           # shadcn/ui 组件
│   ├── pages/
│   │   ├── chat/                # 三栏对话主界面
│   │   ├── agents/              # Agent 管理 (三省六部组织图)
│   │   ├── projects/            # 项目执行 (八节点流程)
│   │   ├── skills/              # 技能市场
│   │   ├── dashboard/           # 仪表盘
│   │   └── settings/            # 系统设置
│   ├── stores/                  # Zustand 状态
│   ├── providers/               # Context Providers
│   ├── routes/                  # 路由配置 (React Router 6)
│   ├── hooks/                   # 自定义 Hooks
│   ├── utils/                   # 工具函数
│   ├── types/                   # TypeScript 类型定义
│   └── styles/                  # 全局样式
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
└── package.json
```

### 1.3 核心页面设计

#### 页面1：三栏对话主界面（抄 Magic ChatLayout）

```
┌──────────────┬─────────────────────────┬──────────────┐
│  会话列表     │     对话消息流           │  Agent 面板  │
│  ─────────   │  ─────────────────────  │  ─────────   │
│  [搜索]      │  CEO: 让我来分析任务...  │  执行状态    │
│  ─────────   │  COO: 建议调用增长部...  │  ● CEO 路由中│
│  项目A       │  ─────────────────────  │  ○ COO 规划  │
│  项目B       │  [Agent讨论气泡]        │  ○ PM 派发   │
│  项目C       │  增长总监: 我认为...     │  ─────────   │
│  ...         │  质疑者: 数据从哪来的？  │  Agent列表   │
│              │  ─────────────────────  │  CEO ★★★★★ │
│              │  [TipTap 富文本输入框]   │  COO ★★★★☆ │
│              │  @CEO 分析下这个需求     │  增长 ★★★☆☆ │
└──────────────┴─────────────────────────┴──────────────┘
```

- 左栏：会话列表 + 搜索 + 新建会话
- 中栏：消息流（Markdown渲染 + Agent气泡 + 工具调用卡片）+ TipTap输入框（支持@提及Agent）
- 右栏：Agent执行状态（实时WebSocket推送）+ Agent列表

#### 页面2：Agent 管理看板（CyberTeam 特色：三省六部组织图）

```
┌───────────────────────────────────────────────────┐
│  [决策层] [协调层] [执行层] [技能市场]             │
├───────────────────────────────────────────────────┤
│                                                   │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐          │
│  │ CEO     │  │ COO     │  │ PM      │          │
│  │ 路由引擎│  │ 规划引擎│  │ 协调器  │          │
│  │ ★★★★★ │  │ ★★★★☆ │  │ ★★★☆☆ │          │
│  └────┬────┘  └────┬────┘  └────┬────┘          │
│       │            │            │                 │
│  ┌────┴────┐  ┌────┴────┐  ┌────┴────┐          │
│  │增长总监 │  │产品总监 │  │技术总监 │          │
│  │9 Agents│  │3 Agents│  │5 Agents│          │
│  └─────────┘  └─────────┘  └─────────┘          │
│                                                   │
└───────────────────────────────────────────────────┘
```

#### 页面3：项目执行看板（八节点流程）

```
┌───────────────────────────────────────────────────┐
│  项目：西北发面包子品牌策划                         │
│  ────────────────────────────────────────         │
│  ① CEO-COO对齐 ──→ ② 策略讨论 ──→ ③ 风险预案    │
│  ──→ ④ CEO汇报 ──→ ⑤ 设计联动 ──→ ⑥ 文案产出   │
│  ──→ ⑦ CEO汇总 ──→ ⑧ 复盘进化                    │
│  ────────────────────────────────────────         │
│  当前节点：③ 风险预案                              │
│  执行 Agent：质疑者 + 增长总监 + 产品总监         │
│  ────────────────────────────────────────         │
│  [Agent 对话记录] [文档产出] [Playground 看板]     │
└───────────────────────────────────────────────────┘
```

### 1.4 WebSocket 客户端（抄 Magic）

核心特性：
- 自动重连（指数退避 3s → 30s）
- 心跳检测（10s 间隔, 2s 超时）
- 网络状态监听（online/offline）
- 页面可见性监听（pause/resume）
- 消息幂等（防止重复）

### 1.5 状态管理（三层架构，抄 Magic）

| 层级 | 技术 | 用途 |
|------|------|------|
| 全局状态 | Zustand | 用户信息、配置、会话列表 |
| 组件状态 | React useState/useReducer | 局部 UI 状态 |
| 服务端状态 | SWR | API 数据缓存与自动同步 |

### 1.6 样式方案

- Tailwind CSS 做布局和工具类
- Ant Design 做复杂组件（Table, Form, Modal, Tabs）
- antd-style 做 CSS-in-JS 动态样式
- OKLCH 颜色空间（抄 Magic）
- 暗黑模式支持（CSS 变量 + class 切换）

---

## 二、后端升级

### 2.1 DDD 分层重构（抄 Magic）

```
当前: api/ → 直接调用 engine/
目标: api/ → service/ → domain/ → infra/

api/          → 接口层 (DTO 转换, 参数校验)
service/      → 应用层 (业务编排, 事务管理)
domain/       → 领域层 (业务规则, 实体模型)
infra/        → 基础设施层 (数据库, Redis, 外部API)
```

### 2.2 WebSocket 支持

```python
# 后端 WebSocket 端点
@app.websocket("/ws/chat/{conversation_id}")
async def ws_chat(websocket: WebSocket, conversation_id: str):
    await websocket.accept()
    # 1. 接收用户消息
    # 2. 分发给 CEO 路由引擎
    # 3. 流式推送 Agent 执行事件
    async for event in agent_runner.run_stream(data):
        await websocket.send_json({
            "type": event.type,  # agent_start / agent_output / agent_complete / debate
            "data": event.data,
            "timestamp": datetime.now().isoformat()
        })
```

### 2.3 SSE 流式输出（抄 Magic）

```python
# 用于不支持 WebSocket 的场景
@app.get("/api/chat/{conversation_id}/stream")
async def stream_chat(conversation_id: str, message: str):
    async def event_generator():
        async for event in agent_runner.run_stream(message):
            yield f"data: {json.dumps(event.dict())}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

### 2.4 事件驱动架构（抄 Magic）

```python
# engine/events.py
class EventBus:
    """全局事件总线"""

    async def emit(self, event_type: str, data: dict):
        # 1. 触发所有订阅者
        # 2. 写入 Redis Stream (持久化)
        # 3. 推送 WebSocket (实时通知)

    def on(self, event_type: str, handler: Callable):
        # 注册事件处理器

# 关键事件类型
EVENT_TYPES = [
    "task.created",        # 任务创建
    "ceo.routed",          # CEO 路由完成
    "coo.planned",         # COO 规划完成
    "agent.started",       # Agent 开始执行
    "agent.completed",     # Agent 执行完成
    "agent.failed",        # Agent 执行失败
    "debate.started",      # 辩论开始
    "debate.converged",    # 辩论收敛
    "approval.requested",  # 审批请求
    "approval.approved",   # 审批通过
    "budget.warning",      # 预算预警
    "task.completed",      # 任务完成
]
```

### 2.5 Agent 编译器（抄 Magic）

```python
# engine/agent_compiler.py
class AgentCompiler:
    """把 SOUL.md + agent.yaml 编译成运行时 Agent"""

    async def compile(self, agent_dir: Path) -> AgentProfile:
        # 1. 读取 agent.yaml
        config = yaml.safe_load((agent_dir / "agent.yaml").read_text())

        # 2. 读取 SOUL.md
        soul = (agent_dir / "SOUL.md").read_text()

        # 3. 读取 prompts/*.prompt（模块化 Prompt）
        prompts = {}
        for p in (agent_dir / "prompts").glob("*.prompt"):
            prompts[p.stem] = p.read_text()

        # 4. 组合编译
        return AgentProfile(
            name=config["name"],
            department=config["department"],
            tools=config.get("tools", []),
            skills=config.get("skills", []),
            model=config.get("model", "main_llm"),
            daily_budget=config.get("daily_budget", 10.0),
            system_prompt=self._compose(soul, prompts),
        )
```

### 2.6 多模型网关（抄 Magic）

```python
# engine/model_gateway.py
class ModelGateway:
    """按任务类型自动选模型"""

    MODEL_MAP = {
        # 决策层用最强模型
        "ceo_route": "claude-opus-4-6",
        "coo_planning": "claude-sonnet-4-6",
        "ceo_review": "claude-opus-4-6",

        # 执行层用快速模型
        "dept_execution": "claude-haiku-4-5",
        "marketing": "claude-sonnet-4-6",
        "engineering": "claude-sonnet-4-6",

        # 辩论用平衡模型
        "debate": "claude-sonnet-4-6",

        # 质量检查用快速模型
        "quality_gate": "claude-haiku-4-5",
    }

    def resolve(self, task_type: str, budget_tier: str = "normal") -> str:
        if budget_tier == "economy":
            return self.ECONOMY_MAP.get(task_type, "claude-haiku-4-5")
        return self.MODEL_MAP.get(task_type, "claude-sonnet-4-6")
```

### 2.7 审批流程（抄 Magic）

```python
# engine/approval.py
class ApprovalService:
    """高危操作审批"""

    HIGH_RISK_ACTIONS = [
        "delete_data",
        "send_email",
        "publish_content",
        "budget_exceed",
    ]

    async def request_approval(self, action: str, agent: str, context: dict):
        # 1. 暂停 Agent 执行
        # 2. 推送审批请求到前端
        # 3. 等待用户决策
        # 4. 返回审批结果
```

### 2.8 预算追踪（抄 Magic）

```python
# engine/budget.py
class BudgetTracker:
    """多级预算控制"""

    async def check_budget(self, level: str, entity_id: str, estimated_cost: float) -> bool:
        """检查预算是否允许"""
        # level: "organization" / "project" / "agent"
        used = await self.get_usage(level, entity_id)
        limit = await self.get_limit(level, entity_id)
        return used + estimated_cost <= limit

    async def record_usage(self, level: str, entity_id: str, tokens: int, cost: float):
        """记录使用量"""
        # 写入 Redis 实时计数
        # 写入数据库持久化
```

---

## 三、数据库升级

### 3.1 新增表

```sql
-- 会话表
CREATE TABLE conversations (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    title VARCHAR(255),
    status VARCHAR(32) DEFAULT 'active',
    project_id VARCHAR(64),
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 消息表
CREATE TABLE messages (
    id VARCHAR(64) PRIMARY KEY,
    conversation_id VARCHAR(64) NOT NULL,
    sender_type VARCHAR(32) NOT NULL,  -- user/agent/system
    sender_id VARCHAR(64),
    sender_name VARCHAR(64),
    department VARCHAR(64),
    content TEXT,
    content_type VARCHAR(32) DEFAULT 'markdown',
    metadata JSON,
    parent_id VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_conv_created (conversation_id, created_at)
);

-- Agent 执行日志
CREATE TABLE agent_executions (
    id VARCHAR(64) PRIMARY KEY,
    task_id VARCHAR(64),
    agent_name VARCHAR(64) NOT NULL,
    department VARCHAR(64),
    status VARCHAR(32) NOT NULL,
    model_id VARCHAR(64),
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    cost_usd DECIMAL(10, 6) DEFAULT 0,
    duration_ms INTEGER,
    input_summary TEXT,
    output_summary TEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    INDEX idx_agent_status (agent_name, status),
    INDEX idx_task (task_id)
);

-- 预算追踪
CREATE TABLE budget_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type VARCHAR(32) NOT NULL,  -- organization/project/agent
    entity_id VARCHAR(64) NOT NULL,
    period DATE NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    cost_usd DECIMAL(10, 6) DEFAULT 0,
    budget_limit DECIMAL(10, 6),
    UNIQUE(entity_type, entity_id, period)
);

-- 审批记录
CREATE TABLE approvals (
    id VARCHAR(64) PRIMARY KEY,
    task_id VARCHAR(64),
    agent_name VARCHAR(64),
    action_type VARCHAR(64) NOT NULL,
    action_detail JSON,
    status VARCHAR(32) DEFAULT 'pending',  -- pending/approved/rejected
    reviewer_id VARCHAR(64),
    review_comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP
);
```

---

## 四、认证与安全

### 4.1 JWT 认证

```python
# backend/app/auth/jwt.py
from jose import jwt

class JWTAuth:
    SECRET_KEY = "cyberteam-secret-key-change-in-production"
    ALGORITHM = "HS256"

    def create_token(self, user_id: str, org_id: str, role: str) -> str:
        return jwt.encode({
            "sub": user_id,
            "org": org_id,
            "role": role,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }, self.SECRET_KEY, algorithm=self.ALGORITHM)
```

### 4.2 多租户

```python
# 所有查询自动加 tenant 过滤
class TenantFilter:
    def filter_query(self, query, tenant_id: str):
        return query.filter(Model.tenant_id == tenant_id)
```

---

## 五、Prompt 工程升级

### 5.1 模块化 Prompt 拆分

每个 Agent 目录结构改为：

```
AGENTS/growth/growth_director/
├── agent.yaml          # 声明式配置
├── SOUL.md             # 角色定义
├── prompts/
│   ├── system.prompt   # 系统提示
│   ├── base.prompt     # 基础指令
│   ├── debate.prompt   # 辩论模式指令
│   └── quality.prompt  # 质量检查指令
└── skills/             # 该 Agent 专属技能
```

### 5.2 双语提示词规范

```markdown
<!--zh
你是增长部总监，负责用户增长策略制定和执行。
-->
You are the Growth Director, responsible for user growth strategy formulation and execution.
```

### 5.3 agent.yaml 声明式配置

```yaml
name: growth_director
department: growth
layer: coordination  # decision/coordination/execution

model: main_llm
daily_budget: 10.0

tools:
  - web_search
  - write_file
  - call_subagent
  - read_file

skills:
  - 增长逻辑梳理法
  - 漏斗分析法
  - A/B测试设计

subordinates:
  - user_growth_expert
  - content_ops_expert
  - channel_promotion_expert

triggers:
  - keyword: ["增长", "拉新", "留存", "转化"]
  - task_type: ["growth_strategy", "user_acquisition"]

approval_required:
  - publish_content
  - budget_exceed_5usd
```

---

## 六、CyberTeam 特色保留与增强

### 6.1 三省六部状态机（保留）

Magic 没有这个，这是 CyberTeam 的核心特色。在抄 Magic 的同时要保留并增强。

### 6.2 Swarm Orchestrator（保留）

Magic 用的是单 Agent 编排，CyberTeam 有 Swarm 群体智能，保留。

### 6.3 辩论引擎（保留+增强）

增加收敛度可视化，在前端展示辩论过程。

### 6.4 质疑者 Agent（保留）

Magic 没有质疑者机制，这是 CyberTeam 的独特设计。

### 6.5 Playground 自动生成（保留）

Magic 没有自动生成看板的功能，保留并增强。

---

## 七、执行顺序

| Phase | 内容 | 并行 Agent |
|-------|------|-----------|
| **P0** | 前端脚手架 + 后端WebSocket + DDD分层 | 3个并行 |
| **P1** | Agent编译器 + 多模型网关 + 事件总线 | 3个并行 |
| **P2** | 数据库升级 + JWT认证 + 预算追踪 | 3个并行 |
| **P3** | 核心页面(对话/看板/项目) + Prompt拆分 | 3个并行 |
