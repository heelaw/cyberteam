"""MCP 图像理解工具 - 本地化实现"""

from typing import Any, Dict
from pathlib import Path

from cyberteam.mcp.registry import ToolDefinition


SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}


def _validate_image_path(file_path: str, base_path: Path = None) -> Path:
    """验证图像路径

    Args:
        file_path: 文件路径
        base_path: 基础路径

    Returns:
        验证后的 Path 对象
    """
    import os

    if not os.path.isabs(file_path):
        if base_path is None:
            base_path = Path(__file__).parent.parent.parent
        file_path = base_path / file_path
    else:
        file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Image not found: {file_path}")

    if file_path.suffix.lower() not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported image format: {file_path.suffix}")

    return file_path


def understand_image_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """图像理解实现

    Args:
        args: 包含 image_path, prompt 参数

    Returns:
        图像分析结果
    """
    image_path = args.get("image_path")
    if not image_path:
        return {"error": "image_path is required"}

    prompt = args.get("prompt", "描述这张图片的内容")

    base_path = None
    if "base_path" in args:
        base_path = Path(args["base_path"])

    try:
        validated_path = _validate_image_path(image_path, base_path)

        # 尝试使用 MiniMax MCP understand_image
        try:
            from mcp__MiniMax__understand_image import understand_image
            result = understand_image(prompt=prompt, image_source=str(validated_path))
            return {
                "image_path": str(validated_path),
                "analysis": result,
                "source": "mcp"
            }
        except ImportError:
            pass

        # 回退方案
        return {
            "image_path": str(validated_path),
            "prompt": prompt,
            "analysis": "",
            "source": "local",
            "message": "Image understanding requires MCP server connection"
        }

    except FileNotFoundError as e:
        return {"error": str(e)}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def extract_image_info_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """提取图像基本信息

    Args:
        args: 包含 image_path 参数

    Returns:
        图像信息
    """
    image_path = args.get("image_path")
    if not image_path:
        return {"error": "image_path is required"}

    base_path = None
    if "base_path" in args:
        base_path = Path(args["base_path"])

    try:
        validated_path = _validate_image_path(image_path, base_path)

        # 获取基本图像信息
        import os
        stat = os.stat(validated_path)

        return {
            "path": str(validated_path),
            "name": validated_path.name,
            "format": validated_path.suffix.lower(),
            "size": stat.st_size,
            "exists": True
        }

    except FileNotFoundError as e:
        return {"error": str(e), "exists": False}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}


def understand_image(image_path: str, prompt: str = "描述这张图片的内容",
                     base_path: Path = None) -> Dict[str, Any]:
    """图像理解的便捷函数

    Args:
        image_path: 图像路径
        prompt: 分析提示
        base_path: 基础路径

    Returns:
        分析结果
    """
    args = {"image_path": image_path, "prompt": prompt}
    if base_path:
        args["base_path"] = str(base_path)
    return understand_image_impl(args)


# 工具定义
understand_image_tool = ToolDefinition(
    name="image_understand",
    description="分析和理解图像内容",
    input_schema={
        "type": "object",
        "properties": {
            "image_path": {"type": "string", "description": "图像路径"},
            "prompt": {"type": "string", "description": "分析提示", "default": "描述这张图片的内容"}
        },
        "required": ["image_path"]
    },
    handler=understand_image_impl,
    source="local",
    metadata={
        "category": "vision",
        "requires_mcp_server": True,
        "supported_formats": list(SUPPORTED_FORMATS)
    }
)

extract_image_info_tool = ToolDefinition(
    name="image_info",
    description="提取图像基本信息",
    input_schema={
        "type": "object",
        "properties": {
            "image_path": {"type": "string", "description": "图像路径"}
        },
        "required": ["image_path"]
    },
    handler=extract_image_info_impl,
    source="local",
    metadata={"category": "vision"}
)


__all__ = [
    "understand_image_tool",
    "extract_image_info_tool",
    "understand_image",
    "SUPPORTED_FORMATS"
]