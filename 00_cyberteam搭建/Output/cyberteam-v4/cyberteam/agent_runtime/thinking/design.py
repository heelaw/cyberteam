"""设计思维专家。

负责视觉设计、品牌形象、UI/UX设计等设计层面的思维注入。
"""

from typing import Any
from cyberteam.agent_runtime.base import ThinkingExpert, AgentMetadata


class DesignExpert(ThinkingExpert):
    """设计思维专家

    提供视觉设计、品牌形象、UI/UX设计等思维框架。
    """

    def __init__(self):
        metadata = AgentMetadata(
            name="design_expert",
            description="设计思维专家：提供视觉设计、品牌形象、UI/UX设计等思维框架",
            version="1.0.0",
            tags=["设计", "品牌", "UI", "UX", "视觉"],
            capabilities=[
                "品牌视觉设计",
                "UI界面设计",
                "用户体验设计",
                "设计系统构建",
                "设计规范制定"
            ]
        )
        super().__init__(metadata, domain="design")
        self.add_framework("design_system")
        self.add_framework("brand_identity")
        self.add_framework("ux_research")

    async def _think_with_frameworks(self, input_data: Any) -> Any:
        """使用设计思维框架分析"""
        return {
            "expert": self.metadata.name,
            "domain": self.domain,
            "frameworks": self.thinking_frameworks,
            "analysis": input_data
        }

    async def execute(self, task: Any) -> Any:
        """执行设计分析任务"""
        return await self.think(task)
