"""CyberTeam V4 Backend — FastAPI 应用入口。

核心功能：
- 任务管理 API
- 意图识别与专家路由
- 辩论引擎控制
- 方案评分与质量门禁
- 状态同步
- WebSocket 实时通信
- SSE 流式输出
- JWT 认证
- 预算追踪与审批

Lifespan 管理：
- startup: 初始化数据库连接、加载配置、初始化核心模块
- shutdown: 关闭连接
"""

import logging
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .db import init_db, close_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
log = logging.getLogger("cyberteam")

# ── Engine 模块路径设置 ──
_backend_path = Path(__file__).parent.parent.parent  # backend/app/ -> cyberteam-v4/
_engine_path = _backend_path / "engine"
_cyberteam_path = _backend_path / "cyberteam"
_integration_path = _backend_path / "integration"
_swarm_path = _backend_path
_frontend_dist_path = _backend_path / "frontend" / "dist"

# 添加到 sys.path
for p in [_backend_path, _engine_path, _cyberteam_path, _integration_path, _swarm_path]:
    p_str = str(p)
    if p_str not in sys.path:
        sys.path.insert(0, p_str)

# ── 模块导入状态 ──
_module_status: Dict[str, Any] = {}


def _check_modules():
    """启动时检查所有模块是否可导入。"""
    global _module_status

    checks = [
        ("engine.ceo", "CEORouter"),
        ("engine.strategy", "StrategyEngine"),
        ("engine.department", "DepartmentExecutor"),
        ("integration.cyberteam_adapter", "CyberTeamAdapter"),
        ("swarm_orchestrator", "SwarmOrchestrator"),
    ]

    # 检查核心模块
    core_checks = [
        ("app.engine.event_bus", "EventBus"),
        ("app.engine.model_gateway", "ModelGateway"),
        ("app.engine.agent_compiler", "AgentCompiler"),
        ("app.engine.swarm_orchestrator", "SwarmOrchestrator"),
        ("app.engine.thinking_injector", "ThinkingInjector"),
        ("app.auth.jwt", "AuthService"),
        ("app.auth.rbac", "RBACService"),
        ("app.db.database", "Base"),
        ("app.queue.task_queue", "TaskQueue"),
    ]

    for module_name, expected_class in checks + core_checks:
        try:
            module = __import__(module_name, fromlist=[expected_class])
            cls = getattr(module, expected_class, None)
            if cls is not None:
                _module_status[module_name] = {"status": "ok", "class": expected_class}
            else:
                _module_status[module_name] = {"status": "error", "reason": f"{expected_class} not found"}
        except Exception as e:
            _module_status[module_name] = {"status": "error", "reason": str(e)}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理。"""
    settings = get_settings()
    log.info(f"CyberTeam V4 Backend starting on port {settings.port}...")

    # 启动检查：验证所有模块导入
    _check_modules()
    ok_count = sum(1 for v in _module_status.values() if v.get("status") == "ok")
    total_count = len(_module_status)
    log.info(f"Module check: {ok_count}/{total_count} modules loaded")

    for mod_name, status in _module_status.items():
        if status["status"] == "ok":
            log.info(f"   [OK] {mod_name}")
        else:
            log.warning(f"   [ERR] {mod_name}: {status.get('reason', 'unknown error')}")

    # 初始化数据库
    await init_db()
    log.info("Database initialized")

    # 初始化事件总线订阅
    _init_event_subscriptions()

    yield

    # 清理
    await close_db()
    log.info("CyberTeam V4 Backend shutdown complete")


def _init_event_subscriptions():
    """初始化事件总线的订阅关系。"""
    try:
        from .engine.event_bus import event_bus

        async def on_approval_requested(event):
            """审批请求事件 -> 推送 WebSocket。"""
            try:
                from .api.websocket import ws_manager
                await ws_manager.broadcast({
                    "type": "approval_request",
                    "data": event.data,
                    "timestamp": event.timestamp,
                })
            except Exception as e:
                log.error(f"Failed to push approval event: {e}")

        async def on_agent_status_change(event):
            """Agent 状态变化 -> 推送 WebSocket。"""
            try:
                from .api.websocket import ws_manager
                await ws_manager.broadcast({
                    "type": event.type,
                    "data": event.data,
                    "timestamp": event.timestamp,
                })
            except Exception as e:
                log.error(f"Failed to push agent status event: {e}")

        event_bus.on("approval.requested", on_approval_requested)
        event_bus.on("approval.approved", on_agent_status_change)
        event_bus.on("approval.rejected", on_agent_status_change)
        event_bus.on("agent.started", on_agent_status_change)
        event_bus.on("agent.completed", on_agent_status_change)
        event_bus.on("agent.failed", on_agent_status_change)
        event_bus.on("budget.warning", on_agent_status_change)

        log.info("Event bus subscriptions initialized")
    except Exception as e:
        log.warning(f"Failed to init event subscriptions: {e}")


app = FastAPI(
    title="CyberTeam V4 API",
    description="AI 模拟公司协作平台后端服务",
    version="4.1.0",
    lifespan=lifespan,
)

# CORS — 明确允许的来源（生产环境应配置具体域名）
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",   # Vite 默认端口
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ── 注册路由 ──

# 原有 API 路由
from .api import tasks, agents, experts, debate, scoring, health, todos, departments, teams, skills, state_machine, rbac_config, reports, review  # market, company excluded: missing models

app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(experts.router, prefix="/api/experts", tags=["experts"])
app.include_router(debate.router, prefix="/api/debate", tags=["debate"])
app.include_router(scoring.router, prefix="/api/scoring", tags=["scoring"])
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(todos.router, prefix="/api/todos", tags=["todos"])
app.include_router(departments.router, prefix="/api/departments", tags=["departments"])
app.include_router(teams.router, prefix="/api/teams", tags=["teams"])
app.include_router(skills.router, prefix="/api/skills", tags=["skills"])
app.include_router(state_machine.router, prefix="/api/config/state-machine", tags=["state-machine"])
app.include_router(rbac_config.router, prefix="/api/config/rbac", tags=["rbac"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(review.router, prefix="/api/review", tags=["review"])
# app.include_router(market.router, prefix="/api/market", tags=["market"])  # excluded: missing Department/Agent models
# app.include_router(company.router, prefix="/api/company", tags=["company"])  # excluded: missing Company/CompanyDepartment models

# 新增：WebSocket 和 SSE 路由
from .api import websocket as ws_api, sse as sse_api

app.include_router(ws_api.router, tags=["websocket"])
app.include_router(sse_api.router, prefix="/api", tags=["sse"])

# 新增：API v1 路由（抄 Magic）
from .api.v1 import chat as v1_chat, agents as v1_agents, projects as v1_projects, skills as v1_skills

app.include_router(v1_chat.router, prefix="/api/v1", tags=["chat v1"])
app.include_router(v1_agents.router, prefix="/api/v1", tags=["agents v1"])
app.include_router(v1_projects.router, prefix="/api/v1", tags=["projects v1"])
app.include_router(v1_skills.router, prefix="/api/v1", tags=["skills v1"])

# ── 静态文件服务（serve frontend dist） ──
if _frontend_dist_path.exists() and _frontend_dist_path.is_dir():
    app.mount(
        "/",
        StaticFiles(directory=str(_frontend_dist_path), html=True),
        name="frontend",
    )
    log.info(f"Frontend static files mounted from {_frontend_dist_path}")


@app.get("/")
async def root():
    return {
        "name": "CyberTeam V4 API",
        "version": "4.1.0",
        "status": "running",
        "features": [
            "tasks", "agents", "experts", "debate", "scoring",
            "websocket", "sse", "auth", "budget", "approval",
        ],
    }


@app.get("/modules")
async def get_module_status():
    """获取模块导入状态。"""
    return {
        "modules": _module_status,
        "total": len(_module_status),
        "ok": sum(1 for v in _module_status.values() if v.get("status") == "ok"),
    }
