#!/usr/bin/env python3
"""
CyberTeam V4 - CEO 路由引擎 (L1)

职责：
1. 需求分拣 (简单咨询 vs 正式任务)
2. 意图识别 (数据分析/内容运营/技术研发/安全合规)
3. 复杂度评估 (高/中/低)
4. 路由决策 (L2/L3A/L3B/L3C)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import re


class Complexity(Enum):
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


class Intent(Enum):
    DATA_ANALYSIS = "数据分析"
    CONTENT_OPS = "内容运营"
    TECH_ENGINEERING = "技术研发"
    SECURITY = "安全合规"
    STRATEGY = "战略规划"
    HR = "人力资源"
    OPERATIONS = "运营支持"
    UNKNOWN = "未知"


class RoutingTarget(Enum):
    L2 = "L2"           # PM + Strategy 协调层
    L3A = "L3A"         # CyberTeam 部门
    L3B = "L3B"         # Gstack Skills
    L3C = "L3C"         # 独立 Agents


@dataclass
class RoutingResult:
    """路由结果"""
    decision: str           # 路由决策
    target: str              # "L2"|"L3A"|"L3B"|"L3C"
    target_name: str         # "PM"|"数据分析部"|"/review"|"gsd-executor"
    intent: str              # 识别的意图
    complexity: str          # "高"|"中"|"低"
    reason: str              # 路由理由


class CEORouter:
    """CEO 任务路由引擎"""

    # 意图关键词映射
    INTENT_KEYWORDS = {
        Intent.DATA_ANALYSIS: [
            "增长", "数据", "分析", "财务", "投资", "ROI", "转化率",
            "GMV", "DAU", "MAU", "留存", "北极星指标", "LTV"
        ],
        Intent.CONTENT_OPS: [
            "内容", "文案", "创作", "文章", "发布", "公众号", "小红书",
            "抖音", "短视频", "脚本", "营销", "推广"
        ],
        Intent.TECH_ENGINEERING: [
            "开发", "代码", "功能", "实现", "修复", "Bug", "架构",
            "测试", "部署", "API", "系统"
        ],
        Intent.SECURITY: [
            "安全", "审计", "合规", "隐私", "漏洞", "渗透"
        ],
        Intent.STRATEGY: [
            "战略", "规划", "方案", "决策", "竞争", "市场", "进入"
        ],
        Intent.HR: [
            "招聘", "绩效", "团队", "人力", "OKR"
        ],
        Intent.OPERATIONS: [
            "运营", "活动", "用户", "社群", "增长黑客"
        ]
    }

    # 简单咨询关键词
    GREETING_KEYWORDS = [
        "你好", "您好", "嗨", "hi", "hello", "在吗", "在不在",
        "谢谢", "感谢", "辛苦了", "好的", "收到", "明白"
    ]

    def __init__(self):
        self.router_config = self._load_router_config()

    def _load_router_config(self) -> dict:
        """加载路由配置"""
        # TODO: 从 config/routing.yaml 加载
        return {
            "complexity_threshold": {
                "high": 100,  # 字符数 > 100 = 高复杂度
                "multi_domain": True  # 涉及多领域
            },
            "timeout": 300  # 默认超时秒数
        }

    def is_simple_consultation(self, user_input: str) -> bool:
        """需求分拣：判断是否为简单咨询"""
        cleaned = user_input.strip().lower()

        # 直接匹配
        for keyword in self.GREETING_KEYWORDS:
            if keyword in cleaned:
                return True

        # 纯符号/纯表情
        if len(re.sub(r'[\w\u4e00-\u9fff]', '', cleaned)) == len(cleaned):
            return True

        return False

    def recognize_intent(self, user_input: str) -> Intent:
        """意图识别"""
        user_input_lower = user_input.lower()

        # 统计关键词匹配
        intent_scores = {}
        for intent, keywords in self.INTENT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in user_input_lower)
            if score > 0:
                intent_scores[intent] = score

        if not intent_scores:
            return Intent.UNKNOWN

        # 返回得分最高的意图
        return max(intent_scores.items(), key=lambda x: x[1])[0]

    def evaluate_complexity(self, user_input: str, intent: Intent) -> Complexity:
        """复杂度评估"""
        # 因素1: 任务描述长度
        length_score = Complexity.LOW
        if len(user_input) > self.router_config["complexity_threshold"]["high"]:
            length_score = Complexity.HIGH
        elif len(user_input) > 50:
            length_score = Complexity.MEDIUM

        # 因素2: 是否涉及多领域
        domain_score = Complexity.LOW
        if len(user_input.split()) > 5 and any(
            kw in user_input.lower()
            for kw in ["并且", "以及", "还有", "和", "and", ","]
        ):
            domain_score = Complexity.HIGH

        # 因素3: 特殊任务类型
        special_score = Complexity.LOW
        if intent in [Intent.DATA_ANALYSIS, Intent.STRATEGY]:
            special_score = Complexity.MEDIUM

        # 综合评估
        scores = [length_score, domain_score, special_score]
        if scores.count(Complexity.HIGH) >= 2:
            return Complexity.HIGH
        elif scores.count(Complexity.MEDIUM) >= 2:
            return Complexity.MEDIUM
        else:
            return Complexity.LOW

    def route(self, user_input: str) -> RoutingResult:
        """执行路由决策"""

        # Step 1: 需求分拣
        if self.is_simple_consultation(user_input):
            return RoutingResult(
                decision="直接回复",
                target="NONE",
                target_name="N/A",
                intent="简单咨询",
                complexity="低",
                reason="简单问候/感谢"
            )

        # Step 2: 意图识别
        intent = self.recognize_intent(user_input)

        # Step 3: 复杂度评估
        complexity = self.evaluate_complexity(user_input, intent)

        # Step 4: 路由决策
        return self._make_routing_decision(user_input, intent, complexity)

    def _make_routing_decision(
        self,
        user_input: str,
        intent: Intent,
        complexity: Complexity
    ) -> RoutingResult:
        """路由决策逻辑"""

        # 规则1: 技术类任务 + 纯技术实现 → L3B (Gstack)
        if intent == Intent.TECH_ENGINEERING:
            if any(kw in user_input.lower() for kw in ["审查", "review", "测试"]):
                return RoutingResult(
                    decision="技术审查",
                    target=RoutingTarget.L3B.value,
                    target_name="/review",
                    intent=intent.value,
                    complexity=complexity.value,
                    reason="代码审查任务"
                )
            return RoutingResult(
                decision="技术研发",
                target=RoutingTarget.L3B.value,
                target_name="/codex",
                intent=intent.value,
                complexity=complexity.value,
                reason="技术开发任务"
            )

        # 规则2: 通用功能开发 → L3C (独立 Agents)
        if any(kw in user_input.lower() for kw in ["实现", "开发", "构建", "create"]):
            if complexity == Complexity.LOW:
                return RoutingResult(
                    decision="通用开发",
                    target=RoutingTarget.L3C.value,
                    target_name="gsd-executor",
                    intent=intent.value,
                    complexity=complexity.value,
                    reason="通用功能开发"
                )

        # 规则3: 复杂任务 → L2 (PM + Strategy)
        if complexity == Complexity.HIGH:
            return RoutingResult(
                decision="复杂任务",
                target=RoutingTarget.L2.value,
                target_name="PM",
                intent=intent.value,
                complexity=complexity.value,
                reason="高复杂度任务需要协调"
            )

        # 规则4: 中等复杂度 + 非技术 → L2 (简单协调)
        if complexity == Complexity.MEDIUM:
            return RoutingResult(
                decision="中等任务",
                target=RoutingTarget.L2.value,
                target_name="PM",
                intent=intent.value,
                complexity=complexity.value,
                reason="中等复杂度任务"
            )

        # 规则5: 默认 → L3A (CyberTeam 部门)
        dept_map = {
            Intent.DATA_ANALYSIS: "数据分析部",
            Intent.CONTENT_OPS: "内容运营部",
            Intent.TECH_ENGINEERING: "技术研发部",
            Intent.SECURITY: "安全合规部",
            Intent.STRATEGY: "战略规划部",
            Intent.HR: "人力资源部",
            Intent.OPERATIONS: "运营支持部"
        }

        return RoutingResult(
            decision="部门执行",
            target=RoutingTarget.L3A.value,
            target_name=dept_map.get(intent, "战略规划部"),
            intent=intent.value,
            complexity=complexity.value,
            reason="直接路由到部门"
        )


def main():
    """CLI 测试"""
    import sys

    router = CEORouter()

    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
    else:
        user_input = input("输入任务描述: ")

    result = router.route(user_input)

    print("\n" + "=" * 50)
    print("CEO 路由结果")
    print("=" * 50)
    print(f"决策: {result.decision}")
    print(f"目标: {result.target} → {result.target_name}")
    print(f"意图: {result.intent}")
    print(f"复杂度: {result.complexity}")
    print(f"理由: {result.reason}")


if __name__ == "__main__":
    main()
