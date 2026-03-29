# MAGIC 技术抄作业清单 — CyberTeam v4 进化指南

> 来源：magic-master 开源竞品分析
> 创建：2026-03-28
> 状态：进行中

---

## 一、核心差异分析

| 维度 | Magic | CyberTeam v4 | 差距 |
|------|-------|-------------|------|
| 后端架构 | PHP+Python+Go 微服务 | 纯 Python（早期版本） | 大 |
| 前端 | React 18 + Ant Design + shadcn/ui + TipTap | 原生 HTML/JS | **巨大** |
| 实时通信 | WebSocket + SSE + Socket.IO | **无** | **巨大** |
| 数据库 | MySQL + Redis + Qdrant | SQLite | 中 |
| 消息队列 | RabbitMQ | **无** | 大 |
| 认证 | JWT + 多租户 RBAC | 静态 RBAC | 大 |
| AI 引擎 | AgentLang 自研编排 | Swarm Orchestrator | 中 |
| Agent 定义 | YAML 声明式 + 编译器 | Markdown SOUL.md | 中 |
| 文件处理 | TipTap 富文本 + Univer 表格 | **无** | **巨大** |
| 数字员工市场 | 完整 marketplace | **无** | **巨大** |
| 监控 | Jaeger 链路追踪 | 无 | 大 |

---

## 二、Phase 1：前端彻底重构

### 1.1 技术栈（已确定，直接用）

```
React 18 + TypeScript + Vite + Ant Design + Tailwind CSS + shadcn/ui
```

### 1.2 目录结构

```
webui/
├── src/
│   ├── apis/                    # API 层
│   │   ├── client.ts           # HTTP 客户端封装
│   │   ├── websocket.ts         # WebSocket 客户端（自动重连+心跳）
│   │   └── modules/
│   │       ├── chat.ts
│   │       ├── agents.ts
│   │       └── projects.ts
│   ├── components/
│   │   ├── base/               # Button/Input/Card 等基础组件
│   │   ├── business/           # 业务组件（ChatBubble/AgentCard）
│   │   └── shadcn-ui/          # shadcn 组件
│   ├── pages/
│   │   ├── Dashboard.tsx       # 仪表盘
│   │   ├── Chat.tsx            # 三栏对话主界面
│   │   ├── Agents.tsx          # Agent 管理
│   │   ├── Departments.tsx      # 部门视图
│   │   ├── Skills.tsx          # 技能市场
│   │   ├── Teams.tsx           # 团队管理
│   │   └── Settings.tsx         # 设置
│   ├── stores/                  # Zustand 状态
│   ├── routes/                  # 路由
│   ├── hooks/                   # 自定义 Hooks
│   └── utils/
├── vite.config.ts
├── tailwind.config.js
└── package.json
```

### 1.3 三栏对话主界面（核心）

```
┌──────────┬──────────────────────┬──────────────┐
│ 会话列表  │     对话流            │  Agent 状态  │
│ (220px)  │     (flex-1)         │   (300px)    │
│          │                     │              │
│ 历史消息  │  AI 回复流式输出      │ 执行节点状态  │
│ 会话搜索  │  @提及 Agent         │ Token 消耗    │
│ 新建对话  │  工具调用卡片         │ 预算显示     │
└──────────┴──────────────────────┴──────────────┘
```

### 1.4 WebSocket 客户端（抄 Magic）

```typescript
// webui/src/apis/websocket.ts
class CyberTeamWebSocket {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectDelay = 30000
  private heartbeatInterval = 10000
  private hbTimer: number | null = null
  private listeners = new Map<string, Function[]>()

  connect(url: string, token: string) {
    this.ws = new WebSocket(`${url}?token=${token}`)
    this.ws.onopen = () => {
      this.reconnectAttempts = 0
      this.startHeartbeat()
    }
    this.ws.onmessage = (e) => {
      const data = JSON.parse(e.data)
      this.listeners.get(data.type)?.forEach(fn => fn(data))
    }
    this.ws.onclose = () => {
      this.stopHeartbeat()
      this.reconnect(url, token)
    }
  }

  private reconnect(url: string, token: string) {
    const delay = Math.min(3000 * 2 ** this.reconnectAttempts, this.maxReconnectDelay)
    setTimeout(() => {
      this.reconnectAttempts++
      this.connect(url, token)
    }, delay)
  }

  private startHeartbeat() {
    this.hbTimer = window.setInterval(() => {
      this.send({ type: 'ping' })
    }, this.heartbeatInterval)
  }

  send(data: object) {
    this.ws?.send(JSON.stringify(data))
  }

  on(type: string, fn: Function) {
    this.listeners.set(type, [...(this.listeners.get(type) || []), fn])
  }
}
```

---

## 三、Phase 2：后端架构升级

### 2.1 FastAPI 目录结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI 入口
│   ├── config.py               # 配置管理
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── chat.py         # 对话 API
│   │   │   ├── agents.py       # Agent 管理
│   │   │   ├── projects.py     # 项目 API
│   │   │   └── skills.py       # 技能 API
│   │   └── ws.py               # WebSocket 端点
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── jwt.py              # JWT 认证
│   │   └── rbac.py             # 角色权限
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py         # 数据库连接
│   │   └── models.py           # SQLAlchemy 模型
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── agent_compiler.py   # Agent 编译器（核心）
│   │   ├── model_gateway.py     # 多模型网关
│   │   ├── event_bus.py        # 事件总线
│   │   ├── swarm_orchestrator.py # Swarm 编排器
│   │   └── thinking_injector.py  # 思维注入
│   └── queue/
│       ├── __init__.py
│       └── task_queue.py        # Redis Stream 队列
├── requirements.txt
└── Dockerfile
```

### 2.2 Agent 编译器（核心创新）

```python
# backend/app/engine/agent_compiler.py

class AgentCompiler:
    """把 SOUL.md + agent.yaml 编译成运行时 AgentProfile"""

    async def compile(self, agent_dir: Path) -> AgentProfile:
        # 1. 读取 agent.yaml（声明式配置）
        config = yaml.safe_load((agent_dir / "agent.yaml").read_text())

        # 2. 读取 SOUL.md（角色定义）
        soul = (agent_dir / "SOUL.md").read_text()

        # 3. 读取 prompts/（模块化 Prompt）
        prompts = {}
        if (agent_dir / "prompts").exists():
            for p in (agent_dir / "prompts").glob("*.prompt"):
                prompts[p.stem] = p.read_text()

        # 4. 读取 SKILL.md（技能定义）
        skills = []
        if (agent_dir / "skills").exists():
            for s in (agent_dir / "skills").glob("*.md"):
                skills.append(self._parse_skill(s))

        # 5. 编译成 AgentProfile
        system_prompt = self._compose(soul, prompts)

        return AgentProfile(
            name=config["name"],
            llm=config.get("llm", "main_llm"),
            tools=config.get("tools", []),
            skills=skills,
            system_prompt=system_prompt,
            departments=config.get("departments", []),
        )
```

### 2.3 多模型网关

```python
# backend/app/engine/model_gateway.py

class ModelGateway:
    """根据任务类型自动选模型"""

    MODEL_MAP = {
        "ceo_route": "claude-opus-4-6",
        "coo_planning": "claude-sonnet-4-6",
        "dept_execution": "claude-haiku-4-5",
        "strategy_debate": "claude-sonnet-4-6",
        "content_generation": "claude-haiku-4-5",
        "code_generation": "claude-opus-4-6",
    }

    def resolve(self, task_type: str, context: dict = None) -> str:
        # 支持动态路由：根据上下文调整模型
        if context and context.get("complexity") == "high":
            return "claude-opus-4-6"
        return self.MODEL_MAP.get(task_type, "claude-sonnet-4-6")
```

### 2.4 事件驱动架构

```python
# backend/app/engine/event_bus.py

@dataclass
class Event:
    type: str
    data: dict
    timestamp: datetime = field(default_factory=datetime.utcnow)

class EventBus:
    def __init__(self):
        self._handlers: dict[str, List[Callable]] = {}
        self._middleware: List[Callable] = []

    def on(self, event_type: str, handler: Callable):
        self._handlers.setdefault(event_type, []).append(handler)

    async def emit(self, event: Event):
        for mw in self._middleware:
            event = await mw(event)
        for handler in self._handlers.get(event.type, []):
            await handler(event)

# 全局事件总线
bus = EventBus()

# 事件类型定义
class EventTypes:
    AGENT_STARTED = "agent.started"
    AGENT_COMPLETED = "agent.completed"
    AGENT_ERROR = "agent.error"
    MESSAGE_RECEIVED = "message.received"
    MESSAGE_SENT = "message.sent"
    TASK_CREATED = "task.created"
    TASK_COMPLETED = "task.completed"
    BUDGET_ALERT = "budget.alert"
```

### 2.5 JWT 认证

```python
# backend/app/auth/jwt.py

from jose import jwt, JWTError
from passlib.context import CryptContext

class AuthService:
    SECRET = settings.SECRET_KEY
    ALGORITHM = "HS256"

    def create_token(self, user_id: str, org_id: str = "default") -> str:
        return jwt.encode({
            "sub": user_id,
            "org": org_id,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }, self.SECRET, algorithm=self.ALGORITHM)

    def verify_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, self.SECRET, algorithms=[self.ALGORITHM])
        except JWTError:
            raise Unauthorized("Invalid token")

    async def get_current_user(self, token: str) -> User:
        payload = self.verify_token(token)
        return await self.user_repo.get_by_id(payload["sub"])
```

---

## 四、Phase 3：CyberTeam 特色保留清单

> 以下是 CyberTeam 独有的能力，抄 Magic 时**绝对不能丢**

### 4.1 三省六部组织架构（保留）

```typescript
// CyberTeam 独有的部门体系
const DEPARTMENTS = {
  // 决策层
  CEO: { name: "CEO", role: "决策中枢", agents: ["总指挥"] },
  PM: { name: "PM", role: "项目协调", agents: ["项目经理"] },

  // 协调层（11部）
  STRATEGY: { name: "战略部", role: "战略规划" },
  PRODUCT: { name: "产品部", role: "产品设计" },
  ENGINEERING: { name: "技术部", role: "技术实现" },
  DESIGN: { name: "设计部", role: "UI/UX设计" },
  OPERATIONS: { name: "运营部", role: "用户增长" },
  FINANCE: { name: "财务部", role: "预算控制" },
  HR: { name: "人事部", role: "人才管理" },
  MARKETING: { name: "市场部", role: "品牌推广" },
  SALES: { name: "销售部", role: "渠道销售" },
  CUSTOMER: { name: "客服部", role: "客户维护" },
  LEGAL: { name: "法务部", role: "合规审查" },
  INFO: { name: "信息部", role: "情报收集" },

  // 执行层
  EXECUTION: { name: "执行部", role: "具体执行" },
}
```

### 4.2 思维注入引擎（CyberTeam 核心）

```python
# backend/app/engine/thinking_injector.py（已存在，需保留）

class ThinkingInjector:
    """把100+思维专家的思维模式注入到任意Agent"""

    EXPERTS = {
        "first_principles": "第一性原理",
        "lateral_thinking": "横向思维",
        "six_hats": "六顶思考帽",
        "moscow": "MoSCoW优先级",
        "kano": "Kano模型",
        # ... 100+ 专家
    }

    def inject(self, agent: AgentProfile, thinking_mode: str) -> AgentProfile:
        """为Agent注入特定思维模式"""
        expert = self.EXPERTS.get(thinking_mode)
        if not expert:
            return agent

        # 在 system_prompt 中注入思维专家的角色
        injected_prompt = f"{agent.system_prompt}\n\n【思维注入】你现在同时扮演{expert}，用此思维模式分析问题。"
        return agent.model_copy(update={"system_prompt": injected_prompt})
```

### 4.3 辩论引擎（CyberTeam 核心）

```python
# backend/app/engine/debate_engine.py（CyberTeam 独有）

class DebateEngine:
    """多Agent辩论引擎，支持正反方观点碰撞"""

    async def run_debate(self, topic: str, participants: list[str]) -> DebateResult:
        # 1. 正方陈述
        pro_agent = await self.compiler.compile("strategy-agent")
        pro_view = await pro_agent.run(f"正面论证：{topic}")

        # 2. 反方陈述
        con_agent = await self.compiler.compile("strategy-agent")
        con_view = await con_agent.run(f"反面论证：{topic}")

        # 3. 综合评估
        judge = await self.compiler.compile("ceo-agent")
        verdict = await judge.run(f"综合正反方观点，给出最终判断：\n正方：{pro_view}\n反方：{con_view}")

        return DebateResult(pro=pro_view, con=con_view, verdict=verdict)
```

### 4.4 八节点执行流程（CyberTeam 流程）

```
CEO-COO对齐 → 策略讨论 → 风险预案 → CEO汇报
    ↓
设计联动 → 文案产出 → CEO汇总 → 复盘进化
    ↓
Playground 生成（交互式看板）
```

### 4.5 质疑者 Agent（CyberTeam 质量门禁）

```python
# CyberTeam 独有的质疑者角色
SOCRATIC_QUESTIONER = """
你是一个质疑者。对每一个结论追问"为什么"和"怎么知道的"。
对每一项数据追问"来源是什么"。对每一个假设追问"验证过吗"。
对每一条建议追问"证据在哪里"。
"""
```

---

## 五、Phase 4：数据模型

### 5.1 核心数据库 Schema

```sql
-- 会话表
CREATE TABLE conversations (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    agent_id VARCHAR(64),
    title VARCHAR(255),
    status VARCHAR(32) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 消息表
CREATE TABLE messages (
    id VARCHAR(64) PRIMARY KEY,
    conversation_id VARCHAR(64) NOT NULL,
    sender_type VARCHAR(32),  -- user/agent/system
    sender_id VARCHAR(64),
    content TEXT,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_conversation (conversation_id, created_at)
);

-- Agent 执行日志
CREATE TABLE agent_executions (
    id VARCHAR(64) PRIMARY KEY,
    task_id VARCHAR(64),
    agent_name VARCHAR(64),
    status VARCHAR(32),
    input TEXT,
    output TEXT,
    tokens_used INTEGER,
    cost_usd DECIMAL(10, 6),
    duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 预算追踪
CREATE TABLE budget_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type VARCHAR(32),
    entity_id VARCHAR(64),
    period DATE,
    tokens_used INTEGER DEFAULT 0,
    cost_usd DECIMAL(10, 6) DEFAULT 0,
    budget_limit DECIMAL(10, 6),
    UNIQUE(entity_type, entity_id, period)
);
```

---

## 六、执行计划

| 优先级 | 任务 | 工作量 | 状态 |
|--------|------|--------|------|
| P0 | 创建本技术清单文档 | 1h | ✅ |
| P0 | 后端 FastAPI 骨架 + 路由 | 3h | 🔄 |
| P0 | 前端三栏对话界面 | 3h | 🔄 |
| P1 | WebSocket 实时通信 | 2h | ⏳ |
| P1 | Agent 编译器 | 2h | ⏳ |
| P1 | 多模型网关 | 1h | ⏳ |
| P1 | 事件驱动架构 | 1h | ⏳ |
| P2 | JWT 认证 | 2h | ⏳ |
| P2 | 数据库 Schema | 1h | ⏳ |
| P2 | Playground 生成器 | 2h | ⏳ |
| P3 | TipTap 富文本编辑器 | 3h | ⏳ |
| P3 | 数字员工市场 | 3h | ⏳ |

---

## 七、双语提示词规范（立即执行）

> Magic 的核心工程实践：在注释中写中文给开发者看，Prompt 正文用英文给 LLM 看

```markdown
<!--zh
## Agent 角色定义

这是一个营销策略专家Agent，负责为品牌制定全渠道营销方案。
继承 CEO 的战略方向，协调设计部、运营部执行。

## 能力范围
- 市场调研与竞品分析
- 营销策略制定
- 渠道规划与分工
- 转化路径设计
-->

You are a marketing strategy expert. Your role is to develop comprehensive
multi-channel marketing plans that align with the CEO's strategic direction.
You coordinate with the Design and Operations departments to execute plans.

## Core Capabilities
- Market research and competitor analysis
- Marketing strategy development
- Channel planning and allocation
- Conversion path design

## Working Process
1. Receive strategic direction from CEO
2. Analyze market context via information gathering
3. Develop strategy with debate if needed
4. Coordinate execution across departments
```

---

*最后更新：2026-03-28*
