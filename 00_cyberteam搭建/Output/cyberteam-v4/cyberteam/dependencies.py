"""CyberTeam V4 第三方依赖管理

本模块列出所有第三方依赖及其版本约束。
"""

import sys
from typing import Dict, List, NamedTuple, Optional


class DependencyInfo(NamedTuple):
    """依赖信息"""
    name: str
    version_constraint: str
    min_version: Optional[str] = None
    max_version: Optional[str] = None
    description: str = ""


# 核心依赖
CORE_DEPENDENCIES: List[DependencyInfo] = [
    DependencyInfo(
        name="typer",
        version_constraint=">=0.9.0,<1.0.0",
        min_version="0.9.0",
        max_version="1.0.0",
        description="CLI 应用程序框架"
    ),
    DependencyInfo(
        name="pyyaml",
        version_constraint=">=6.0,<7.0",
        min_version="6.0",
        max_version="7.0",
        description="YAML 解析和生成"
    ),
    DependencyInfo(
        name="rich",
        version_constraint=">=13.0.0,<14.0.0",
        min_version="13.0.0",
        max_version="14.0.0",
        description="富文本和精美格式化"
    ),
    DependencyInfo(
        name="pydantic",
        version_constraint=">=2.0.0,<3.0.0",
        min_version="2.0.0",
        max_version="3.0.0",
        description="数据验证和设置管理"
    ),
    DependencyInfo(
        name="aiosqlite",
        version_constraint=">=0.19.0,<1.0.0",
        min_version="0.19.0",
        max_version="1.0.0",
        description="异步 SQLite 数据库"
    ),
    DependencyInfo(
        name="fastapi",
        version_constraint=">=0.100.0,<1.0.0",
        min_version="0.100.0",
        max_version="1.0.0",
        description="现代快速的 Web 框架"
    ),
    DependencyInfo(
        name="uvicorn",
        version_constraint=">=0.23.0,<1.0.0",
        min_version="0.23.0",
        max_version="1.0.0",
        description="ASGI 服务器"
    ),
]

# 开发依赖
DEV_DEPENDENCIES: List[DependencyInfo] = [
    DependencyInfo(
        name="pytest",
        version_constraint=">=7.0.0,<9.0.0",
        min_version="7.0.0",
        max_version="9.0.0",
        description="测试框架"
    ),
    DependencyInfo(
        name="pytest-asyncio",
        version_constraint=">=0.21.0,<1.0.0",
        min_version="0.21.0",
        max_version="1.0.0",
        description="异步测试支持"
    ),
    DependencyInfo(
        name="black",
        version_constraint=">=23.0.0,<24.0.0",
        min_version="23.0.0",
        max_version="24.0.0",
        description="代码格式化工具"
    ),
    DependencyInfo(
        name="ruff",
        version_constraint=">=0.1.0,<1.0.0",
        min_version="0.1.0",
        max_version="1.0.0",
        description="快速 Python 代码检查"
    ),
]


def get_all_dependencies() -> List[DependencyInfo]:
    """获取所有依赖"""
    return CORE_DEPENDENCIES + DEV_DEPENDENCIES


def check_dependency(name: str) -> tuple[bool, Optional[str]]:
    """检查依赖是否已安装并满足版本要求

    Args:
        name: 依赖名称

    Returns:
        (是否满足要求, 错误信息)
    """
    try:
        module = __import__(name)
    except ImportError:
        return False, f"模块 '{name}' 未安装"

    # 检查版本
    if hasattr(module, "__version__"):
        version = module.__version__
        for dep in CORE_DEPENDENCIES + DEV_DEPENDENCIES:
            if dep.name == name:
                # 简单版本检查
                if dep.min_version and version < dep.min_version:
                    return False, f"模块 '{name}' 版本 {version} 不满足最低要求 {dep.min_version}"
                if dep.max_version and version >= dep.max_version:
                    return False, f"模块 '{name}' 版本 {version} 超过最高限制 {dep.max_version}"
                return True, None

    return True, None


def check_all_dependencies() -> Dict[str, tuple[bool, Optional[str]]]:
    """检查所有依赖

    Returns:
        依赖检查结果字典 {依赖名: (是否满足, 错误信息)}
    """
    results = {}
    for dep in CORE_DEPENDENCIES:
        results[dep.name] = check_dependency(dep.name)
    return results


def print_dependency_status() -> None:
    """打印依赖状态"""
    print("=" * 60)
    print("CyberTeam V4 依赖检查")
    print("=" * 60)

    all_ok = True
    for dep in CORE_DEPENDENCIES:
        ok, error = check_dependency(dep.name)
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {dep.name} ({dep.version_constraint})")
        if not ok and error:
            print(f"       错误: {error}")
            all_ok = False

    print("=" * 60)
    if all_ok:
        print("所有依赖检查通过!")
    else:
        print("部分依赖检查失败，请安装缺失的依赖。")
    print()


# 导出
__all__ = [
    "DependencyInfo",
    "CORE_DEPENDENCIES",
    "DEV_DEPENDENCIES",
    "get_all_dependencies",
    "check_dependency",
    "check_all_dependencies",
    "print_dependency_status",
]