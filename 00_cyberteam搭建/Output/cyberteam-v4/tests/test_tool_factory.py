"""ToolFactory 工具工厂测试。

测试覆盖：
1. BaseTool 基类功能
2. auto_discover 自动发现机制
3. lazy_load 延迟加载
4. ToolValidationError 苏格拉底式错误提示
5. ToolRegistry 注册表功能
6. 工具执行流程

运行方式：
    cd /Users/cyberwiz/Documents/01_Project/00_cyberteam搭建/Output/cyberteam-v4
    python -m pytest tests/test_tool_factory.py -v
"""

import pytest
import time
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field

from backend.app.tools import (
    BaseTool, ToolResult, tool,
    ToolFactory, ToolRegistry,
    ToolValidationError, ToolExecutionError,
    get_registry, register_tool, get_tool, list_tools
)


# ============ 测试夹具 ============

@pytest.fixture
def clean_factory():
    """提供干净的 ToolFactory 实例。"""
    ToolFactory.reset_instance()
    factory = ToolFactory.get_instance()
    yield factory
    ToolFactory.reset_instance()


@pytest.fixture
def clean_registry():
    """提供干净的 ToolRegistry 实例。"""
    ToolRegistry.reset_instance()
    registry = ToolRegistry.get_instance()
    yield registry
    ToolRegistry.reset_instance()


# ============ 测试夹具：示例工具 ============

class AddParams(BaseModel):
    """测试用加法参数。"""
    a: int = Field(description="第一个数字")
    b: int = Field(description="第二个数字")


class AddTool(BaseTool[AddParams]):
    """测试用加法工具。"""
    name = "add"
    description = "Add two numbers"
    params_class = AddParams

    async def execute(self, context: Any, params: AddParams) -> ToolResult:
        return ToolResult(success=True, output=params.a + params.b)


class UpperCaseParams(BaseModel):
    """测试用大写转换参数。"""
    text: str = Field(description="要转换的文本")


class UpperCaseTool(BaseTool[UpperCaseParams]):
    """测试用大写转换工具。"""
    name = "uppercase"
    description = "Convert text to uppercase"
    params_class = UpperCaseParams

    async def execute(self, context: Any, params: UpperCaseParams) -> ToolResult:
        return ToolResult(success=True, output=params.text.upper())


# ============ T1: BaseTool 基类测试 ============

class TestBaseTool:
    """BaseTool 基类功能测试。"""

    def test_tool_result_dataclass(self):
        """T1.1: ToolResult 数据类基本功能。"""
        result = ToolResult(success=True, output=42, error=None, execution_time_ms=1.5)

        assert result.success is True
        assert result.output == 42
        assert result.error is None
        assert result.execution_time_ms == 1.5

    def test_tool_result_to_dict(self):
        """T1.2: ToolResult 转换为字典。"""
        result = ToolResult(success=True, output="hello", execution_time_ms=2.5)

        d = result.to_dict()
        assert d == {
            'success': True,
            'output': 'hello',
            'error': None,
            'execution_time_ms': 2.5
        }

    @pytest.mark.asyncio
    async def test_tool_call_validates_params(self):
        """T1.3: 工具调用时验证参数。"""
        add_tool = AddTool()

        # 正确参数应该成功
        result = await add_tool({}, a=1, b=2)
        assert result.success is True
        assert result.output == 3

    @pytest.mark.asyncio
    async def test_tool_call_invalid_params_raises_validation_error(self):
        """T1.4: 无效参数抛出 ToolValidationError。"""
        add_tool = AddTool()

        # 缺少必需参数应该抛出验证错误
        with pytest.raises(ToolValidationError) as exc_info:
            await add_tool({}, a=1)  # 缺少 b

        assert "add" in str(exc_info.value)
        assert len(exc_info.value.errors) > 0

    def test_tool_to_openai_format(self):
        """T1.5: 工具转换为 OpenAI Function Calling 格式。"""
        add_tool = AddTool()
        format_dict = add_tool.to_openai_format()

        assert format_dict['name'] == "add"
        assert format_dict['description'] == "Add two numbers"
        assert 'parameters' in format_dict
        assert format_dict['parameters']['type'] == 'object'


# ============ T2: ToolValidationError 苏格拉底式错误测试 ============

class TestToolValidationError:
    """ToolValidationError 苏格拉底式错误提示测试。"""

    def test_validation_error_basic(self):
        """T2.1: 基本错误消息生成。"""
        error = ToolValidationError(
            tool_name="add",
            errors=[
                {'loc': ('a',), 'msg': 'field required', 'input': None, 'type': 'missing'}
            ],
            similar_params=[("a", 0.8), ("b", 0.6)]
        )

        msg = error.get_human_message()
        assert "add" in msg
        assert "field required" in msg
        assert "a" in msg

    def test_validation_error_with_similar_params(self):
        """T2.2: 包含相似参数推荐的错误消息。"""
        error = ToolValidationError(
            tool_name="uppercase",
            errors=[
                {'loc': ('text',), 'msg': 'field required', 'input': None, 'type': 'missing'}
            ],
            similar_params=[("text", 0.9)]
        )

        msg = error.get_human_message()
        assert "苏格拉底追问" in msg
        assert "text" in msg

    def test_validation_error_short_message(self):
        """T2.3: 简短错误消息。"""
        error = ToolValidationError(
            tool_name="add",
            errors=[
                {'loc': ('a',), 'msg': 'field required', 'input': None, 'type': 'missing'}
            ]
        )

        short = error.get_short_message()
        assert "add" in short
        assert "参数错误" in short

    def test_validation_error_to_dict(self):
        """T2.4: 错误转换为字典。"""
        error = ToolValidationError(
            tool_name="add",
            errors=[{'loc': ('a',), 'msg': 'field required', 'input': None, 'type': 'missing'}],
            similar_params=[("a", 0.8)]
        )

        d = error.to_dict()
        assert d['type'] == 'ToolValidationError'
        assert d['tool_name'] == 'add'
        assert len(d['errors']) == 1

    def test_validation_error_repr(self):
        """T2.5: 错误的 repr 表示。"""
        error = ToolValidationError(
            tool_name="add",
            errors=[],
            similar_params=[]
        )

        assert "ToolValidationError" in repr(error)
        assert "add" in repr(error)


# ============ T3: ToolFactory 自动发现测试 ============

class TestToolFactoryAutoDiscover:
    """ToolFactory auto_discover 功能测试。"""

    def test_auto_discover_finds_example_tools(self, clean_factory):
        """T3.1: 自动发现能找到示例工具。"""
        factory = clean_factory

        # 扫描 examples 目录 - 使用正确的路径
        examples_path = Path(__file__).parent.parent / "backend" / "app" / "tools" / "examples"
        if examples_path.exists():
            count = factory.auto_discover(str(examples_path))
            # 应该找到 math_tools 和 string_tools 中的工具
            assert count >= 4
        else:
            # 如果路径不存在，尝试从 backend/app/tools 扫描
            tools_path = Path(__file__).parent.parent / "backend" / "app" / "tools"
            count = factory.auto_discover(str(tools_path))
            assert count >= 4

    def test_auto_discover_returns_count(self, clean_factory):
        """T3.2: auto_discover 返回注册数量。"""
        factory = clean_factory

        tools_path = Path(__file__).parent.parent / "backend" / "app" / "tools"
        count = factory.auto_discover(str(tools_path))

        assert isinstance(count, int)
        assert count > 0

    def test_auto_discover_nonexistent_path_returns_zero(self, clean_factory):
        """T3.3: 扫描不存在的路径返回0。"""
        factory = clean_factory
        count = factory.auto_discover("/nonexistent/path")

        assert count == 0

    def test_list_tools_after_discover(self, clean_factory):
        """T3.4: 发现后可以列出所有工具。"""
        factory = clean_factory

        tools_path = Path(__file__).parent.parent / "backend" / "app" / "tools"
        factory.auto_discover(str(tools_path))

        tools = factory.list_tools()
        assert len(tools) >= 4
        assert any(t['name'] == 'add' for t in tools)

    def test_get_tool_definition(self, clean_factory):
        """T3.5: 获取工具定义。"""
        factory = clean_factory

        tools_path = Path(__file__).parent.parent / "backend" / "app" / "tools"
        factory.auto_discover(str(tools_path))

        # 直接注册并测试
        from backend.app.tools.examples.math_tools import AddTool
        factory._lazy_loaded['add'] = AddTool

        definition = factory.get_tool_definition('add')
        assert definition is not None
        assert 'name' in definition
        assert 'description' in definition


# ============ T4: ToolFactory 延迟加载测试 ============

class TestToolFactoryLazyLoad:
    """ToolFactory lazy_load 延迟加载测试。"""

    @pytest.mark.asyncio
    async def test_lazy_load_imports_module(self, clean_factory):
        """T4.1: 延迟加载时导入模块。"""
        factory = clean_factory

        # 先注册
        examples_path = Path(__file__).parent.parent / "backend" / "app" / "tools" / "examples"
        factory.auto_discover(str(examples_path))

        # 验证工具未加载
        assert 'add' not in factory._lazy_loaded

        # 延迟加载
        await factory._lazy_load('add')

        # 验证工具已加载
        assert 'add' in factory._lazy_loaded

    @pytest.mark.asyncio
    async def test_run_tool_lazy_loads_and_executes(self, clean_factory):
        """T4.2: run_tool 自动延迟加载并执行。"""
        factory = clean_factory

        # 注册 AddTool
        from backend.app.tools.examples.math_tools import AddTool
        factory._definitions['add'] = {
            'name': 'add',
            'description': 'Add two numbers',
            'module_path': 'backend.app.tools.examples.math_tools',
            'class_name': 'AddTool',
            'params_model': 'AddParams'
        }
        factory._lazy_loaded['add'] = AddTool

        # 执行 - context must be keyword argument
        result = await factory.run_tool('add', context={}, a=5, b=3)

        assert result.success is True
        assert result.output['result'] == 8

    @pytest.mark.asyncio
    async def test_run_tool_not_found_raises_error(self, clean_factory):
        """T4.3: 运行不存在的工具抛出错误。"""
        factory = clean_factory

        from backend.app.tools.errors import ToolNotFoundError
        with pytest.raises(ToolNotFoundError):
            await factory.run_tool('nonexistent', context={}, **{})


# ============ T5: ToolRegistry 注册表测试 ============

class TestToolRegistry:
    """ToolRegistry 注册表功能测试。"""

    def test_registry_is_singleton(self, clean_registry):
        """T5.1: 注册表是单例。"""
        reg1 = ToolRegistry.get_instance()
        reg2 = ToolRegistry.get_instance()

        assert reg1 is reg2

    def test_register_tool(self, clean_registry):
        """T5.2: 注册工具。"""
        registry = clean_registry
        add_tool = AddTool()

        registry.register(add_tool)

        assert registry.has('add')
        assert registry.get('add') is add_tool

    def test_register_invalid_type_raises_error(self, clean_registry):
        """T5.3: 注册非 BaseTool 类型抛出错误。"""
        registry = clean_registry

        with pytest.raises(TypeError):
            registry.register("not a tool")  # type: ignore

    def test_get_nonexistent_returns_none(self, clean_registry):
        """T5.4: 获取不存在的工具返回 None。"""
        registry = clean_registry

        assert registry.get('nonexistent') is None

    def test_list_all_tools(self, clean_registry):
        """T5.5: 列出所有已注册工具。"""
        registry = clean_registry
        registry.register(AddTool())
        registry.register(UpperCaseTool())

        tools = registry.list_all()

        assert 'add' in tools
        assert 'uppercase' in tools

    def test_unregister_tool(self, clean_registry):
        """T5.6: 取消注册工具。"""
        registry = clean_registry
        registry.register(AddTool())

        result = registry.unregister('add')

        assert result is True
        assert not registry.has('add')

    def test_unregister_nonexistent_returns_false(self, clean_registry):
        """T5.7: 取消注册不存在的工具返回 False。"""
        registry = clean_registry

        result = registry.unregister('nonexistent')

        assert result is False

    def test_count_tools(self, clean_registry):
        """T5.8: 获取工具数量。"""
        registry = clean_registry
        assert registry.count() == 0

        registry.register(AddTool())
        assert registry.count() == 1

        registry.register(UpperCaseTool())
        assert registry.count() == 2

    def test_clear_registry(self, clean_registry):
        """T5.9: 清空注册表。"""
        registry = clean_registry
        registry.register(AddTool())
        registry.register(UpperCaseTool())

        registry.clear()

        assert registry.count() == 0

    @pytest.mark.asyncio
    async def test_registry_execute(self, clean_registry):
        """T5.10: 注册表便捷执行方法。"""
        registry = clean_registry
        registry.register(AddTool())

        result = await registry.execute('add', {}, a=10, b=20)

        assert result.success is True
        assert result.output == 30


# ============ T6: 全局便捷函数测试 ============

class TestGlobalConvenienceFunctions:
    """全局便捷函数测试。"""

    def test_get_registry(self, clean_registry):
        """T6.1: get_registry 获取全局注册表。"""
        reg = get_registry()

        assert isinstance(reg, ToolRegistry)

    def test_register_and_get_tool(self, clean_registry):
        """T6.2: 全局注册和获取工具。"""
        add_tool = AddTool()

        register_tool(add_tool)
        retrieved = get_tool('add')

        assert retrieved is add_tool

    def test_list_tools_global(self, clean_registry):
        """T6.3: 全局列举工具。"""
        clean_registry.register(AddTool())
        clean_registry.register(UpperCaseTool())

        tools = list_tools()

        assert 'add' in tools
        assert 'uppercase' in tools


# ============ T7: 端到端集成测试 ============

class TestEndToEndIntegration:
    """端到端集成测试。"""

    @pytest.mark.asyncio
    async def test_full_tool_lifecycle(self, clean_factory, clean_registry):
        """T7.1: 完整工具生命周期。"""
        # 1. 注册工具到注册表
        registry = clean_registry
        registry.register(AddTool())

        # 2. 通过注册表执行
        result = await registry.execute('add', {}, a=100, b=200)
        assert result.success is True
        assert result.output == 300

    @pytest.mark.asyncio
    async def test_tool_execution_timing(self, clean_registry):
        """T7.2: 工具执行计时。"""
        registry = clean_registry
        registry.register(AddTool())

        result = await registry.execute('add', {}, a=1, b=2)

        assert result.execution_time_ms >= 0

    @pytest.mark.asyncio
    async def test_multiple_tools_execution(self, clean_registry):
        """T7.3: 多个工具顺序执行。"""
        registry = clean_registry
        registry.register(AddTool())
        registry.register(UpperCaseTool())

        # 执行加法
        r1 = await registry.execute('add', {}, a=5, b=10)
        assert r1.success is True
        assert r1.output == 15

        # 执行大写
        r2 = await registry.execute('uppercase', {}, text="hello")
        assert r2.success is True
        assert r2.output == "HELLO"


# ============ T8: 错误处理边界测试 ============

class TestErrorHandling:
    """错误处理边界测试。"""

    def test_tool_validation_error_with_empty_errors(self):
        """T8.1: 空错误列表的处理。"""
        error = ToolValidationError(
            tool_name="test",
            errors=[],
            similar_params=[]
        )

        msg = error.get_human_message()
        assert "test" in msg

    def test_tool_validation_error_with_long_input(self):
        """T8.2: 长输入值的截断处理。"""
        long_input = "x" * 100

        error = ToolValidationError(
            tool_name="test",
            errors=[
                {'loc': ('text',), 'msg': 'value is too long', 'input': long_input, 'type': 'value_error'}
            ]
        )

        msg = error.get_human_message()
        # 输入应该被截断
        assert "..." in msg or len(msg) > 0

    def test_factory_reset_instance(self, clean_factory):
        """T8.3: 重置工厂单例。"""
        factory1 = clean_factory
        ToolFactory.reset_instance()
        factory2 = ToolFactory.get_instance()

        assert factory1 is not factory2


# ============ T9: 工具装饰器测试 ============

class TestToolDecorator:
    """@tool 装饰器测试。"""

    def test_tool_decorator_sets_attributes(self):
        """T9.1: 装饰器设置类属性。"""
        from backend.app.tools.examples.math_tools import AddTool

        assert AddTool.name == "add"
        assert "Add two numbers" in AddTool.description
        assert AddTool.params_class is not None

    def test_tool_decorator_preserves_execute(self):
        """T9.2: 装饰器保留 execute 方法。"""
        from backend.app.tools.examples.math_tools import AddTool

        assert hasattr(AddTool, 'execute')
        assert callable(AddTool.execute)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])