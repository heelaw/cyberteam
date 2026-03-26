"""人力资源思维专家。

负责人才招聘、团队管理、组织发展等人力资源层面的思维注入。
"""

from typing import Any
from cyberteam.agent_runtime.base import ThinkingExpert, AgentMetadata


class HumanResourcesExpert(ThinkingExpert):
    """人力资源思维专家

    提供人才招聘、团队管理、组织发展等思维框架。
    """

    def __init__(self):
        metadata = AgentMetadata(
            name="human_resources_expert",
            description="人力资源思维专家：提供人才招聘、团队管理、组织发展等思维框架",
            version="1.0.0",
            tags=["HR", "人才", "团队", "组织"],
            capabilities=[
                "人才招聘策略",
                "团队管理方法",
                "组织架构设计",
                "绩效管理",
                "培训发展"
            ]
        )
        super().__init__(metadata, domain="human_resources")
        self.add_framework("org_design")
        self.add_framework("performance_management")
        self.add_framework("talent_development")

    async def _think_with_frameworks(self, input_data: Any) -> Any:
        """使用HR思维框架分析"""
        return {
            "expert": self.metadata.name,
            "domain": self.domain,
            "frameworks": self.thinking_frameworks,
            "analysis": input_data
        }

    async def execute(self, task: Any) -> Any:
        """执行HR分析任务"""
        return await self.think(task)
