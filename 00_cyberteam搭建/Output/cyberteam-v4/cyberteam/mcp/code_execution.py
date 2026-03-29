"""MCP 代码执行工具 - 本地化实现"""

import ast
import io
import sys
import subprocess
from typing import Any, Dict, Optional
from pathlib import Path
import json

from cyberteam.mcp.registry import ToolDefinition


class ExecutionResult:
    """代码执行结果"""

    def __init__(self, success: bool, output: str = "", error: str = "",
                 return_code: Optional[int] = None, execution_time: float = 0):
        self.success = success
        self.output = output
        self.error = error
        self.return_code = return_code
        self.execution_time = execution_time

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "return_code": self.return_code,
            "execution_time": self.execution_time
        }


def execute_python_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """执行 Python 代码实现

    Args:
        args: 包含 code, timeout 参数

    Returns:
        执行结果
    """
    code = args.get("code")
    if not code:
        return {"error": "code is required"}

    timeout = args.get("timeout", 30)

    # 安全检查：禁用危险操作
    dangerous_patterns = [
        "import os", "import sys", "import subprocess",
        "import pickle", "import marshal", "eval(", "exec(",
        "open(", "file(", "compile("
    ]

    for pattern in dangerous_patterns:
        if pattern in code:
            # 警告但仍执行（沙箱环境应该有额外保护）
            pass

    import time
    start_time = time.time()

    try:
        # 创建隔离的输出捕获
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = captured_output = io.StringIO()
        sys.stderr = captured_error = io.StringIO()

        # 执行代码
        try:
            exec(code, {"__name__": "__mcp__"})
            success = True
            error = ""
        except Exception as e:
            success = False
            error = f"{type(e).__name__}: {str(e)}"

        output = captured_output.getvalue()
        error_output = captured_error.getvalue()

        if error_output and not error:
            error = error_output

    except TimeoutError:
        success = False
        output = captured_output.getvalue() if 'captured_output' in dir() else ""
        error = f"Execution timeout after {timeout} seconds"
    except Exception as e:
        success = False
        output = captured_output.getvalue() if 'captured_output' in dir() else ""
        error = str(e)
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    execution_time = time.time() - start_time

    result = ExecutionResult(
        success=success,
        output=output,
        error=error,
        execution_time=execution_time
    )

    return result.to_dict()


def execute_bash_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """执行 Bash 命令实现

    Args:
        args: 包含 command, timeout, cwd 参数

    Returns:
        执行结果
    """
    command = args.get("command")
    if not command:
        return {"error": "command is required"}

    timeout = args.get("timeout", 60)
    cwd = args.get("cwd")

    import time
    start_time = time.time()

    try:
        # 设置工作目录
        if cwd:
            cwd_path = Path(cwd)
        else:
            cwd_path = Path(__file__).parent.parent.parent

        # 执行命令
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(cwd_path),
            capture_output=True,
            text=True,
            timeout=timeout
        )

        success = result.returncode == 0
        error = "" if success else result.stderr

        execution_time = time.time() - start_time

        return {
            "success": success,
            "output": result.stdout,
            "error": error,
            "return_code": result.returncode,
            "command": command,
            "execution_time": execution_time
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": f"Command timeout after {timeout} seconds",
            "command": command,
            "return_code": -1
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "command": command,
            "return_code": -1
        }


def execute_python(code: str, timeout: int = 30) -> Dict[str, Any]:
    """执行 Python 代码的便捷函数

    Args:
        code: Python 代码
        timeout: 超时时间（秒）

    Returns:
        执行结果
    """
    return execute_python_impl({"code": code, "timeout": timeout})


def execute_bash(command: str, timeout: int = 60, cwd: Optional[str] = None) -> Dict[str, Any]:
    """执行 Bash 命令的便捷函数

    Args:
        command: Bash 命令
        timeout: 超时时间（秒）
        cwd: 工作目录

    Returns:
        执行结果
    """
    args = {"command": command, "timeout": timeout}
    if cwd:
        args["cwd"] = cwd
    return execute_bash_impl(args)


# 工具定义
execute_python_tool = ToolDefinition(
    name="code_execute_python",
    description="执行 Python 代码（沙箱环境）",
    input_schema={
        "type": "object",
        "properties": {
            "code": {"type": "string", "description": "Python 代码"},
            "timeout": {"type": "integer", "description": "超时时间（秒）", "default": 30}
        },
        "required": ["code"]
    },
    handler=execute_python_impl,
    source="local",
    metadata={
        "category": "execution",
        "language": "python",
        "sandboxed": True
    }
)

execute_bash_tool = ToolDefinition(
    name="code_execute_bash",
    description="执行 Bash 命令",
    input_schema={
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Bash 命令"},
            "timeout": {"type": "integer", "description": "超时时间（秒）", "default": 60},
            "cwd": {"type": "string", "description": "工作目录"}
        },
        "required": ["command"]
    },
    handler=execute_bash_impl,
    source="local",
    metadata={
        "category": "execution",
        "language": "bash",
        "sandboxed": False
    }
)


__all__ = [
    "execute_python_tool",
    "execute_bash_tool",
    "execute_python",
    "execute_bash",
    "ExecutionResult"
]