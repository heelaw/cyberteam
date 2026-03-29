"""数据分析思维专家。

负责数据分析、指标监控、数据驱动决策等数据层面的思维注入。
"""

from typing import Any
from cyberteam.agent_runtime.base import ThinkingExpert, AgentMetadata


class DataExpert(ThinkingExpert):
    """数据分析思维专家

    提供数据分析、指标监控、数据驱动决策等思维框架。
    """

    def __init__(self):
        metadata = AgentMetadata(
            name="data_expert",
            description="数据分析思维专家：提供数据分析、指标监控、数据驱动决策等思维框架",
            version="1.0.0",
            tags=["数据", "分析", "指标", "洞察"],
            capabilities=[
                "数据分析方法",
                "指标体系设计",
                "数据可视化",
                "趋势预测",
                "洞察发现"
            ]
        )
        super().__init__(metadata, domain="data")
        self.add_framework("kpi")
        self.add_framework("data_dashboard")
        self.add_framework("statistical_analysis")

    async def _think_with_frameworks(self, input_data: Any) -> Any:
        """使用数据思维框架分析"""
        return {
            "expert": self.metadata.name,
            "domain": self.domain,
            "frameworks": self.thinking_frameworks,
            "analysis": input_data
        }

    async def execute(self, task: Any) -> Any:
        """执行数据分析任务"""
        return await self.think(task)
