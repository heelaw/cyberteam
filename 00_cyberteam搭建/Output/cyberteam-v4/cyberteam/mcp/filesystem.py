"""MCP 文件系统工具 - 本地化实现"""

import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from cyberteam.mcp.registry import ToolDefinition


def _get_project_path() -> Path:
    """获取项目路径"""
    return Path(__file__).parent.parent.parent


def read_file_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """读取文件实现

    Args:
        args: 包含 path, offset, limit 参数

    Returns:
        文件内容
    """
    file_path = args.get("path")
    if not file_path:
        return {"error": "path is required"}

    # 支持绝对路径和相对路径
    if not os.path.isabs(file_path):
        base_path = Path(args.get("base_path", _get_project_path()))
        file_path = base_path / file_path
    else:
        file_path = Path(file_path)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            offset = args.get("offset", 0)
            limit = args.get("limit")

            if offset > 0:
                f.seek(offset)

            if limit:
                content = f.read(limit)
            else:
                content = f.read()

        return {
            "content": content,
            "path": str(file_path),
            "size": len(content),
            "offset": offset
        }
    except FileNotFoundError:
        return {"error": f"File not found: {file_path}"}
    except Exception as e:
        return {"error": str(e)}


def write_file_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """写入文件实现

    Args:
        args: 包含 path, content 参数

    Returns:
        写入结果
    """
    file_path = args.get("path")
    content = args.get("content", "")

    if not file_path:
        return {"error": "path is required"}

    if not os.path.isabs(file_path):
        base_path = Path(args.get("base_path", _get_project_path()))
        file_path = base_path / file_path
    else:
        file_path = Path(file_path)

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return {
            "success": True,
            "path": str(file_path),
            "size": len(content)
        }
    except Exception as e:
        return {"error": str(e)}


def list_directory_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """列出目录实现

    Args:
        args: 包含 path, include_hidden 参数

    Returns:
        目录列表
    """
    dir_path = args.get("path")
    if not dir_path:
        return {"error": "path is required"}

    if not os.path.isabs(dir_path):
        base_path = Path(args.get("base_path", _get_project_path()))
        dir_path = base_path / dir_path
    else:
        dir_path = Path(dir_path)

    include_hidden = args.get("include_hidden", False)

    try:
        entries = []
        for entry in os.listdir(dir_path):
            if not include_hidden and entry.startswith('.'):
                continue

            full_path = dir_path / entry
            stat = os.stat(full_path)

            entries.append({
                "name": entry,
                "type": "directory" if os.path.isdir(full_path) else "file",
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })

        return {
            "path": str(dir_path),
            "entries": entries,
            "count": len(entries)
        }
    except FileNotFoundError:
        return {"error": f"Directory not found: {dir_path}"}
    except Exception as e:
        return {"error": str(e)}


def search_files_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """搜索文件实现

    Args:
        args: 包含 path, pattern, exclude 参数

    Returns:
        匹配的文件列表
    """
    search_path = args.get("path")
    pattern = args.get("pattern", "*")
    exclude = args.get("exclude", [])

    if not search_path:
        return {"error": "path is required"}

    if not os.path.isabs(search_path):
        base_path = Path(args.get("base_path", _get_project_path()))
        search_path = base_path / search_path
    else:
        search_path = Path(search_path)

    try:
        results = []
        for root, dirs, files in os.walk(search_path):
            # 排除目录
            dirs[:] = [d for d in dirs if d not in exclude]

            for file in files:
                if pattern == "*" or pattern in file:
                    full_path = Path(root) / file
                    results.append(str(full_path))

        return {
            "path": str(search_path),
            "pattern": pattern,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        return {"error": str(e)}


def get_file_info_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """获取文件信息实现

    Args:
        args: 包含 path 参数

    Returns:
        文件信息
    """
    file_path = args.get("path")
    if not file_path:
        return {"error": "path is required"}

    if not os.path.isabs(file_path):
        base_path = Path(args.get("base_path", _get_project_path()))
        file_path = base_path / file_path
    else:
        file_path = Path(file_path)

    try:
        stat = os.stat(file_path)
        return {
            "path": str(file_path),
            "exists": True,
            "is_file": os.path.isfile(file_path),
            "is_directory": os.path.isdir(file_path),
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "permissions": oct(stat.st_mode)[-3:]
        }
    except FileNotFoundError:
        return {"error": f"File not found: {file_path}", "exists": False}
    except Exception as e:
        return {"error": str(e)}


# 工具定义
read_file_tool = ToolDefinition(
    name="filesystem_read_file",
    description="读取文件内容，支持指定偏移量和限制",
    input_schema={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "文件路径"},
            "offset": {"type": "integer", "description": "读取偏移量", "default": 0},
            "limit": {"type": "integer", "description": "读取字节限制"}
        },
        "required": ["path"]
    },
    handler=read_file_impl,
    source="local"
)

write_file_tool = ToolDefinition(
    name="filesystem_write_file",
    description="写入内容到文件",
    input_schema={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "文件路径"},
            "content": {"type": "string", "description": "文件内容"}
        },
        "required": ["path", "content"]
    },
    handler=write_file_impl,
    source="local"
)

list_directory_tool = ToolDefinition(
    name="filesystem_list_directory",
    description="列出目录内容",
    input_schema={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "目录路径"},
            "include_hidden": {"type": "boolean", "description": "包含隐藏文件", "default": False}
        },
        "required": ["path"]
    },
    handler=list_directory_impl,
    source="local"
)

search_files_tool = ToolDefinition(
    name="filesystem_search",
    description="搜索文件",
    input_schema={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "搜索路径"},
            "pattern": {"type": "string", "description": "文件名匹配模式"},
            "exclude": {"type": "array", "description": "排除的目录", "items": {"type": "string"}}
        },
        "required": ["path"]
    },
    handler=search_files_impl,
    source="local"
)

get_file_info_tool = ToolDefinition(
    name="filesystem_get_info",
    description="获取文件或目录信息",
    input_schema={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "文件或目录路径"}
        },
        "required": ["path"]
    },
    handler=get_file_info_impl,
    source="local"
)


__all__ = [
    "read_file_tool",
    "write_file_tool",
    "list_directory_tool",
    "search_files_tool",
    "get_file_info_tool"
]