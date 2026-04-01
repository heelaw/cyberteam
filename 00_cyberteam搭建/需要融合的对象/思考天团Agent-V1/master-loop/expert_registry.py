#!/usr/bin/env python3
"""
专家注册表 - 14个思维专家的路由配置
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


class ExpertCategory(Enum):
    """专家分类"""
    DECISION = "决策"
    ANALYSIS = "分析"
    CREATIVE = "创意"
    EXECUTION = "执行"
    MANAGEMENT = "管理"


@dataclass
class Expert:
    """专家定义"""
    id: str
    name: str
    name_cn: str
    category: ExpertCategory
    triggers: List[str]
    skills: List[str]
    description: str
    agent_path: str


EXPERT_REGISTRY: Dict[str, Expert] = {
    "kahneman": Expert(
        id="kahneman", name="Kahneman", name_cn="卡尼曼",
        category=ExpertCategory.DECISION,
        triggers=["选择", "风险", "纠结", "决策", "判断"],
        skills=["认知偏差识别", "噪声评估", "决策辅助"],
        description="决策心理学专家",
        agent_path="agents/kahneman/AGENT.md"
    ),
    "first-principle": Expert(
        id="first-principle", name="FirstPrinciple", name_cn="第一性原理",
        category=ExpertCategory.CREATIVE,
        triggers=["创新", "颠覆", "从零开始", "本质"],
        skills=["本质分析", "假设挑战", "创新重构"],
        description="第一性原理专家",
        agent_path="agents/first-principle/AGENT.md"
    ),
    "swot-tows": Expert(
        id="swot-tows", name="SWOTTOWS", name_cn="SWOT分析",
        category=ExpertCategory.ANALYSIS,
        triggers=["战略", "竞争", "优势", "劣势", "机会", "威胁"],
        skills=["SWOT分析", "TOWS策略", "战略规划"],
        description="战略分析专家",
        agent_path="agents/swot-tows/AGENT.md"
    ),
    "fivewhy": Expert(
        id="fivewhy", name="FiveWhy", name_cn="5Why分析",
        category=ExpertCategory.ANALYSIS,
        triggers=["为什么", "原因", "追问", "溯源"],
        skills=["根因分析", "连续追问", "问题溯源"],
        description="5Why分析专家",
        agent_path="agents/fivewhy/AGENT.md"
    ),
    "ai-board": Expert(
        id="ai-board", name="AIBoard", name_cn="AI私董会",
        category=ExpertCategory.DECISION,
        triggers=["投资", "商业决策", "董事会"],
        skills=["投资分析", "商业模式评估", "风险评估"],
        description="AI私董会",
        agent_path="agents/ai-board/AGENT.md"
    ),
}


class ExpertRouter:
    def route(self, query: str) -> List[Expert]:
        query_lower = query.lower()
        scores = {}
        for expert_id, expert in EXPERT_REGISTRY.items():
            score = sum(10 for t in expert.triggers if t.lower() in query_lower)
            if score > 0:
                scores[expert_id] = score
        sorted_experts = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [EXPERT_REGISTRY[eid] for eid, _ in sorted_experts]

    def get_expert_by_id(self, expert_id: str) -> Optional[Expert]:
        return EXPERT_REGISTRY.get(expert_id)


router = ExpertRouter()
