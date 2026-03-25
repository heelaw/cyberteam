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
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .db import init_db, close_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
log = logging.getLogger("cyberteam")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理。"""
    settings = get_settings()
    log.info(f"🏛️ CyberTeam V4 Backend starting on port {settings.port}...")

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
from .api import tasks, agents, experts, debate, scoring, health

app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(experts.router, prefix="/api/experts", tags=["experts"])
app.include_router(debate.router, prefix="/api/debate", tags=["debate"])
app.include_router(scoring.router, prefix="/api/scoring", tags=["scoring"])
app.include_router(health.router, tags=["health"])


@app.get("/")
async def root():
    return {
        "name": "CyberTeam V4 API",
        "version": "4.0.0",
        "status": "running",
    }