"""Experts API — 意图识别与专家路由。"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db

log = logging.getLogger("cyberteam.api.experts")
router = APIRouter()


# ── 关键词到专家的映射 ──

KEYWORD_EXPERT_MAP = {
    # kahneman
    "选择": ["kahneman"], "风险": ["kahneman"], "决策": ["kahneman"],
    "偏差": ["kahneman"], "概率": ["kahneman"], "收益": ["kahneman"],
    "损失": ["kahneman"], "确定性": ["kahneman"],

    # first_principle
    "创新": ["first_principle"], "突破": ["first_principle"],
    "从零开始": ["first_principle"], "本质": ["first_principle"],
    "根本": ["first_principle"], "重新": ["first_principle"],

    # six_hats
    "全面": ["six_hats"], "分析": ["six_hats"], "盲点": ["six_hats"],
    "多角度": ["six_hats"], "考虑": ["six_hats"],

    # swot_tows
    "战略": ["swot_tows"], "竞争": ["swot_tows"], "优势": ["swot_tows"],
    "劣势": ["swot_tows"], "机会": ["swot_tows"], "威胁": ["swot_tows"],
    "市场": ["swot_tows"], "定位": ["swot_tows"],

    # five_why
    "根因": ["five_why"], "挖掘": ["five_why"], "为什么": ["five_why"],
    "原因": ["five_why"], "问题": ["five_why"],

    # goldlin
    "动机": ["goldlin"], "目的": ["goldlin"], "驱动": ["goldlin"],
    "目标": ["goldlin"], "意图": ["goldlin"],

    # grow
    "达成": ["grow"], "路径": ["grow"], "规划": ["grow"],
    "成长": ["grow"], "发展": ["grow"],

    # kiss
    "简化": ["kiss"], "复盘": ["kiss"], "优化": ["kiss"],
    "精简": ["kiss"], "效率": ["kiss"],

    # mckinsey
    "结构化": ["mckinsey"], "逻辑": ["mckinsey"], "框架": ["mckinsey"],
    "分析": ["mckinsey"], "方法": ["mckinsey"],

    # porter_five_forces
    "行业": ["porter_five_forces"], "护城河": ["porter_five_forces"],
    "供应商": ["porter_five_forces"], "替代": ["porter_five_forces"],
    "进入壁垒": ["porter_five_forces"],

    # reverse_thinking
    "风险": ["reverse_thinking"], "预判": ["reverse_thinking"],
    "漏洞": ["reverse_thinking"], "失败": ["reverse_thinking"],
    "问题": ["reverse_thinking"],

    # mckinsey_7s
    "组织": ["mckinsey_7s"], "能力": ["mckinsey_7s"],
    "系统": ["mckinsey_7s"], "风格": ["mckinsey_7s"],

    # wbs
    "分解": ["wbs"], "任务": ["wbs"], "计划": ["wbs"],
    "执行": ["wbs"], "子任务": ["wbs"], "里程碑": ["wbs"],

    # kotter_change
    "变革": ["kotter_change"], "阻力": ["kotter_change"],
    "推动": ["kotter_change"], "实施": ["kotter_change"],
    "改变": ["kotter_change"],
}

# 默认触发专家（当没有匹配时）
DEFAULT_EXPERTS = [
    "kahneman", "first_principle", "six_hats", "mckinsey",
    "swot_tows", "wbs", "reverse_thinking", "grow"
]


# ── Schemas ──

class IntentClassifyRequest(BaseModel):
    """意图分类请求。"""
    user_input: str = Field(..., description="用户输入")


class IntentClassifyResponse(BaseModel):
    """意图分类响应。"""
    experts: list[str] = Field(..., description="推荐触发的专家列表")
    confidence: float = Field(..., description="置信度")
    keywords: list[str] = Field(..., description="识别的关键词")


class ExpertRouteRequest(BaseModel):
    """专家路由请求。"""
    task_id: str = Field(..., description="任务ID")
    experts: list[str] = Field(..., description="专家列表")


class ExpertRouteResponse(BaseModel):
    """专家路由响应。"""
    task_id: str
    expert_tasks: list[dict] = Field(..., description="专家任务列表")


# ── Helper Functions ──

def classify_intent(user_input: str) -> tuple[list[str], float, list[str]]:
    """意图分类：识别用户输入中的关键信息，匹配专家。

    Returns:
        (experts, confidence, keywords): 专家列表、置信度、关键词列表
    """
    # 简单分词（按空格和标点）
    import re
    words = re.split(r'[,\s，。！？、：；]+', user_input.lower())

    # 统计匹配的专家
    expert_counts: dict[str, int] = {}
    detected_keywords: list[str] = []

    for word in words:
        if not word:
            continue
        for keyword, experts in KEYWORD_EXPERT_MAP.items():
            if keyword in word or word in keyword:
                detected_keywords.append(keyword)
                for expert in experts:
                    expert_counts[expert] = expert_counts.get(expert, 0) + 1

    # 按匹配次数排序，取前8个专家
    if expert_counts:
        sorted_experts = sorted(expert_counts.items(), key=lambda x: x[1], reverse=True)
        selected_experts = [e[0] for e in sorted_experts[:8]]
        confidence = min(0.9, 0.5 + len(detected_keywords) * 0.05)
    else:
        # 使用默认专家
        selected_experts = DEFAULT_EXPERTS.copy()
        confidence = 0.3

    return selected_experts, confidence, list(set(detected_keywords))


# ── Endpoints ──

@router.post("/classify", response_model=IntentClassifyResponse)
async def classify_intent_endpoint(
    body: IntentClassifyRequest,
):
    """意图分类：分析用户输入，推荐触发的专家。"""
    experts, confidence, keywords = classify_intent(body.user_input)

    log.info(f"Intent classified: {len(experts)} experts, confidence={confidence:.2f}")

    return IntentClassifyResponse(
        experts=experts,
        confidence=confidence,
        keywords=keywords,
    )


@router.post("/route")
async def route_experts(
    body: ExpertRouteRequest,
    db: AsyncSession = Depends(get_db),
):
    """专家路由：为每个专家创建任务规范。"""
    from ..models import Task, TaskState
    from sqlalchemy import select

    # 验证任务存在
    stmt = select(Task).filter(Task.task_id == body.task_id)
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 为每个专家创建任务规范
    expert_tasks = []
    for i, expert_id in enumerate(body.experts):
        expert_tasks.append({
            "expert_id": expert_id,
            "order": i + 1,
            "status": "pending",
        })

    log.info(f"Experts routed: task={body.task_id}, experts={body.experts}")

    return ExpertRouteResponse(
        task_id=body.task_id,
        expert_tasks=expert_tasks,
    )


@router.get("/{expert_id}/info")
async def get_expert_info(expert_id: str):
    """获取专家信息。"""
    from .agents import EXPERT_FRAMEWORKS

    if expert_id not in EXPERT_FRAMEWORKS:
        raise HTTPException(status_code=404, detail=f"Expert not found: {expert_id}")

    info = EXPERT_FRAMEWORKS[expert_id]
    return {
        "expert_id": expert_id,
        "name": info["name"],
        "framework": info["framework"],
        "description": info["description"],
        "keywords": info["keywords"],
    }