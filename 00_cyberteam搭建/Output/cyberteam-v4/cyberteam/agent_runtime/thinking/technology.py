"""技术思维专家。

负责技术架构、系统设计、技术选型等技术层面的思维注入。
"""

from typing import Any
from cyberteam.agent_runtime.base import ThinkingExpert, AgentMetadata


class TechnologyExpert(ThinkingExpert):
    """技术思维专家

    提供技术架构、系统设计、技术选型等思维框架。
    """

    def __init__(self):
        metadata = AgentMetadata(
            name="technology_expert",
            description="技术思维专家：提供技术架构、系统设计、技术选型等思维框架",
            version="1.0.0",
            tags=["技术", "架构", "系统", "设计"],
            capabilities=[
                "系统架构设计",
                "技术选型评估",
                "性能优化分析",
                "安全性评估",
                "可扩展性设计"
            ]
        )
        super().__init__(metadata, domain="technology")
        self.add_framework("system_design")
        self.add_framework("tech_stack")
        self.add_framework("microservices")

    async def _think_with_frameworks(self, input_data: Any) -> Any:
        """使用技术思维框架分析"""
        return {
            "expert": self.metadata.name,
            "domain": self.domain,
            "frameworks": self.thinking_frameworks,
            "analysis": input_data
        }

    async def execute(self, task: Any) -> Any:
        """执行技术分析任务"""
        return await self.think(task)
