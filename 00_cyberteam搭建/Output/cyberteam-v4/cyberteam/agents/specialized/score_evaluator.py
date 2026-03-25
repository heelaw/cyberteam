"""Score Evaluator 专业 Agent。

负责评估和打分，输出量化的评估结果。
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from cyberteam.agents.base import SpecializedAgent, AgentMetadata


@dataclass
class ScoreItem:
    """评分项"""
    criterion: str
    score: float  # 0-10
    weight: float  # 权重
    comment: str = ""


class ScoreEvaluator(SpecializedAgent):
    """Score Evaluator - 评分评估器

    负责评估和打分，输出量化的评估结果。
    """

    def __init__(self):
        metadata = AgentMetadata(
            name="score_evaluator",
            description="Score Evaluator：评估和打分，输出量化评估结果",
            version="1.0.0",
            tags=["评估", "打分", "评分", "量化"],
            capabilities=[
                "多维度评估",
                "加权评分",
                "排名比较",
                "趋势分析",
                "报告生成"
            ]
        )
        super().__init__(metadata)
        self.items: List[ScoreItem] = []

    def _do_initialize(self) -> None:
        """初始化评分器"""
        pass

    async def _specialized_think(self, input_data: Any) -> Any:
        """执行评分逻辑"""
        return {
            "evaluator": self.metadata.name,
            "mode": "scoring",
            "input": input_data
        }

    async def execute(self, task: Any) -> Any:
        """执行评估任务"""
        result = await self.think(task)
        return result

    def add_item(self, criterion: str, score: float, weight: float = 1.0, comment: str = "") -> None:
        """添加评分项"""
        if 0 <= score <= 10:
            self.items.append(ScoreItem(criterion, score, weight, comment))

    def clear_items(self) -> None:
        """清除所有评分项"""
        self.items.clear()

    async def evaluate(self, subject: str) -> Dict[str, Any]:
        """执行评估"""
        if not self.items:
            return {
                "subject": subject,
                "status": "no_items",
                "final_score": None
            }

        total_weighted_score = sum(item.score * item.weight for item in self.items)
        total_weight = sum(item.weight for item in self.items)
        final_score = total_weighted_score / total_weight if total_weight > 0 else 0

        return {
            "subject": subject,
            "items": [
                {
                    "criterion": item.criterion,
                    "score": item.score,
                    "weight": item.weight,
                    "comment": item.comment
                }
                for item in self.items
            ],
            "total_weighted_score": total_weighted_score,
            "total_weight": total_weight,
            "final_score": round(final_score, 2),
            "grade": self._get_grade(final_score)
        }

    @staticmethod
    def _get_grade(score: float) -> str:
        """根据分数获取等级"""
        if score >= 9:
            return "A+"
        elif score >= 8:
            return "A"
        elif score >= 7:
            return "B+"
        elif score >= 6:
            return "B"
        elif score >= 5:
            return "C"
        else:
            return "D"
