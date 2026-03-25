"""Growth Skill - 增长技能集。

提供增长相关的技能，包括：
- 用户增长策略
- 内容运营策略
- 活动运营策略
- 营销增长策略
- 品牌营销策略
- 效果营销策略

这些技能继承自 v3 运营资产的知识库。
"""

import json
from typing import Any, Dict, List, Optional
from pathlib import Path

from cyberteam.skills.base import BaseSkill, SkillMetadata


# Skill元数据定义（从v3运营资产注入）
GROWTH_SKILLS = {
    "汇报框架": {
        "name": "汇报框架",
        "description": "结构化向上沟通：背景→问题→方案→请求",
        "triggers": ["周报", "月报", "汇报", "述职"],
        "tags": ["growth", "management", "communication"],
        "source": "skills/v3-agents/ops/01_汇报框架Agent"
    },
    "时间管理": {
        "name": "时间管理",
        "description": "优先级四象限：重要紧急/重要不紧急/紧急不重要/不紧急不重要",
        "triggers": ["时间管理", "优先级", "日程"],
        "tags": ["growth", "management", "efficiency"],
        "source": "skills/v3-agents/ops/02_时间管理Agent"
    },
    "进度管理": {
        "name": "进度管理",
        "description": "甘特图+里程碑追踪，确保项目按时交付",
        "triggers": ["进度", "项目管理", "里程碑", "甘特图"],
        "tags": ["growth", "management", "tracking"],
        "source": "skills/v3-agents/ops/03_进度管理Agent"
    },
    "复盘模板": {
        "name": "复盘模板",
        "description": "目标达成+数据+问题+行动四步法",
        "triggers": ["复盘", "总结", "反思"],
        "tags": ["growth", "management", "learning"],
        "source": "skills/v3-agents/ops/04_复盘模板Agent"
    },
    "用户增长": {
        "name": "用户增长",
        "description": "RFM模型+用户生命周期管理+AARRR漏斗",
        "triggers": ["用户增长", "DAU", "MAU", "拉新", "激活", "留存"],
        "tags": ["growth", "user", "operations"],
        "source": "skills/v3-agents/ops/用户运营Agent"
    },
    "内容运营": {
        "name": "内容运营",
        "description": "PGC+UGC+AIGC配比；选题三叉模型；流量/粘性/转化三类内容",
        "triggers": ["内容运营", "选题", "PGC", "UGC", "AIGC"],
        "tags": ["growth", "content", "operations"],
        "source": "skills/v3-agents/ops/内容运营Agent"
    },
    "活动运营": {
        "name": "活动运营",
        "description": "引流/促活/转化/品牌四类活动；八步闭环法",
        "triggers": ["活动运营", "大促", "活动策划", "裂变"],
        "tags": ["growth", "activity", "operations"],
        "source": "skills/v3-agents/ops/活动策划Agent"
    },
    "增长营销": {
        "name": "增长营销",
        "description": "四象限渠道模型；Lookalike人群扩展；杠铃策略",
        "triggers": ["增长营销", "渠道", "投放", "ROI"],
        "tags": ["growth", "marketing", "channel"],
        "source": "skills/v3-agents/ops/增长Agent"
    },
    "品牌营销": {
        "name": "品牌营销",
        "description": "STP定位；认知→认同→追随三阶段；品效协同",
        "triggers": ["品牌营销", "定位", "品牌", "公关"],
        "tags": ["growth", "marketing", "brand"],
        "source": "skills/v3-agents/ops/商业认知咨询Agent"
    },
    "效果营销": {
        "name": "效果营销",
        "description": "oCPM/oCPA投放；ROI>1.5及格；LTV/CAC>3健康",
        "triggers": ["效果营销", "投放", "转化", "ROI", "CAC"],
        "tags": ["growth", "marketing", "performance"],
        "source": "skills/v3-agents/ops/渠道推广Agent"
    },
    "团队管理": {
        "name": "团队管理",
        "description": "1v1沟通+激励体系+人力盘点+IDP计划",
        "triggers": ["团队管理", "人力", "激励", "绩效"],
        "tags": ["growth", "management", "hr"],
        "source": "skills/v3-agents/ops/团队管理Agent"
    },
    "策略规划": {
        "name": "策略规划",
        "description": "北极星指标→增长模型→策略地图→执行计划",
        "triggers": ["策略规划", "战略", "OKR", "KPI"],
        "tags": ["growth", "strategy", "planning"],
        "source": "skills/v3-agents/ops/策略规划Agent"
    },
}


class ReportingFrameworkSkill(BaseSkill):
    """汇报框架Skill

    继承自 v3 运营资产的汇报框架Agent知识。
    提供结构化向上沟通能力。
    """

    def __init__(self):
        metadata = SkillMetadata(
            name="汇报框架",
            description="结构化向上沟通：背景→问题→方案→请求。包含电梯法则30秒汇报和标准汇报模板。",
            tags=["growth", "management", "communication"],
            triggers=["周报", "月报", "汇报", "述职", "述标"]
        )
        super().__init__(metadata)

    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """执行汇报框架"""
        task = input_data if isinstance(input_data, str) else context.get("task", "")

        # 电梯法则：30秒核心
        elevator_pitch = self._elevator_pitch(task)

        # 标准汇报模板
        report_template = self._report_template(task)

        return {
            "skill": "汇报框架",
            "elevator_pitch": elevator_pitch,
            "template": report_template,
            "principles": [
                "结论先行",
                "数据支撑",
                "方案导向",
                "简洁有力"
            ]
        }

    def _elevator_pitch(self, task: str) -> str:
        """30秒电梯法则"""
        return f"[30秒汇报] 核心问题：{task}。关键请求：..."

    def _report_template(self, task: str) -> str:
        """标准汇报模板"""
        return f"""## 汇报模板
### 背景
{context.get("background", "")}
### 问题
{context.get("problem", task)}
### 方案
{context.get("solution", "")}
### 请求
{context.get("request", "")}"""


class TimeManagementSkill(BaseSkill):
    """时间管理Skill

    继承自 v3 运营资产的时间管理Agent知识。
    提供优先级四象限管理能力。
    """

    def __init__(self):
        metadata = SkillMetadata(
            name="时间管理",
            description="优先级四象限：重要紧急/重要不紧急/紧急不重要/不紧急不重要。支持任务优先级排序和时间分配。",
            tags=["growth", "management", "efficiency"],
            triggers=["时间管理", "优先级", "日程", "任务排序"]
        )
        super().__init__(metadata)

    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """执行时间管理"""
        tasks = context.get("tasks", []) if context else []

        # 四象限分类
        quadrant_1 = []  # 重要紧急
        quadrant_2 = []  # 重要不紧急
        quadrant_3 = []  # 紧急不重要
        quadrant_4 = []  # 不紧急不重要

        for task in tasks:
            importance = task.get("importance", 5)
            urgency = task.get("urgency", 5)
            if importance >= 4 and urgency >= 4:
                quadrant_1.append(task)
            elif importance >= 4 and urgency < 4:
                quadrant_2.append(task)
            elif importance < 4 and urgency >= 4:
                quadrant_3.append(task)
            else:
                quadrant_4.append(task)

        return {
            "skill": "时间管理",
            "quadrant_1_重要紧急": quadrant_1,
            "quadrant_2_重要不紧急": quadrant_2,
            "quadrant_3_紧急不重要": quadrant_3,
            "quadrant_4_不紧急不重要": quadrant_4,
            "recommendation": "优先处理Q1，合理安排Q2，控制Q3，委托或删除Q4"
        }


class ProgressTrackingSkill(BaseSkill):
    """进度管理Skill

    继承自 v3 运营资产的进度管理Agent知识。
    提供甘特图+里程碑追踪能力。
    """

    def __init__(self):
        metadata = SkillMetadata(
            name="进度管理",
            description="甘特图+里程碑追踪，确保项目按时交付。支持项目进度可视化和风险预警。",
            tags=["growth", "management", "tracking"],
            triggers=["进度", "项目管理", "里程碑", "甘特图", "延期"]
        )
        super().__init__(metadata)

    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """执行进度管理"""
        project = context.get("project", {}) if context else {}

        milestones = project.get("milestones", [])
        current_progress = project.get("progress", 0)

        # 里程碑检查
        upcoming_milestones = [m for m in milestones if not m.get("completed", False)]

        return {
            "skill": "进度管理",
            "current_progress": current_progress,
            "upcoming_milestones": upcoming_milestones,
            "status": "正常" if current_progress >= 50 else "滞后预警"
        }


class RetrospectiveSkill(BaseSkill):
    """复盘Skill

    继承自 v3 运营资产的复盘模板Agent知识。
    提供目标达成+数据+问题+行动四步法。
    """

    def __init__(self):
        metadata = SkillMetadata(
            name="复盘模板",
            description="目标达成+数据+问题+行动四步法。支持活动复盘、项目复盘、季度复盘。",
            tags=["growth", "management", "learning"],
            triggers=["复盘", "总结", "反思", "review"]
        )
        super().__init__(metadata)

    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """执行复盘"""
        retrospective = context or {}

        return {
            "skill": "复盘模板",
            "step_1_目标达成": retrospective.get("objectives", ""),
            "step_2_数据分析": retrospective.get("data", ""),
            "step_3_问题分析": retrospective.get("problems", ""),
            "step_4_行动计划": retrospective.get("actions", ""),
            "template": "目标→数据→问题→行动"
        }


class UserGrowthSkill(BaseSkill):
    """用户增长Skill

    继承自 v3 运营资产的用户运营Agent知识。
    提供RFM模型+用户生命周期管理+AARRR漏斗。
    """

    def __init__(self):
        metadata = SkillMetadata(
            name="用户增长",
            description="RFM模型+用户生命周期管理+AARRR漏斗。覆盖拉新→激活→留存→变现→推荐全链路。",
            tags=["growth", "user", "operations"],
            triggers=["用户增长", "DAU", "MAU", "拉新", "激活", "留存", "RFM", "AARRR"]
        )
        super().__init__(metadata)

    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """执行用户增长策略"""
        action = context.get("action", "strategy") if context else "strategy"

        if action == "rfm":
            return self._rfm_analysis(context)
        elif action == "lifecycle":
            return self._lifecycle_management(context)
        elif action == "aarrr":
            return self._aarrr_funnel(context)
        else:
            return self._growth_strategy(context)

    def _rfm_analysis(self, context: Dict) -> Dict:
        """RFM分析"""
        return {
            "skill": "用户增长-RFM",
            "recency": "最近消费时间",
            "frequency": "消费频率",
            "monetary": "消费金额",
            "segments": ["高价值用户", "潜力用户", "流失风险用户", "沉默用户"]
        }

    def _lifecycle_management(self, context: Dict) -> Dict:
        """用户生命周期管理"""
        return {
            "skill": "用户增长-生命周期",
            "stages": ["引入期", "成长期", "成熟期", "衰退期", "流失期"],
            "metrics": ["激活率", "留存率", "复购率", "LTV"]
        }

    def _aarrr_funnel(self, context: Dict) -> Dict:
        """AARRR漏斗"""
        return {
            "skill": "用户增长-AARRR",
            " Acquisition获取": "渠道获客",
            " Activation激活": "首活体验",
            " Retention留存": "持续价值",
            " Referral推荐": "社交裂变",
            " Revenue变现": "付费转化"
        }

    def _growth_strategy(self, context: Dict) -> Dict:
        """增长策略"""
        return {
            "skill": "用户增长策略",
            "focus": "先留存再拉新",
            "principles": [
                "LTV/CAC > 3 是健康底线",
                "次留率 < 40% 即预警",
                "激活率 < 30% 即预警"
            ]
        }


class ContentOperationsSkill(BaseSkill):
    """内容运营Skill

    继承自 v3 运营资产的内容运营Agent知识。
    提供PGC+UGC+AIGC配比；选题三叉模型；流量/粘性/转化三类内容。
    """

    def __init__(self):
        metadata = SkillMetadata(
            name="内容运营",
            description="PGC+UGC+AIGC配比；选题三叉模型（热点30%+用户30%+数据40%）；流量/粘性/转化三类内容动态配比。",
            tags=["growth", "content", "operations"],
            triggers=["内容运营", "选题", "PGC", "UGC", "AIGC", "文案", "爆款"]
        )
        super().__init__(metadata)

    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """执行内容运营策略"""
        stage = context.get("stage", "growth") if context else "growth"

        if stage == "initial":
            # 初期：70%粘性 + 30%转化
            allocation = {"粘性型": "70%", "转化型": "30%", "流量型": "0%"}
        elif stage == "growth":
            # 增长期：50%流量 + 30%粘性 + 20%转化
            allocation = {"流量型": "50%", "粘性型": "30%", "转化型": "20%"}
        else:
            # 成熟期：30%流量 + 40%粘性 + 30%转化
            allocation = {"流量型": "30%", "粘性型": "40%", "转化型": "30%"}

        return {
            "skill": "内容运营",
            "stage": stage,
            "allocation": allocation,
            "production_mix": {"PGC": "60%", "UGC": "30%", "AIGC": "10%"},
            "topic_sources": {"热点追踪": "30%", "用户反馈": "30%", "数据洞察": "40%"}
        }


class ActivityOperationsSkill(BaseSkill):
    """活动运营Skill

    继承自 v3 运营资产的活动策划Agent知识。
    提供引流/促活/转化/品牌四类活动；八步闭环法。
    """

    def __init__(self):
        metadata = SkillMetadata(
            name="活动运营",
            description="引流/促活/转化/品牌四类活动；八步闭环法；ROI三级标准；风控+熔断机制。",
            tags=["growth", "activity", "operations"],
            triggers=["活动运营", "大促", "活动策划", "裂变", "秒杀"]
        )
        super().__init__(metadata)

    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """执行活动运营策略"""
        activity_type = context.get("type", "promotion") if context else "promotion"

        return {
            "skill": "活动运营",
            "activity_types": {
                "引流型": {"目标": "拉新", "ROI基准": "CAC < 平均30%"},
                "促活型": {"目标": "活跃", "ROI基准": "参与率提升"},
                "转化型": {"目标": "变现", "ROI基准": "ROI > 3"},
                "品牌型": {"目标": "心智", "ROI基准": "品牌指数提升"}
            },
            "eight_step_process": [
                "目标对齐", "创意策划", "方案评审", "项目排期",
                "预热造势", "上线执行", "收尾交付", "深度复盘"
            ],
            "current_type": activity_type
        }


class GrowthMarketingSkill(BaseSkill):
    """增长营销Skill

    继承自 v3 运营资产的渠道推广Agent知识。
    提供四象限渠道模型；Lookalike人群扩展；杠铃策略。
    """

    def __init__(self):
        metadata = SkillMetadata(
            name="增长营销",
            description="四象限渠道模型（规模×ROI）；杠铃策略（80%验证+20%测试）；U型归因。",
            tags=["growth", "marketing", "channel"],
            triggers=["增长营销", "渠道", "投放", "ROI", "Lookalike", "归因"]
        )
        super().__init__(metadata)

    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """执行增长营销策略"""
        return {
            "skill": "增长营销",
            "channel_matrix": {
                "高ROI高量": "重点投入",
                "高ROI低量": "培育优化",
                "低ROI高量": "谨慎控制",
                "低ROI低量": "淘汰测试"
            },
            "batting_strategy": {"验证渠道": "80%", "测试渠道": "20%"},
            "attribution_model": "U型归因（首40%+末40%+中间20%）"
        }


class BrandMarketingSkill(BaseSkill):
    """品牌营销Skill

    继承自 v3 运营资产的商业认知咨询Agent知识。
    提供STP定位；认知→认同→追随三阶段；品效协同。
    """

    def __init__(self):
        metadata = SkillMetadata(
            name="品牌营销",
            description="STP定位；认知→认同→追随三阶段；品效协同；三级危机响应。",
            tags=["growth", "marketing", "brand"],
            triggers=["品牌营销", "定位", "品牌", "公关", "危机", "NPS"]
        )
        super().__init__(metadata)

    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """执行品牌营销策略"""
        return {
            "skill": "品牌营销",
            "stp": ["市场细分", "目标选择", "品牌定位"],
            "three_stages": {
                "认知": "曝光+记忆",
                "认同": "信任+偏好",
                "追随": "忠诚+推荐"
            },
            "brand_metrics": ["NPS", "品牌搜索指数", "声量占比"],
            "crisis_levels": {
                "一级": {"响应": "1小时内", "范围": "重大事故"},
                "二级": {"响应": "12小时内", "范围": "局部投诉"},
                "三级": {"响应": "即时", "范围": "个别抱怨"}
            }
        }


class PerformanceMarketingSkill(BaseSkill):
    """效果营销Skill

    继承自 v3 运营资产的渠道推广Agent知识。
    提供oCPM/oCPA投放；ROI>1.5及格；LTV/CAC>3健康。
    """

    def __init__(self):
        metadata = SkillMetadata(
            name="效果营销",
            description="oCPM/oCPA投放；ROI>1.5及格/3优秀；LTV/CAC>3健康；账户三层结构。",
            tags=["growth", "marketing", "performance"],
            triggers=["效果营销", "投放", "转化", "ROI", "CAC", "LTV", "oCPA"]
        )
        super().__init__(metadata)

    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """执行效果营销策略"""
        return {
            "skill": "效果营销",
            "bidding_strategy": "优先oCPA（按转化出价）",
            "roi_standards": {"及格": 1.5, "优秀": 3.0},
            "ltv_cac_standard": "LTV/CAC > 3",
            "account_structure": {
                "Campaign层": "按目标划分（下载/表单/销售）",
                "AdSet层": "按人群定向划分",
                "Ad层": "按创意素材划分"
            },
            "funnel": ["曝光→点击→访问→转化→付费"]
        }


class TeamManagementSkill(BaseSkill):
    """团队管理Skill

    继承自 v3 运营资产的团队管理Agent知识。
    提供1v1沟通+激励体系+人力盘点+IDP计划。
    """

    def __init__(self):
        metadata = SkillMetadata(
            name="团队管理",
            description="1v1沟通+激励体系+人力盘点+IDP计划+OKR管理。",
            tags=["growth", "management", "hr"],
            triggers=["团队管理", "人力", "激励", "绩效", "OKR", "1v1"]
        )
        super().__init__(metadata)

    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """执行团队管理"""
        action = context.get("action", "management") if context else "management"

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
    """策略规划Skill

    继承自 v3 运营资产的策略规划Agent知识。
    提供北极星指标→增长模型→策略地图→执行计划。
    """

    def __init__(self):
        metadata = SkillMetadata(
            name="策略规划",
            description="北极星指标→增长模型→策略地图→执行计划。包含OKR拆解和KPI体系。",
            tags=["growth", "strategy", "planning"],
            triggers=["策略规划", "战略", "OKR", "KPI", "北极星", "目标拆解"]
        )
        super().__init__(metadata)

    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """执行策略规划"""
        return {
            "skill": "策略规划",
            "framework": "北极星指标→增长模型→策略地图→执行计划",
            "decomposition": {
                "O": "目标（Objective）",
                "KR": "关键结果（Key Results）"
            },
            "top3_kpis": [
                "北极星指标（最终价值）",
                "增长健康度（LTV/CAC/留存）",
                "实验效能（数量×转化×速度）"
            ]
        }


# 导出所有Skill类
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


# 全局注册函数
def register_all_growth_skills():
    """注册所有增长Skill到全局注册表"""
    from cyberteam.skills.registry import get_registry

    registry = get_registry()
    skills = [
        ReportingFrameworkSkill(),
        TimeManagementSkill(),
        ProgressTrackingSkill(),
        RetrospectiveSkill(),
        UserGrowthSkill(),
        ContentOperationsSkill(),
        ActivityOperationsSkill(),
        GrowthMarketingSkill(),
        BrandMarketingSkill(),
        PerformanceMarketingSkill(),
        TeamManagementSkill(),
        StrategyPlanningSkill(),
    ]

    for skill in skills:
        registry.register(
            name=skill.metadata.name,
            skill_class=type(skill),
            metadata=skill.metadata,
            category="growth"
        )

    return [s.metadata.name for s in skills]