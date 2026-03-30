"""示例工具包。

本包包含使用 BaseTool 基类的示例工具，用于演示：
1. 如何定义 Pydantic 参数模型
2. 如何继承 BaseTool 实现工具
3. 如何使用 @tool 装饰器
4. 如何进行参数验证

示例工具：
- MathTools: 数学计算工具（加减乘除）
- StringTools: 字符串处理工具
"""

from .math_tools import AddTool, MultiplyTool
from .string_tools import UpperCaseTool, LowerCaseTool

__all__ = [
    'AddTool',
    'MultiplyTool',
    'UpperCaseTool',
    'LowerCaseTool',
]