"""法务思维专家。

负责合同审核、知识产权、法律风险等法务层面的思维注入。
"""

from typing import Any
from cyberteam.agents.base import ThinkingExpert, AgentMetadata


class LegalExpert(ThinkingExpert):
    """法务思维专家

    提供合同审核、知识产权、法律风险等思维框架。
    """

    def __init__(self):
        metadata = AgentMetadata(
            name="legal_expert",
            description="法务思维专家：提供合同审核、知识产权、法律风险等思维框架",
            version="1.0.0",
            tags=["法务", "合同", "知识产权", "合规"],
            capabilities=[
                "合同审核",
                "知识产权保护",
                "法律风险识别",
                "合规性审查",
                "纠纷处理"
            ]
        )
        super().__init__(metadata, domain="legal")
        self.add_framework("contract_review")
        self.add_framework("ip_protection")
        self.add_framework("risk_legal")

    async def _think_with_frameworks(self, input_data: Any) -> Any:
        """使用法务思维框架分析"""
        return {
            "expert": self.metadata.name,
            "domain": self.domain,
            "frameworks": self.thinking_frameworks,
            "analysis": input_data
        }

    async def execute(self, task: Any) -> Any:
        """执行法务分析任务"""
        return await self.think(task)
