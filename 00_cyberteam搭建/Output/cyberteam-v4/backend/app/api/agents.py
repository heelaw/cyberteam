"""Agents API — Agent 信息管理。"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db

log = logging.getLogger("cyberteam.api.agents")
router = APIRouter()


# ── 14个思维专家定义 ──

EXPERT_FRAMEWORKS = {
    "kahneman": {
        "name": "卡尼曼决策专家",
        "framework": " Kahneman 前景理论",
        "description": "从风险决策、损失厌恶、概率偏差角度分析",
        "keywords": ["选择", "风险", "决策", "偏差", "概率"],
    },
    "first_principle": {
        "name": "第一性原理专家",
        "framework": " First Principles Thinking",
        "description": "从基本假设出发，回归事物本质",
        "keywords": ["创新", "突破", "从零开始", "本质"],
    },
    "six_hats": {
        "name": "六顶思考帽专家",
        "framework": " De Bono 六顶思考帽",
        "description": "全面分析，避免思维盲点",
        "keywords": ["全面", "分析", "避免盲点", "多角度"],
    },
    "swot_tows": {
        "name": "SWOT+TOWS专家",
        "framework": " SWOT + TOWS 矩阵",
        "description": "战略规划与竞争分析",
        "keywords": ["战略", "竞争", "优势", "劣势", "机会", "威胁"],
    },
    "five_why": {
        "name": "5Why根因分析专家",
        "framework": " 5Why 分析法",
        "description": "深入挖掘问题根本原因",
        "keywords": ["根因", "挖掘", "为什么", "本质问题"],
    },
    "goldlin": {
        "name": "吉德林法则专家",
        "framework": " 吉德林法则",
        "description": "明确问题动机和目的",
        "keywords": ["动机", "目的", "驱动", "核心目标"],
    },
    "grow": {
        "name": "GROW模型专家",
        "framework": " GROW 目标达成模型",
        "description": "目标设定与达成路径",
        "keywords": ["目标", "达成", "路径", " coaching"],
    },
    "kiss": {
        "name": "KISS复盘专家",
        "framework": " KISS 复盘法",
        "description": "简化方案，避免过度复杂",
        "keywords": ["简化", "复盘", "优化", "精简"],
    },
    "mckinsey": {
        "name": "麦肯锡方法专家",
        "framework": " McKinsey 结构化分析",
        "description": "逻辑严谨的结构化分析",
        "keywords": ["结构化", "逻辑", "分析", "框架"],
    },
    "porter_five_forces": {
        "name": "波特五力专家",
        "framework": " Porter 五力模型",
        "description": "行业竞争结构与护城河分析",
        "keywords": ["行业", "竞争", "护城河", "供应商", "买家"],
    },
    "reverse_thinking": {
        "name": "逆向思维专家",
        "framework": " 逆向思维",
        "description": "风险预判与漏洞发现",
        "keywords": ["风险", "预判", "漏洞", "失败", "反向"],
    },
    "mckinsey_7s": {
        "name": "McKinsey 7S专家",
        "framework": " McKinsey 7S 模型",
        "description": "组织能力诊断",
        "keywords": ["组织", "能力", "战略", "系统", "风格"],
    },
    "wbs": {
        "name": "WBS任务分解专家",
        "framework": " WBS 工作分解结构",
        "description": "执行计划制定",
        "keywords": ["分解", "任务", "计划", "执行", "子任务"],
    },
    "kotter_change": {
        "name": "Kotter变革专家",
        "framework": " Kotter 变革管理",
        "description": "变革推动与阻力克服",
        "keywords": ["变革", "阻力", "推动", "实施"],
    },
}


# ── 6个执行部门定义 ──

DEPARTMENTS = {
    "product": {
        "name": "产品部",
        "description": "需求分析、产品设计、功能规划",
        "responsibility": "产品规划与设计",
    },
    "engineering": {
        "name": "技术部",
        "description": "技术方案、架构设计、开发实现",
        "responsibility": "技术实现",
    },
    "design": {
        "name": "设计部",
        "description": "UI设计、用户体验、品牌视觉",
        "responsibility": "设计创作",
    },
    "operations": {
        "name": "运营部",
        "description": "用户增长、内容运营、活动策划",
        "responsibility": "运营策略",
    },
    "finance": {
        "name": "财务部",
        "description": "预算规划、成本控制、投资分析",
        "responsibility": "财务规划",
    },
    "hr": {
        "name": "人力部",
        "description": "招聘方案、团队激励、文化建设",
        "responsibility": "人力资源",
    },
}


# ── Schemas ──

class AgentOut(BaseModel):
    """Agent 信息输出。"""
    agent_id: str
    name: str
    type: str  # expert | department
    framework: str | None = None
    description: str
    keywords: list[str] | None = None


# ── Endpoints ──

@router.get("")
async def list_agents(
    agent_type: str | None = Query(None, description="过滤类型: expert/department"),
    db: AsyncSession = Depends(get_db),
):
    """获取所有 Agent 列表。"""
    agents = []

    if agent_type is None or agent_type == "expert":
        for expert_id, info in EXPERT_FRAMEWORKS.items():
            agents.append({
                "agent_id": expert_id,
                "name": info["name"],
                "type": "expert",
                "framework": info["framework"],
                "description": info["description"],
                "keywords": info["keywords"],
            })

    if agent_type is None or agent_type == "department":
        for dept_id, info in DEPARTMENTS.items():
            agents.append({
                "agent_id": dept_id,
                "name": info["name"],
                "type": "department",
                "framework": None,
                "description": info["description"],
                "responsibility": info["responsibility"],
            })

    return {"agents": agents, "total": len(agents)}


@router.get("/{agent_id}")
async def get_agent(agent_id: str):
    """获取指定 Agent 信息。"""
    if agent_id in EXPERT_FRAMEWORKS:
        info = EXPERT_FRAMEWORKS[agent_id]
        return {
            "agent_id": agent_id,
            "name": info["name"],
            "type": "expert",
            "framework": info["framework"],
            "description": info["description"],
            "keywords": info["keywords"],
        }

    if agent_id in DEPARTMENTS:
        info = DEPARTMENTS[agent_id]
        return {
            "agent_id": agent_id,
            "name": info["name"],
            "type": "department",
            "description": info["description"],
            "responsibility": info["responsibility"],
        }

    raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")