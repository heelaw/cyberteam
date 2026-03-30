"""
技能管理 API

提供技能的 CRUD 接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.engine.skill_registry import Skill, SkillRegistry, skill_registry

router = APIRouter(prefix="/api/skills", tags=["skills"])


# === Request/Response Models ===

class CreateSkillRequest(BaseModel):
    """创建技能请求"""
    name: str
    description: str
    category: str
    prompt_template: str
    keywords: List[str] = []
    tools: List[str] = []


class SkillResponse(BaseModel):
    """技能响应"""
    id: str
    name: str
    description: str
    category: str
    keywords: List[str]
    tools: List[str]


def skill_to_response(skill: Skill) -> SkillResponse:
    """转换为响应模型"""
    return SkillResponse(
        id=skill.id,
        name=skill.name,
        description=skill.description,
        category=skill.category,
        keywords=skill.keywords,
        tools=skill.tools
    )


# === API Endpoints ===

@router.get("", response_model=List[SkillResponse])
async def list_skills():
    """列出所有技能"""
    skills = skill_registry.list_all()
    return [skill_to_response(s) for s in skills]


@router.get("/categories")
async def list_categories():
    """列出所有分类"""
    categories = set(s.category for s in skill_registry.list_all())
    return {"categories": list(categories)}


@router.get("/category/{category}", response_model=List[SkillResponse])
async def list_skills_by_category(category: str):
    """按分类列出技能"""
    skills = skill_registry.list_by_category(category)
    return [skill_to_response(s) for s in skills]


@router.get("/match", response_model=SkillResponse)
async def match_skill(task: str):
    """根据任务匹配最佳技能"""
    skill = skill_registry.find_best_match(task)
    if not skill:
        raise HTTPException(status_code=404, detail="No matching skill found")
    return skill_to_response(skill)


@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(skill_id: str):
    """获取技能详情"""
    skill = skill_registry.get(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill_to_response(skill)


@router.post("", response_model=SkillResponse)
async def create_skill(request: CreateSkillRequest):
    """创建技能"""
    import uuid
    skill = Skill(
        id=f"custom_{uuid.uuid4().hex[:8]}",
        name=request.name,
        description=request.description,
        category=request.category,
        prompt_template=request.prompt_template,
        keywords=request.keywords,
        tools=request.tools
    )
    skill_registry.register(skill)
    return skill_to_response(skill)


@router.post("/execute", response_model=dict)
async def execute_with_skill(task: str, skill_id: str = None):
    """使用指定技能执行任务"""
    # 找到最佳匹配的技能
    skill = skill_registry.get(skill_id) if skill_id else skill_registry.find_best_match(task)

    if not skill:
        # 使用默认
        prompt = f"请处理以下任务：\n\n{task}"
    else:
        prompt = skill.prompt_template.format(task=task)

    from app.integration.claude_cli import ClaudeCLI, ClaudeConfig
    cli = ClaudeCLI(ClaudeConfig(model="opus"))
    result = cli.run(prompt)

    return {
        "task": task,
        "skill_id": skill.id if skill else None,
        "skill_name": skill.name if skill else "default",
        "result": result
    }
