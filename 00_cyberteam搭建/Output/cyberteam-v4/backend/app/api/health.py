"""Health API — 健康检查。"""

import logging

from fastapi import APIRouter

log = logging.getLogger("cyberteam.api.health")
router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查。"""
    return {
        "status": "ok",
        "service": "CyberTeam V4 API",
        "version": "4.0.0",
    }


@router.get("/ready")
async def readiness_check():
    """就绪检查。"""
    # 可以在这里添加更多依赖检查
    return {
        "status": "ready",
        "checks": {
            "database": "ok",
            "api": "ok",
        },
    }