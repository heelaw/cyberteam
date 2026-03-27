"""CyberTeam V4 Backend — FastAPI 应用入口。

核心功能：
- 任务管理 API
- 意图识别与专家路由
- 辩论引擎控制
- 方案评分与质量门禁
- 状态同步

Lifespan 管理：
- startup: 初始化数据库连接、加载配置
- shutdown: 关闭连接
"""

import logging
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

    for module_name, expected_class in checks:
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
    log.info(f"🏛️ CyberTeam V4 Backend starting on port {settings.port}...")

    # 启动检查：验证所有模块导入
    _check_modules()
    ok_count = sum(1 for v in _module_status.values() if v.get("status") == "ok")
    total_count = len(_module_status)
    log.info(f"🔍 Module check: {ok_count}/{total_count} modules loaded")

    for mod_name, status in _module_status.items():
        if status["status"] == "ok":
            log.info(f"   ✅ {mod_name}")
        else:
            log.warning(f"   ❌ {mod_name}: {status.get('reason', 'unknown error')}")

    # 初始化数据库
    await init_db()
    log.info("✅ Database initialized")

    yield

    # 清理
    await close_db()
    log.info("CyberTeam V4 Backend shutdown complete")


app = FastAPI(
    title="CyberTeam V4 API",
    description="AI 模拟公司协作平台后端服务",
    version="4.0.0",
    lifespan=lifespan,
)

# CORS — 开发环境允许所有来源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
from .api import tasks, agents, experts, debate, scoring, health, todos

app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(experts.router, prefix="/api/experts", tags=["experts"])
app.include_router(debate.router, prefix="/api/debate", tags=["debate"])
app.include_router(scoring.router, prefix="/api/scoring", tags=["scoring"])
app.include_router(health.router, tags=["health"])
app.include_router(todos.router, prefix="/api/todos", tags=["todos"])


@app.get("/")
async def root():
    return {
        "name": "CyberTeam V4 API",
        "version": "4.0.0",
        "status": "running",
    }


@app.get("/modules")
async def get_module_status():
    """获取模块导入状态。"""
    return {
        "modules": _module_status,
        "total": len(_module_status),
        "ok": sum(1 for v in _module_status.values() if v.get("status") == "ok"),
    }