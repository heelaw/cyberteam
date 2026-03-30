"""工具注册表 - 全局工具注册与管理。

ToolRegistry 提供全局工具注册表功能：
1. 单例模式：全局只有一个注册表实例
2. 工具注册：register(tool)
3. 工具获取：get(name)
4. 工具列举：list_all()
5. 工具检查：has(name)
6. 批量注册：register_many(tools)

使用示例：
    registry = ToolRegistry.get_instance()

    # 注册工具
    registry.register(MyTool())

    # 获取工具
    tool = registry.get("my_tool")

    # 列举所有工具
    all_tools = registry.list_all()

    # 批量注册
    registry.register_many([tool1, tool2])
"""

from __future__ import annotations

from typing import Optional
from collections.abc import Sequence

from .base import BaseTool, ToolResult


class ToolRegistry:
    """全局工具注册表。

    提供工具的注册、获取、列举等基本管理功能。
    采用单例模式，确保全局只有一个注册表实例。

    Attributes:
        _instance: 单例实例
        _tools: 工具字典 {name -> BaseTool instance}
    """

    _instance: Optional['ToolRegistry'] = None
    _tools: dict[str, BaseTool]

    def __init__(self):
        """初始化注册表（建议使用 get_instance）。"""
        self._tools: dict[str, BaseTool] = {}

    @classmethod
    def get_instance(cls) -> 'ToolRegistry':
        """获取 ToolRegistry 单例。"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """重置单例（主要用于测试）。"""
        cls._instance = None
        cls._tools = {}

    def register(self, tool: BaseTool) -> None:
        """注册工具。

        Args:
            tool: BaseTool 子类实例

        Raises:
            TypeError: 如果 tool 不是 BaseTool 实例
            ValueError: 如果工具名称为空
        """
        if not isinstance(tool, BaseTool):
            raise TypeError(
                f"tool must be a BaseTool instance, got {type(tool)}"
            )

        if not tool.name:
            raise ValueError("tool.name cannot be empty")

        self._tools[tool.name] = tool

    def register_many(self, tools: Sequence[BaseTool]) -> int:
        """批量注册工具。

        Args:
            tools: BaseTool 实例序列

        Returns:
            成功注册的工具数量
        """
        count = 0
        for tool in tools:
            try:
                self.register(tool)
                count += 1
            except (TypeError, ValueError):
                # 跳过无效工具
                continue
        return count

    def get(self, name: str) -> Optional[BaseTool]:
        """获取工具实例。

        Args:
            name: 工具名称

        Returns:
            BaseTool 实例，或 None（如果工具不存在）
        """
        return self._tools.get(name)

    def has(self, name: str) -> bool:
        """检查工具是否已注册。

        Args:
            name: 工具名称

        Returns:
            True 如果工具已注册
        """
        return name in self._tools

    def list_all(self) -> list[str]:
        """列出所有已注册工具名称。

        Returns:
            工具名称列表
        """
        return list(self._tools.keys())

    def list_loaded(self) -> list[dict]:
        """列出所有已注册工具的详细信息。

        Returns:
            工具信息列表
        """
        return [
            {
                'name': tool.name,
                'description': tool.description,
                'has_params_class': tool.params_class is not None
            }
            for tool in self._tools.values()
        ]

    def unregister(self, name: str) -> bool:
        """取消注册工具。

        Args:
            name: 工具名称

        Returns:
            True 如果工具被移除，False 如果工具不存在
        """
        if name in self._tools:
            del self._tools[name]
            return True
        return False

    def clear(self) -> None:
        """清空注册表。"""
        self._tools.clear()

    def count(self) -> int:
        """获取已注册工具数量。

        Returns:
            工具数量
        """
        return len(self._tools)

    def get_by_prefix(self, prefix: str) -> list[BaseTool]:
        """获取名称以指定前缀开头的所有工具。

        Args:
            prefix: 名称前缀

        Returns:
            匹配的工具列表
        """
        return [
            tool for tool in self._tools.values()
            if tool.name.startswith(prefix)
        ]

    async def execute(self, name: str, context: Any, **params) -> ToolResult:
        """便捷方法：注册并执行工具。

        Args:
            name: 工具名称
            context: 执行上下文
            **params: 工具参数

        Returns:
            ToolResult: 执行结果

        Raises:
            ValueError: 如果工具不存在
        """
        tool = self.get(name)
        if tool is None:
            raise ValueError(f"Tool '{name}' not found in registry")

        return await tool(context, **params)


# 全局便捷函数
def get_registry() -> ToolRegistry:
    """获取全局工具注册表实例。"""
    return ToolRegistry.get_instance()


def register_tool(tool: BaseTool) -> None:
    """全局注册工具。"""
    ToolRegistry.get_instance().register(tool)


def get_tool(name: str) -> Optional[BaseTool]:
    """全局获取工具。"""
    return ToolRegistry.get_instance().get(name)


def list_tools() -> list[str]:
    """全局列举所有工具名称。"""
    return ToolRegistry.get_instance().list_all()