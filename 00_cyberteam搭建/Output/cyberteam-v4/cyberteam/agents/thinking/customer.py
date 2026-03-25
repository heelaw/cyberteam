"""客户关系思维专家。

负责客户服务、客户满意度、客户忠诚度等客户层面的思维注入。
"""

from typing import Any
from cyberteam.agents.base import ThinkingExpert, AgentMetadata


class CustomerExpert(ThinkingExpert):
    """客户关系思维专家

    提供客户服务、客户满意度、客户忠诚度等思维框架。
    """

    def __init__(self):
        metadata = AgentMetadata(
            name="customer_expert",
            description="客户关系思维专家：提供客户服务、客户满意度、客户忠诚度等思维框架",
            version="1.0.0",
            tags=["客户", "服务", "满意度", "忠诚度"],
            capabilities=[
                "客户满意度分析",
                "客户旅程设计",
                "售后服务优化",
                "客户投诉处理",
                "客户忠诚度提升"
            ]
        )
        super().__init__(metadata, domain="customer")
        self.add_framework("csat")
        self.add_framework("nps")
        self.add_framework("customer_journey_map")

    async def _think_with_frameworks(self, input_data: Any) -> Any:
        """使用客户思维框架分析"""
        return {
            "expert": self.metadata.name,
            "domain": self.domain,
            "frameworks": self.thinking_frameworks,
            "analysis": input_data
        }

    async def execute(self, task: Any) -> Any:
        """执行客户分析任务"""
        return await self.think(task)
