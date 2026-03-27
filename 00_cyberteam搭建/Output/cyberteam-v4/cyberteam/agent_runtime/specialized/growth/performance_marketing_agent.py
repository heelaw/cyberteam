"""PerformanceMarketingAgent - 效果营销专家。

负责：
- oCPM/oCPA投放
- ROI优化（>1.5及格，>3优秀）
- LTV/CAC分析（>3健康）
- 账户三层结构
- 转化漏斗优化

继承v3运营资产渠道推广Agent知识。
"""

from typing import Any, Dict, List, Optional

from cyberteam.agent_runtime.base import SpecializedAgent, AgentMetadata
from cyberteam.skills.growth import PerformanceMarketingSkill


class PerformanceMarketingAgent(SpecializedAgent):
    """效果营销专家 Agent

    负责效果营销全链路：
    1. 出价策略：
       - oCPM：按千次曝光优化
       - oCPA：按转化出价（优先）
    2. ROI标准：
       - 及格线：ROI > 1.5
       - 优秀线：ROI > 3.0
    3. LTV/CAC健康标准：
       - LTV/CAC > 3 健康
       - LTV/CAC < 3 预警
    4. 账户三层结构：
       - Campaign层：按目标划分
       - AdSet层：按人群定向
       - Ad层：按素材创意
    5. 转化漏斗：曝光→点击→访问→转化→付费
    """

    def __init__(self):
        metadata = AgentMetadata(
            name="PerformanceMarketingAgent",
            description="效果营销专家：oCPA投放+ROI优化+LTV/CAC+账户结构+转化漏斗",
            version="1.0.0",
            tags=["growth", "marketing", "performance", "ocpa", "roi"],
            capabilities=[
                "投放策略",
                "ROI优化",
                "LTV/CAC分析",
                "账户结构优化",
                "转化率提升",
            ],
        )
        super().__init__(metadata)

        # 引用效果营销Skill
        self.performance_marketing_skill = PerformanceMarketingSkill()

        # ROI标准
        self.roi_standards = {"及格": 1.5, "优秀": 3.0}
        self.ltv_cac_standard = 3.0

        # 漏斗阶段
        self.funnel_stages = ["曝光", "点击", "访问", "转化", "付费"]

    def _do_initialize(self) -> None:
        """初始化效果营销"""
        pass

    async def _specialized_think(self, input_data: Any) -> Any:
        """效果营销的专业思考"""
        context = input_data if isinstance(input_data, dict) else {"task": input_data}

        result = await self.performance_marketing_skill.execute(None, context)

        return {
            "agent": self.metadata.name,
            "mode": "performance_marketing",
            "result": result,
            "roi_standards": self.roi_standards,
            "ltv_cac_standard": self.ltv_cac_standard,
            "funnel_stages": self.funnel_stages,
        }

    async def optimize_campaign(self, campaign_data: Dict) -> Dict[str, Any]:
        """优化投放方案"""
        current_roi = campaign_data.get("roi", 0)
        ltv_cac = campaign_data.get("ltv_cac", 0)

        recommendations = []

        # ROI诊断
        if current_roi < 1.5:
            recommendations.append("ROI低于及格线，建议优化转化路径或暂停投放")
        elif current_roi < 3:
            recommendations.append("ROI达到及格线，持续优化向优秀线努力")
        else:
            recommendations.append("ROI优秀，保持当前策略适度放量")

        # LTV/CAC诊断
        if ltv_cac < 3:
            recommendations.append("LTV/CAC低于健康线，需提升用户价值或降低获客成本")
        else:
            recommendations.append("LTV/CAC健康，可适度加大投放")

        return {
            "agent": self.metadata.name,
            "current_roi": current_roi,
            "current_ltv_cac": ltv_cac,
            "recommendations": recommendations,
            "next_action": "A/B测试素材，人群定向优化",
        }

    def analyze_funnel(self, funnel_data: Dict) -> Dict[str, Any]:
        """分析漏斗"""
        stages = self.funnel_stages
        rates = []

        for i in range(len(stages) - 1):
            from_count = funnel_data.get(stages[i], 0)
            to_count = funnel_data.get(stages[i + 1], 0)
            if from_count > 0:
                rate = (to_count / from_count) * 100
                rates.append(f"{stages[i]}→{stages[i+1]}: {rate:.1f}%")
            else:
                rates.append(f"{stages[i]}→{stages[i+1]}: N/A")

        # 找出最大流失点
        max_loss_point = "待分析"
        if len(funnel_data) > 1:
            loss_rates = []
            for i in range(len(stages) - 1):
                from_count = funnel_data.get(stages[i], 1)
                to_count = funnel_data.get(stages[i + 1], 0)
                loss_rates.append((stages[i], (from_count - to_count) / from_count * 100))
            if loss_rates:
                max_loss_point = max(loss_rates, key=lambda x: x[1])[0]

        return {
            "agent": self.metadata.name,
            "funnel_rates": rates,
            "max_loss_point": max_loss_point,
            "recommendation": f"优先优化{max_loss_point}环节",
        }

    async def execute(self, task: Any) -> Any:
        """执行效果营销任务"""
        return await self.think(task)
