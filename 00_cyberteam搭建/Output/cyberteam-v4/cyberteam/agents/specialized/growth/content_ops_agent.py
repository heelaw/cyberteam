"""ContentOpsAgent - 内容运营专家。

负责：
- PGC+UGC+AIGC内容配比
- 选题三叉模型（热点30%+用户30%+数据40%）
- 内容分类（流量型/粘性型/转化型）
- 爆款内容策划
- 内容矩阵规划

继承v3运营资产内容运营Agent知识。
"""

from typing import Any, Dict, List, Optional

from cyberteam.agents.base import SpecializedAgent, AgentMetadata
from cyberteam.skills.growth import ContentOperationsSkill


class ContentOpsAgent(SpecializedAgent):
    """内容运营专家 Agent

    负责内容运营全链路：
    1. 内容配比：PGC(60%) + UGC(30%) + AIGC(10%)
    2. 选题模型：热点30% + 用户30% + 数据40%
    3. 内容分类：
       - 流量型：引流获客
       - 粘性型：促活留存
       - 转化型：付费变现
    4. 阶段配比：
       - 初期：70%粘性 + 30%转化
       - 增长：50%流量 + 30%粘性 + 20%转化
       - 成熟：30%流量 + 40%粘性 + 30%转化

    爆款逻辑：
    - 情绪触发：恐惧/愤怒/惊讶
    - 社交货币：分享动机
    - 实用价值：干货技能
    """

    def __init__(self):
        metadata = AgentMetadata(
            name="ContentOpsAgent",
            description="内容运营专家：PGC+UGC+AIGC配比+选题三叉模型+内容分类运营",
            version="1.0.0",
            tags=["growth", "content", "operations", "pugc", "选题"],
            capabilities=[
                "内容配比规划",
                "选题策划",
                "爆款创作",
                "内容矩阵",
                "数据复盘",
            ],
        )
        super().__init__(metadata)

        # 引用内容运营Skill
        self.content_ops_skill = ContentOperationsSkill()

        # 爆款元素
        self.viral_elements = {
            "情绪触发": ["恐惧", "愤怒", "惊讶", "感动", "好笑"],
            "社交货币": ["身份认同", "利他分享", "话题谈资"],
            "实用价值": ["技能干货", "资源福利", "方法论"],
        }

    def _do_initialize(self) -> None:
        """初始化内容运营"""
        pass

    async def _specialized_think(self, input_data: Any) -> Any:
        """内容运营的专业思考"""
        context = input_data if isinstance(input_data, dict) else {"task": input_data}
        stage = context.get("stage", "growth")

        result = await self.content_ops_skill.execute(None, context)

        return {
            "agent": self.metadata.name,
            "mode": "content_operations",
            "stage": stage,
            "result": result,
            "viral_elements": self.viral_elements,
        }

    async def plan_content_matrix(self, business_stage: str) -> Dict[str, Any]:
        """规划内容矩阵"""
        result = await self.content_ops_skill.execute(None, {"stage": business_stage})
        return {
            "content_matrix": result,
            "stage": business_stage,
            "recommendations": self._get_content_recommendations(business_stage),
        }

    def _get_content_recommendations(self, stage: str) -> List[str]:
        """获取内容建议"""
        recommendations = {
            "initial": [
                "聚焦粘性型内容，建立用户认知",
                "减少流量型投入，专注产品价值传递",
                "转化型内容测试为主，小规模尝试",
            ],
            "growth": [
                "加大流量型投入，快速扩大用户池",
                "保持粘性型内容稳定输出",
                "增加转化型内容，配合增长活动",
            ],
            "mature": [
                "流量型内容降本增效",
                "粘性型内容为主，提升用户忠诚度",
                "转化型内容精细化运营",
            ],
        }
        return recommendations.get(stage, recommendations["growth"])

    async def execute(self, task: Any) -> Any:
        """执行内容运营任务"""
        return await self.think(task)
