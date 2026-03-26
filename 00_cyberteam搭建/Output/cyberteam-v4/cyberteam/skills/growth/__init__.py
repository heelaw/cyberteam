"""Growth Skills - 增长技能集.

提供增长相关的 Skills：
- 用户增长策略 (UserGrowthSkill)
- 内容运营策略 (ContentOperationsSkill)
- 活动运营策略 (ActivityOperationsSkill)
- 增长营销策略 (GrowthMarketingSkill)
- 品牌营销策略 (BrandMarketingSkill)
- 效果营销策略 (PerformanceMarketingSkill)
- 团队管理策略 (TeamManagementSkill)
- 策略规划 (StrategyPlanningSkill)
- 汇报框架 (ReportingFrameworkSkill)
- 时间管理 (TimeManagementSkill)
- 进度管理 (ProgressTrackingSkill)
- 复盘 (RetrospectiveSkill)
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class SkillMetadata:
    """Skill 元数据"""
    name: str
    description: str
    tags: list
    triggers: list


class BaseSkill:
    """Skill 基类"""
    def __init__(self, metadata: SkillMetadata):
        self.metadata = metadata

    def initialize(self):
        """初始化 Skill"""
        pass

    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """执行 Skill"""
        raise NotImplementedError


class ReportingFrameworkSkill(BaseSkill):
    """汇报框架 Skill - 结构化向上沟通"""

    def __init__(self):
        metadata = SkillMetadata(
            name="汇报框架",
            description="结构化向上沟通：背景→问题→方案→请求",
            tags=["growth", "management", "communication"],
            triggers=["周报", "月报", "汇报", "述职"]
        )
        super().__init__(metadata)

    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        task = input_data if isinstance(input_data, str) else (context.get("task", "") if context else "")
        return {
            "skill": "汇报框架",
            "elevator_pitch": f"[30秒] 核心问题：{task}",
            "template": "背景→问题→方案→请求",
            "principles": ["结论先行", "数据支撑", "方案导向", "简洁有力"]
        }


class TimeManagementSkill(BaseSkill):
    """时间管理 Skill - 优先级四象限"""

    def __init__(self):
        metadata = SkillMetadata(
            name="时间管理",
            description="优先级四象限：重要紧急/重要不紧急/紧急不重要/不紧急不重要",
            tags=["growth", "management", "efficiency"],
            triggers=["时间管理", "优先级", "日程"]
        )
        super().__init__(metadata)

    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        tasks = context.get("tasks", []) if context else []
        q1, q2, q3, q4 = [], [], [], []
        for task in tasks:
            imp = task.get("importance", 5)
            urg = task.get("urgency", 5)
            if imp >= 4 and urg >= 4:
                q1.append(task)
            elif imp >= 4:
                q2.append(task)
            elif urg >= 4:
                q3.append(task)
            else:
                q4.append(task)
        return {
            "skill": "时间管理",
            "Q1_重要紧急": q1,
            "Q2_重要不紧急": q2,
            "Q3_紧急不重要": q3,
            "Q4_不紧急不重要": q4,
            "recommendation": "优先Q1，合理Q2，控制Q3，委托/删除Q4"
        }


class ProgressTrackingSkill(BaseSkill):
    """进度管理 Skill - 甘特图+里程碑追踪"""

    def __init__(self):
        metadata = SkillMetadata(
            name="进度管理",
            description="甘特图+里程碑追踪，确保项目按时交付",
            tags=["growth", "management", "tracking"],
            triggers=["进度", "项目管理", "里程碑", "甘特图"]
        )
        super().__init__(metadata)

    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        project = context or {}
        milestones = project.get("milestones", [])
        progress = project.get("progress", 0)
        return {
            "skill": "进度管理",
            "current_progress": progress,
            "upcoming_milestones": [m for m in milestones if not m.get("completed")],
            "status": "正常" if progress >= 50 else "滞后预警"
        }


class RetrospectiveSkill(BaseSkill):
    """复盘 Skill - 目标达成+数据+问题+行动"""

    def __init__(self):
        metadata = SkillMetadata(
            name="复盘模板",
            description="目标达成+数据+问题+行动四步法",
            tags=["growth", "management", "learning"],
            triggers=["复盘", "总结", "反思"]
        )
        super().__init__(metadata)

    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        retro = context or {}
        return {
            "skill": "复盘模板",
            "step1_目标达成": retro.get("objectives", ""),
            "step2_数据分析": retro.get("data", ""),
            "step3_问题分析": retro.get("problems", ""),
            "step4_行动计划": retro.get("actions", ""),
            "template": "目标→数据→问题→行动"
        }


class UserGrowthSkill(BaseSkill):
    """用户增长 Skill - RFM+生命周期+AARRR"""

    def __init__(self):
        metadata = SkillMetadata(
            name="用户增长",
            description="RFM模型+用户生命周期管理+AARRR漏斗",
            tags=["growth", "user", "operations"],
            triggers=["用户增长", "DAU", "MAU", "拉新", "激活", "留存"]
        )
        super().__init__(metadata)

    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        action = context.get("action", "strategy") if context else "strategy"
        if action == "rfm":
            return self._rfm()
        elif action == "lifecycle":
            return self._lifecycle()
        elif action == "aarrr":
            return self._aarrr()
        return {"skill": "用户增长", "focus": "先留存再拉新"}

    def _rfm(self):
        return {
            "recency": "最近消费时间",
            "frequency": "消费频率",
            "monetary": "消费金额",
            "segments": ["高价值", "潜力", "流失风险", "沉默"]
        }

    def _lifecycle(self):
        return {
            "stages": ["引入期", "成长期", "成熟期", "衰退期", "流失期"],
            "metrics": ["激活率", "留存率", "复购率", "LTV"]
        }

    def _aarrr(self):
        return {
            "Acquisition": "渠道获客",
            "Activation": "首活体验",
            "Retention": "持续价值",
            "Referral": "社交裂变",
            "Revenue": "付费转化"
        }


class ContentOperationsSkill(BaseSkill):
    """内容运营 Skill - PGC+UGC+AIGC"""

    def __init__(self):
        metadata = SkillMetadata(
            name="内容运营",
            description="PGC+UGC+AIGC配比；选题三叉模型",
            tags=["growth", "content", "operations"],
            triggers=["内容运营", "选题", "PGC", "UGC", "AIGC"]
        )
        super().__init__(metadata)

    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        stage = context.get("stage", "growth") if context else "growth"
        if stage == "initial":
            allocation = {"粘性型": "70%", "转化型": "30%", "流量型": "0%"}
        elif stage == "growth":
            allocation = {"流量型": "50%", "粘性型": "30%", "转化型": "20%"}
        else:
            allocation = {"流量型": "30%", "粘性型": "40%", "转化型": "30%"}
        return {
            "skill": "内容运营",
            "stage": stage,
            "allocation": allocation,
            "production_mix": {"PGC": "60%", "UGC": "30%", "AIGC": "10%"},
            "topic_sources": {"热点": "30%", "用户反馈": "30%", "数据": "40%"}
        }


class ActivityOperationsSkill(BaseSkill):
    """活动运营 Skill - 八步闭环法"""

    def __init__(self):
        metadata = SkillMetadata(
            name="活动运营",
            description="引流/促活/转化/品牌四类活动；八步闭环",
            tags=["growth", "activity", "operations"],
            triggers=["活动运营", "大促", "裂变", "秒杀"]
        )
        super().__init__(metadata)

    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        return {
            "skill": "活动运营",
            "types": {
                "引流型": {"目标": "拉新", "ROI基准": "CAC < 30%"},
                "促活型": {"目标": "活跃", "ROI基准": "参与率提升"},
                "转化型": {"目标": "变现", "ROI基准": "ROI > 3"},
                "品牌型": {"目标": "心智", "ROI基准": "品牌指数提升"}
            },
            "eight_steps": ["目标对齐", "创意策划", "方案评审", "项目排期", "预热造势", "上线执行", "收尾交付", "深度复盘"]
        }


class GrowthMarketingSkill(BaseSkill):
    """增长营销 Skill - 四象限渠道+杠铃策略"""

    def __init__(self):
        metadata = SkillMetadata(
            name="增长营销",
            description="四象限渠道模型；杠铃策略；U型归因",
            tags=["growth", "marketing", "channel"],
            triggers=["增长营销", "渠道", "投放", "Lookalike"]
        )
        super().__init__(metadata)

    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        return {
            "skill": "增长营销",
            "channel_matrix": {
                "高ROI高量": "重点投入",
                "高ROI低量": "培育优化",
                "低ROI高量": "谨慎控制",
                "低ROI低量": "淘汰测试"
            },
            "batting_strategy": {"验证渠道": "80%", "测试渠道": "20%"},
            "attribution": "U型归因（首40%+末40%+中间20%）"
        }


class BrandMarketingSkill(BaseSkill):
    """品牌营销 Skill - STP+品效协同"""

    def __init__(self):
        metadata = SkillMetadata(
            name="品牌营销",
            description="STP定位；认知→认同→追随三阶段；品效协同",
            tags=["growth", "marketing", "brand"],
            triggers=["品牌营销", "定位", "公关", "危机"]
        )
        super().__init__(metadata)

    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        return {
            "skill": "品牌营销",
            "stp": ["市场细分", "目标选择", "品牌定位"],
            "three_stages": {"认知": "曝光+记忆", "认同": "信任+偏好", "追随": "忠诚+推荐"},
            "brand_metrics": ["NPS", "品牌搜索指数", "声量占比"],
            "crisis_levels": {"一级": "1小时", "二级": "12小时", "三级": "即时"}
        }


class PerformanceMarketingSkill(BaseSkill):
    """效果营销 Skill - oCPA+ROI管理"""

    def __init__(self):
        metadata = SkillMetadata(
            name="效果营销",
            description="oCPM/oCPA投放；ROI>1.5及格/3优秀；LTV/CAC>3",
            tags=["growth", "marketing", "performance"],
            triggers=["效果营销", "投放", "ROI", "CAC", "LTV"]
        )
        super().__init__(metadata)

    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        return {
            "skill": "效果营销",
            "bidding": "优先oCPA",
            "roi_standards": {"及格": 1.5, "优秀": 3.0},
            "ltv_cac": "LTV/CAC > 3",
            "account_structure": {
                "Campaign层": "按目标划分",
                "AdSet层": "按人群定向",
                "Ad层": "按创意素材"
            },
            "funnel": ["曝光→点击→访问→转化→付费"]
        }


class TeamManagementSkill(BaseSkill):
    """团队管理 Skill - 1v1+激励+IDP"""

    def __init__(self):
        metadata = SkillMetadata(
            name="团队管理",
            description="1v1沟通+激励体系+人力盘点+IDP计划",
            tags=["growth", "management", "hr"],
            triggers=["团队管理", "人力", "激励", "绩效", "1v1"]
        )
        super().__init__(metadata)

    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        return {
            "skill": "团队管理",
            "tools": {
                "1v1沟通": "绩效反馈+职业发展",
                "激励体系": "物质+精神+社交三层激励",
                "人力盘点": "能力矩阵+人才梯队",
                "IDP计划": "个人发展+成长路径"
            },
            "focus": "80%资源投入20%高绩效员工"
        }


class StrategyPlanningSkill(BaseSkill):
    """策略规划 Skill - 北极星+OKR"""

    def __init__(self):
        metadata = SkillMetadata(
            name="策略规划",
            description="北极星指标→增长模型→策略地图→执行计划",
            tags=["growth", "strategy", "planning"],
            triggers=["策略规划", "战略", "OKR", "KPI", "北极星"]
        )
        super().__init__(metadata)

    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        return {
            "skill": "策略规划",
            "framework": "北极星指标→增长模型→策略地图→执行计划",
            "decomposition": {"O": "目标", "KR": "关键结果"},
            "top3_kpis": ["北极星指标", "增长健康度", "实验效能"]
        }


__all__ = [
    "ReportingFrameworkSkill",
    "TimeManagementSkill",
    "ProgressTrackingSkill",
    "RetrospectiveSkill",
    "UserGrowthSkill",
    "ContentOperationsSkill",
    "ActivityOperationsSkill",
    "GrowthMarketingSkill",
    "BrandMarketingSkill",
    "PerformanceMarketingSkill",
    "TeamManagementSkill",
    "StrategyPlanningSkill",
]
