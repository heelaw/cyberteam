"""战略思维专家。

负责企业战略规划、竞争分析、商业模式设计等战略层面的思维注入。
"""

from typing import Any
from cyberteam.agent_runtime.base import ThinkingExpert, AgentMetadata


class StrategyExpert(ThinkingExpert):
    """战略思维专家

    提供战略规划、竞争分析、商业模式创新等思维框架。
    """

    def __init__(self):
        metadata = AgentMetadata(
            name="strategy_expert",
            description="战略思维专家：提供战略规划、竞争分析、商业模式设计等思维框架",
            version="1.0.0",
            tags=["战略", "商业", "竞争", "规划"],
            capabilities=[
                "SWOT/TOWS分析",
                "商业模式画布",
                "五力模型分析",
                "战略路径规划",
                "竞争格局分析"
            ]
        )
        super().__init__(metadata, domain="strategy")
        self.add_framework("swot_tows")
        self.add_framework("business_model_canvas")
        self.add_framework("five_forces")

    async def _think_with_frameworks(self, input_data: Any) -> Any:
        """使用战略思维框架分析"""
        return {
            "expert": self.metadata.name,
            "domain": self.domain,
            "frameworks": self.thinking_frameworks,
            "analysis": input_data
        }

    async def execute(self, task: Any) -> Any:
        """执行战略分析任务"""
        return await self.think(task)
