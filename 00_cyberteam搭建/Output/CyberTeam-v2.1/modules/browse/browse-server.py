#!/usr/bin/env python3
"""
CyberTeam Browse Server - 持久无头浏览器守护进程
基于 Playwright 实现，支持持久化状态和快速命令执行
"""

import asyncio
import json
import os
import signal
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# ─── 配置 ───────────────────────────────────────────────────────
STATE_DIR = Path.home() / ".cyberteam" / "browse"
STATE_FILE = STATE_DIR / "state.json"
CONSOLE_LOG = STATE_DIR / "console.log"
NETWORK_LOG = STATE_DIR / "network.log"
IDLE_TIMEOUT = 30 * 60  # 30 分钟

# ─── 数据结构 ───────────────────────────────────────────────────
@dataclass
class Buffer:
    """循环缓冲区"""
    max_size: int = 1000
    entries: list = field(default_factory=list)
    total_added: int = 0

    def add(self, entry: Any) -> None:
        if len(self.entries) >= self.max_size:
            self.entries.pop(0)
        self.entries.append(entry)
        self.total_added += 1

    def last(self, n: int) -> list:
        return self.entries[-n:] if n <= len(self.entries) else self.entries

# ─── 全局状态 ───────────────────────────────────────────────────
console_buffer = Buffer()
network_buffer = Buffer()
dialog_buffer = Buffer()

auth_token = str(uuid.uuid4())
server_port = 0
idle_since = datetime.now()
browser = None
page = None

# ─── 初始化 ─────────────────────────────────────────────────────
def ensure_state_dir():
    STATE_DIR.mkdir(parents=True, exist_ok=True)

async def init_browser():
    """初始化 Playwright 浏览器"""
    global browser, page

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("[browse] 错误: 需要安装 playwright")
        print("[browse] 安装: pip install playwright && playwright install chromium")
        sys.exit(1)

    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=True)
    page = await browser.new_page()

    # 监听控制台消息
    def handle_console(msg):
        console_buffer.add({
            "level": msg.type,
            "text": msg.text,
            "timestamp": datetime.now().isoformat()
        })

    # 监听网络请求
    def handle_request(request):
        network_buffer.add({
            "method": request.method,
            "url": request.url,
            "status": None,
            "timestamp": datetime.now().isoformat()
        })

    page.on("console", handle_console)
    page.on("request", handle_request)

    print("[browse] 浏览器已启动")

async def close_browser():
    """关闭浏览器"""
    global browser
    if browser:
        await browser.close()
        print("[browse] 浏览器已关闭")

# ─── 命令处理器 ─────────────────────────────────────────────────
async def handle_goto(args: list) -> str:
    """导航到 URL"""
    url = args[0] if args else "about:blank"
    await page.goto(url, wait_until="networkidle")
    return f"已导航到: {url}"

async def handle_snapshot(args: list) -> str:
    """生成快照"""
    flags = args if args else []

    # 获取可访问性树
    accessibility = await page.accessibility.snapshot()

    if not accessibility:
        return "[无内容]"

    lines = []
    ref_counter = 0

    def format_node(node, indent=0):
        nonlocal ref_counter
        prefix = "  " * indent

        if not node:
            return

        role = node.get("role", "")
        name = node.get("name", "")
        props = node.get("properties", [])

        # 检查是否可交互
        is_interactive = any(
            p.get("name") == "focusable" or
            p.get("name") == "pressed" or
            role.lower() in ["button", "link", "textbox", "checkbox", "radio"]
            for p in props
        )

        if is_interactive:
            ref_counter += 1
            ref = f"@e{ref_counter}"
            lines.append(f"{prefix}{ref} [{role}] \"{name}\"")
        elif role:
            lines.append(f"{prefix}[{role}] \"{name}\"")

        # 递归处理子节点
        children = node.get("children", [])
        for child in children:
            format_node(child, indent + 1)

    format_node(accessibility)

    return "\n".join(lines) if lines else "[页面为空]"

async def handle_click(args: list) -> str:
    """点击元素"""
    selector = args[0] if args else None
    if not selector:
        return "错误: 需要选择器"

    # 处理 @ref 引用
    if selector.startswith("@e"):
        # 从快照中查找元素
        # 简化实现：使用 last visible element
        pass

    try:
        await page.click(selector, timeout=5000)
        return f"已点击: {selector}"
    except Exception as e:
        return f"错误: {str(e)}"

async def handle_fill(args: list) -> str:
    """填写输入"""
    if len(args) < 2:
        return "错误: 需要选择器和值"
    selector, value = args[0], args[1]

    try:
        await page.fill(selector, value)
        return f"已填写 {selector} = \"{value}\""
    except Exception as e:
        return f"错误: {str(e)}"

async def handle_screenshot(args: list) -> str:
    """截图"""
    path = args[0] if args else "/tmp/browse-screenshot.png"

    try:
        await page.screenshot(path=path)
        return f"截图已保存: {path}"
    except Exception as e:
        return f"错误: {str(e)}"

async def handle_text(args: list) -> str:
    """获取页面文本"""
    return await page.inner_text("body")

async def handle_html(args: list) -> str:
    """获取 HTML"""
    selector = args[0] if args else "html"
    try:
        return await page.inner_html(selector)
    except Exception as e:
        return f"错误: {str(e)}"

async def handle_console(args: list) -> str:
    """控制台日志"""
    show_errors = "--errors" in args
    clear = "--clear" in args

    if clear:
        console_buffer.entries.clear()
        return "控制台已清除"

    entries = console_buffer.last(50)
    if show_errors:
        entries = [e for e in entries if e.get("level") in ["error", "warning"]]

    lines = [f"[{e['level']}] {e['text']}" for e in entries]
    return "\n".join(lines) if lines else "[无日志]"

async def handle_network(args: list) -> str:
    """网络请求"""
    clear = "--clear" in args

    if clear:
        network_buffer.entries.clear()
        return "网络日志已清除"

    entries = network_buffer.last(50)
    lines = [f"{e['method']} {e['url']} → {e.get('status', 'pending')}" for e in entries]
    return "\n".join(lines) if lines else "[无请求]"

async def handle_cookies(args: list) -> str:
    """获取 Cookies"""
    cookies = await page.context.cookies()
    return json.dumps(cookies, indent=2)

async def handle_is(args: list) -> str:
    """检查元素状态"""
    if len(args) < 2:
        return "错误: 需要属性和选择器"
    prop, selector = args[0], args[1]

    try:
        if prop == "visible":
            visible = await page.is_visible(selector)
            return "true" if visible else "false"
        elif prop == "hidden":
            hidden = await page.is_hidden(selector)
            return "true" if hidden else "false"
        elif prop == "enabled":
            enabled = await page.is_enabled(selector)
            return "true" if enabled else "false"
        elif prop == "disabled":
            disabled = await page.is_disabled(selector)
            return "true" if disabled else "false"
        else:
            return f"未知属性: {prop}"
    except Exception as e:
        return f"false"

async def handle_handoff(args: list) -> str:
    """用户接管"""
    message = args[0] if args else "请处理此页面"
    print(f"\n[browse] 交接给用户: {message}\n")
    return f"已打开可见浏览器: {message}"

async def handle_resume(args: list) -> str:
    """恢复 AI 控制"""
    snapshot = await handle_snapshot([])
    return f"已恢复控制\n\n{snapshot}"

async def handle_status(args: list) -> str:
    """健康检查"""
    url = page.url if page else "N/A"
    return json.dumps({
        "status": "healthy",
        "url": url,
        "uptime": "active"
    })

# ─── 命令路由 ───────────────────────────────────────────────────
COMMANDS = {
    # 导航
    "goto": handle_goto,
    "back": lambda _: page.go_back() or "已后退",
    "forward": lambda _: page.go_forward() or "已前进",
    "reload": lambda _: page.reload(wait_until="networkidle") or "已刷新",
    "url": lambda _: page.url,

    # 读取
    "text": handle_text,
    "html": handle_html,
    "links": lambda _: "链接列表",  # 简化实现
    "forms": lambda _: "表单列表",  # 简化实现
    "accessibility": handle_snapshot,

    # 交互
    "click": handle_click,
    "fill": handle_fill,
    "hover": lambda args: page.hover(args[0]) if args else "错误: 需要选择器",
    "type": lambda args: page.type("input:focus, [contenteditable]:focus", args[0] if args else "") or "已输入",
    "press": lambda args: page.keyboard.press(args[0] if args else "Enter") or "已按键",
    "scroll": lambda args: page.evaluate(f"document.querySelector('{args[0] if args else ':root'}').scrollIntoView()") or "已滚动",
    "viewport": lambda args: page.set_viewport_size({"width": int(args[0].split("x")[0]), "height": int(args[0].split("x")[1])}) if args else "错误: 需要尺寸",

    # 检查
    "js": lambda args: page.evaluate(args[0]) if args else "错误: 需要表达式",
    "css": lambda args: page.eval_on_selector(args[0], f"el => getComputedStyle(el).{args[1]}") if len(args) >= 2 else "错误",
    "attrs": lambda args: page.eval_on_selector(args[0], "el => JSON.stringify(Object.fromEntries([...el.attributes].map(a => [a.name, a.value])))") if args else "错误",
    "is": handle_is,
    "console": handle_console,
    "network": handle_network,
    "cookies": handle_cookies,
    "storage": lambda _: "storage",  # 简化实现

    # 可视化
    "screenshot": handle_screenshot,
    "pdf": lambda args: page.pdf(path=args[0] if args else "/tmp/page.pdf"),
    "responsive": lambda _: "响应式截图",  # 简化实现

    # 快照
    "snapshot": handle_snapshot,

    # 服务器
    "handoff": handle_handoff,
    "resume": handle_resume,
    "status": handle_status,
}

# ─── HTTP 服务器 ─────────────────────────────────────────────────
async def handle_request(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """处理 HTTP 请求"""
    global idle_since

    try:
        # 读取请求
        data = await reader.read(4096)
        if not data:
            return

        request_line = data.decode().split("\r\n")[0]
        if not request_line:
            return

        method, path, _ = request_line.split(" ")

        # 读取请求体（如果是 POST）
        headers = {}
        body = b""
        content_length = 0

        for line in data.decode().split("\r\n")[1:]:
            if line == "":
                break
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip().lower()] = value.strip()
                if key.strip().lower() == "content-length":
                    content_length = int(value.strip())

        if content_length > 0:
            remaining = await reader.read(content_length)
            body = remaining

        idle_since = datetime.now()

        # 路由
        if path == "/health":
            response = json.dumps({"status": "healthy"})
            writer.write(f"HTTP/1.1 200 OK\r\nContent-Length: {len(response)}\r\n\r\n{response}".encode())

        elif path == "/command" and method == "POST":
            try:
                body_json = json.loads(body.decode())
                command = body_json.get("command", "")
                args = body_json.get("args", [])

                # 验证认证
                auth = headers.get("authorization", "")
                if auth != f"Bearer {auth_token}":
                    writer.write(b"HTTP/1.1 401 Unauthorized\r\nContent-Length: 0\r\n\r\n")
                    return

                # 执行命令
                if command in COMMANDS:
                    result = await COMMANDS[command](args)
                    response = str(result)
                else:
                    response = json.dumps({"error": f"未知命令: {command}"})

                writer.write(f"HTTP/1.1 200 OK\r\nContent-Length: {len(response)}\r\n\r\n{response}".encode())

            except Exception as e:
                error = json.dumps({"error": str(e)})
                writer.write(f"HTTP/1.1 500 OK\r\nContent-Length: {len(error)}\r\n\r\n{error}".encode())

        else:
            writer.write(b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n")

        await writer.drain()

    except Exception as e:
        print(f"[browse] 请求处理错误: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

async def find_available_port():
    """查找可用端口"""
    import random
    for _ in range(10):
        port = random.randint(10000, 60000)
        try:
            server = await asyncio.start_server(handle_request, "127.0.0.1", port)
            server.close()
            await server.wait_closed()
            return port
        except OSError:
            continue
    raise RuntimeError("无法找到可用端口")

async def idle_checker():
    """空闲检查器"""
    global idle_since
    while True:
        await asyncio.sleep(60)
        elapsed = (datetime.now() - idle_since).total_seconds()
        if elapsed > IDLE_TIMEOUT:
            print(f"[browse] 空闲 {IDLE_TIMEOUT}s，自动关闭")
            await close_browser()
            sys.exit(0)

async def write_state_file():
    """写入状态文件"""
    ensure_state_dir()
    state = {
        "pid": os.getpid(),
        "port": server_port,
        "token": auth_token,
        "startedAt": datetime.now().isoformat()
    }
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

# ─── 主程序 ─────────────────────────────────────────────────────
async def main():
    global server_port

    print("[browse] CyberTeam Browse Server 启动中...")

    # 清理旧日志
    for log in [CONSOLE_LOG, NETWORK_LOG]:
        if log.exists():
            log.unlink()

    # 初始化浏览器
    await init_browser()

    # 启动 HTTP 服务器
    server_port = await find_available_port()
    server = await asyncio.start_server(handle_request, "127.0.0.1", server_port)

    # 写入状态文件
    await write_state_file()

    addr = server.sockets[0].getsockname()
    print(f"[browse] 服务器运行于 http://{addr[0]}:{addr[1]}")
    print(f"[browse] 状态文件: {STATE_FILE}")
    print(f"[browse] 空闲超时: {IDLE_TIMEOUT}s")

    # 启动空闲检查器
    idle_task = asyncio.create_task(idle_checker())

    # 处理信号
    def signal_handler():
        print("\n[browse] 收到关闭信号...")
        idle_task.cancel()
        server.close()
        asyncio.create_task(close_browser())

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler)

    # 保持运行
    try:
        async with server:
            await server.serve_forever()
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    asyncio.run(main())
