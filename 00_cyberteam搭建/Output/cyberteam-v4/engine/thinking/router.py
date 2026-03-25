"""
思维路由 - 根据任务特征选择合适的思维模型组合

核心思想：
- 不同任务需要不同的思维模型组合
- 简单任务用单一模型
- 复杂任务用 2-3 个模型的组合
- 模型选择基于任务特征匹配
"""

from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from .models import ThinkingModel, ModelCombination, TaskContext, ModelCategory


# 意图类型到触发词的映射规则（用于匹配模型）
INTENT_TRIGGER_RULES: Dict[str, List[Tuple[str, float]]] = {
    "数据分析": [
        ("分析", 0.9),
        ("数据", 0.8),
        ("概率", 0.7),
        ("贝叶斯", 0.7),
        ("增长", 0.7),
        ("ROI", 0.6),
    ],
    "内容运营": [
        ("内容", 0.9),
        ("创作", 0.8),
        ("文案", 0.8),
        ("六顶", 0.7),
        ("营销", 0.7),
    ],
    "技术研发": [
        ("技术", 0.9),
        ("系统", 0.8),
        ("架构", 0.8),
        ("第一性原理", 0.7),
        ("逆向", 0.6),
    ],
    "安全合规": [
        ("安全", 0.9),
        ("风险", 0.8),
        ("二阶", 0.7),
        ("预演失败", 0.7),
    ],
    "战略规划": [
        ("战略", 0.9),
        ("SWOT", 0.8),
        ("五力", 0.7),
        ("博弈", 0.7),
        ("二阶", 0.6),
    ],
    "人力资源": [
        ("人力", 0.9),
        ("招聘", 0.8),
        ("团队", 0.7),
        ("绩效", 0.6),
    ],
    "运营支持": [
        ("运营", 0.9),
        ("流程", 0.8),
        ("迭代", 0.7),
        ("优化", 0.6),
    ],
    "财务投资": [
        ("财务", 0.9),
        ("投资", 0.8),
        ("成本", 0.7),
        ("机会成本", 0.7),
        ("沉没", 0.6),
    ],
}

# 复杂度到模型数量的映射
COMPLEXITY_MODEL_COUNT = {
    "低": 1,
    "中": 2,
    "高": 3,
}

# 模型互斥规则（不应该同时使用）
MUTUALLY_EXCLUSIVE = {
    frozenset(["sunk-cost", "opportunity-cost"]),  # 成本类二选一
}


@dataclass
class RoutingResult:
    """路由结果"""
    combination: ModelCombination
    reasoning: str
    confidence: float


class ThinkingRouter:
    """
    思维路由 - 根据任务特征选择思维模型组合

    使用方式：
        router = ThinkingRouter(loader)
        result = router.route(context)
        prompt = result.combination.to_prompt()
    """

    def __init__(self, loader):
        self.loader = loader
        self._model_cache: Dict[str, ThinkingModel] = {}

    def route(self, context: TaskContext) -> RoutingResult:
        """
        根据任务上下文路由到合适的思维模型组合

        Args:
            context: 任务上下文

        Returns:
            RoutingResult: 包含模型组合和路由理由
        """
        # 1. 获取意图对应的触发词规则
        intent_triggers = INTENT_TRIGGER_RULES.get(
            context.intent,
            [("分析", 0.7)]
        )

        # 2. 获取复杂度决定的模型数量
        model_count = COMPLEXITY_MODEL_COUNT.get(context.complexity, 1)

        # 3. 基于触发词匹配模型
        matched_models = self._match_models_by_triggers(
            intent_triggers, context.task_description
        )

        # 4. 如果匹配不够，按模型分类补充
        if len(matched_models) < model_count:
            category_models = self._get_models_by_category(context.intent)
            for model in category_models[:model_count - len(matched_models)]:
                if model not in matched_models:
                    matched_models.append(model)

        # 5. 选择最佳组合（考虑互斥规则）
        selected = self._select_combination_by_models(matched_models, model_count)

        # 6. 构建组合
        reasoning = self._build_reasoning(context, selected)

        combination = ModelCombination(models=selected, reasoning=reasoning)
        confidence = min(0.9, 0.5 + 0.1 * len(selected))

        return RoutingResult(
            combination=combination,
            reasoning=reasoning,
            confidence=confidence
        )

    def _match_models_by_triggers(
        self,
        triggers: List[Tuple[str, float]],
        task_text: str
    ) -> List[ThinkingModel]:
        """通过触发词列表匹配模型"""
        matched_models: List[ThinkingModel] = []
        scores: Dict[str, float] = {}

        all_models = self.loader.get_all_models()
        task_lower = task_text.lower()

        for trigger, base_score in triggers:
            trigger_lower = trigger.lower()

            for model in all_models:
                # 检查触发词是否在任务描述中
                if trigger_lower in task_lower:
                    score = base_score
                # 检查触发词是否在模型的关键词中
                elif any(trigger_lower in kw.lower() for kw in model.trigger_keywords):
                    score = base_score * 0.7
                # 检查触发词是否在模型名称中
                elif trigger_lower in model.name.lower():
                    score = base_score * 0.8
                else:
                    continue

                if model.id not in scores or scores[model.id] < score:
                    scores[model.id] = score
                    if model not in matched_models:
                        matched_models.append(model)

        # 按得分排序
        matched_models.sort(key=lambda m: scores.get(m.id, 0), reverse=True)

        return matched_models

    def _get_models_by_category(self, intent: str) -> List[ThinkingModel]:
        """根据意图获取对应分类的模型"""
        category_map = {
            "数据分析": ModelCategory.ANALYSIS,
            "内容运营": ModelCategory.CREATIVE,
            "技术研发": ModelCategory.SYSTEM,
            "安全合规": ModelCategory.EVALUATION,
            "战略规划": ModelCategory.DECISION,
            "人力资源": ModelCategory.DECISION,
            "运营支持": ModelCategory.SYSTEM,
            "财务投资": ModelCategory.ANALYSIS,
        }

        category = category_map.get(intent, ModelCategory.ANALYSIS)
        return self.loader.get_by_category(category)

    def _select_combination_by_models(
        self,
        models: List[ThinkingModel],
        count: int
    ) -> List[ThinkingModel]:
        """选择模型组合（考虑互斥规则）"""
        selected = []
        excluded_ids = set()

        for model in models:
            if len(selected) >= count:
                break

            # 检查是否被排除
            if model.id in excluded_ids:
                continue

            selected.append(model)

            # 排除互斥的模型
            for exclusive_pair in MUTUALLY_EXCLUSIVE:
                if model.id in exclusive_pair:
                    excluded_ids.update(exclusive_pair - {model.id})

        return selected

    def _build_reasoning(self, context: TaskContext, models: List[ThinkingModel]) -> str:
        """构建路由理由"""
        model_names = [m.name for m in models]
        return (
            f"任务「{context.task_description[:20]}...」"
            f"（意图：{context.intent}，复杂度：{context.complexity}）"
            f"选用思维模型：{', '.join(model_names)}"
        )

    def get_recommendations(self, context: TaskContext, top_n: int = 5) -> List[str]:
        """获取推荐模型 ID 列表"""
        intent_triggers = INTENT_TRIGGER_RULES.get(context.intent, [("分析", 0.7)])
        matched_models = self._match_models_by_triggers(
            intent_triggers, context.task_description
        )
        return [m.id for m in matched_models[:top_n]]
