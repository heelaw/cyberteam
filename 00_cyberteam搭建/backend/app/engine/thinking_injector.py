"""Thinking injector for CyberTeam - injects thinking modes into agents."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Callable, Union
from enum import Enum


class ThinkingMode(str, Enum):
    """Built-in thinking modes."""
    FIRST_PRINCIPLES = "first_principles"
    SIX_HATS = "six_hats"
    MOSCOW = "moscow"
    KANO = "kano"
    SWOT = "swot"
    PDCA = "pdca"
    AIDA = "aida"
    FAB = "fab"
    SMART = "smart"
    OCCAM = "occam"
    LATTICE = "lattice"
    MIND_MAP = "mind_map"
    STAR = "star"
    CATWOAE = "catwoae"
    USP = "usp"
    PESTEL = "pestel"
    RFM = "rfm"
    AARRR = "aarrr"
    RACE = "race"
    GROW = "grow"
    CLEAR = "clear"


@dataclass
class ThinkingExpert:
    """A thinking expert definition."""
    name: str
    mode: ThinkingMode
    description: str
    questions: list[str]
    process: str
    department: str  # Which department uses this thinking


# Built-in 20+ thinking experts
THINKING_EXPERTS: dict[ThinkingMode, ThinkingExpert] = {
    ThinkingMode.FIRST_PRINCIPLES: ThinkingExpert(
        name="第一性原理专家",
        mode=ThinkingMode.FIRST_PRINCIPLES,
        description="从最基本的不可分解的事实出发进行推理",
        questions=[
            "这个问题最基本的事实是什么？",
            "有哪些假设是我们认为是理所当然的？",
            "如果移除这个假设，还剩下什么？",
            "能否用更基础的原理来解释？",
        ],
        process="识别假设 → 分解问题 → 追溯基本原理 → 重新构建",
        department="strategy",
    ),
    ThinkingMode.SIX_HATS: ThinkingExpert(
        name="六顶思考帽专家",
        mode=ThinkingMode.SIX_HATS,
        description="从六个不同角度分析问题",
        questions=[
            "白帽：事实和数据是什么？",
            "红帽：情感和直觉如何？",
            "黑帽：风险和隐患有哪些？",
            "黄帽：价值和收益是什么？",
            "绿帽：有哪些创新方案？",
            "蓝帽：整体流程如何控制？",
        ],
        process="蓝帽开场 → 白帽事实 → 红帽情感 → 黄帽价值 → 黑帽风险 → 绿帽创新 → 蓝帽总结",
        department="management",
    ),
    ThinkingMode.MOSCOW: ThinkingExpert(
        name="MoSCoW优先级专家",
        mode=ThinkingMode.MOSCOW,
        description="对需求进行优先级排序",
        questions=[
            "Must have（必须有）：没有这个会失败吗？",
            "Should have（应该有）：影响有多大？",
            "Could have（可以有）：加分项是什么？",
            "Won't have（不会有）：明确放弃什么？",
        ],
        process="收集需求 → 分类 → 排序 → 确认优先级",
        department="management",
    ),
    ThinkingMode.KANO: ThinkingExpert(
        name="Kano模型专家",
        mode=ThinkingMode.KANO,
        description="分析用户需求与满意度关系",
        questions=[
            "基本型需求：用户认为理所当然的吗？",
            "期望型需求：用户明确要求的是什么？",
            "兴奋型需求：超出用户预期的有哪些？",
            "无差异需求：用户不在意的是什么？",
        ],
        process="识别需求 → 分类 → 规划产品路线",
        department="product",
    ),
    ThinkingMode.SWOT: ThinkingExpert(
        name="SWOT分析专家",
        mode=ThinkingMode.SWOT,
        description="分析优势、劣势、机会、威胁",
        questions=[
            "S: 我们的核心优势是什么？",
            "W: 主要劣势和短板在哪？",
            "O: 市场机会和趋势是什么？",
            "T: 竞争对手威胁和风险有哪些？",
        ],
        process="收集信息 → 绘制SWOT矩阵 → 制定策略",
        department="strategy",
    ),
    ThinkingMode.PDCA: ThinkingExpert(
        name="PDCA循环专家",
        mode=ThinkingMode.PDCA,
        description="计划-执行-检查-行动的循环改进",
        questions=[
            "Plan: 目标和计划是什么？",
            "Do: 具体执行步骤和分工？",
            "Check: 如何衡量结果？",
            "Act: 下一步改进措施？",
        ],
        process="计划 → 执行 → 检查 → 行动 → 循环",
        department="operations",
    ),
    ThinkingMode.AIDA: ThinkingExpert(
        name="AIDA文案专家",
        mode=ThinkingMode.AIDA,
        description="注意力-兴趣-欲望-行动文案模型",
        questions=[
            "Attention: 如何吸引用户注意？",
            "Interest: 如何激发兴趣？",
            "Desire: 如何唤起欲望？",
            "Action: 如何促使行动？",
        ],
        process="吸引注意 → 激发兴趣 → 唤起欲望 → 促成行动",
        department="marketing",
    ),
    ThinkingMode.FAB: ThinkingExpert(
        name="FAB卖点专家",
        mode=ThinkingMode.FAB,
        description="特性-优势-利益的卖点梳理",
        questions=[
            "Feature: 产品特性是什么？",
            "Advantage: 相比竞品优势在哪？",
            "Benefit: 给用户带来什么利益？",
        ],
        process="梳理特性 → 提炼优势 → 转化利益",
        department="marketing",
    ),
    ThinkingMode.SMART: ThinkingExpert(
        name="SMART目标专家",
        mode=ThinkingMode.SMART,
        description="设定具体可衡量的目标",
        questions=[
            "Specific：目标具体吗？",
            "Measurable：如何衡量成功？",
            "Achievable：目标可实现吗？",
            "Relevant：与整体战略相关吗？",
            "Time-bound：有明确截止日期吗？",
        ],
        process="定义目标 → 验证SMART → 分解里程碑",
        department="management",
    ),
    ThinkingMode.OCCAM: ThinkingExpert(
        name="奥卡姆剃刀专家",
        mode=ThinkingMode.OCCAM,
        description="如无必要勿增实体",
        questions=[
            "这个需求真的必要吗？",
            "能否用更简单的方案替代？",
            "增加这个复杂度带来什么价值？",
            "最简单的解法是什么？",
        ],
        process="分析需求 → 寻找简单方案 → 验证有效性 → 实施",
        department="engineering",
    ),
    ThinkingMode.LATTICE: ThinkingExpert(
        name="格栅思维专家",
        mode=ThinkingMode.LATTICE,
        description="跨学科跨领域整合思维",
        questions=[
            "其他领域有哪些类似问题？",
            "跨学科知识如何应用？",
            "不同领域的原理能否组合？",
            "灵感来源有哪些？",
        ],
        process="确定问题 → 跨学科研究 → 知识整合 → 创新应用",
        department="strategy",
    ),
    ThinkingMode.MIND_MAP: ThinkingExpert(
        name="思维导图专家",
        mode=ThinkingMode.MIND_MAP,
        description="从中心向外发散的思维结构",
        questions=[
            "核心问题/主题是什么？",
            "主要分支有哪些？",
            "每个分支的子主题？",
            "如何关联和排序？",
        ],
        process="确定中心 → 展开分支 → 补充细节 → 优化结构",
        department="planning",
    ),
    ThinkingMode.STAR: ThinkingExpert(
        name="STAR故事专家",
        mode=ThinkingMode.STAR,
        description="情境-任务-行动-结果的故事框架",
        questions=[
            "Situation: 背景情境是什么？",
            "Task: 面临的任务和挑战？",
            "Action: 采取了什么行动？",
            "Result: 取得了什么结果？",
        ],
        process="描述情境 → 明确任务 → 叙述行动 → 展示结果",
        department="marketing",
    ),
    ThinkingMode.CATWOAE: ThinkingExpert(
        name="CATWOAE分析专家",
        mode=ThinkingMode.CATWOAE,
        description="全面分析问题的影响因素",
        questions=[
            "Creators: 谁创造了这个问题？",
            "Actors: 谁参与了？",
            "Transformers: 谁改变了它？",
            "Owners: 谁拥有它？",
            "Affected: 谁受到影响？",
            "Environment: 环境因素有哪些？",
        ],
        process="识别各方 → 分析影响 → 制定方案",
        department="strategy",
    ),
    ThinkingMode.USP: ThinkingExpert(
        name="USP独特卖点专家",
        mode=ThinkingMode.USP,
        description="提炼独特的销售主张",
        questions=[
            "产品最独特的点是什么？",
            "这个点对用户有何价值？",
            "竞品能否复制这个点？",
            "如何用一句话表达？",
        ],
        process="分析独特性 → 验证用户价值 → 提炼USP",
        department="marketing",
    ),
    ThinkingMode.PESTEL: ThinkingExpert(
        name="PESTEL宏观分析专家",
        mode=ThinkingMode.PESTEL,
        description="分析宏观环境的六大因素",
        questions=[
            "Political: 政策法律影响？",
            "Economic: 经济环境变化？",
            "Social: 社会文化趋势？",
            "Technological: 技术创新影响？",
            "Environmental: 环境可持续发展？",
            "Legal: 法规合规要求？",
        ],
        process="收集信息 → 六大因素分析 → 识别机会威胁",
        department="strategy",
    ),
    ThinkingMode.RFM: ThinkingExpert(
        name="RFM用户分层专家",
        mode=ThinkingMode.RFM,
        description="最近-频率- monetary用户价值分析",
        questions=[
            "Recency: 最近一次购买何时？",
            "Frequency: 购买频率如何？",
            "Monetary: 消费金额多少？",
        ],
        process="数据收集 → RFM打分 → 用户分层 → 精准营销",
        department="marketing",
    ),
    ThinkingMode.AARRR: ThinkingExpert(
        name="AARRR海盗模型专家",
        mode=ThinkingMode.AARRR,
        description="用户生命周期的五个指标",
        questions=[
            "Acquisition: 如何获取用户？",
            "Activation: 如何激活用户？",
            "Retention: 如何留存用户？",
            "Revenue: 如何实现收入？",
            "Referral: 如何推荐裂变？",
        ],
        process="获取 → 激活 → 留存 → 收入 → 推荐",
        department="growth",
    ),
    ThinkingMode.RACE: ThinkingExpert(
        name="RACE营销漏斗专家",
        mode=ThinkingMode.RACE,
        description="全链路营销覆盖",
        questions=[
            "Reach: 如何扩大触达？",
            "Act: 如何促使行动？",
            "Convert: 如何实现转化？",
            "Engage: 如何持续互动？",
        ],
        process="全渠道覆盖 → 精准触达 → 转化优化 → 私域运营",
        department="marketing",
    ),
    ThinkingMode.GROW: ThinkingExpert(
        name="GROW教练模型专家",
        mode=ThinkingMode.GROW,
        description="目标-现状-方案-意愿的教练对话",
        questions=[
            "Goal: 目标是什么？",
            "Reality: 现状如何？",
            "Options: 有哪些方案？",
            "Will: 行动意愿和计划？",
        ],
        process="明确目标 → 分析现状 → 探索方案 → 确认行动",
        department="hr",
    ),
    ThinkingMode.CLEAR: ThinkingExpert(
        name="CLEAR敏捷团队专家",
        mode=ThinkingMode.CLEAR,
        description="高效团队协作的六个要素",
        questions=[
            "Collaborate: 如何协作？",
            "Lead: 谁是领导者？",
            "Energize: 如何保持活力？",
            "Achieve: 如何达成目标？",
            "Review: 如何复盘改进？",
        ],
        process="建立协作 → 明确领导 → 保持活力 → 达成目标 → 持续复盘",
        department="management",
    ),
}


class ThinkingInjector:
    """Injects thinking modes into agent execution."""

    def __init__(self):
        self.experts = THINKING_EXPERTS
        self._custom_experts: dict[str, ThinkingExpert] = {}

    def inject(
        self,
        agent_name: str,
        thinking_mode: Union[str, ThinkingMode],
        context: Optional[dict] = None,
    ) -> str:
        """Inject thinking mode into agent.

        Args:
            agent_name: Name of the agent
            thinking_mode: Mode to inject
            context: Optional context data

        Returns:
            Injected system prompt
        """
        if isinstance(thinking_mode, str):
            try:
                mode = ThinkingMode(thinking_mode)
            except ValueError:
                # Check custom modes
                if thinking_mode in self._custom_experts:
                    mode = thinking_mode
                else:
                    raise ValueError(f"Unknown thinking mode: {thinking_mode}")
        else:
            mode = thinking_mode

        # Get expert
        if isinstance(mode, str):
            expert = self._custom_experts.get(mode)
        else:
            expert = self.experts.get(mode)

        if not expert:
            return ""

        # Compose injection prompt
        injection = f"""
## Thinking Mode: {expert.name}

{expert.description}

### Process
{expert.process}

### Key Questions
"""
        for q in expert.questions:
            injection += f"- {q}\n"

        return injection

    def get_expert(self, mode: ThinkingMode) -> Optional[ThinkingExpert]:
        """Get a thinking expert by mode."""
        return self.experts.get(mode)

    def list_modes(self) -> list[ThinkingMode]:
        """List all available thinking modes."""
        return list(self.experts.keys())

    def add_custom_expert(self, expert: ThinkingExpert) -> None:
        """Add a custom thinking expert."""
        self._custom_experts[expert.name] = expert


# Global instance
thinking_injector = ThinkingInjector()
