"""MCP CDP 浏览器工具 - 集成 web-access skill 的 CDP Proxy 能力"""

import subprocess
import json
import time
import os
from typing import Any, Dict, List, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

from cyberteam.mcp.registry import ToolDefinition

# CDP Proxy 配置
CDP_PROXY_HOST = os.environ.get("CDP_PROXY_HOST", "localhost")
CDP_PROXY_PORT = os.environ.get("CDP_PROXY_PORT", "3456")
CDP_BASE_URL = f"http://{CDP_PROXY_HOST}:{CDP_PROXY_PORT}"

# web-access skill 路径
WEB_ACCESS_SKILL_DIR = os.path.expanduser("~/.claude/skills/web-access")


def _check_deps() -> Dict[str, Any]:
    """检查依赖并确保 CDP Proxy 就绪"""
    script_path = os.path.join(WEB_ACCESS_SKILL_DIR, "scripts", "check-deps.sh")

    if not os.path.exists(script_path):
        return {
            "status": "error",
            "message": f"web-access skill not found at {script_path}",
            "hint": "请确保已安装 web-access skill"
        }

    try:
        result = subprocess.run(
            ["bash", script_path],
            capture_output=True,
            text=True,
            timeout=60
        )

        output = result.stdout + result.stderr
        return {
            "status": "ready" if result.returncode == 0 else "not_ready",
            "output": output,
            "message": output.strip()
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "依赖检查超时"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def _start_proxy() -> bool:
    """启动 CDP Proxy"""
    script_path = os.path.join(WEB_ACCESS_SKILL_DIR, "scripts", "cdp-proxy.mjs")

    try:
        subprocess.Popen(
            ["node", script_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        time.sleep(2)  # 等待 Proxy 启动
        return True
    except Exception:
        return False


def _http_request(path: str, method: str = "GET", data: Optional[str] = None) -> Dict[str, Any]:
    """发送 HTTP 请求到 CDP Proxy"""
    url = f"{CDP_BASE_URL}{path}"

    try:
        req = Request(url, method=method, data=data.encode() if data else None)
        req.add_header("Content-Type", "application/json")

        with urlopen(req, timeout=30) as response:
            content = response.read().decode()

            # 尝试解析 JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"raw": content}

    except HTTPError as e:
        return {"error": f"HTTP {e.code}", "message": e.reason}
    except URLError as e:
        return {"error": "connection_failed", "message": str(e.reason)}
    except Exception as e:
        return {"error": "unknown", "message": str(e)}


def _ensure_proxy_ready() -> bool:
    """确保 CDP Proxy 已就绪"""
    result = _http_request("/targets")
    if isinstance(result, list):
        return True

    # 尝试启动 Proxy
    return _start_proxy() and _http_request("/targets", timeout=5) is not None


# === CDP Browser 工具实现 ===

def cdp_check_deps_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """检查 CDP 依赖"""
    result = _check_deps()

    if result["status"] == "ready":
        return {
            "status": "ready",
            "message": result["message"],
            "tools": {
                "web_search": "可使用 WebSearch/WebFetch",
                "cdp_browser": "CDP Proxy 已就绪，可操控 Chrome 浏览器"
            }
        }
    else:
        return {
            "status": "not_ready",
            "message": result["message"],
            "setup_instructions": [
                "1. Chrome 地址栏打开 chrome://inspect/#remote-debugging",
                "2. 勾选 Allow remote debugging for this browser instance",
                "3. 重启 Chrome（如需要）",
                "4. 运行: bash ~/.claude/skills/web-access/scripts/check-deps.sh"
            ]
        }


def cdp_list_targets_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """列出所有打开的标签页"""
    if not _ensure_proxy_ready():
        return {"error": "CDP Proxy 未就绪，请先运行 cdp_check_deps"}

    result = _http_request("/targets")

    if isinstance(result, list):
        return {
            "targets": [
                {
                    "id": t.get("id"),
                    "title": t.get("title", ""),
                    "url": t.get("url", ""),
                    "type": t.get("type", "")
                }
                for t in result
            ]
        }
    return result


def cdp_new_tab_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """创建新的后台标签页"""
    url = args.get("url")
    if not url:
        return {"error": "url 参数必需"}

    if not _ensure_proxy_ready():
        return {"error": "CDP Proxy 未就绪"}

    result = _http_request(f"/new?url={url}")

    if "error" not in result:
        return {
            "status": "success",
            "target_id": result.get("targetId"),
            "url": url,
            "message": f"已创建新标签页: {url}"
        }
    return result


def cdp_eval_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """在标签页中执行 JavaScript"""
    target_id = args.get("target")
    script = args.get("script", "")

    if not target_id:
        return {"error": "target 参数必需"}
    if not script:
        return {"error": "script 参数必需"}

    if not _ensure_proxy_ready():
        return {"error": "CDP Proxy 未就绪"}

    result = _http_request(f"/eval?target={target_id}", method="POST", data=script)

    return {
        "target": target_id,
        "result": result
    }


def cdp_click_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """点击页面元素 (JS click)"""
    target_id = args.get("target")
    selector = args.get("selector", "")

    if not target_id or not selector:
        return {"error": "target 和 selector 参数必需"}

    if not _ensure_proxy_ready():
        return {"error": "CDP Proxy 未就绪"}

    result = _http_request(f"/click?target={target_id}", method="POST", data=selector)

    return {
        "target": target_id,
        "selector": selector,
        "result": result
    }


def cdp_scroll_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """滚动页面"""
    target_id = args.get("target")
    y = args.get("y")
    direction = args.get("direction")

    if not target_id:
        return {"error": "target 参数必需"}
    if not y and not direction:
        return {"error": "y 或 direction 参数必需"}

    if not _ensure_proxy_ready():
        return {"error": "CDP Proxy 未就绪"}

    path = f"/scroll?target={target_id}"
    if y:
        path += f"&y={y}"
    if direction:
        path += f"&direction={direction}"

    result = _http_request(path)

    return {
        "target": target_id,
        "result": result
    }


def cdp_screenshot_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """截取页面截图"""
    target_id = args.get("target")
    file_path = args.get("file", "/tmp/cdp-screenshot.png")

    if not target_id:
        return {"error": "target 参数必需"}

    if not _ensure_proxy_ready():
        return {"error": "CDP Proxy 未就绪"}

    result = _http_request(f"/screenshot?target={target_id}&file={file_path}")

    return {
        "target": target_id,
        "file": file_path,
        "result": result
    }


def cdp_close_tab_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """关闭标签页"""
    target_id = args.get("target")

    if not target_id:
        return {"error": "target 参数必需"}

    if not _ensure_proxy_ready():
        return {"error": "CDP Proxy 未就绪"}

    result = _http_request(f"/close?target={target_id}")

    return {
        "target": target_id,
        "result": result
    }


def cdp_navigate_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """导航到 URL"""
    target_id = args.get("target")
    url = args.get("url")

    if not target_id or not url:
        return {"error": "target 和 url 参数必需"}

    if not _ensure_proxy_ready():
        return {"error": "CDP Proxy 未就绪"}

    result = _http_request(f"/navigate?target={target_id}&url={url}")

    return {
        "target": target_id,
        "url": url,
        "result": result
    }


# === 工具定义 ===

cdp_check_deps_tool = ToolDefinition(
    name="cdp_check_deps",
    description="检查 CDP 浏览器依赖和连接状态",
    input_schema={
        "type": "object",
        "properties": {},
        "required": []
    },
    handler=cdp_check_deps_impl,
    source="cdp",
    metadata={"category": "browser", "requires_chrome": True}
)

cdp_list_targets_tool = ToolDefinition(
    name="cdp_list_targets",
    description="列出用户 Chrome 中所有打开的标签页",
    input_schema={
        "type": "object",
        "properties": {},
        "required": []
    },
    handler=cdp_list_targets_impl,
    source="cdp",
    metadata={"category": "browser", "requires_chrome": True}
)

cdp_new_tab_tool = ToolDefinition(
    name="cdp_new_tab",
    description="在 Chrome 中创建新的后台标签页",
    input_schema={
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "目标 URL"}
        },
        "required": ["url"]
    },
    handler=cdp_new_tab_impl,
    source="cdp",
    metadata={"category": "browser", "requires_chrome": True}
)

cdp_eval_tool = ToolDefinition(
    name="cdp_eval",
    description="在标签页中执行 JavaScript，可读写 DOM、提取数据、操控元素",
    input_schema={
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "标签页 target ID"},
            "script": {"type": "string", "description": "要执行的 JavaScript 代码"}
        },
        "required": ["target", "script"]
    },
    handler=cdp_eval_impl,
    source="cdp",
    metadata={"category": "browser", "requires_chrome": True}
)

cdp_click_tool = ToolDefinition(
    name="cdp_click",
    description="点击页面元素 (使用 JS el.click())",
    input_schema={
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "标签页 target ID"},
            "selector": {"type": "string", "description": "CSS 选择器"}
        },
        "required": ["target", "selector"]
    },
    handler=cdp_click_impl,
    source="cdp",
    metadata={"category": "browser", "requires_chrome": True}
)

cdp_scroll_tool = ToolDefinition(
    name="cdp_scroll",
    description="滚动页面，可指定像素或方向(bottom)",
    input_schema={
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "标签页 target ID"},
            "y": {"type": "integer", "description": "垂直滚动像素"},
            "direction": {"type": "string", "description": "滚动方向 (bottom)"}
        },
        "required": ["target"]
    },
    handler=cdp_scroll_impl,
    source="cdp",
    metadata={"category": "browser", "requires_chrome": True}
)

cdp_screenshot_tool = ToolDefinition(
    name="cdp_screenshot",
    description="截取页面截图",
    input_schema={
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "标签页 target ID"},
            "file": {"type": "string", "description": "截图保存路径", "default": "/tmp/cdp-screenshot.png"}
        },
        "required": ["target"]
    },
    handler=cdp_screenshot_impl,
    source="cdp",
    metadata={"category": "browser", "requires_chrome": True}
)

cdp_close_tab_tool = ToolDefinition(
    name="cdp_close_tab",
    description="关闭标签页",
    input_schema={
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "标签页 target ID"}
        },
        "required": ["target"]
    },
    handler=cdp_close_tab_impl,
    source="cdp",
    metadata={"category": "browser", "requires_chrome": True}
)

cdp_navigate_tool = ToolDefinition(
    name="cdp_navigate",
    description="在标签页中导航到 URL",
    input_schema={
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "标签页 target ID"},
            "url": {"type": "string", "description": "目标 URL"}
        },
        "required": ["target", "url"]
    },
    handler=cdp_navigate_impl,
    source="cdp",
    metadata={"category": "browser", "requires_chrome": True}
)


# 便捷函数
def check_browser_deps() -> Dict[str, Any]:
    """检查浏览器依赖"""
    return cdp_check_deps_impl({})


def list_browser_tabs() -> Dict[str, Any]:
    """列出所有标签页"""
    return cdp_list_targets_impl({})


def open_new_tab(url: str) -> Dict[str, Any]:
    """打开新标签页"""
    return cdp_new_tab_impl({"url": url})


def eval_in_tab(target_id: str, script: str) -> Dict[str, Any]:
    """在标签页中执行 JS"""
    return cdp_eval_impl({"target": target_id, "script": script})


def click_element(target_id: str, selector: str) -> Dict[str, Any]:
    """点击元素"""
    return cdp_click_impl({"target": target_id, "selector": selector})


def scroll_page(target_id: str, y: int = None, direction: str = None) -> Dict[str, Any]:
    """滚动页面"""
    return cdp_scroll_impl({"target": target_id, "y": y, "direction": direction})


def take_screenshot(target_id: str, file_path: str = "/tmp/cdp-screenshot.png") -> Dict[str, Any]:
    """截图"""
    return cdp_screenshot_impl({"target": target_id, "file": file_path})


def close_tab(target_id: str) -> Dict[str, Any]:
    """关闭标签页"""
    return cdp_close_tab_impl({"target": target_id})


def navigate_tab(target_id: str, url: str) -> Dict[str, Any]:
    """导航"""
    return cdp_navigate_impl({"target": target_id, "url": url})


__all__ = [
    # 工具定义
    "cdp_check_deps_tool",
    "cdp_list_targets_tool",
    "cdp_new_tab_tool",
    "cdp_eval_tool",
    "cdp_click_tool",
    "cdp_scroll_tool",
    "cdp_screenshot_tool",
    "cdp_close_tab_tool",
    "cdp_navigate_tool",
    # 便捷函数
    "check_browser_deps",
    "list_browser_tabs",
    "open_new_tab",
    "eval_in_tab",
    "click_element",
    "scroll_page",
    "take_screenshot",
    "close_tab",
    "navigate_tab",
]
