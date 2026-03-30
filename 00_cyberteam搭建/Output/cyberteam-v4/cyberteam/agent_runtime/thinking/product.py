"""产品思维专家。

负责产品规划、需求分析、用户体验设计等产品层面的思维注入。
"""

from typing import Any
from cyberteam.agent_runtime.base import ThinkingExpert, AgentMetadata


class ProductExpert(ThinkingExpert):
    """产品思维专家

    提供产品规划、需求分析、用户体验设计等思维框架。
    """

    def __init__(self):
        metadata = AgentMetadata(
            name="product_expert",
            description="产品思维专家：提供产品规划、需求分析、用户体验设计等思维框架",
            version="1.0.0",
            tags=["产品", "需求", "UX", "规划"],
            capabilities=[
                "用户画像分析",
                "需求优先级排序",
                "MVP设计",
                "产品路线图规划",
                "A/B测试设计"
            ]
        )
        super().__init__(metadata, domain="product")
        self.add_framework("user_persona")
        self.add_framework("moscow")
        self.add_framework("mvp")
        self.add_framework("aarrr")

    async def _think_with_frameworks(self, input_data: Any) -> Any:
        """使用产品思维框架分析"""
        return {
            "expert": self.metadata.name,
            "domain": self.domain,
            "frameworks": self.thinking_frameworks,
            "analysis": input_data
        }

    async def execute(self, task: Any) -> Any:
        """执行产品分析任务"""
        return await self.think(task)
