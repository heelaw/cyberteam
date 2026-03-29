"""财务思维专家。

负责财务分析、投资决策、成本控制等财务层面的思维注入。
"""

from typing import Any
from cyberteam.agent_runtime.base import ThinkingExpert, AgentMetadata


class FinanceExpert(ThinkingExpert):
    """财务思维专家

    提供财务分析、投资决策、成本控制等思维框架。
    """

    def __init__(self):
        metadata = AgentMetadata(
            name="finance_expert",
            description="财务思维专家：提供财务分析、投资决策、成本控制等思维框架",
            version="1.0.0",
            tags=["财务", "投资", "成本", "收益"],
            capabilities=[
                "财务分析",
                "投资回报分析",
                "成本效益分析",
                "预算规划",
                "风险评估"
            ]
        )
        super().__init__(metadata, domain="finance")
        self.add_framework("roi")
        self.add_framework("npv")
        self.add_framework("break_even")

    async def _think_with_frameworks(self, input_data: Any) -> Any:
        """使用财务思维框架分析"""
        return {
            "expert": self.metadata.name,
            "domain": self.domain,
            "frameworks": self.thinking_frameworks,
            "analysis": input_data
        }

    async def execute(self, task: Any) -> Any:
        """执行财务分析任务"""
        return await self.think(task)
