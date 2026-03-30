"""工具工厂 - 自动发现 + 延迟加载 + 缓存。

ToolFactory 是 CyberTeam V4 工具系统的核心组件：
1. auto_discover: 扫描目录，自动注册 @tool 装饰的工具（不导入）
2. lazy_load: 真正使用时才导入模块（延迟加载）
3. 预构建定义缓存：避免每次启动重新扫描
4. 工具执行：统一入口，自动参数验证

核心设计：
- 单例模式：全局只有一个 ToolFactory 实例
- 延迟加载：工具模块在第一次调用时才导入
- 自动发现：扫描指定目录下的所有工具定义

使用示例：
    factory = ToolFactory.get_instance()

    # 自动发现工具（扫描目录，不导入）
    factory.auto_discover("/path/to/tools")

    # 获取工具定义（OpenAI 格式）
    definition = factory.get_tool_definition("add")
    print(definition)

    # 运行工具（自动延迟加载 + 参数验证）
    result = await factory.run_tool("add", context={}, a=1, b=2)
    print(result)
"""

from __future__ import annotations

import os
import re
import ast
import time
import inspect
import importlib
from pathlib import Path
from typing import Optional, Any, Callable
from collections.abc import Callable as ABCCallable

from .base import BaseTool, ToolResult
from .errors import ToolNotFoundError, ToolExecutionError


# 全局单例
_instance: Optional['ToolFactory'] = None


class ToolFactory:
    """
    工具工厂 - 自动发现 + 延迟加载 + 缓存。

    核心功能：
    1. auto_discover: 扫描目录找到所有 @tool 装饰的工具
    2. lazy_load: 第一次调用时才导入工具模块
    3. run_tool: 统一执行入口
    4. get_tool_definition: 获取工具的 OpenAI Function Calling 格式

    Attributes:
        _definitions: 工具定义缓存 {name -> definition}
        _lazy_loaded: 已延迟加载的工具类 {name -> class}
        _executors: 预注册的同步执行器 {name -> callable}
        _discovered: 是否已完成自动发现
    """

    _instance: Optional['ToolFactory'] = None

    def __init__(self, cache_path: Optional[str] = None):
        """
        Args:
            cache_path: 可选的缓存文件路径（暂未实现）
        """
        self._definitions: dict[str, dict] = {}  # name -> definition
        self._lazy_loaded: dict[str, type[BaseTool]] = {}  # name -> class
        self._executors: dict[str, Callable] = {}  # name -> sync executor
        self._discovered: bool = False
        self._cache_path = cache_path
        self._discover_paths: list[str] = []

    @classmethod
    def get_instance(cls) -> 'ToolFactory':
        """获取 ToolFactory 单例。"""
        global _instance
        if _instance is None:
            _instance = cls()
        return _instance

    @classmethod
    def reset_instance(cls) -> None:
        """重置单例（主要用于测试）。"""
        global _instance
        _instance = None

    def auto_discover(self, base_path: str) -> int:
        """扫描目录，自动注册所有 @tool 装饰的工具。

        扫描策略：
        1. 递归遍历 base_path 下所有 .py 文件
        2. 解析 AST 找到 @tool 装饰器
        3. 提取元数据（name, description, params_model）
        4. 不导入模块，只记录定义（延迟加载）

        Args:
            base_path: 扫描的基础目录路径

        Returns:
            注册的工具数量
        """
        base = Path(base_path)
        if not base.exists():
            return 0

        count = 0
        self._discover_paths.append(str(base))

        # 递归扫描所有 .py 文件
        for py_file in base.rglob("*.py"):
            # 跳过 __init__.py 和 __pycache__
            if "__pycache__" in str(py_file):
                continue

            try:
                discovered = self._scan_file(py_file)
                count += discovered
            except Exception as e:
                # 扫描失败不影响其他文件
                print(f"[ToolFactory] Warning: Failed to scan {py_file}: {e}")

        self._discovered = True
        return count

    def _scan_file(self, py_file: Path) -> int:
        """扫描单个 Python 文件，提取 @tool 装饰的工具。

        Args:
            py_file: Python 文件路径

        Returns:
            该文件中发现的工具数量
        """
        content = py_file.read_text(encoding='utf-8')

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return 0

        count = 0

        # 查找所有被 @tool 装饰的类
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 检查是否有 @tool 装饰器
                tool_decorator = self._find_tool_decorator(node.decorator_list)
                if tool_decorator:
                    # 提取装饰器参数
                    name, description, params_model = self._extract_decorator_args(
                        tool_decorator, node.name
                    )

                    # 获取模块路径
                    module_path = self._file_to_module(py_file)

                    # 注册工具定义
                    self._definitions[name] = {
                        'name': name,
                        'description': description or f"Tool: {name}",
                        'params_model': params_model,
                        'module_path': module_path,
                        'class_name': node.name,
                        'file_path': str(py_file)
                    }
                    count += 1
                else:
                    # 检查是否是直接定义的工具类（有 name, description, params_class 属性）
                    maybe_tool = self._detect_direct_tool(node)
                    if maybe_tool:
                        name, description, params_model = maybe_tool
                        module_path = self._file_to_module(py_file)

                        self._definitions[name] = {
                            'name': name,
                            'description': description,
                            'params_model': params_model,
                            'module_path': module_path,
                            'class_name': node.name,
                            'file_path': str(py_file)
                        }
                        count += 1

        return count

    def _detect_direct_tool(self, node: ast.ClassDef) -> Optional[tuple[str, str, str]]:
        """检测直接定义的工具类（通过类属性）。

        检查类是否有以下属性：
        - name: str
        - description: str
        - params_class: Type[BaseModel]

        Args:
            node: AST 类节点

        Returns:
            (name, description, params_model) 或 None
        """
        name = None
        description = None
        params_model = None

        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                # 类型注解的赋值: name: str = "xxx"
                attr_name = item.target.id
                if attr_name == 'name' and isinstance(item.value, ast.Constant):
                    name = item.value.value
                elif attr_name == 'description' and isinstance(item.value, ast.Constant):
                    description = item.value.value
                elif attr_name == 'params_class' and isinstance(item.value, ast.Name):
                    params_model = item.value.id
            elif isinstance(item, ast.Assign):
                # 普通赋值: name = "xxx"
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attr_name = target.id
                        if attr_name == 'name' and isinstance(item.value, ast.Constant):
                            name = item.value.value
                        elif attr_name == 'description' and isinstance(item.value, ast.Constant):
                            description = item.value.value
                        elif attr_name == 'params_class' and isinstance(item.value, ast.Name):
                            params_model = item.value.id

        if name and description and params_model:
            return (name, description, params_model)
        return None

    def _find_tool_decorator(self, decorator_list: list) -> Optional[ast.expr]:
        """从装饰器列表中找到 @tool 装饰器。

        Args:
            decorator_list: 类的装饰器列表

        Returns:
            @tool 装饰器节点，或 None
        """
        for decorator in decorator_list:
            # 处理 @tool 或 @tool(...) 形式
            if isinstance(decorator, ast.Name) and decorator.id == 'tool':
                return decorator
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name) and decorator.func.id == 'tool':
                    return decorator
        return None

    def _extract_decorator_args(
        self, decorator: ast.expr, class_name: str
    ) -> tuple[str, str, str]:
        """从装饰器节点提取参数。

        Args:
            decorator: @tool(...) 装饰器节点
            class_name: 类名（用于默认值）

        Returns:
            (name, description, params_model)
        """
        name = class_name.lower().replace('tool', '')
        description = ""
        params_model = f"{class_name}Params"

        if isinstance(decorator, ast.Call):
            # @tool(name="xxx", description="xxx", params_model=XXX)
            for keyword in decorator.keywords:
                if keyword.arg == 'name' and isinstance(keyword.value, ast.Constant):
                    name = keyword.value.value
                elif keyword.arg == 'description' and isinstance(keyword.value, ast.Constant):
                    description = keyword.value.value
                elif keyword.arg == 'params_model' and isinstance(keyword.value, ast.Name):
                    params_model = keyword.value.id

        return name, description, params_model

    def _file_to_module(self, py_file: Path) -> str:
        """将文件路径转换为模块路径。

        Args:
            py_file: Python 文件路径

        Returns:
            模块路径，如 "backend.app.tools.examples.math_tools"
        """
        # 找到项目根目录
        parts = py_file.parts

        # 找到 backend/app/tools 所在位置
        try:
            idx = parts.index('backend')
            module_parts = parts[idx:]
            # 移除 .py 扩展名
            module_parts = [p.replace('.py', '') for p in module_parts]
            return '.'.join(module_parts)
        except ValueError:
            # 如果不在 backend 目录下，尝试从当前工作目录计算
            try:
                idx = parts.index('app')
                module_parts = parts[idx:]
                module_parts = [p.replace('.py', '') for p in module_parts]
                return '.'.join(module_parts)
            except ValueError:
                # 最后尝试使用相对路径
                return str(py_file).replace('/', '.').replace('.py', '')

    async def run_tool(self, tool_name: str, context: Any, **params) -> ToolResult:
        """运行工具（含延迟加载）。

        执行流程：
        1. 检查工具是否已注册
        2. 检查是否已延迟加载，未加载则导入
        3. 实例化工具
        4. 调用工具（自动参数验证）

        Args:
            tool_name: 工具名称
            context: 执行上下文
            **params: 工具参数

        Returns:
            ToolResult: 执行结果

        Raises:
            ToolNotFoundError: 工具未注册
            ToolExecutionError: 工具执行失败
        """
        # Step 1: 检查是否已注册
        if tool_name not in self._definitions:
            available = list(self._definitions.keys())
            raise ToolNotFoundError(tool_name, available)

        # Step 2: 延迟加载
        if tool_name not in self._lazy_loaded:
            await self._lazy_load(tool_name)

        # Step 3: 实例化并调用
        tool_class = self._lazy_loaded[tool_name]
        tool_instance = tool_class()

        try:
            result = await tool_instance(context, **params)
            return result
        except Exception as e:
            if isinstance(e, (ToolNotFoundError, ToolExecutionError)):
                raise
            raise ToolExecutionError(tool_name, str(e))

    async def _lazy_load(self, tool_name: str) -> None:
        """延迟导入工具模块。

        Args:
            tool_name: 工具名称
        """
        definition = self._definitions.get(tool_name)
        if not definition:
            raise ToolNotFoundError(tool_name)

        module_path = definition['module_path']

        try:
            # 动态导入模块
            module = importlib.import_module(module_path)
            cls_name = definition['class_name']
            cls = getattr(module, cls_name)

            # 验证是 BaseTool 子类
            if not issubclass(cls, BaseTool):
                raise TypeError(
                    f"{cls_name} must be a BaseTool subclass, got {type(cls)}"
                )

            self._lazy_loaded[tool_name] = cls

        except ImportError as e:
            raise ToolExecutionError(
                tool_name,
                f"Failed to import module '{module_path}': {e}"
            )
        except AttributeError as e:
            raise ToolExecutionError(
                tool_name,
                f"Class '{definition['class_name']}' not found in module: {e}"
            )

    def register_executor(self, name: str, executor: Callable) -> None:
        """注册同步执行器（用于简单的函数式工具）。

        Args:
            name: 工具名称
            executor: 可调用对象，会被包装为异步执行
        """
        self._executors[name] = executor

    async def run_executor(self, name: str, context: Any, **params) -> ToolResult:
        """运行已注册的同步执行器。

        Args:
            name: 工具名称
            context: 执行上下文
            **params: 工具参数

        Returns:
            ToolResult: 执行结果
        """
        if name not in self._executors:
            raise ToolNotFoundError(name, list(self._executors.keys()))

        executor = self._executors[name]
        start = time.time()

        try:
            # 调用执行器
            if inspect.iscoroutinefunction(executor):
                output = await executor(context, **params)
            else:
                output = executor(context, **params)

            return ToolResult(
                success=True,
                output=output,
                execution_time_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                execution_time_ms=(time.time() - start) * 1000
            )

    def get_tool_definition(self, tool_name: str) -> Optional[dict]:
        """获取工具定义（OpenAI Function Calling 格式）。

        Args:
            tool_name: 工具名称

        Returns:
            工具定义字典，或 None（如果工具未注册）
        """
        definition = self._definitions.get(tool_name)
        if not definition:
            return None

        # 如果已延迟加载，可以返回完整定义
        if tool_name in self._lazy_loaded:
            cls = self._lazy_loaded[tool_name]
            instance = cls()
            return instance.to_openai_format()

        # 返回基础定义
        return {
            'name': definition['name'],
            'description': definition['description'],
            'parameters': {
                'type': 'object',
                'properties': {},
                # params_model 信息仅用于调试
                '_params_model': definition['params_model']
            }
        }

    def list_tools(self) -> list[dict]:
        """列出所有已注册工具。

        Returns:
            工具定义列表
        """
        return [
            {
                'name': name,
                'description': defn.get('description', ''),
                'module_path': defn.get('module_path', ''),
                'class_name': defn.get('class_name', ''),
                'is_loaded': name in self._lazy_loaded
            }
            for name, defn in self._definitions.items()
        ]

    def list_tool_names(self) -> list[str]:
        """列出所有已注册工具名称。

        Returns:
            工具名称列表
        """
        return list(self._definitions.keys())

    def is_discovered(self) -> bool:
        """检查是否已完成自动发现。"""
        return self._discovered

    def get_discover_stats(self) -> dict:
        """获取发现统计信息。"""
        return {
            'total_registered': len(self._definitions),
            'total_loaded': len(self._lazy_loaded),
            'discover_paths': self._discover_paths,
            'is_discovered': self._discovered
        }