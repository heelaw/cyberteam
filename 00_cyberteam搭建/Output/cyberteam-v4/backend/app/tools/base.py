"""工具基类 - Pydantic 参数验证 + 统一调用入口。

本模块定义了 CyberTeam V4 工具系统的核心抽象：
- BaseTool: 所有工具的基类，支持泛型参数 TParams（Pydantic BaseModel）
- ToolResult: 工具执行结果的统一封装
- @tool 装饰器: 用于注册工具类

核心特性：
1. 泛型参数验证：TParams 必须是 Pydantic BaseModel 子类
2. 延迟加载：工具实例化时才真正导入模块
3. OpenAI Function Calling 格式转换
4. 苏格拉底式错误提示（通过 ToolValidationError）
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TypeVar, Generic, Any, Callable, Type, get_type_hints, get_origin, get_args
from pydantic import BaseModel, ValidationError, create_model
from pydantic.fields import FieldInfo

from .errors import ToolValidationError

# 泛型参数 TParams必须是 Pydantic BaseModel
TParams = TypeVar('TParams', bound=BaseModel)


@dataclass
class ToolResult:
    """工具执行结果统一封装。"""
    success: bool
    output: Any = None
    error: str = None
    execution_time_ms: float = 0.0

    def to_dict(self) -> dict:
        """转换为字典格式。"""
        return {
            'success': self.success,
            'output': self.output,
            'error': self.error,
            'execution_time_ms': round(self.execution_time_ms, 2)
        }


class BaseTool(ABC, Generic[TParams]):
    """工具基类，泛型参数 TParams 必须是 Pydantic BaseModel。

    使用示例：
        class AddParams(BaseModel):
            a: int
            b: int

        class AddTool(BaseTool[AddParams]):
            name = "add"
            description = "Add two numbers"
            params_class = AddParams

            async def execute(self, context: Any, params: AddParams) -> ToolResult:
                return ToolResult(success=True, output=params.a + params.b)

    """

    # 类属性（子类必须覆盖）
    name: str = ""
    description: str = ""
    params_class: Type[TParams] = None

    # 内部状态
    _registered_callbacks: list[Callable] = field(default_factory=list, repr=False)

    def __init_subclass__(cls, **kwargs):
        """注册时检查泛型参数是否合法。"""
        super().__init_subclass__(**kwargs)

        # 获取泛型参数的原始类型
        origin = get_origin(cls)
        if origin is not None:
            args = get_args(origin)
            if args:
                param_type = args[0]
                # 检查是否是 Pydantic BaseModel 的子类
                if not (isinstance(param_type, type) and issubclass(param_type, BaseModel)):
                    raise TypeError(
                        f"BaseTool[{param_type}] 的泛型参数必须是 Pydantic BaseModel 的子类，"
                        f"got {param_type}"
                    )

    def to_openai_format(self) -> dict:
        """转换为 OpenAI Function Calling 格式。"""
        if self.params_class is None:
            raise ValueError(f"Tool '{self.name}' must define params_class")

        schema = self.params_class.model_json_schema()

        # 确保 parameters 包含 type
        if 'type' not in schema:
            schema['type'] = 'object'

        return {
            'name': self.name,
            'description': self.description,
            'parameters': schema
        }

    def _find_similar_params(self, validation_error: ValidationError) -> list[tuple[str, float]]:
        """根据验证错误找到相似的正确参数名。

        Args:
            validation_error: Pydantic 验证异常

        Returns:
            [(参数名, 相似度分数), ...] 按相似度降序排列
        """
        from difflib import get_close_matches

        if self.params_class is None:
            return []

        # 获取所有有效的字段名
        valid_fields = list(self.params_class.model_fields.keys())

        similar = []
        for error in validation_error.errors():
            # 获取错误位置（可能是嵌套的）
            loc = error.get('loc', [])
            if loc:
                # 取最后一个位置作为参数名
                field_name = str(loc[-1])
                # 找到相似的参数名
                matches = get_close_matches(field_name, valid_fields, n=3, cutoff=0.5)
                for match in matches:
                    # 计算相似度分数（简化版）
                    score = 0.8 if field_name in match or match in field_name else 0.6
                    similar.append((match, score))

        return similar

    async def __call__(self, context: Any, **kwargs) -> ToolResult:
        """统一调用入口：参数验证 + 执行。

        Args:
            context: 执行上下文（可以是任何对象）
            **kwargs: 工具参数字典

        Returns:
            ToolResult: 执行结果

        Raises:
            ToolValidationError: 参数验证失败时抛出
        """
        start = time.time()

        # Step 1: 参数验证
        try:
            validated = self.params_class(**kwargs)
        except ValidationError as e:
            # Pydantic 验证失败 → 苏格拉底式追问
            similar = self._find_similar_params(e)
            raise ToolValidationError(
                tool_name=self.name,
                errors=e.errors(),
                similar_params=similar,
                expected_signature=str(self.params_class.model_json_schema().get('type', 'object'))
            )

        # Step 2: 执行工具
        try:
            result = await self.execute(context, validated)
            result.execution_time_ms = (time.time() - start) * 1000
            return result
        except Exception as ex:
            from .errors import ToolExecutionError
            raise ToolExecutionError(
                tool_name=self.name,
                reason=str(ex)
            )

    @abstractmethod
    async def execute(self, context: Any, params: TParams) -> ToolResult:
        """执行工具，返回 ToolResult。

        Args:
            context: 执行上下文
            params: 已经过 Pydantic 验证的参数对象

        Returns:
            ToolResult: 执行结果
        """
        pass

    def register_callback(self, callback: Callable) -> None:
        """注册工具执行完成后的回调函数。

        Args:
            callback: 回调函数，签名为 (ToolResult) -> None
        """
        self._registered_callbacks.append(callback)

    def _notify_callbacks(self, result: ToolResult) -> None:
        """通知所有回调函数。"""
        for callback in self._registered_callbacks:
            try:
                callback(result)
            except Exception:
                pass  # 回调异常不影响主流程


def tool(name: str, description: str, params_model: Type[BaseModel]) -> Callable:
    """工具装饰器 - 用于自动注册工具。

    使用示例：
        @tool(name="add", description="Add two numbers", params_model=AddParams)
        class AddTool(BaseTool[AddParams]):
            params_class = AddParams

            async def execute(self, context, params):
                return ToolResult(success=True, output=params.a + params.b)

    Args:
        name: 工具名称
        description: 工具描述
        params_model: Pydantic 参数模型类

    Returns:
        装饰器函数
    """
    def decorator(cls: Type[BaseTool]) -> Type[BaseTool]:
        # 动态设置类属性
        cls.name = name
        cls.description = description
        cls.params_class = params_model
        return cls

    return decorator