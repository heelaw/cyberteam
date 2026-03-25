"""GrowthMarketingAgent - 增长营销专家。

负责：
- 四象限渠道模型（规模×ROI）
- Lookalike人群扩展
- 杠铃策略（80%验证+20%测试）
- U型归因
- 渠道优化

继承v3运营资产渠道推广Agent知识。
"""

from typing import Any, Dict, List, Optional

from cyberteam.agents.base import SpecializedAgent, AgentMetadata
from cyberteam.skills.growth import GrowthMarketingSkill


class GrowthMarketingAgent(SpecializedAgent):
    """增长营销专家 Agent

    负责增长营销全链路：
    1. 四象限渠道模型：
       - 高ROI高量：重点投入
       - 高ROI低量：培育优化
       - 低ROI高量：谨慎控制
       - 低ROI低量：淘汰测试
    2. 杠铃策略：
       - 80%资源：已验证渠道
       - 20%资源：测试新渠道
    3. Lookalike人群扩展
    4. U型归因：首触40% + 末触40% + 中间20%
    """

    def __init__(self):
        metadata = AgentMetadata(
            name="GrowthMarketingAgent",
            description="增长营销专家：四象限渠道模型+Lookalike人群+杠铃策略+U型归因",
            version="1.0.0",
            tags=["growth", "marketing", "channel", "lookalike", "归因"],
            capabilities=[
                "渠道规划",
                "人群扩展",
                "ROI优化",
                "归因分析",
                "预算分配",
            ],
        )
        super().__init__(metadata)

        # 引用增长营销Skill
        self.growth_marketing_skill = GrowthMarketingSkill()

        # 渠道矩阵
        self.channel_matrix = {
            "高ROI高量": "重点投入，追求规模",
            "高ROI低量": "培育优化，提升规模",
            "低ROI高量": "谨慎控制，优化ROI",
            "低ROI低量": "淘汰测试，止损",
        }

    def _do_initialize(self) -> None:
        """初始化增长营销"""
        pass

    async def _specialized_think(self, input_data: Any) -> Any:
        """增长营销的专业思考"""
        context = input_data if isinstance(input_data, dict) else {"task": input_data}

        result = await self.growth_marketing_skill.execute(None, context)

        return {
            "agent": self.metadata.name,
            "mode": "growth_marketing",
            "result": result,
            "channel_matrix": self.channel_matrix,
            "batting_strategy": {"验证渠道": "80%", "测试渠道": "20%"},
            "attribution": "U型归因（首触40%+末触40%+中间20%）",
        }

    async def plan_channel_investment(self, channels: List[Dict]) -> Dict[str, Any]:
        """规划渠道投入"""
        # 按ROI和规模分类
        investment_plan = {}
        for channel in channels:
            name = channel.get("name", "")
            roi = channel.get("roi", 0)
            volume = channel.get("volume", 0)

            if roi > 2 and volume > 10000:
                quadrant = "高ROI高量"
            elif roi > 2 and volume <= 10000:
                quadrant = "高ROI低量"
            elif roi <= 2 and volume > 10000:
                quadrant = "低ROI高量"
            else:
                quadrant = "低ROI低量"

            investment_plan[name] = {
                "quadrant": quadrant,
                "strategy": self.channel_matrix[quadrant],
                "recommended_investment": self._calculate_investment(quadrant, channel),
            }

        return {
            "agent": self.metadata.name,
            "investment_plan": investment_plan,
            "batting_strategy": "80%验证 + 20%测试",
        }

    def _calculate_investment(self, quadrant: str, channel: Dict) -> str:
        """计算建议投入"""
        base = channel.get("current_investment", 1000)
        if quadrant == "高ROI高量":
            return f"+50% (建议{base * 1.5})"
        elif quadrant == "高ROI低量":
            return f"+20% (建议{base * 1.2})"
        elif quadrant == "低ROI高量":
            return f"-30% (建议{base * 0.7})"
        else:
            return f"-100% (建议{0})"

    async def execute(self, task: Any) -> Any:
        """执行增长营销任务"""
        return await self.think(task)
