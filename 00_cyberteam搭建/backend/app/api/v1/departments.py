"""Departments API — 三省六部组织架构。"""
from __future__ import annotations

from fastapi import APIRouter

from app.engine.agent_compiler import agent_compiler

router = APIRouter()


@router.get("")
async def list_departments() -> list[dict]:
    """List all departments with their agents."""
    agents = agent_compiler.get_available_agents()
    dept_map: dict[str, list] = {}
    for a in agents:
        for dept in a.departments:
            dept_map.setdefault(dept, []).append({
                "name": a.name,
                "description": a.description,
                "skills": a.skills,
                "tools": a.tools,
            })

    result = []
    # Standard Six Ministries + Decision layer
    standard_depts = [
        ("decision", "决策层", "CEO/COO/PM 战略决策"),
        ("executive", "总经办", "执行协调"),
        ("engineering", "工部", "技术开发"),
        ("marketing", "礼部", "市场营销"),
        ("operations", "户部", "运营管理"),
        ("design", "刑部", "设计创作"),
        ("product", "吏部", "产品规划"),
        ("finance", "度支", "财务预算"),
        ("hr", "礼部", "人力资源"),
    ]
    for dept_id, dept_name, desc in standard_depts:
        agents_in = dept_map.get(dept_id, [])
        result.append({
            "id": dept_id,
            "name": dept_name,
            "description": desc,
            "agents_count": len(agents_in),
            "agents": agents_in,
        })

    # Add any departments from agents not in standard list
    for dept_id, agents_in in dept_map.items():
        if dept_id not in {d[0] for d in standard_depts}:
            result.append({
                "id": dept_id,
                "name": dept_id.title(),
                "description": f"{dept_id} department",
                "agents_count": len(agents_in),
                "agents": agents_in,
            })

    return result


@router.get("/{dept_id}")
async def get_department(dept_id: str) -> dict:
    """Get a single department by ID."""
    agents = agent_compiler.get_available_agents()
    dept_agents = [
        {"name": a.name, "description": a.description, "skills": a.skills}
        for a in agents
        if dept_id in a.departments
    ]
    if not dept_agents:
        from fastapi import HTTPException
        raise HTTPException(404, f"Department '{dept_id}' not found")
    return {"id": dept_id, "agents": dept_agents}
