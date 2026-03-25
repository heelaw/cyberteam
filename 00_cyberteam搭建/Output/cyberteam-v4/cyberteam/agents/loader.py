"""CyberTeam Agent 加载器。

自动扫描并注册所有 Agent。
"""

import importlib
import pkgutil
from pathlib import Path
from typing import List, Optional, Type

from cyberteam.agents.base import BaseAgent, ThinkingExpert, SpecializedAgent, AgentMetadata
from cyberteam.agents.registry import AgentRegistry, get_registry


class AgentLoader:
    """Agent 加载器

    扫描 agents/ 目录，自动注册所有 Agent。
    """

    def __init__(self, base_path: Optional[Path] = None):
        if base_path is None:
            # 默认路径
            self.base_path = Path(__file__).parent
        else:
            self.base_path = base_path

    def scan_thinking_experts(self) -> List[str]:
        """扫描并注册思维专家"""
        registry = get_registry()
        registered = []

        thinking_path = self.base_path / "thinking"
        if not thinking_path.exists():
            return registered

        for module_info in pkgutil.iter_modules([str(thinking_path)]):
            module_name = module_info.name
            try:
                # 动态导入模块
                module = importlib.import_module(
                    f"cyberteam.agents.thinking.{module_name}"
                )

                # 查找模块中的 Agent 类
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, ThinkingExpert)
                        and attr != ThinkingExpert
                    ):
                        # 创建实例并注册
                        instance = attr()
                        registry.register(
                            name=instance.metadata.name,
                            agent_class=attr,
                            metadata=instance.metadata,
                            category="thinking"
                        )
                        registered.append(instance.metadata.name)

            except Exception as e:
                print(f"Warning: Failed to load thinking expert {module_name}: {e}")

        return registered

    def scan_specialized_agents(self) -> List[str]:
        """扫描并注册专业 Agent"""
        registry = get_registry()
        registered = []

        specialized_path = self.base_path / "specialized"
        if not specialized_path.exists():
            return registered

        for module_info in pkgutil.iter_modules([str(specialized_path)]):
            module_name = module_info.name
            try:
                module = importlib.import_module(
                    f"cyberteam.agents.specialized.{module_name}"
                )

                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, SpecializedAgent)
                        and attr != SpecializedAgent
                    ):
                        instance = attr()
                        registry.register(
                            name=instance.metadata.name,
                            agent_class=attr,
                            metadata=instance.metadata,
                            category="specialized"
                        )
                        registered.append(instance.metadata.name)

            except Exception as e:
                print(f"Warning: Failed to load specialized agent {module_name}: {e}")

        return registered

    def load_all(self) -> int:
        """加载所有 Agent，返回加载数量"""
        total = 0
        total += len(self.scan_thinking_experts())
        total += len(self.scan_specialized_agents())
        return total

    @staticmethod
    def list_agents(category: Optional[str] = None) -> List[str]:
        """列出已注册的 Agent"""
        return get_registry().list_agents(category)

    @staticmethod
    def get_agent(name: str) -> Optional[BaseAgent]:
        """获取 Agent 实例"""
        registry = get_registry()
        agent_class = registry.get_agent_class(name)
        if agent_class:
            return agent_class()
        return None

    @staticmethod
    def spawn_agent(name: str, **kwargs) -> Optional[BaseAgent]:
        """创建 Agent 实例"""
        agent = AgentLoader.get_agent(name)
        if agent:
            agent.initialize()
        return agent


# 全局加载器实例
_default_loader: Optional[AgentLoader] = None


def get_loader() -> AgentLoader:
    """获取全局加载器"""
    global _default_loader
    if _default_loader is None:
        _default_loader = AgentLoader()
    return _default_loader


def list_agents(category: Optional[str] = None) -> List[str]:
    """列出所有已注册的 Agent"""
    return AgentLoader.list_agents(category)


def get_agent(name: str) -> Optional[BaseAgent]:
    """获取 Agent 实例"""
    return AgentLoader.get_agent(name)


def spawn_agent(name: str, **kwargs) -> Optional[BaseAgent]:
    """创建 Agent 实例"""
    return AgentLoader.spawn_agent(name, **kwargs)
