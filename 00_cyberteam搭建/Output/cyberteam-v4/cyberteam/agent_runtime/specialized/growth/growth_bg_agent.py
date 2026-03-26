"""GrowthBGAgent - 增长事业群总指挥。

增长BG总指挥，负责：
- 战略规划与目标设定
- 团队管理与协调
- 跨部门资源调配
- KPI监控与追踪
- 战役/专家/单兵三种作战模式调度

继承v3运营资产的8轮Q&A业务灵魂。
"""

from typing import Any, Dict, List, Optional

from cyberteam.agent_runtime.base import SpecializedAgent, AgentMetadata
from skills.third_party.growth import (
    ReportingFrameworkSkill,
    TimeManagementSkill,
    ProgressTrackingSkill,
    RetrospectiveSkill,
    StrategyPlanningSkill,
    TeamManagementSkill,
)


class GrowthBGAgent(SpecializedAgent):
    """增长事业群总指挥 Agent

    增长BG总指挥是增长事业群的决策中枢，负责：
    1. 战略规划：北极星指标→增长模型→策略地图→执行计划
    2. 团队管理：战役/专家/单兵三种作战模式
    3. KPI监控：北极星+健康度+实验效能
    4. 跨部门协调：产品/技术/市场的协同

    增长理念（8轮Q&A注入）：
    - 先留存再拉新
    - 数据+实验驱动
    - 模型驱动
    - 80/20聚焦
    """

    def __init__(self):
        metadata = AgentMetadata(
            name="GrowthBGAgent",
            description="增长事业群总指挥：负责战略规划、团队管理、跨部门协调、KPI监控",
            version="1.0.0",
            tags=["growth", "bg", "leader", "strategy"],
            capabilities=[
                "战略规划",
                "团队管理",
                "跨部门协调",
                "KPI监控",
                "资源调配",
                "战役调度",
            ],
        )
        super().__init__(metadata)

        # 引用知识层的Skills
        self.skills = {
            "汇报框架": ReportingFrameworkSkill(),
            "时间管理": TimeManagementSkill(),
            "进度管理": ProgressTrackingSkill(),
            "复盘模板": RetrospectiveSkill(),
            "策略规划": StrategyPlanningSkill(),
            "团队管理": TeamManagementSkill(),
        }

        # 增长理念（8轮Q&A灵魂注入）
        self.growth_principles = {
            "retention_first": "先留存再拉新，LTV/CAC > 3",
            "data_driven": "数据+实验驱动，Everything is Test",
            "model_driven": "模型驱动，流程化复制",
            "focus_8020": "80/20聚焦，资源投入高回报点",
        }

        # KPI体系
        self.kpi_system = {
            "north_star": "北极星指标（最终价值）",
            "health_metrics": "增长健康度（LTV/CAC/留存）",
            "experiment_efficiency": "实验效能（数量×转化×速度）",
        }

        # 三种作战模式
        self.battle_modes = {
            "campaign": "战役模式：大促/品牌活动",
            "expert": "专家模式：专题深度",
            "solo": "单兵模式：快速响应",
        }

    def _do_initialize(self) -> None:
        """初始化增长BG总指挥"""
        pass

    async def _specialized_think(self, input_data: Any) -> Any:
        """增长BG的战略思考"""
        task = input_data if isinstance(input_data, str) else input_data.get("task", "")
        context = input_data if isinstance(input_data, dict) else {}

        # 确定作战模式
        battle_mode = self._determine_battle_mode(task, context)

        # 构建思考结果
        return {
            "agent": self.metadata.name,
            "mode": "growth_bg_strategy",
            "task": task,
            "battle_mode": battle_mode,
            "principles": self.growth_principles,
            "kpi_system": self.kpi_system,
            "skills_available": list(self.skills.keys()),
        }

    def _determine_battle_mode(self, task: str, context: Dict) -> str:
        """确定作战模式"""
        task_lower = task.lower()

        if any(k in task_lower for k in ["大促", "品牌", "活动", "campaign"]):
            return "campaign"
        elif any(k in task_lower for k in ["专家", "深度", "专题"]):
            return "expert"
        else:
            return "solo"

    async def execute(self, task: Any) -> Any:
        """执行增长BG任务"""
        result = await self.think(task)

        # 根据battle_mode分发任务
        battle_mode = result.get("battle_mode", "solo")

        if battle_mode == "campaign":
            result["dispatch"] = "战役模式：组建临时项目组，集中资源攻坚"
        elif battle_mode == "expert":
            result["dispatch"] = "专家模式：指定专家深度负责"
        else:
            result["dispatch"] = "单兵模式：快速响应，即时交付"

        return result

    async def plan_strategy(self, objective: str) -> Dict[str, Any]:
        """策略规划"""
        strategy_skill = self.skills["策略规划"]
        return await strategy_skill.execute(objective)

    async def report(self, task: str) -> Dict[str, Any]:
        """汇报"""
        report_skill = self.skills["汇报框架"]
        return await report_skill.execute(task)

    async def retrospective(self, context: Dict) -> Dict[str, Any]:
        """复盘"""
        retro_skill = self.skills["复盘模板"]
        return await retro_skill.execute(None, context)
