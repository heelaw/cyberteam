"""MCP 工具注册表 - 本地化实现"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
import logging


logger = logging.getLogger(__name__)


@dataclass
class ToolDefinition:
    """工具定义"""
    name: str
    description: str
    input_schema: Dict[str, Any] = field(default_factory=dict)
    handler: Optional[Callable] = field(default=None, repr=False)
    source: str = "local"  # local, mcp, custom
    metadata: Dict[str, Any] = field(default_factory=dict)


class ToolRegistry:
    """MCP 工具注册表

    统一管理所有 MCP 工具的注册和调用。
    """

    _instance: Optional["ToolRegistry"] = None
    _tools: Dict[str, ToolDefinition] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._register_builtin_tools()
            self._initialized = True

    def _register_builtin_tools(self) -> None:
        """注册内置工具"""
        # 文件系统工具
        from cyberteam.mcp import filesystem
        self.register(filesystem.read_file_tool)
        self.register(filesystem.write_file_tool)
        self.register(filesystem.list_directory_tool)
        self.register(filesystem.search_files_tool)
        self.register(filesystem.get_file_info_tool)

        # Web 搜索工具
        from cyberteam.mcp import web_search
        self.register(web_search.web_search_tool)
        self.register(web_search.web_fetch_tool)

        # 图像理解工具
        from cyberteam.mcp import image_understanding
        self.register(image_understanding.understand_image_tool)

        # 代码执行工具
        from cyberteam.mcp import code_execution
        self.register(code_execution.execute_python_tool)
        self.register(code_execution.execute_bash_tool)

        # CDP 浏览器工具 (web-access skill 集成)
        from cyberteam.mcp import cdp_browser
        self.register(cdp_browser.cdp_check_deps_tool)
        self.register(cdp_browser.cdp_list_targets_tool)
        self.register(cdp_browser.cdp_new_tab_tool)
        self.register(cdp_browser.cdp_eval_tool)
        self.register(cdp_browser.cdp_click_tool)
        self.register(cdp_browser.cdp_scroll_tool)
        self.register(cdp_browser.cdp_screenshot_tool)
        self.register(cdp_browser.cdp_close_tab_tool)
        self.register(cdp_browser.cdp_navigate_tool)

    def register(self, tool: ToolDefinition) -> None:
        """注册工具

        Args:
            tool: 工具定义
        """
        self._tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name}")

    def unregister(self, name: str) -> bool:
        """注销工具

        Args:
            name: 工具名称

        Returns:
            是否成功注销
        """
        if name in self._tools:
            del self._tools[name]
            return True
        return False

    def get(self, name: str) -> Optional[ToolDefinition]:
        """获取工具定义

        Args:
            name: 工具名称

        Returns:
            工具定义
        """
        return self._tools.get(name)

    def get_handler(self, name: str) -> Optional[Callable]:
        """获取工具处理函数

        Args:
            name: 工具名称

        Returns:
            处理函数
        """
        tool = self._tools.get(name)
        return tool.handler if tool else None

    def list_all(self) -> List[ToolDefinition]:
        """列出所有工具

        Returns:
            工具定义列表
        """
        return list(self._tools.values())

    def list_by_source(self, source: str) -> List[ToolDefinition]:
        """按来源列出工具

        Args:
            source: 工具来源

        Returns:
            工具定义列表
        """
        return [t for t in self._tools.values() if t.source == source]

    def search(self, query: str) -> List[ToolDefinition]:
        """搜索工具

        Args:
            query: 搜索关键词

        Returns:
            匹配的工具列表
        """
        query_lower = query.lower()
        results = []
        for tool in self._tools.values():
            if (query_lower in tool.name.lower() or
                query_lower in tool.description.lower()):
                results.append(tool)
        return results

    @classmethod
    def list_all_tools(cls) -> List[Dict[str, Any]]:
        """列出所有工具（兼容接口）

        Returns:
            工具列表
        """
        instance = cls()
        return [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.input_schema,
                "source": t.source
            }
            for t in instance._tools.values()
        ]

    def clear(self) -> None:
        """清空注册表"""
        self._tools.clear()

    def __repr__(self) -> str:
        return f"ToolRegistry(tools={len(self._tools)})"


# 便捷函数
def register_tool(name: str, description: str, handler: Callable,
                 input_schema: Optional[Dict[str, Any]] = None,
                 source: str = "custom") -> None:
    """注册工具的便捷函数

    Args:
        name: 工具名称
        description: 工具描述
        handler: 处理函数
        input_schema: 输入模式
        source: 来源
    """
    tool = ToolDefinition(
        name=name,
        description=description,
        input_schema=input_schema or {},
        handler=handler,
        source=source
    )
    ToolRegistry().register(tool)


def get_tool(name: str) -> Optional[ToolDefinition]:
    """获取工具定义

    Args:
        name: 工具名称

    Returns:
        工具定义
    """
    return ToolRegistry().get(name)


def list_tools() -> List[Dict[str, Any]]:
    """列出所有工具

    Returns:
        工具列表
    """
    return ToolRegistry.list_all_tools()


__all__ = ["ToolRegistry", "ToolDefinition", "register_tool", "get_tool", "list_tools"]