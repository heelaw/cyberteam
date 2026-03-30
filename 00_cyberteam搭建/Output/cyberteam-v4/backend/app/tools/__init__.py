"""CyberTeam V4 工具系统导出。

本包提供完整的工具工厂系统：
- BaseTool: 工具基类，支持 Pydantic 参数验证
- ToolResult: 统一结果封装
- ToolFactory: 自动发现 + 延迟加载
- ToolRegistry: 全局工具注册表
- 错误类: ToolValidationError, ToolExecutionError, ToolNotFoundError

使用示例：
    from backend.app.tools import (
        BaseTool, ToolResult,
        ToolFactory, ToolRegistry,
        ToolValidationError, ToolExecutionError,
        tool
    )

    # 创建工具
    class AddParams(BaseModel):
        a: int
        b: int

    @tool(name="add", description="Add two numbers", params_model=AddParams)
    class AddTool(BaseTool[AddParams]):
        async def execute(self, context, params):
            return ToolResult(success=True, output=params.a + params.b)

    # 注册和运行
    factory = ToolFactory.get_instance()
    factory.auto_discover("/path/to/tools")

    result = await factory.run_tool("add", {}, a=1, b=2)
"""

from .base import BaseTool, ToolResult, tool
from .tool_factory import ToolFactory
from .registry import ToolRegistry, get_registry, register_tool, get_tool, list_tools
from .errors import (
    ToolValidationError,
    ToolExecutionError,
    ToolNotFoundError,
    ToolRegistrationError
)

__all__ = [
    # 核心类
    'BaseTool',
    'ToolResult',
    'ToolFactory',
    'ToolRegistry',

    # 装饰器
    'tool',

    # 便捷函数
    'get_registry',
    'register_tool',
    'get_tool',
    'list_tools',

    # 错误类
    'ToolValidationError',
    'ToolExecutionError',
    'ToolNotFoundError',
    'ToolRegistrationError',
]