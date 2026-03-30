"""数学计算工具示例。

本模块演示如何使用 BaseTool 创建简单的数学计算工具。
包含：
- AddParams: 加法参数模型
- AddTool: 加法工具
- MultiplyParams: 乘法参数模型
- MultiplyTool: 乘法工具

使用示例：
    # 直接使用
    params = AddParams(a=1, b=2)
    tool = AddTool()
    result = await tool.execute({}, params)
    print(result.output)  # 3

    # 通过工厂调用
    factory = ToolFactory.get_instance()
    result = await factory.run_tool("add", {}, a=1, b=2)
"""

from pydantic import BaseModel, Field

from backend.app.tools import BaseTool, ToolResult, tool


class AddParams(BaseModel):
    """加法工具参数。"""
    a: int = Field(description="第一个数字")
    b: int = Field(description="第二个数字")


class AddTool(BaseTool[AddParams]):
    """加法工具 - 计算两个数的和。"""

    name = "add"
    description = "Add two numbers and return the sum"
    params_class = AddParams

    async def execute(self, context, params: AddParams) -> ToolResult:
        """执行加法计算。

        Args:
            context: 执行上下文（此处未使用）
            params: AddParams 实例，已通过 Pydantic 验证

        Returns:
            ToolResult: 包含 a + b 的结果
        """
        result = params.a + params.b
        return ToolResult(
            success=True,
            output={
                'operation': 'add',
                'operands': [params.a, params.b],
                'result': result
            }
        )


class MultiplyParams(BaseModel):
    """乘法工具参数。"""
    a: int = Field(description="第一个数字")
    b: int = Field(description="第二个数字")


class MultiplyTool(BaseTool[MultiplyParams]):
    """乘法工具 - 计算两个数的乘积。"""

    name = "multiply"
    description = "Multiply two numbers and return the product"
    params_class = MultiplyParams

    async def execute(self, context, params: MultiplyParams) -> ToolResult:
        """执行乘法计算。

        Args:
            context: 执行上下文
            params: MultiplyParams 实例

        Returns:
            ToolResult: 包含 a * b 的结果
        """
        result = params.a * params.b
        return ToolResult(
            success=True,
            output={
                'operation': 'multiply',
                'operands': [params.a, params.b],
                'result': result
            }
        )