# web-access Skill 集成说明

## 集成概述

CyberTeam-v4 已成功集成 [web-access](https://github.com/eze-is/web-access) skill，提供完整的浏览器自动化联网能力。

## 能力矩阵

| 工具 | 功能 | 数据源 |
|------|------|--------|
| `web_search` | 网络搜索 | MCP (stub) / MiniMax MCP |
| `web_fetch` | 网页内容获取 | MCP (stub) / MiniMax MCP |
| `cdp_*` | 浏览器自动化 | **web-access CDP Proxy** ✅ |

## CDP 浏览器工具 (新增)

| 工具 | 功能 |
|------|------|
| `cdp_check_deps` | 检查 Chrome 和 CDP Proxy 依赖 |
| `cdp_list_targets` | 列出所有打开的标签页 |
| `cdp_new_tab` | 创建新后台标签页 |
| `cdp_eval` | 执行 JavaScript (读写 DOM) |
| `cdp_click` | 点击页面元素 |
| `cdp_scroll` | 滚动页面 |
| `cdp_screenshot` | 页面截图 |
| `cdp_close_tab` | 关闭标签页 |
| `cdp_navigate` | 导航到 URL |

## 前置配置

### 1. Chrome 远程调试

1. Chrome 地址栏打开 `chrome://inspect/#remote-debugging`
2. 勾选 **Allow remote debugging for this browser instance**
3. 重启 Chrome（如需要）

### 2. 检查依赖

```bash
bash ~/.claude/skills/web-access/scripts/check-deps.sh
```

预期输出：
```
node: ok (v22.x.x)
chrome: ok (port 9222)
proxy: ready
```

### 3. 启动 CDP Proxy（如未自动启动）

```bash
node ~/.claude/skills/web-access/scripts/cdp-proxy.mjs &
```

## 使用方式

### Python API

```python
from cyberteam.mcp.cdp_browser import (
    check_browser_deps,
    list_browser_tabs,
    open_new_tab,
    eval_in_tab,
    click_element,
    take_screenshot,
    close_tab
)

# 1. 检查依赖
result = check_browser_deps()
print(result)

# 2. 列出所有标签页
tabs = list_browser_tabs()
print(tabs["targets"])

# 3. 打开新标签页
result = open_new_tab("https://www.example.com")
target_id = result["target_id"]

# 4. 在标签页中执行 JavaScript
content = eval_in_tab(target_id, "document.title")
print(content["result"])

# 5. 截图
screenshot = take_screenshot(target_id, "/tmp/page.png")

# 6. 关闭标签页
close_tab(target_id)
```

### 通过 ToolRegistry 调用

```python
from cyberteam.mcp.registry import ToolRegistry

registry = ToolRegistry()

# 获取工具
tool = registry.get("cdp_new_tab")
if tool:
    result = tool.handler({"url": "https://www.example.com"})
    print(result)
```

## 架构说明

```
┌─────────────────────────────────────────────────────────┐
│                    CyberTeam-v4                          │
├─────────────────────────────────────────────────────────┤
│  MCP Registry                                           │
│  ├── web_search_tool (stub)                            │
│  ├── web_fetch_tool (stub)                             │
│  └── cdp_browser_tools (9个) ← 新增                    │
├─────────────────────────────────────────────────────────┤
│  cdp_browser.py ← 适配器层                              │
│  └── 调用 web-access skill                              │
├─────────────────────────────────────────────────────────┤
│  web-access skill (~/.claude/skills/web-access)        │
│  ├── cdp-proxy.mjs ← HTTP API 服务器                    │
│  └── scripts/                                           │
├─────────────────────────────────────────────────────────┤
│  用户 Chrome (chrome://inspect)                         │
│  └── WebSocket ← CDP 协议                               │
└─────────────────────────────────────────────────────────┘
```

## 文件清单

| 文件 | 说明 |
|------|------|
| `SKILLS/third-party/web-access` | 符号链接 → `~/.claude/skills/web-access` |
| `cyberteam/mcp/cdp_browser.py` | CDP 浏览器工具适配器 (新增) |
| `cyberteam/mcp/registry.py` | 已更新，注册 CDP 工具 |

## 与现有 web_search 的关系

| 场景 | 推荐工具 |
|------|----------|
| 简单搜索 | `web_search` (MiniMax MCP) |
| 已知 URL 内容提取 | `web_fetch` (MiniMax MCP) |
| 需要登录态 / 动态页面 | `cdp_*` (web-access) |
| 社交媒体操作 | `cdp_*` (web-access) |

## 故障排除

### proxy: not connected

```bash
# 1. 检查 Chrome 调试端口
chrome://inspect/#remote-debugging

# 2. 重启 Chrome 并勾选 Allow remote debugging

# 3. 手动启动 Proxy
node ~/.claude/skills/web-access/scripts/cdp-proxy.mjs &
```

### node: missing

安装 Node.js 22+:
```bash
# macOS
brew install node@22

# Linux
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## 参考链接

- [web-access GitHub](https://github.com/eze-is/web-access)
- [web-access 完整文档](https://github.com/eze-is/web-access/blob/main/SKILL.md)
