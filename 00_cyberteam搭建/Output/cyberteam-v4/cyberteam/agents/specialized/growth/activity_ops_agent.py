"""ActivityOpsAgent - 活动运营专家。

负责：
- 四类活动运营（引流/促活/转化/品牌）
- 八步闭环法
- 活动ROI标准
- 风控+熔断机制
- 大促策划

继承v3运营资产活动策划Agent知识。
"""

from typing import Any, Dict, List, Optional

from cyberteam.agents.base import SpecializedAgent, AgentMetadata
from cyberteam.skills.growth import ActivityOperationsSkill


class ActivityOpsAgent(SpecializedAgent):
    """活动运营专家 Agent

    负责活动运营全链路：
    1. 四类活动：
       - 引流型：拉新获客，CAC < 平均30%
       - 促活型：活跃用户，参与率提升
       - 转化型：付费变现，ROI > 3
       - 品牌型：心智占领，品牌指数提升
    2. 八步闭环法：目标对齐→创意策划→方案评审→项目排期→预热造势→上线执行→收尾交付→深度复盘
    3. ROI三级标准：
       - 引流型：CAC效率
       - 促活型：参与率
       - 转化型：ROI > 3
    4. 风控+熔断机制
    """

    def __init__(self):
        metadata = AgentMetadata(
            name="ActivityOpsAgent",
            description="活动运营专家：四类活动+八步闭环+ROI标准+风控熔断",
            version="1.0.0",
            tags=["growth", "activity", "operations", "campaign", "促销"],
            capabilities=[
                "活动策划",
                "引流获客",
                "促活运营",
                "转化提升",
                "品牌建设",
                "ROI追踪",
            ],
        )
        super().__init__(metadata)

        # 引用活动运营Skill
        self.activity_ops_skill = ActivityOperationsSkill()

        # ROI标准
        self.roi_standards = {
            "引流型": {"metric": "CAC", "standard": "< 平均CAC的30%"},
            "促活型": {"metric": "参与率", "standard": "参与率提升20%+"},
            "转化型": {"metric": "ROI", "standard": "> 3"},
            "品牌型": {"metric": "品牌指数", "standard": "指数提升15%+"},
        }

        # 风控等级
        self.risk_levels = {
            "green": "正常活动",
            "yellow": "预警，需要关注",
            "red": "熔断，立即停止",
        }

    def _do_initialize(self) -> None:
        """初始化活动运营"""
        pass

    async def _specialized_think(self, input_data: Any) -> Any:
        """活动运营的专业思考"""
        context = input_data if isinstance(input_data, dict) else {"task": input_data}
        activity_type = context.get("type", "promotion")

        result = await self.activity_ops_skill.execute(None, context)

        return {
            "agent": self.metadata.name,
            "mode": "activity_operations",
            "activity_type": activity_type,
            "result": result,
            "roi_standards": self.roi_standards,
            "eight_steps": [
                "目标对齐",
                "创意策划",
                "方案评审",
                "项目排期",
                "预热造势",
                "上线执行",
                "收尾交付",
                "深度复盘",
            ],
        }

    async def plan_campaign(self, campaign_type: str, objective: str) -> Dict[str, Any]:
        """策划活动"""
        result = await self.activity_ops_skill.execute(None, {"type": campaign_type})

        return {
            "campaign_type": campaign_type,
            "objective": objective,
            "activity_plan": result,
            "roi_target": self.roi_standards.get(campaign_type, {}),
            "eight_step_process": result.get("eight_step_process", []),
        }

    def assess_risk(self, current_data: Dict) -> str:
        """评估活动风险"""
        roi = current_data.get("roi", 0)
        participation = current_data.get("participation_rate", 0)

        if roi < 0.5 or participation < 5:
            return self.risk_levels["red"]
        elif roi < 1.5 or participation < 15:
            return self.risk_levels["yellow"]
        return self.risk_levels["green"]

    async def execute(self, task: Any) -> Any:
        """执行活动运营任务"""
        return await self.think(task)
