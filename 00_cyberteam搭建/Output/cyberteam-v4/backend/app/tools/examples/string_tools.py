"""字符串处理工具示例。

本模块演示如何使用 BaseTool 创建字符串处理工具。
包含：
- UpperCaseParams: 大写转换参数
- UpperCaseTool: 大写转换工具
- LowerCaseParams: 小写转换参数
- LowerCaseTool: 小写转换工具

使用示例：
    params = UpperCaseParams(text="hello")
    tool = UpperCaseTool()
    result = await tool.execute({}, params)
    print(result.output)  # "HELLO"
"""

from pydantic import BaseModel, Field

from backend.app.tools import BaseTool, ToolResult


class UpperCaseParams(BaseModel):
    """大写转换工具参数。"""
    text: str = Field(description="要转换的文本")


class UpperCaseTool(BaseTool[UpperCaseParams]):
    """大写转换工具 - 将文本转换为大写。"""

    name = "uppercase"
    description = "Convert text to uppercase"
    params_class = UpperCaseParams

    async def execute(self, context, params: UpperCaseParams) -> ToolResult:
        """执行大写转换。

        Args:
            context: 执行上下文
            params: UpperCaseParams 实例

        Returns:
            ToolResult: 包含转换后的文本
        """
        return ToolResult(
            success=True,
            output={
                'original': params.text,
                'uppercased': params.text.upper()
            }
        )


class LowerCaseParams(BaseModel):
    """小写转换工具参数。"""
    text: str = Field(description="要转换的文本")


class LowerCaseTool(BaseTool[LowerCaseParams]):
    """小写转换工具 - 将文本转换为小写。"""

    name = "lowercase"
    description = "Convert text to lowercase"
    params_class = LowerCaseParams

    async def execute(self, context, params: LowerCaseParams) -> ToolResult:
        """执行小写转换。

        Args:
            context: 执行上下文
            params: LowerCaseParams 实例

        Returns:
            ToolResult: 包含转换后的文本
        """
        return ToolResult(
            success=True,
            output={
                'original': params.text,
                'lowercased': params.text.lower()
            }
        )