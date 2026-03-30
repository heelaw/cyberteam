"""Health API — 健康检查。"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any, List

from fastapi import APIRouter

from ..config import get_settings

log = logging.getLogger("cyberteam.api.health")
router = APIRouter()

# ── 模块路径设置 ──
_backend_path = Path(__file__).parent.parent.parent
_engine_path = _backend_path / "engine"
_cyberteam_path = _backend_path / "cyberteam"
_integration_path = _backend_path / "integration"

for p in [str(_backend_path), str(_engine_path), str(_cyberteam_path), str(_integration_path)]:
    if p not in sys.path:
        sys.path.insert(0, p)


def _check_module(module_name: str, class_name: str) -> dict[str, Any]:
    """检查单个模块是否可用"""
    try:
        module = __import__(module_name, fromlist=[class_name])
        cls = getattr(module, class_name, None)
        if cls is not None:
            return {"status": "ok", "class": class_name}
        return {"status": "error", "reason": f"{class_name} not found in {module_name}"}
    except Exception as e:
        return {"status": "error", "reason": str(e)}


def _get_all_module_status() -> dict[str, Any]:
    """获取所有模块状态"""
    modules = {
        "engine.ceo": "CEORouter",
        "engine.strategy": "StrategyEngine",
        "engine.department": "DepartmentExecutor",
        "integration.cyberteam_adapter": "CyberTeamAdapter",
        "swarm_orchestrator": "SwarmOrchestrator",
    }

    results = {}
    for module_name, class_name in modules.items():
        results[module_name] = _check_module(module_name, class_name)

    return results


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
    modules = _get_all_module_status()
    ok_count = sum(1 for v in modules.values() if v.get("status") == "ok")

    return {
        "status": "ready" if ok_count == len(modules) else "degraded",
        "checks": {
            "database": "ok",
            "api": "ok",
            "modules": f"{ok_count}/{len(modules)}",
        },
        "module_details": modules,
    }


@router.get("/modules")
async def get_module_status():
    """获取所有 Engine 模块状态"""
    modules = _get_all_module_status()

    return {
        "modules": modules,
        "total": len(modules),
        "ok": sum(1 for v in modules.values() if v.get("status") == "ok"),
    }


@router.get("/skills")
async def get_available_skills():
    """获取所有可用的 Skills"""
    skills = []

    # Gstack Skills
    try:
        from engine.department import GstackAdapter
        gstack = GstackAdapter()
        for skill in gstack.list_skills():
            skills.append({
                "name": skill,
                "type": "gstack",
                "category": "engineering"
            })
    except Exception as e:
        log.warning(f"Failed to load Gstack Skills: {e}")

    return {"skills": skills, "total": len(skills)}


@router.get("/agents/system")
async def get_system_agents():
    """获取所有系统 Agents"""
    agents = []

    # Agent Adapter Agents
    try:
        from engine.department import AgentAdapter
        agent_adapter = AgentAdapter()
        for agent in agent_adapter.list_agents():
            agents.append({
                "name": agent,
                "type": "system",
                "description": agent_adapter.AGENTS.get(agent, "")
            })
    except Exception as e:
        log.warning(f"Failed to load System Agents: {e}")

    return {"agents": agents, "total": len(agents)}