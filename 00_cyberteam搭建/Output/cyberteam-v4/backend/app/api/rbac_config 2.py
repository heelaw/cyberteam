"""RBAC Config API — 权限矩阵配置与控制。

提供 RESTful API 用于管理 CyberTeam RBAC 权限矩阵。
"""

import logging
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

log = logging.getLogger("cyberteam.api.rbac_config")
router = APIRouter()

# ── Engine 模块路径设置 ──
_backend_path = Path(__file__).parent.parent.parent
_engine_path = _backend_path / "engine"

for p in [str(_backend_path), str(_engine_path)]:
    if p not in sys.path:
        sys.path.insert(0, p)


# ── 内存存储 ──
_rbac_config = {
    "enabled": True,
    "matrix": None,  # None means use default
}


# ── Schemas ──

class RBACConfigRequest(BaseModel):
    """RBAC 配置请求"""
    enabled: bool = True
    matrix: Optional[Dict[str, List[str]]] = None


class RBACConfigResponse(BaseModel):
    """RBAC 配置响应"""
    enabled: bool
    has_custom_matrix: bool
    total_agents: int


class AgentInfoResponse(BaseModel):
    """Agent 信息响应"""
    id: str
    label: str
    layer: str
    role: str
    duty: str
    allow_agents: List[str]


class PermissionCheckRequest(BaseModel):
    """权限检查请求"""
    from_agent: str
    to_agent: str


class PermissionCheckResponse(BaseModel):
    """权限检查响应"""
    allowed: bool
    reason: str


class PermissionUpdateRequest(BaseModel):
    """权限更新请求"""
    from_agent: str
    to_agents: List[str]


# ── Endpoints ──

@router.get("/config", response_model=RBACConfigResponse)
async def get_config():
    """获取 RBAC 配置"""
    from engine.rbac import RBACMatrix

    rbac = RBACMatrix(custom_matrix=_rbac_config.get("matrix"))
    total_agents = len(rbac.matrix)

    return RBACConfigResponse(
        enabled=_rbac_config["enabled"],
        has_custom_matrix=_rbac_config["matrix"] is not None,
        total_agents=total_agents,
    )


@router.post("/config")
async def update_config(config: RBACConfigRequest):
    """更新 RBAC 配置"""
    global _rbac_config

    _rbac_config["enabled"] = config.enabled
    if config.matrix is not None:
        _rbac_config["matrix"] = config.matrix

    log.info(f"RBAC config updated: enabled={config.enabled}")

    return {
        "status": "ok",
        "config": _rbac_config,
    }


@router.get("/agents")
async def list_agents(layer: Optional[str] = None):
    """获取所有 Agent 列表"""
    from engine.rbac import RBACMatrix, AgentLayer

    rbac = RBACMatrix(custom_matrix=_rbac_config.get("matrix"))

    agents = []
    for agent_id in rbac.matrix.keys():
        info = rbac.get_agent_info(agent_id)
        if info:
            if layer and info.layer.value != layer:
                continue
            agents.append({
                "id": info.id,
                "label": info.label,
                "layer": info.layer.value,
                "role": info.role,
                "duty": info.duty,
                "allow_agents": info.allow_agents,
            })

    return {"agents": agents, "total": len(agents)}


@router.get("/agents/{agent_id}", response_model=AgentInfoResponse)
async def get_agent(agent_id: str):
    """获取单个 Agent 信息"""
    from engine.rbac import RBACMatrix

    rbac = RBACMatrix(custom_matrix=_rbac_config.get("matrix"))
    info = rbac.get_agent_info(agent_id)

    if not info:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")

    return AgentInfoResponse(
        id=info.id,
        label=info.label,
        layer=info.layer.value,
        role=info.role,
        duty=info.duty,
        allow_agents=info.allow_agents,
    )


@router.get("/agents/{agent_id}/allowed")
async def get_allowed_agents(agent_id: str):
    """获取 Agent 可通信的目标列表"""
    from engine.rbac import RBACMatrix

    rbac = RBACMatrix(custom_matrix=_rbac_config.get("matrix"))
    allowed = rbac.get_allowed_agents(agent_id)

    return {
        "agent_id": agent_id,
        "allowed_agents": allowed,
        "count": len(allowed),
    }


@router.get("/agents/{agent_id}/can-reach")
async def get_can_reach_me(agent_id: str):
    """获取可以联系该 Agent 的所有 Agent"""
    from engine.rbac import RBACMatrix

    rbac = RBACMatrix(custom_matrix=_rbac_config.get("matrix"))
    can_reach = rbac.get_can_reach_me(agent_id)

    return {
        "agent_id": agent_id,
        "can_reach_me": list(can_reach),
        "count": len(can_reach),
    }


@router.get("/layers")
async def list_layers():
    """获取所有层级"""
    from engine.rbac import AgentLayer

    layers = []
    for layer in AgentLayer:
        layers.append({
            "value": layer.value,
            "name": layer.name,
        })

    return {"layers": layers}


@router.get("/layers/{layer}/agents")
async def get_agents_by_layer(layer: str):
    """获取指定层级的所有 Agent"""
    from engine.rbac import RBACMatrix, AgentLayer

    rbac = RBACMatrix(custom_matrix=_rbac_config.get("matrix"))

    try:
        agent_layer = AgentLayer(layer)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid layer: {layer}")

    agents = rbac.get_agents_by_layer(agent_layer)

    return {
        "layer": layer,
        "agents": agents,
        "count": len(agents),
    }


@router.post("/check")
async def check_permission(body: PermissionCheckRequest):
    """检查两个 Agent 之间是否可以通信"""
    from engine.rbac import RBACMatrix

    if not _rbac_config["enabled"]:
        return PermissionCheckResponse(
            allowed=True,
            reason="RBAC is disabled"
        )

    rbac = RBACMatrix(custom_matrix=_rbac_config.get("matrix"))
    result = rbac.can_communicate(body.from_agent, body.to_agent)

    return PermissionCheckResponse(
        allowed=result.allowed,
        reason=result.reason,
    )


@router.post("/check-dispatch")
async def check_dispatch_permission(body: PermissionCheckRequest):
    """检查调度权限"""
    from engine.rbac import RBACMatrix

    if not _rbac_config["enabled"]:
        return PermissionCheckResponse(
            allowed=True,
            reason="RBAC is disabled"
        )

    rbac = RBACMatrix(custom_matrix=_rbac_config.get("matrix"))
    result = rbac.can调度(body.from_agent, body.to_agent)

    return PermissionCheckResponse(
        allowed=result.allowed,
        reason=result.reason,
    )


@router.get("/routing/{from_agent}/{to_agent}")
async def get_routing_path(from_agent: str, to_agent: str):
    """计算两个 Agent 之间的路由路径"""
    from engine.rbac import RBACMatrix

    rbac = RBACMatrix(custom_matrix=_rbac_config.get("matrix"))
    path = rbac.get_routing_path(from_agent, to_agent)

    return {
        "from_agent": from_agent,
        "to_agent": to_agent,
        "path": path,
        "can_direct": len(path) == 2,
        "steps": len(path) - 1 if path else 0,
    }


@router.put("/matrix/{agent_id}")
async def update_agent_permissions(agent_id: str, body: PermissionUpdateRequest):
    """更新 Agent 的权限白名单"""
    from engine.rbac import RBACMatrix

    global _rbac_config

    if _rbac_config["matrix"] is None:
        _rbac_config["matrix"] = {}

    _rbac_config["matrix"][agent_id] = body.to_agents

    log.info(f"Updated permissions for {agent_id}: {body.to_agents}")

    return {
        "status": "ok",
        "agent_id": agent_id,
        "new_allow_list": body.to_agents,
    }


@router.get("/matrix")
async def get_full_matrix():
    """获取完整权限矩阵"""
    from engine.rbac import RBACMatrix

    rbac = RBACMatrix(custom_matrix=_rbac_config.get("matrix"))

    # 构建矩阵视图
    agents = list(rbac.matrix.keys())
    matrix = {}

    for from_agent in agents:
        row = {}
        for to_agent in agents:
            result = rbac.can_communicate(from_agent, to_agent)
            row[to_agent] = result.allowed
        matrix[from_agent] = row

    return {
        "agents": agents,
        "matrix": matrix,
        "enabled": _rbac_config["enabled"],
    }


@router.get("/validate/{agent_config_name}")
async def validate_edict_format(agent_config_name: str):
    """验证 Edict 格式的 Agent 配置"""
    from engine.rbac import RBACMatrix

    rbac = RBACMatrix(custom_matrix=_rbac_config.get("matrix"))

    # 检查是否支持该配置
    if agent_config_name == "edict":
        return {
            "valid": True,
            "format": "edict",
            "description": "Edict allowAgents 白名单格式",
            "supported": True,
        }

    return {
        "valid": False,
        "format": agent_config_name,
        "supported": False,
    }
