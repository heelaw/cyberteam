"""State Machine API — 三省六部状态机配置与控制。

提供 RESTful API 用于管理 CyberTeam 任务状态机。
"""

import logging
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

log = logging.getLogger("cyberteam.api.state_machine")
router = APIRouter()

# ── Engine 模块路径设置 ──
_backend_path = Path(__file__).parent.parent.parent
_engine_path = _backend_path / "engine"

for p in [str(_backend_path), str(_engine_path)]:
    if p not in sys.path:
        sys.path.insert(0, p)


# ── 内存存储 ──
_state_machines: Dict[str, Any] = {}
_state_machine_config = {
    "enabled": True,
    "states": ["pending", "taizi", "zhongshu", "menxia", "assigned", "doing", "review", "done"],
}


# ── Schemas ──

class StateMachineConfigRequest(BaseModel):
    """状态机配置请求"""
    enabled: bool = True
    states: Optional[List[str]] = None


class StateMachineConfigResponse(BaseModel):
    """状态机配置响应"""
    enabled: bool
    states: List[str]
    total_states: int


class TaskStateCreate(BaseModel):
    """创建任务状态"""
    task_id: Optional[str] = None
    title: str = ""
    description: str = ""
    user_input: str = ""
    priority: str = "中"


class TaskStateResponse(BaseModel):
    """任务状态响应"""
    task_id: str
    trace_id: str
    state: str
    current_node: Optional[str]
    prince_agent: Optional[str]
    zhongshu_agent: Optional[str]
    menxia_agent: Optional[str]
    shangshu_agent: Optional[str]
    six_ministries: Dict[str, str]
    completed_nodes: List[str]
    active_node: Optional[str]
    score: Optional[float]
    score_breakdown: Dict[str, float]
    transitions: List[dict]
    created_at: str
    updated_at: str
    completed_at: Optional[str]
    title: str
    description: str
    priority: str
    tags: List[str]


class TransitionRequest(BaseModel):
    """状态转换请求"""
    to_state: str
    reason: str = "system"
    triggered_by: str = "system"
    metadata: Optional[dict] = None


class AgentAssignRequest(BaseModel):
    """Agent分配请求"""
    role: str  # prince/zhongshu/menxia/shangshu 或六部
    agent_id: str


class ScoreRequest(BaseModel):
    """评分请求"""
    total: float
    breakdown: Dict[str, float]


# ── Endpoints ──

@router.get("/config", response_model=StateMachineConfigResponse)
async def get_config():
    """获取状态机配置"""
    return StateMachineConfigResponse(
        enabled=_state_machine_config["enabled"],
        states=_state_machine_config["states"],
        total_states=len(_state_machine_config["states"]),
    )


@router.post("/config")
async def update_config(config: StateMachineConfigRequest):
    """更新状态机配置"""
    global _state_machine_config

    _state_machine_config["enabled"] = config.enabled
    if config.states:
        _state_machine_config["states"] = config.states

    log.info(f"State machine config updated: enabled={config.enabled}")

    return {
        "status": "ok",
        "config": _state_machine_config,
    }


@router.get("/states")
async def list_states():
    """获取所有可用状态"""
    from engine.state_machine import EdictState, STATE_METADATA

    states = []
    for state in EdictState:
        meta = STATE_METADATA.get(state, {})
        states.append({
            "value": state.value,
            "name": meta.get("name", ""),
            "description": meta.get("description", ""),
            "department": meta.get("department", ""),
        })

    return {"states": states}


@router.post("/tasks", response_model=TaskStateResponse)
async def create_task_state(body: TaskStateCreate):
    """创建任务状态机"""
    if not _state_machine_config["enabled"]:
        raise HTTPException(status_code=400, detail="State machine is disabled")

    try:
        from engine.state_machine import create_state_machine, EdictState

        sm = create_state_machine(
            task_id=body.task_id,
            title=body.title,
            description=body.description,
            user_input=body.user_input,
            priority=body.priority,
        )

        _state_machines[sm.state.task_id] = sm

        log.info(f"Task state created: {sm.state.task_id}")

        return TaskStateResponse(**sm.state.to_dict())

    except Exception as e:
        log.error(f"Failed to create task state: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}", response_model=TaskStateResponse)
async def get_task_state(task_id: str):
    """获取任务状态"""
    if task_id not in _state_machines:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")

    sm = _state_machines[task_id]
    return TaskStateResponse(**sm.state.to_dict())


@router.get("/tasks")
async def list_tasks(
    state: Optional[str] = Query(None, description="Filter by state"),
    limit: int = Query(50, ge=1, le=100),
):
    """获取所有任务状态"""
    tasks = []
    for task_id, sm in _state_machines.items():
        if state and sm.state.state.value != state:
            continue
        tasks.append(TaskStateResponse(**sm.state.to_dict()))
        if len(tasks) >= limit:
            break

    return {"tasks": tasks, "total": len(_state_machines)}


@router.post("/tasks/{task_id}/transition")
async def transition_state(task_id: str, body: TransitionRequest):
    """执行状态转换"""
    if task_id not in _state_machines:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")

    try:
        from engine.state_machine import EdictState, TransitionReason, InvalidTransitionError

        # 解析目标状态
        try:
            to_state = EdictState(body.to_state)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid state: {body.to_state}")

        # 解析转换原因
        try:
            reason = TransitionReason(body.reason)
        except ValueError:
            reason = TransitionReason.SYSTEM

        sm = _state_machines[task_id]
        transition = sm.transition(
            to_state=to_state,
            reason=reason,
            triggered_by=body.triggered_by,
            metadata=body.metadata,
        )

        log.info(f"Task {task_id} transitioned to {body.to_state}")

        return {
            "status": "ok",
            "task_id": task_id,
            "from_state": transition.from_state.value,
            "to_state": transition.to_state.value,
            "reason": transition.reason.value,
            "timestamp": transition.timestamp.isoformat(),
        }

    except InvalidTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log.error(f"Transition failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/{task_id}/agents")
async def assign_agent(task_id: str, body: AgentAssignRequest):
    """分配Agent到角色"""
    if task_id not in _state_machines:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")

    sm = _state_machines[task_id]
    sm.assign_agent(role=body.role, agent_id=body.agent_id)

    log.info(f"Agent {body.agent_id} assigned to role {body.role} for task {task_id}")

    return {"status": "ok", "role": body.role, "agent_id": body.agent_id}


@router.post("/tasks/{task_id}/score")
async def set_score(task_id: str, body: ScoreRequest):
    """设置质量评分"""
    if task_id not in _state_machines:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")

    sm = _state_machines[task_id]
    sm.set_score(total=body.total, breakdown=body.breakdown)

    log.info(f"Score set for task {task_id}: {body.total}")

    return {"status": "ok", "total": body.total, "breakdown": body.breakdown}


@router.get("/tasks/{task_id}/progress")
async def get_progress(task_id: str):
    """获取任务进度"""
    if task_id not in _state_machines:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")

    sm = _state_machines[task_id]
    return sm.get_progress()


@router.get("/tasks/{task_id}/flow")
async def get_flow_summary(task_id: str):
    """获取流程摘要"""
    if task_id not in _state_machines:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")

    sm = _state_machines[task_id]
    return {"flow": sm.get_flow_summary()}


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """删除任务状态"""
    if task_id not in _state_machines:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")

    del _state_machines[task_id]
    log.info(f"Task {task_id} deleted")

    return {"status": "ok", "message": f"Task {task_id} deleted"}
