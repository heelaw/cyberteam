"""UserOpsAgent - 用户运营专家。

负责：
- RFM模型分析
- 用户生命周期管理
- AARRR漏斗优化
- 用户分层运营
- 留存提升策略

继承v3运营资产用户运营Agent知识。
"""

from typing import Any, Dict, List, Optional

from cyberteam.agent_runtime.base import SpecializedAgent, AgentMetadata
from skills.third_party.growth import UserGrowthSkill


class UserOpsAgent(SpecializedAgent):
    """用户运营专家 Agent

    负责用户全生命周期运营：
    1. RFM模型：Recency/Frequency/Monetary分析
    2. 用户生命周期：引入→成长→成熟→衰退→流失
    3. AARRR漏斗：获取→激活→留存→变现→推荐
    4. 用户分层：高低价值/潜力/流失风险/沉默用户
    5. 留存提升：次留率<40%预警

    健康标准：
    - LTV/CAC > 3
    - 次留率 > 40%
    - 激活率 > 30%
    """

    def __init__(self):
        metadata = AgentMetadata(
            name="UserOpsAgent",
            description="用户运营专家：RFM模型+用户生命周期+AARRR漏斗+分层运营",
            version="1.0.0",
            tags=["growth", "user", "operations", "retention"],
            capabilities=[
                "RFM分析",
                "生命周期管理",
                "AARRR优化",
                "用户分层",
                "留存提升",
                "DAU/MAU监控",
            ],
        )
        super().__init__(metadata)

        # 引用用户增长Skill
        self.user_growth_skill = UserGrowthSkill()

        # 用户分层定义
        self.user_segments = {
            "高价值用户": {"特征": "高RFM", "策略": "VIP服务"},
            "潜力用户": {"特征": "高F高M低R", "策略": "促活召回"},
            "流失风险用户": {"特征": "低R中F中M", "策略": "预警干预"},
            "沉默用户": {"特征": "低R低F低M", "策略": "流失定义"},
        }

        # 健康度标准
        self.health_standards = {
            "ltv_cac": "> 3 健康",
            "retention_d1": "> 40% 预警线",
            "activation_rate": "> 30% 预警线",
        }

    def _do_initialize(self) -> None:
        """初始化用户运营"""
        pass

    async def _specialized_think(self, input_data: Any) -> Any:
        """用户运营的专业思考"""
        context = input_data if isinstance(input_data, dict) else {"task": input_data}
        action = context.get("action", "strategy")

        if action == "rfm":
            return await self._rfm_analysis(context)
        elif action == "lifecycle":
            return await self._lifecycle_management(context)
        elif action == "aarrr":
            return await self._aarrr_funnel(context)
        else:
            return await self._user_growth_strategy(context)

    async def _rfm_analysis(self, context: Dict) -> Dict[str, Any]:
        """RFM分析"""
        result = await self.user_growth_skill.execute(None, {"action": "rfm", **context})
        return {
            "agent": self.metadata.name,
            "mode": "rfm_analysis",
            "result": result,
            "segments": self.user_segments,
        }

    async def _lifecycle_management(self, context: Dict) -> Dict[str, Any]:
        """用户生命周期管理"""
        result = await self.user_growth_skill.execute(None, {"action": "lifecycle", **context})
        return {
            "agent": self.metadata.name,
            "mode": "lifecycle_management",
            "result": result,
            "stages": ["引入期", "成长期", "成熟期", "衰退期", "流失期"],
        }

    async def _aarrr_funnel(self, context: Dict) -> Dict[str, Any]:
        """AARRR漏斗分析"""
        result = await self.user_growth_skill.execute(None, {"action": "aarrr", **context})
        return {
            "agent": self.metadata.name,
            "mode": "aarrr_funnel",
            "result": result,
            "health_standards": self.health_standards,
        }

    async def _user_growth_strategy(self, context: Dict) -> Dict[str, Any]:
        """用户增长策略"""
        result = await self.user_growth_skill.execute(None, {"action": "strategy", **context})
        return {
            "agent": self.metadata.name,
            "mode": "user_growth_strategy",
            "result": result,
            "principle": "先留存再拉新",
        }

    async def execute(self, task: Any) -> Any:
        """执行用户运营任务"""
        return await self.think(task)
