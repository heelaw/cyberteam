"""Skills API endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.engine.thinking_injector import thinking_injector, ThinkingMode

router = APIRouter()


class ThinkingExpertResponse(BaseModel):
    """Thinking expert information."""
    name: str
    mode: str
    description: str
    questions: list[str]
    process: str
    department: str


class SkillInfoResponse(BaseModel):
    """Skill information response."""
    name: str
    category: str
    description: str
    triggers: list[str]
    workflow: str


@router.get("/thinking")
async def list_thinking_experts() -> list[ThinkingExpertResponse]:
    """List all available thinking experts."""
    experts = thinking_injector.list_modes()
    result = []
    for mode in experts:
        expert = thinking_injector.get_expert(mode)
        if expert:
            result.append(ThinkingExpertResponse(
                name=expert.name,
                mode=expert.mode.value,
                description=expert.description,
                questions=expert.questions,
                process=expert.process,
                department=expert.department,
            ))
    return result


@router.get("/thinking/{mode}", response_model=ThinkingExpertResponse)
async def get_thinking_expert(mode: str) -> ThinkingExpertResponse:
    """Get a specific thinking expert by mode."""
    try:
        thinking_mode = ThinkingMode(mode)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Thinking mode '{mode}' not found")

    expert = thinking_injector.get_expert(thinking_mode)
    if not expert:
        raise HTTPException(status_code=404, detail=f"Thinking expert '{mode}' not found")

    return ThinkingExpertResponse(
        name=expert.name,
        mode=expert.mode.value,
        description=expert.description,
        questions=expert.questions,
        process=expert.process,
        department=expert.department,
    )


@router.post("/thinking/{mode}/inject")
async def inject_thinking(
    mode: str,
    agent_name: str,
    context: Optional[dict] = None,
) -> dict:
    """Inject a thinking mode into an agent and return the enhanced prompt."""
    try:
        thinking_mode = ThinkingMode(mode)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Thinking mode '{mode}' not found")

    injection = thinking_injector.inject(agent_name, thinking_mode, context)

    return {
        "agent_name": agent_name,
        "mode": mode,
        "injection": injection,
    }


@router.get("")
async def list_skills(
    department: Optional[str] = None,
) -> list[SkillInfoResponse]:
    """List available skills, optionally filtered by department."""
    # Placeholder - in real implementation, would scan skills directories
    skills = [
        SkillInfoResponse(
            name="内容创作",
            category="marketing",
            description="创建各类营销内容",
            triggers=["需要写文案", "创作内容"],
            workflow="需求分析 → 素材收集 → 创作 → 审核",
        ),
        SkillInfoResponse(
            name="数据分析",
            category="analytics",
            description="分析业务数据",
            triggers=["分析数据", "数据报告"],
            workflow="数据收集 → 清洗 → 分析 → 可视化",
        ),
        SkillInfoResponse(
            name="项目管理",
            category="management",
            description="管理项目进度",
            triggers=["项目管理", "跟踪进度"],
            workflow="立项 → 计划 → 执行 → 复盘",
        ),
    ]

    if department:
        skills = [s for s in skills if s.category == department]

    return skills


@router.get("/{skill_name}")
async def get_skill(skill_name: str) -> SkillInfoResponse:
    """Get details of a specific skill."""
    # Placeholder implementation
    skills_map = {
        "内容创作": SkillInfoResponse(
            name="内容创作",
            category="marketing",
            description="创建各类营销内容",
            triggers=["需要写文案", "创作内容"],
            workflow="需求分析 → 素材收集 → 创作 → 审核",
        ),
        "数据分析": SkillInfoResponse(
            name="数据分析",
            category="analytics",
            description="分析业务数据",
            triggers=["分析数据", "数据报告"],
            workflow="数据收集 → 清洗 → 分析 → 可视化",
        ),
        "项目管理": SkillInfoResponse(
            name="项目管理",
            category="management",
            description="管理项目进度",
            triggers=["项目管理", "跟踪进度"],
            workflow="立项 → 计划 → 执行 → 复盘",
        ),
    }

    if skill_name not in skills_map:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")

    return skills_map[skill_name]
