#!/usr/bin/env python3
"""
CyberTeam V4 - 专家辩论引擎 (Debate Engine)

支持多专家辩论，模拟真实会议室决策流程：
1. 参与专家选择
2. 观点陈述
3. 质疑与反驳
4. 收敛判断
5. 共识聚合
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import json


class DebateState(Enum):
    """辩论状态"""
    PREPARING = "preparing"      # 准备中
    IN_PROGRESS = "in_progress"  # 进行中
    CONVERGED = "converged"      # 已收敛
    DEADLOCKED = "deadlocked"    # 僵局
    COMPLETED = "completed"      # 完成


class RoundType(Enum):
    """辩论轮次类型"""
    OPENING = "opening"         # 开场陈述
    ARGUMENT = "argument"        # 观点陈述
    COUNTER = "counter"          # 质疑反驳
    SYNTHESIS = "synthesis"      # 综合意见
    FINAL = "final"             # 最终结论


@dataclass
class ExpertOpinion:
    """专家观点"""
    expert_id: str
    expert_name: str
    framework: str
    opinion: str
    confidence: float = 0.8
    concerns: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class DebateRound:
    """辩论轮次"""
    round_id: int
    round_type: RoundType
    speaker: str  # 发言专家ID
    content: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class DebateSession:
    """辩论会话"""
    session_id: str
    task_id: str
    topic: str
    participants: list[str]  # 专家ID列表
    state: DebateState
    current_round: int = 0
    max_rounds: int = 5
    convergence_score: float = 0.0
    threshold: float = 0.3  # 收敛阈值
    rounds: list[DebateRound] = field(default_factory=list)
    opinions: list[ExpertOpinion] = field(default_factory=list)
    final_consensus: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class DebateEngine:
    """专家辩论引擎"""

    # 专家框架定义
    EXPERT_PROMPTS = {
        "kahneman": {
            "name": "卡尼曼决策专家",
            "role": "从风险决策、损失厌恶角度分析",
            "focus": ["概率偏差", "风险评估", "损失厌恶"]
        },
        "first_principle": {
            "name": "第一性原理专家",
            "role": "回归事物本质，从基本假设出发",
            "focus": ["本质问题", "基本假设", "创新突破"]
        },
        "six_hats": {
            "name": "六顶思考帽专家",
            "role": "全面分析，避免思维盲点",
            "focus": ["多角度", "全面评估", "风险识别"]
        },
        "swot_tows": {
            "name": "SWOT+TOWS专家",
            "role": "战略规划与竞争分析",
            "focus": ["竞争优势", "战略选择", "机会威胁"]
        },
        "five_why": {
            "name": "5Why根因分析专家",
            "role": "深入挖掘问题根本原因",
            "focus": ["根因分析", "问题本质", "因果链"]
        },
        "mckinsey": {
            "name": "麦肯锡方法专家",
            "role": "结构化分析，MECE原则",
            "focus": ["结构化", "逻辑分析", "框架应用"]
        },
        "reverse_thinking": {
            "name": "逆向思维专家",
            "role": "风险预判与漏洞发现",
            "focus": ["风险预判", "漏洞识别", "失败模式"]
        },
        "grow": {
            "name": "GROW模型专家",
            "role": "目标设定与达成路径",
            "focus": ["目标明确", "路径规划", "行动方案"]
        }
    }

    def __init__(self):
        self.sessions: dict[str, DebateSession] = {}

    def create_session(
        self,
        task_id: str,
        topic: str,
        expert_ids: list[str],
        max_rounds: int = 5,
        threshold: float = 0.3
    ) -> DebateSession:
        """创建辩论会话"""
        session_id = str(uuid.uuid4())

        session = DebateSession(
            session_id=session_id,
            task_id=task_id,
            topic=topic,
            participants=expert_ids,
            state=DebateState.PREPARING,
            max_rounds=max_rounds,
            threshold=threshold
        )

        self.sessions[session_id] = session
        return session

    def start_debate(self, session_id: str) -> DebateSession:
        """开始辩论"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        session.state = DebateState.IN_PROGRESS
        session.current_round = 1

        # 添加开场轮次
        opening = DebateRound(
            round_id=0,
            round_type=RoundType.OPENING,
            speaker="system",
            content=f"话题讨论：{session.topic}\n参与专家：{', '.join([self.EXPERT_PROMPTS.get(e, {}).get('name', e) for e in session.participants])}"
        )
        session.rounds.append(opening)

        return session

    def add_opinion(
        self,
        session_id: str,
        expert_id: str,
        opinion: str,
        concerns: list[str] = None,
        suggestions: list[str] = None
    ) -> ExpertOpinion:
        """添加专家观点"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        expert_info = self.EXPERT_PROMPTS.get(expert_id, {})

        expert_opinion = ExpertOpinion(
            expert_id=expert_id,
            expert_name=expert_info.get("name", expert_id),
            framework=expert_info.get("role", ""),
            opinion=opinion,
            concerns=concerns or [],
            suggestions=suggestions or []
        )

        session.opinions.append(expert_opinion)

        # 添加辩论轮次
        round_type = RoundType.ARGUMENT if len(session.opinions) <= len(session.participants) else RoundType.COUNTER
        debate_round = DebateRound(
            round_id=len(session.rounds),
            round_type=round_type,
            speaker=expert_id,
            content=opinion
        )
        session.rounds.append(debate_round)
        session.updated_at = datetime.utcnow().isoformat()

        return expert_opinion

    def check_convergence(self, session_id: str) -> dict[str, Any]:
        """检查收敛状态"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        if len(session.opinions) < 2:
            return {"converged": False, "score": 0.0, "reason": "观点不足"}

        # 简化收敛判断：基于建议的重叠度
        all_suggestions = []
        for opinion in session.opinions:
            all_suggestions.extend(opinion.suggestions)

        # 简单的相似度计算
        unique_suggestions = set(all_suggestions)
        overlap_score = 1.0 - (len(unique_suggestions) / max(len(all_suggestions), 1))

        session.convergence_score = overlap_score
        converged = overlap_score >= session.threshold

        if converged:
            session.state = DebateState.CONVERGED

        return {
            "converged": converged,
            "score": overlap_score,
            "threshold": session.threshold,
            "opinion_count": len(session.opinions)
        }

    def generate_synthesis(self, session_id: str) -> str:
        """生成综合意见"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        # 按专家聚合观点
        synthesis_parts = ["## 综合分析\n"]

        for opinion in session.opinions:
            synthesis_parts.append(f"### {opinion.expert_name}\n")
            synthesis_parts.append(f"- 观点: {opinion.opinion}\n")
            if opinion.concerns:
                synthesis_parts.append(f"- 顾虑: {', '.join(opinion.concerns)}\n")
            if opinion.suggestions:
                synthesis_parts.append(f"- 建议: {', '.join(opinion.suggestions)}\n")
            synthesis_parts.append("\n")

        # 添加共识部分
        synthesis_parts.append("### 共识建议\n")
        all_suggestions = []
        for opinion in session.opinions:
            all_suggestions.extend(opinion.suggestions)

        # 统计建议出现频率
        from collections import Counter
        suggestion_counts = Counter(all_suggestions)
        top_suggestions = suggestion_counts.most_common(3)

        for suggestion, count in top_suggestions:
            synthesis_parts.append(f"- {suggestion} (支持: {count}/{len(session.opinions)})\n")

        session.final_consensus = "".join(synthesis_parts)
        session.state = DebateState.COMPLETED

        # 添加最终轮次
        final_round = DebateRound(
            round_id=len(session.rounds),
            round_type=RoundType.FINAL,
            speaker="system",
            content=session.final_consensus
        )
        session.rounds.append(final_round)

        return session.final_consensus

    def get_session(self, session_id: str) -> Optional[DebateSession]:
        """获取会话"""
        return self.sessions.get(session_id)

    def get_session_status(self, session_id: str) -> dict[str, Any]:
        """获取会话状态"""
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}

        return {
            "session_id": session.session_id,
            "task_id": session.task_id,
            "topic": session.topic,
            "state": session.state.value,
            "current_round": session.current_round,
            "max_rounds": session.max_rounds,
            "participants": session.participants,
            "opinion_count": len(session.opinions),
            "convergence_score": session.convergence_score,
            "has_consensus": session.final_consensus is not None
        }


def main():
    """CLI 测试"""
    engine = DebateEngine()

    # 创建辩论
    session = engine.create_session(
        task_id="test-task-001",
        topic="如何提升用户留存率？",
        expert_ids=["kahneman", "first_principle", "swot_tows"],
        max_rounds=3
    )

    print(f"创建辩论会话: {session.session_id}")
    print(f"话题: {session.topic}")
    print(f"参与专家: {session.participants}")
    print()

    # 开始辩论
    engine.start_debate(session.session_id)
    print("=== 辩论开始 ===\n")

    # 添加观点
    engine.add_opinion(
        session.session_id,
        "kahneman",
        "从损失厌恶角度，用户留存关键在于降低切换成本，提供渐进式价值回报。",
        concerns=["用户可能对短期激励免疫"],
        suggestions=["设计成长体系", "渐进式奖励"]
    )

    engine.add_opinion(
        session.session_id,
        "first_principle",
        "回归本质：留存是因为产品解决了用户核心问题。",
        concerns=["可能忽视竞争对手"],
        suggestions=["聚焦核心价值", "减少干扰功能"]
    )

    engine.add_opinion(
        session.session_id,
        "swot_tows",
        "从SWOT分析，机会在于SO策略（利用优势抓住机会）。",
        concerns=["需要资源投入"],
        suggestions=["精准投放", "口碑传播"]
    )

    print("=== 收敛检查 ===")
    result = engine.check_convergence(session.session_id)
    print(f"收敛状态: {result}")
    print()

    # 生成综合
    print("=== 生成综合意见 ===")
    synthesis = engine.generate_synthesis(session.session_id)
    print(synthesis[:500] + "...")


if __name__ == "__main__":
    main()
