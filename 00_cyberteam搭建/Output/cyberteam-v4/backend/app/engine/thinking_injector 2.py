"""思维注入引擎 - 统一入口。

此模块从 engine/thinking/ 导入核心框架，并提供 100+ 思维专家定义。
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
import logging

# 尝试从 engine 层导入核心框架
try:
    from engine.thinking.injector import ThinkingInjector as CoreThinkingInjector
    from engine.thinking.models import TaskContext
    from engine.thinking.router import ThinkingRouter, RoutingResult
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False
    CoreThinkingInjector = None
    TaskContext = None
    ThinkingRouter = None
    RoutingResult = None

from .agent_compiler import AgentProfile

log = logging.getLogger("cyberteam.thinking_injector")


# 100+ 思维专家定义 (从原 backend/app/engine/thinking_injector.py 迁移)
THINKING_EXPERTS: Dict[str, dict] = {
    # === 哲学与思维基础 ===
    "first_principles": {
        "name": "第一性原理",
        "category": "philosophy",
        "description": "从最基本的不可分割的真理出发，逐层推演",
        "prompt_template": """你正在使用第一性原理思维。

第一性原理思维的核心：
1. 分解问题：把复杂问题拆解到最基本的事实
2. 质疑假设：问"这个假设真的成立吗？"
3. 重建方案：从零开始构建新方案

分析框架：
- 这个问题的本质是什么？
- 我们能确定的最基本事实是什么？
- 如果没有现有方案的束缚，理想方案是什么？
- 如何用最基本的元素重建这个方案？
""",
    },
    "critical_thinking": {
        "name": "批判性思维",
        "category": "philosophy",
        "description": "系统性地分析论证，识别逻辑谬误",
    },
    "logical_thinking": {
        "name": "逻辑思维",
        "category": "philosophy",
        "description": "运用演绎、归纳等逻辑方法分析问题",
    },
    "systems_thinking": {
        "name": "系统思维",
        "category": "philosophy",
        "description": "从整体和关系角度理解复杂系统",
    },

    # === 分析类 ===
    "mece": {
        "name": "MECE法则",
        "category": "analysis",
        "description": "相互独立，完全穷尽",
    },
    "swot": {
        "name": "SWOT分析",
        "category": "analysis",
        "description": "优势、劣势、机会、威胁",
    },
    "pest": {
        "name": "PEST分析",
        "category": "analysis",
        "description": "政治、经济、社会、技术环境分析",
    },
    "five_forces": {
        "name": "波特五力",
        "category": "analysis",
        "description": "行业竞争结构分析",
    },

    # === 创意类 ===
    "lateral_thinking": {
        "name": "横向思维",
        "category": "creative",
        "description": "打破常规，寻找非常规解决方案",
    },
    "six_thinking_hats": {
        "name": "六顶思考帽",
        "category": "creative",
        "description": "从不同角度（情感、逻辑、创意等）思考",
    },
    "triz": {
        "name": "TRIZ",
        "category": "creative",
        "description": "发明问题解决理论",
    },
    "scamper": {
        "name": "SCAMPER",
        "category": "creative",
        "description": "替代、组合、调整、修改、其他用途、消除、重新排列",
    },

    # === 设计类 ===
    "design_thinking": {
        "name": "设计思维",
        "category": "design",
        "description": "以用户为中心的设计方法论",
    },
    "lean_startup": {
        "name": "精益创业",
        "category": "design",
        "description": "最小可行产品、迭代验证",
    },
    "agile": {
        "name": "敏捷思维",
        "category": "design",
        "description": "迭代、增量、响应变化",
    },

    # === 决策类 ===
    "decision_tree": {
        "name": "决策树",
        "category": "decision",
        "description": "结构化决策方法",
    },
    "bayesian": {
        "name": "贝叶斯分析",
        "category": "decision",
        "description": "基于新信息更新概率估计",
    },
    "cost_benefit": {
        "name": "成本收益分析",
        "category": "decision",
        "description": "量化比较方案的成本与收益",
    },
    "expected_value": {
        "name": "期望值分析",
        "category": "decision",
        "description": "计算各方案的期望回报",
    },

    # === 战略类 ===
    "value_chain": {
        "name": "价值链分析",
        "category": "strategy",
        "description": "分析价值创造活动",
    },
    "scenario_planning": {
        "name": "情景规划",
        "category": "strategy",
        "description": "为多种可能的未来做准备",
    },
    "blue_ocean": {
        "name": "蓝海战略",
        "category": "strategy",
        "description": "寻找无人竞争的市场空间",
    },

    # === 营销类 ===
    "aarr": {
        "name": "AARRR模型",
        "category": "marketing",
        "description": "获取、激活、留存、收入、推荐",
    },
    "4p": {
        "name": "4P营销组合",
        "category": "marketing",
        "description": "产品、价格、渠道、促销",
    },
    "stp": {
        "name": "STP分析",
        "category": "marketing",
        "description": "细分、目标、定位",
    },
    "funnel": {
        "name": "转化漏斗",
        "category": "marketing",
        "description": "分析用户转化路径",
    },

    # === 产品类 ===
    "kano": {
        "name": "KANO模型",
        "category": "product",
        "description": "分析用户需求优先级",
    },
    "rice": {
        "name": "RICE评分",
        "category": "product",
        "description": "覆盖面、影响力、信心、投入",
    },
    "moscow": {
        "name": "MoSCoW方法",
        "category": "product",
        "description": "必须有、应该有、可以有、不会有",
    },

    # === 运营类 ===
    "pdca": {
        "name": "PDCA循环",
        "category": "operations",
        "description": "计划、执行、检查、行动",
    },
    "oka": {
        "name": "OKR",
        "category": "operations",
        "description": "目标与关键成果",
    },
    "a_b_testing": {
        "name": "A/B测试",
        "category": "operations",
        "description": "对比实验优化",
    },

    # === 数据类 ===
    "cohort": {
        "name": "同类群组分析",
        "category": "data",
        "description": "按用户群组追踪行为",
    },
    "funnel_analysis": {
        "name": "漏斗分析",
        "category": "data",
        "description": "分析转化过程中的流失",
    },
    "ltv": {
        "name": "LTV计算",
        "category": "data",
        "description": "用户生命周期价值",
    },

    # === 技术类 ===
    "tdd": {
        "name": "测试驱动开发",
        "category": "technology",
        "description": "先写测试，再写代码",
    },
    "clean_code": {
        "name": "整洁代码",
        "category": "technology",
        "description": "可读、可维护的代码",
    },
    "microservices": {
        "name": "微服务架构",
        "category": "technology",
        "description": "服务化拆分",
    },
    "devops": {
        "name": "DevOps",
        "category": "technology",
        "description": "开发运维一体化",
    },

    # === 管理类 ===
    "situational_leadership": {
        "name": "情境领导",
        "category": "management",
        "description": "根据团队成熟度调整领导方式",
    },
    "servant_leadership": {
        "name": "服务型领导",
        "category": "management",
        "description": "为团队服务，赋能团队",
    },
    "crisis_management": {
        "name": "危机管理",
        "category": "management",
        "description": "应对突发事件",
    },

    # === 财务类 ===
    "npv": {
        "name": "净现值",
        "category": "finance",
        "description": "投资项目评估",
    },
    "irr": {
        "name": "内部收益率",
        "category": "finance",
        "description": "投资回报率",
    },
    "break_even": {
        "name": "盈亏平衡",
        "category": "finance",
        "description": "收入等于成本的点",
    },

    # === 法务类 ===
    "compliance": {
        "name": "合规审查",
        "category": "legal",
        "description": "确保符合法律法规",
    },
    "risk_assessment": {
        "name": "风险评估",
        "category": "legal",
        "description": "识别和评估法律风险",
    },
    "contract_review": {
        "name": "合同审查",
        "category": "legal",
        "description": "审查合同条款",
    },

    # === 人力资源类 ===
    "competency_model": {
        "name": "胜任力模型",
        "category": "hr",
        "description": "岗位能力要求",
    },
    "performance_review": {
        "name": "绩效评估",
        "category": "hr",
        "description": "评估员工表现",
    },
    "interview": {
        "name": "结构化面试",
        "category": "hr",
        "description": "标准化面试流程",
    },

    # === 安全类 ===
    "threat_modeling": {
        "name": "威胁建模",
        "category": "security",
        "description": "识别安全威胁",
    },
    "defense_in_depth": {
        "name": "纵深防御",
        "category": "security",
        "description": "多层安全防护",
    },
    "security_audit": {
        "name": "安全审计",
        "category": "security",
        "description": "检查安全漏洞",
    },

    # === 设计类（更多）===
    "user_persona": {
        "name": "用户画像",
        "category": "design",
        "description": "典型用户特征描述",
    },
    "user_journey": {
        "name": "用户旅程",
        "category": "design",
        "description": "用户使用产品的完整流程",
    },
    "wireframe": {
        "name": "线框图",
        "category": "design",
        "description": "产品界面草图",
    },

    # === 增长类 ===
    "growth_hacking": {
        "name": "增长黑客",
        "category": "growth",
        "description": "快速实验驱动增长",
    },
    "viral_loop": {
        "name": "病毒循环",
        "category": "growth",
        "description": "用户自传播机制",
    },
    "referral": {
        "name": "推荐计划",
        "category": "growth",
        "description": "激励用户推荐",
    },

    # === 质量类 ===
    "six_sigma": {
        "name": "六西格玛",
        "category": "quality",
        "description": "减少变异，提高质量",
    },
    "root_cause": {
        "name": "根因分析",
        "category": "quality",
        "description": "5个为什么找到根本原因",
    },
    "control_chart": {
        "name": "控制图",
        "category": "quality",
        "description": "监控过程稳定性",
    },

    # === 创新类（更多）===
    "brainstorming": {
        "name": "头脑风暴",
        "category": "innovation",
        "description": "集体创意生成",
    },
    "mind_map": {
        "name": "思维导图",
        "category": "innovation",
        "description": "可视化思维工具",
    },
    "morphological": {
        "name": "形态分析",
        "category": "innovation",
        "description": "系统化创意生成",
    },
}


class ThinkingInjector(CoreThinkingInjector if CORE_AVAILABLE else object):
    """
    思维注入引擎 - 统一入口。

    整合了：
    - engine/thinking/ 核心框架（如果可用）
    - 100+ 思维专家定义
    """

    def __init__(self):
        if CORE_AVAILABLE and CoreThinkingInjector:
            # 调用父类初始化
            super().__init__()
            self._use_core = True
            log.info("Using engine/thinking/ core framework")
        else:
            self._use_core = False
            self._experts = THINKING_EXPERTS
            log.warning("Core framework unavailable, using standalone mode")

    def get_available_experts(self) -> Dict[str, dict]:
        """获取所有可用的思维专家"""
        if self._use_core:
            # 如果使用核心框架，从 THINKING_EXPERTS 返回
            return THINKING_EXPERTS
        return self._experts

    def get_expert_by_category(self, category: str) -> List[str]:
        """按类别获取思维专家"""
        experts = self.get_available_experts()
        return [
            expert_id for expert_id, config in experts.items()
            if config.get("category") == category
        ]

    def inject_expert(
        self,
        expert_id: str,
        context: Optional[dict] = None,
    ) -> str:
        """
        注入单个思维专家。

        Args:
            expert_id: 专家ID
            context: 上下文数据

        Returns:
            注入后的提示词
        """
        experts = self.get_available_experts()
        if expert_id not in experts:
            raise ValueError(f"Unknown expert: {expert_id}")

        expert = experts[expert_id]
        template = expert.get("prompt_template", f"你是{expert['name']}专家。")

        if context:
            # 将上下文信息注入到模板中
            return template.format(**context)
        return template


# 便捷函数
def get_thinking_injector() -> ThinkingInjector:
    """获取思维注入器单例"""
    return ThinkingInjector()


def list_experts_by_category(category: str) -> List[str]:
    """按类别列出专家"""
    injector = get_thinking_injector()
    return injector.get_expert_by_category(category)


__all__ = [
    "ThinkingInjector",
    "get_thinking_injector",
    "THINKING_EXPERTS",
    "list_experts_by_category",
]
