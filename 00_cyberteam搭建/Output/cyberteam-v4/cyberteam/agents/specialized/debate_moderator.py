"""Debate Moderator 专业 Agent。

负责主持辩论，评估各方观点，生成裁决。
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from cyberteam.agents.base import SpecializedAgent, AgentMetadata


@dataclass
class DebatePosition:
    """辩论立场"""
    agent_name: str
    position: str
    arguments: List[str]
    strength: float  # 0-1
    weaknesses: List[str]


class DebateModerator(SpecializedAgent):
    """Debate Moderator - 辩论主持人

    负责主持辩论，评估各方观点，生成裁决。
    """

    def __init__(self):
        metadata = AgentMetadata(
            name="debate_moderator",
            description="Debate Moderator：主持辩论，评估观点，生成裁决",
            version="1.0.0",
            tags=["辩论", "评估", "裁决", "观点"],
            capabilities=[
                "论点评估",
                "逻辑分析",
                "偏见检测",
                "裁决生成",
                "总结陈述"
            ]
        )
        super().__init__(metadata)
        self.positions: List[DebatePosition] = []

    def _do_initialize(self) -> None:
        """初始化辩论主持人"""
        pass

    async def _specialized_think(self, input_data: Any) -> Any:
        """评估辩论观点"""
        return {
            "moderator": self.metadata.name,
            "mode": "debate_moderation",
            "input": input_data
        }

    async def execute(self, task: Any) -> Any:
        """执行辩论主持任务"""
        result = await self.think(task)
        return result

    def add_position(self, position: DebatePosition) -> None:
        """添加辩论立场"""
        self.positions.append(position)

    def clear_positions(self) -> None:
        """清除所有立场"""
        self.positions.clear()

    async def moderate(self, topic: str) -> Dict[str, Any]:
        """主持辩论"""
        if not self.positions:
            return {
                "topic": topic,
                "status": "no_positions",
                "verdict": None
            }

        # 简单评估逻辑
        total_strength = sum(p.strength for p in self.positions)
        avg_strength = total_strength / len(self.positions) if self.positions else 0

        strongest = max(self.positions, key=lambda p: p.strength) if self.positions else None

        return {
            "topic": topic,
            "positions_count": len(self.positions),
            "average_strength": avg_strength,
            "strongest_position": strongest.agent_name if strongest else None,
            "verdict": self._generate_verdict(strongest)
        }

    def _generate_verdict(self, winner: Optional[DebatePosition]) -> str:
        """生成裁决"""
        if winner:
            return f"{winner.agent_name} 的观点最具说服力"
        return "未能形成明确裁决"
