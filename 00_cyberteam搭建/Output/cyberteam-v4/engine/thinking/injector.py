"""
思维注入器 - 将思维模型注入到 Agent 的决策过程中

核心思想：
- Agent 在做决策时，可以注入一个或多个思维模型
- 思维模型以 prompt 的形式注入
- Agent 会按照思维模型的框架进行思考
"""

from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass
from .models import ThinkingModel, ThinkingResult, ModelCombination, TaskContext
from .router import ThinkingRouter, RoutingResult


@dataclass
class InjectionContext:
    """注入上下文"""
    agent_name: str              # Agent 名称
    agent_role: str             # Agent 角色 (PM/运营/技术等)
    task: str                    # 当前任务
    additional_context: Optional[Dict[str, Any]] = None


class ThinkingInjector:
    """
    思维注入器

    使用方式：
        injector = ThinkingInjector()
        injector.load_models()

        # 方式1: 自动路由注入
        result = injector.inject_auto(
            agent_name="PM Agent",
            agent_role="产品管理",
            context=TaskContext(...)
        )

        # 方式2: 手动指定模型注入
        result = injector.inject_manual(
            agent_name="PM Agent",
            agent_role="产品管理",
            task="分析用户增长策略",
            model_ids=["first-principle", "swot-tows"]
        )

        # 获取注入后的 prompt
        print(result.injected_prompt)
    """

    def __init__(self, router: Optional[ThinkingRouter] = None):
        self.router = router
        self._loaded = False

    def load_models(self) -> int:
        """加载所有思维模型"""
        if self.router is None:
            from .loader import ThinkingLoader
            loader = ThinkingLoader()
            self.router = ThinkingRouter(loader)

        models = self.router.loader.load_all()
        self._loaded = True
        return len(models)

    def inject_auto(self, context: InjectionContext) -> "InjectionResult":
        """
        自动路由注入 - 根据任务上下文自动选择思维模型

        Args:
            context: 注入上下文

        Returns:
            InjectionResult: 包含注入的 prompt 和元数据
        """
        if not self._loaded:
            self.load_models()

        # 构建任务上下文
        task_context = TaskContext(
            task_description=context.task,
            intent=self._infer_intent(context),
            complexity=self._infer_complexity(context),
            domain=self._infer_domain(context),
        )

        # 路由选择
        routing_result = self.router.route(task_context)

        # 构建注入 prompt
        injected_prompt = self._build_injected_prompt(
            context=context,
            routing_result=routing_result
        )

        return InjectionResult(
            success=True,
            injected_prompt=injected_prompt,
            models_used=[m.id for m in routing_result.combination.models],
            model_names=[m.name for m in routing_result.combination.models],
            routing_reasoning=routing_result.reasoning,
            confidence=routing_result.confidence,
            task_context=task_context,
        )

    def inject_manual(
        self,
        agent_name: str,
        agent_role: str,
        task: str,
        model_ids: List[str],
        intent: str = "技术研发",
        complexity: str = "中"
    ) -> "InjectionResult":
        """
        手动指定注入 - 明确指定使用哪些思维模型

        Args:
            agent_name: Agent 名称
            agent_role: Agent 角色
            task: 当前任务
            model_ids: 要注入的模型 ID 列表
            intent: 意图类型
            complexity: 复杂度

        Returns:
            InjectionResult: 包含注入的 prompt 和元数据
        """
        if not self._loaded:
            self.load_models()

        context = InjectionContext(
            agent_name=agent_name,
            agent_role=agent_role,
            task=task
        )

        task_context = TaskContext(
            task_description=task,
            intent=intent,
            complexity=complexity,
            domain=self._infer_domain(context),
        )

        # 获取指定的模型
        models = []
        for mid in model_ids:
            model = self.router.loader.get_model(mid)
            if model:
                models.append(model)

        if not models:
            return InjectionResult(
                success=False,
                injected_prompt="",
                models_used=[],
                model_names=[],
                routing_reasoning="未找到指定的思维模型",
                confidence=0.0,
                task_context=task_context,
            )

        combination = ModelCombination(models=models, reasoning=f"手动指定: {', '.join([m.name for m in models])}")

        injected_prompt = self._build_injected_prompt(
            context=context,
            routing_result=RoutingResult(
                combination=combination,
                reasoning=f"手动指定使用: {', '.join([m.name for m in models])}",
                confidence=0.95
            )
        )

        return InjectionResult(
            success=True,
            injected_prompt=injected_prompt,
            models_used=model_ids,
            model_names=[m.name for m in models],
            routing_reasoning=f"手动指定: {', '.join([m.name for m in models])}",
            confidence=0.95,
            task_context=task_context,
        )

    def inject_for_debate(
        self,
        task: str,
        stance: str,
        models: List[str]
    ) -> str:
        """
        为辩论注入思维模型

        Args:
            task: 辩题
            stance: 立场
            models: 要使用的模型列表

        Returns:
            str: 注入后的辩论 prompt
        """
        if not self._loaded:
            self.load_models()

        model_prompts = []
        for mid in models:
            model = self.router.loader.get_model(mid)
            if model:
                model_prompts.append(model.to_prompt())

        prompt = f"""【辩论任务】
辩题：{task}
你的立场：{stance}

请运用以下思维模型进行辩论准备：
{chr(10).join(model_prompts)}

请先输出每个模型的分析，然后给出你的辩论论点。
"""
        return prompt

    def _build_injected_prompt(
        self,
        context: InjectionContext,
        routing_result: RoutingResult
    ) -> str:
        """构建完整的注入 prompt"""
        models = routing_result.combination.models

        # Header
        header = f"""【思维注入 - {context.agent_name}】
角色：{context.agent_role}
任务：{context.task}

{routing_result.reasoning}

{"="*60}
"""

        # 思维模型 prompt
        model_prompts = [m.to_prompt() for m in models]

        # Footer
        footer = f"""
{"="*60}
请先用以上思维模型分析任务，然后给出你的决策建议。
"""

        return header + "\n\n".join(model_prompts) + footer

    def _infer_intent(self, context: InjectionContext) -> str:
        """推断意图"""
        task_lower = context.task.lower()

        intent_rules = {
            "数据分析": ["分析", "数据", "统计", "增长", "ROI"],
            "内容运营": ["内容", "文案", "创作", "发布", "营销"],
            "技术研发": ["开发", "代码", "功能", "实现", "修复"],
            "安全合规": ["安全", "审计", "合规", "隐私"],
            "战略规划": ["战略", "规划", "方案", "决策"],
            "人力资源": ["招聘", "团队", "绩效", "管理"],
            "运营支持": ["运营", "流程", "优化", "效率"],
            "财务投资": ["财务", "投资", "预算", "成本"],
        }

        for intent, keywords in intent_rules.items():
            if any(kw in task_lower for kw in keywords):
                return intent

        return "技术研发"  # 默认

    def _infer_complexity(self, context: InjectionContext) -> str:
        """推断复杂度"""
        task = context.task

        # 复杂度指标
        high_complexity = ["战略", "规划", "方案", "设计", "架构", "全面", "体系"]
        low_complexity = ["简单", "快速", "基础", "日常", "常规"]

        for kw in high_complexity:
            if kw in task:
                return "高"

        for kw in low_complexity:
            if kw in task:
                return "低"

        return "中"  # 默认

    def _infer_domain(self, context: InjectionContext) -> str:
        """推断领域"""
        # 从 agent_role 推断
        role = context.agent_role.lower()

        domain_map = {
            "产品": "产品",
            "运营": "运营",
            "技术": "技术",
            "增长": "增长",
            "市场": "市场",
            "品牌": "品牌",
            "财务": "财务",
            "人力": "人力",
        }

        for key, domain in domain_map.items():
            if key in role:
                return domain

        return "通用"


@dataclass
class InjectionResult:
    """注入结果"""
    success: bool
    injected_prompt: str
    models_used: List[str]
    model_names: List[str]
    routing_reasoning: str
    confidence: float
    task_context: TaskContext
