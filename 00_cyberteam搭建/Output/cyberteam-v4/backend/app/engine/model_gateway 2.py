"""多模型网关 - 按任务类型自动选模型（抄 Magic）。

设计理念：
- 决策层（CEO/COO）用最强模型，保证决策质量
- 协调层（PM）用平衡模型，兼顾质量和成本
- 执行层用快速模型，提高吞吐量
- 支持 economy 模式，在预算紧张时自动降级

模型映射策略：
- normal: 按任务类型匹配最优模型
- economy: 全部降级到更便宜的模型
- custom: 支持通过配置覆盖默认映射
"""

from typing import Dict, Optional
import logging

log = logging.getLogger("cyberteam.engine.model_gateway")


class ModelGateway:
    """按任务类型自动选择模型。

    用法:
        gateway = ModelGateway()
        model = gateway.resolve("ceo_route")  # -> "claude-opus-4-6"
        model = gateway.resolve("ceo_route", budget_tier="economy")  # -> "claude-sonnet-4-6"
    """

    # 标准模式：按任务类型匹配模型
    MODEL_MAP: Dict[str, str] = {
        # 决策层 - 用最强模型
        "ceo_route": "claude-opus-4-6",
        "coo_planning": "claude-sonnet-4-6",
        "ceo_review": "claude-opus-4-6",
        # 协调层 - 用平衡模型
        "pm_dispatch": "claude-sonnet-4-6",
        # 执行层 - 用快速模型
        "dept_execution": "claude-haiku-4-5",
        "marketing": "claude-sonnet-4-6",
        "engineering": "claude-sonnet-4-6",
        # 辩论 - 用平衡模型
        "debate": "claude-sonnet-4-6",
        # 质量检查 - 用快速模型
        "quality_gate": "claude-haiku-4-5",
        # 质疑者 - 用平衡模型
        "socratic_question": "claude-sonnet-4-6",
        # 内容生成
        "content_generation": "claude-haiku-4-5",
        "code_generation": "claude-opus-4-6",
        # 分析类
        "analysis": "claude-sonnet-4-6",
        "research": "claude-sonnet-4-6",
    }

    # 经济模式：降级映射
    ECONOMY_MAP: Dict[str, str] = {
        "ceo_route": "claude-sonnet-4-6",
        "coo_planning": "claude-haiku-4-5",
        "ceo_review": "claude-sonnet-4-6",
        "pm_dispatch": "claude-haiku-4-5",
        "dept_execution": "claude-haiku-4-5",
        "debate": "claude-haiku-4-5",
        "socratic_question": "claude-haiku-4-5",
        "content_generation": "claude-haiku-4-5",
        "code_generation": "claude-sonnet-4-6",
    }

    # 默认模型
    DEFAULT_MODEL = "claude-sonnet-4-6"
    ECONOMY_DEFAULT = "claude-haiku-4-5"

    def __init__(self):
        self._custom_map: Dict[str, str] = {}

    def resolve(self, task_type: str, budget_tier: str = "normal") -> str:
        """根据任务类型和预算层级选择模型。

        Args:
            task_type: 任务类型（如 ceo_route, dept_execution）
            budget_tier: 预算层级（normal/economy）

        Returns:
            模型标识符
        """
        # 优先使用自定义映射
        custom_key = f"{task_type}:{budget_tier}"
        if custom_key in self._custom_map:
            model = self._custom_map[custom_key]
            log.debug(f"Custom model resolved: {task_type} [{budget_tier}] -> {model}")
            return model

        # 标准映射逻辑
        if budget_tier == "economy":
            model = self.ECONOMY_MAP.get(task_type, self.ECONOMY_DEFAULT)
        else:
            model = self.MODEL_MAP.get(task_type, self.DEFAULT_MODEL)

        log.debug(f"Model resolved: {task_type} [{budget_tier}] -> {model}")
        return model

    def set_custom(self, task_type: str, model: str, budget_tier: str = "normal") -> None:
        """设置自定义模型映射。"""
        key = f"{task_type}:{budget_tier}"
        self._custom_map[key] = model
        log.info(f"Custom model mapping set: {key} -> {model}")

    def get_all_mappings(self) -> Dict[str, str]:
        """获取所有模型映射。"""
        return dict(self.MODEL_MAP)

    def get_economy_mappings(self) -> Dict[str, str]:
        """获取经济模式映射。"""
        return dict(self.ECONOMY_MAP)

    def get_custom_mappings(self) -> Dict[str, str]:
        """获取自定义映射。"""
        return dict(self._custom_map)

    def clear_custom_mappings(self) -> None:
        """清除所有自定义映射。"""
        self._custom_map.clear()
        log.info("Custom model mappings cleared")


# 全局单例
model_gateway = ModelGateway()
