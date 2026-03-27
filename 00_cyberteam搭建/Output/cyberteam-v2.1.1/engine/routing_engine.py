# CyberTeam v2.0.1 - 任务路由引擎
"""
路由引擎：将用户意图 + 思维专家选择 → Agent任务分配
承上: thinking_injector.py 的输出
启下: ClawTeam spawn + Agent执行
"""

import json
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

from .thinking_injector import ThinkingContext, Expert


@dataclass
class RoutingRule:
    """路由规则"""
    name: str
    triggers: List[str]           # 触发关键词
    agents: List[str]              # 匹配的Agent ID列表
    priority: int = 1             # 优先级 (数字越大越高)
    required_experts: List[str] = field(default_factory=list)  # 必需的思维专家


@dataclass
class AgentSpec:
    """Agent规格"""
    id: str
    name: str
    name_cn: str
    category: str                 # expert / department / china_platform
    focus_areas: List[str]
    trigger_keywords: List[str]
    tools: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    max_concurrent: int = 2


@dataclass
class RouteResult:
    """路由结果"""
    selected_agents: List[AgentSpec]
    task_assignments: List[Dict[str, Any]]
    reasoning_chain: List[str]
    confidence: float = 0.0


class RoutingEngine:
    """
    任务路由引擎

    输入: ThinkingContext (来自 thinking_injector)
    输出: RouteResult (Agent分配方案)

    工作流程:
    1. 分析意图 + 专家选择结果
    2. 匹配路由规则 (routing.yaml)
    3. 生成Agent任务分配方案
    4. 输出 spawn 指令
    """

    def __init__(self, routing_config_path: str = None):
        self.config_path = routing_config_path or str(
            Path(__file__).parent.parent / "config" / "routing.yaml"
        )
        self.agents: Dict[str, AgentSpec] = {}
        self.rules: List[RoutingRule] = []
        self._load_config()

    def _load_config(self):
        """加载路由配置"""
        try:
            import yaml
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            self._load_agents(config.get("agents", []))
            self._load_rules(config.get("rules", []))
        except (FileNotFoundError, ImportError, Exception):
            self._load_builtin()

    def _load_builtin(self):
        """内置路由配置 (无yaml依赖时)"""
        self.agents = BUILTIN_AGENTS
        self.rules = BUILTIN_RULES

    def _load_builtin_json(self):
        """内置JSON路由配置"""
        pass

    def _load_agents(self, agent_configs: List[Dict]):
        """加载Agent配置"""
        for cfg in agent_configs:
            agent = AgentSpec(
                id=cfg["id"],
                name=cfg.get("name", cfg["id"]),
                name_cn=cfg.get("name_cn", cfg["id"]),
                category=cfg.get("category", "general"),
                focus_areas=cfg.get("focus_areas", []),
                trigger_keywords=cfg.get("triggers", []),
                tools=cfg.get("tools", []),
                skills=cfg.get("skills", []),
                max_concurrent=cfg.get("max_concurrent", 2)
            )
            self.agents[agent.id] = agent

    def _load_rules(self, rule_configs: List[Dict]):
        """加载路由规则"""
        for cfg in rule_configs:
            rule = RoutingRule(
                name=cfg["name"],
                triggers=cfg.get("triggers", []),
                agents=cfg.get("agents", []),
                priority=cfg.get("priority", 1),
                required_experts=cfg.get("required_experts", [])
            )
            self.rules.append(rule)

    def route(self, thinking_ctx: ThinkingContext, user_goal: str = "") -> RouteResult:
        """
        核心方法：对 ThinkingContext 进行路由决策

        Args:
            thinking_ctx: 思维注入引擎的输出
            user_goal: 原始用户目标

        Returns:
            RouteResult: 包含选中的Agent和任务分配
        """
        reasoning = []
        reasoning.append("=== 路由决策 ===")

        # Step 1: 分析意图 + 专家
        selected_experts = thinking_ctx.selected_experts
        expert_categories = {e.category for e in selected_experts}
        expert_ids = {e.id for e in selected_experts}
        reasoning.append(f"激活专家类别: {expert_categories}")
        reasoning.append(f"激活专家: {[e.name_cn for e in selected_experts]}")

        # Step 2: 意图分类 (从thinking_injector继承)
        intents = self._classify_from_experts(selected_experts)
        reasoning.append(f"推断意图: {intents}")

        # Step 3: 匹配路由规则
        matched_rules = self._match_rules(
            user_goal + " " + " ".join(expert_categories),
            intents,
            expert_ids
        )
        reasoning.append(f"匹配规则: {[r.name for r in matched_rules]}")

        # Step 4: 选择Agent
        selected_agents = self._select_agents(matched_rules, selected_experts)
        reasoning.append(f"选中Agent: {[a.id for a in selected_agents]}")

        # Step 5: 生成任务分配
        assignments = self._generate_assignments(
            selected_agents, selected_experts, thinking_ctx, user_goal
        )
        reasoning.append(f"生成任务: {len(assignments)}个")

        # Step 6: 计算置信度
        confidence = self._calculate_confidence(
            selected_agents, matched_rules, selected_experts
        )
        reasoning.append(f"路由置信度: {confidence:.1%}")

        return RouteResult(
            selected_agents=selected_agents,
            task_assignments=assignments,
            reasoning_chain=reasoning,
            confidence=confidence
        )

    def _classify_from_experts(self, experts: List[Expert]) -> List[str]:
        """从选中的专家推断意图"""
        categories = [e.category for e in experts]
        intents = []

        if "strategy" in categories:
            intents.append("strategy")
        if "growth" in categories or "execution" in categories:
            intents.append("growth")
        if "product" in categories or "analysis" in categories:
            intents.append("product")
        if "creative" in categories:
            intents.append("creative")
        if "management" in categories:
            intents.append("management")
        if "decision" in categories:
            intents.append("decision")

        return intents or ["general"]

    def _match_rules(
        self,
        text: str,
        intents: List[str],
        expert_ids: set
    ) -> List[RoutingRule]:
        """匹配路由规则"""
        matched = []

        for rule in self.rules:
            score = 0

            # 意图匹配
            for intent in intents:
                if intent in rule.triggers:
                    score += 3

            # 专家匹配
            for req_exp in rule.required_experts:
                if req_exp in expert_ids:
                    score += 2

            # 关键词匹配
            for trigger in rule.triggers:
                if trigger in text.lower():
                    score += 1

            if score > 0:
                matched.append((rule, score))

        # 按分数排序
        matched.sort(key=lambda x: -x[1])
        return [r for r, s in matched]

    def _select_agents(
        self,
        rules: List[RoutingRule],
        experts: List[Expert]
    ) -> List[AgentSpec]:
        """选择最合适的Agent"""
        candidates = {}

        for rule in rules[:3]:  # 取top 3规则
            for agent_id in rule.agents:
                if agent_id in self.agents:
                    candidates[agent_id] = self.agents[agent_id]

        # 如果没有匹配规则，用专家类别推断
        if not candidates:
            expert_cats = {e.category for e in experts}
            candidates = self._infer_agents_from_category(expert_cats)

        return list(candidates.values())[:5]  # 最多5个Agent

    def _infer_agents_from_category(self, categories: set) -> Dict[str, AgentSpec]:
        """从专家类别推断需要的Agent"""
        mapping = {
            "strategy": ["strategy-director", "investor-agent"],
            "product": ["product-director", "product-agent"],
            "execution": ["tech-director", "eng-agent"],
            "creative": ["design-director", "design-agent"],
            "growth": ["marketing-director", "ops-agent"],
            "management": ["hr-agent"],
        }
        result = {}
        for cat in categories:
            for agent_id in mapping.get(cat, []):
                if agent_id in self.agents:
                    result[agent_id] = self.agents[agent_id]
        return result

    def _generate_assignments(
        self,
        agents: List[AgentSpec],
        experts: List[Expert],
        thinking_ctx: ThinkingContext,
        user_goal: str
    ) -> List[Dict[str, Any]]:
        """生成Agent任务分配"""
        assignments = []
        assignment_id = 1

        for agent in agents:
            # 过滤相关的思维专家
            relevant_experts = [
                e for e in experts
                if e.category in agent.focus_areas
                or any(kw in " ".join(agent.focus_areas) for kw in [e.category])
            ]

            assignment = {
                "id": f"task-{assignment_id:03d}",
                "agent_id": agent.id,
                "agent_name": agent.name_cn,
                "goal": self._formulate_goal(agent, user_goal),
                "thinking_injection": [
                    f"- {e.name_cn}: {e.description}"
                    for e in relevant_experts[:3]
                ],
                "output_format": self._get_output_format(agent.category),
                "quality_gate": "L2",
                "pua_enabled": True,
            }
            assignments.append(assignment)
            assignment_id += 1

        return assignments

    def _formulate_goal(self, agent: AgentSpec, user_goal: str) -> str:
        """为Agent生成任务目标"""
        goal_templates = {
            "expert": "针对目标「{goal}」，运用你的专业知识深入分析并给出方案",
            "department": "执行「{goal}」相关的{area}任务，输出可直接交付的结果",
            "china_platform": "基于「{goal}」，制定{area}平台的具体运营策略",
        }
        template = goal_templates.get(agent.category, goal_templates["department"])
        return template.format(
            goal=user_goal,
            area=" / ".join(agent.focus_areas[:2])
        )

    def _get_output_format(self, category: str) -> Dict[str, Any]:
        """获取输出格式规范"""
        formats = {
            "expert": {
                "type": "analysis_report",
                "sections": ["现状分析", "问题诊断", "方案建议", "行动计划"],
                "required_evidence": True
            },
            "department": {
                "type": "execution_result",
                "sections": ["执行结果", "交付物", "数据指标", "下一步"],
                "required_evidence": True
            },
            "china_platform": {
                "type": "platform_strategy",
                "sections": ["平台分析", "内容策略", "执行计划", "ROI预估"],
                "required_evidence": True
            }
        }
        return formats.get(category, formats["department"])

    def _calculate_confidence(
        self,
        agents: List[AgentSpec],
        rules: List[RoutingRule],
        experts: List[Expert]
    ) -> float:
        """计算路由置信度"""
        if not agents:
            return 0.0

        # 规则匹配率
        rule_score = min(len(rules) / 3, 1.0) * 0.4

        # 专家覆盖率
        expert_score = min(len(experts) / 3, 1.0) * 0.3

        # Agent选择合理性 (是否有匹配的focus)
        agent_score = min(len(agents) / 3, 1.0) * 0.3

        return rule_score + expert_score + agent_score

    def generate_spawn_commands(self, result: RouteResult) -> List[Dict[str, str]]:
        """生成 ClawTeam spawn 命令"""
        commands = []
        for assignment in result.task_assignments:
            cmd = {
                "agent_name": assignment["agent_id"],
                "prompt": self._build_spawn_prompt(assignment),
                "type": "general-purpose"
            }
            commands.append(cmd)
        return commands

    def _build_spawn_prompt(self, assignment: Dict) -> str:
        """构建spawn prompt"""
        parts = [
            f"# 任务: {assignment['goal']}",
            f"# Agent: {assignment['agent_name']}",
            "\n## 思维注入",
            "\n".join(assignment["thinking_injection"]),
            f"\n## 输出格式: {assignment['output_format']['type']}",
            f"## 质量门控: {assignment['quality_gate']}",
            "\n## PUA机制",
            "当执行层表现不佳时，自动升级压力等级。",
            "L1: 温和失望 → L2: 追问原因 → L3: 质疑能力 → L4: 要求重做",
        ]
        return "\n".join(parts)


# ============================================================
# 内置Agent配置 (无yaml时使用)
# ============================================================

BUILTIN_AGENTS: Dict[str, AgentSpec] = {}

# 管理层Agent (来自layers/management/)
for _id, _cfg in [
    ("strategy-director", {"name": "战略总监", "cat": "department", "focus": ["战略规划", "竞争分析", "商业模式"]}),
    ("product-director", {"name": "产品总监", "cat": "department", "focus": ["产品规划", "需求管理", "产品迭代"]}),
    ("tech-director", {"name": "技术总监", "cat": "department", "focus": ["技术架构", "技术选型", "研发管理"]}),
    ("design-director", {"name": "设计总监", "cat": "department", "focus": ["设计战略", "设计系统", "用户体验"]}),
    ("ops-director", {"name": "运营总监", "cat": "department", "focus": ["运营策略", "流程优化", "效率提升"]}),
    ("finance-director", {"name": "财务总监", "cat": "department", "focus": ["财务规划", "成本控制", "投资决策"]}),
    ("marketing-director", {"name": "市场总监", "cat": "department", "focus": ["市场策略", "品牌推广", "增长获客"]}),
    ("hr-director", {"name": "人力总监", "cat": "department", "focus": ["人才战略", "组织设计", "文化建设"]}),
]:
    BUILTIN_AGENTS[_id] = AgentSpec(
        id=_id,
        name=_id,
        name_cn=_cfg["name"],
        category=_cfg["cat"],
        focus_areas=_cfg["focus"],
        trigger_keywords=_cfg["focus"],
    )

# v2.1运营专家Agent
for _id, _cfg in [
    ("investor-agent", {"name": "投资人专家", "focus": ["TAM/SAM/SOM", "六维评估", "财务尽职调查"]}),
    ("strategy-agent", {"name": "策略专家", "focus": ["竞争策略", "市场破局", "杠杆破局点"]}),
    ("incentive-agent", {"name": "激励专家", "focus": ["增长飞轮", "留存策略", "激励体系"]}),
    ("framework-agent", {"name": "框架专家", "focus": ["MECE分析", "金字塔原理", "问题拆解"]}),
    ("planning-agent", {"name": "规划专家", "focus": ["里程碑设定", "进度追踪", "复盘方法"]}),
    ("activity-agent", {"name": "活动专家", "focus": ["活动策划", "运营日历", "事件营销"]}),
    ("newmedia-agent", {"name": "新媒体专家", "focus": ["内容矩阵", "平台运营", "短文案"]}),
    ("teamwork-agent", {"name": "团队管理专家", "focus": ["协作流程", "知识管理", "效率优化"]}),
]:
    BUILTIN_AGENTS[_id] = AgentSpec(
        id=_id,
        name=_id,
        name_cn=_cfg["name"],
        category="expert",
        focus_areas=_cfg["focus"],
        trigger_keywords=_cfg["focus"],
    )

# 内置路由规则
BUILTIN_RULES = [
    RoutingRule(
        name="战略规划",
        triggers=["战略", "竞争", "规划", "商业模式", "strategy"],
        agents=["strategy-director", "investor-agent"],
        priority=3,
        required_experts=["swot-tows", "porters-five", "bcg-matrix"]
    ),
    RoutingRule(
        name="产品设计",
        triggers=["产品", "功能", "需求", "设计", "product"],
        agents=["product-director"],
        priority=3,
        required_experts=["first-principle", "design-thinking"]
    ),
    RoutingRule(
        name="技术开发",
        triggers=["技术", "开发", "代码", "架构", "技术选型"],
        agents=["tech-director", "eng-agent"],
        priority=3,
        required_experts=["first-principle"]
    ),
    RoutingRule(
        name="增长获客",
        triggers=["增长", "获客", "用户", "DAU", "变现", "growth"],
        agents=["marketing-director", "ops-director", "incentive-agent"],
        priority=3,
        required_experts=["growth", "aarrr"]
    ),
    RoutingRule(
        name="内容运营",
        triggers=["内容", "新媒体", "文案", "种草", "短视频"],
        agents=["newmedia-agent"],
        priority=2,
        required_experts=[]
    ),
    RoutingRule(
        name="活动运营",
        triggers=["活动", "策划", "运营日历", "事件营销"],
        agents=["activity-agent"],
        priority=2,
        required_experts=[]
    ),
    RoutingRule(
        name="财务分析",
        triggers=["财务", "预算", "成本", "ROI", "投资"],
        agents=["finance-director", "investor-agent"],
        priority=2,
        required_experts=["dcfl"]
    ),
    RoutingRule(
        name="团队管理",
        triggers=["团队", "组织", "管理", "招聘", "人力"],
        agents=["hr-director", "teamwork-agent"],
        priority=2,
        required_experts=["mckinsey-7s", "kotter"]
    ),
]


# ============================================================
# 快速测试
# ============================================================
if __name__ == "__main__":
    from thinking_injector import ThinkingInjector

    injector = ThinkingInjector()
    router = RoutingEngine()

    test_cases = [
        "我想做一个在线教育平台，目标是一年内10万付费用户",
        "帮我分析竞争对手的SWOT",
        "制定抖音内容运营策略",
    ]

    for goal in test_cases:
        print(f"\n{'='*60}")
        print(f"目标: {goal}")
        ctx = injector.process(goal)
        result = router.route(ctx, goal)
        print(f"路由置信度: {result.confidence:.1%}")
        print(f"选中Agent: {[a.name_cn for a in result.selected_agents]}")
        print(f"任务数: {len(result.task_assignments)}")
        for a in result.task_assignments:
            print(f"  → {a['id']} @ {a['agent_name']}")
