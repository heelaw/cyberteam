# CyberTeam Browse - 持久无头浏览器

## 功能概述

CyberTeam Browse 是一个持久无头浏览器模块，基于 Playwright 实现，专为 AI 代理和自动化测试设计。

### 核心特性

- **持久守护进程**: 首次启动后持续运行，~100ms/命令（vs 新建 30 秒）
- **状态保持**: 跨调用维护登录、Cookies、Session
- **智能定位器**: @e1, @e2 等 Ref 引用替代 CSS 选择器
- **Cookie 管理**: 从 Chrome/Arc/Brave/Edge 导入会话
- **用户交接**: handoff/resume 支持 CAPTCHA 和 MFA 处理

## 安装要求

### 必需依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.8+ | 服务器运行时 |
| **Playwright** | 最新 | 浏览器自动化 |
| **Bun** | 1.0+ | 可选：CLI 加速 |

### 安装步骤

#### 1. 安装 Python 依赖

```bash
pip install playwright
playwright install chromium
```

#### 2. 安装 Bun（可选）

```bash
curl -fsSL https://bun.sh/install | bash
```

#### 3. 设置权限

```bash
chmod +x browse.sh
chmod +x browse-server.py
```

## 命令参考

### 导航命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `goto <url>` | 打开 URL | `goto https://github.com` |
| `back` | 后退 | `back` |
| `forward` | 前进 | `forward` |
| `reload` | 刷新 | `reload` |
| `url` | 当前 URL | `url` |

### 读取命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `text` | 页面文本 | `text` |
| `html [选择器]` | HTML 内容 | `html #content` |
| `links` | 所有链接 | `links` |
| `forms` | 表单字段 | `forms` |
| `accessibility` | ARIA 树 | `accessibility` |

### 交互命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `click <选择器>` | 点击 | `click @e1` |
| `fill <选择器> <值>` | 填写 | `fill @e2 "hello"` |
| `select <选择器> <选项>` | 选择 | `select @e3 "option1"` |
| `hover <选择器>` | 悬停 | `hover @e1` |
| `type <文本>` | 输入 | `type "hello"` |
| `press <按键>` | 按键 | `press Enter` |
| `scroll [选择器]` | 滚动 | `scroll` |
| `wait <条件>` | 等待 | `wait @e1` |
| `upload <选择器> <文件>` | 上传 | `upload @e1 file.pdf` |
| `viewport <WxH>` | 视口 | `viewport 1280x720` |

### 检查命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `js <表达式>` | JS 表达式 | `js "document.title"` |
| `css <选择器> <属性>` | CSS 值 | `css @e1 "color"` |
| `attrs <选择器>` | 元素属性 | `attrs @e1` |
| `is <属性> <选择器>` | 状态检查 | `is visible @e1` |
| `console [--errors]` | 控制台 | `console --errors` |
| `network` | 网络请求 | `network` |
| `cookies` | Cookies | `cookies` |
| `storage` | 存储 | `storage` |

### 可视化命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `screenshot [路径]` | 截图 | `screenshot /tmp/shot.png` |
| `pdf [路径]` | PDF | `pdf /tmp/page.pdf` |
| `responsive [前缀]` | 响应式 | `responsive /tmp/layout` |
| `diff <url1> <url2>` | 对比 | `diff url1 url2` |

### 快照命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `snapshot` | 生成快照 | `snapshot` |
| `snapshot -i` | 仅交互元素 | `snapshot -i` |
| `snapshot -D` | 与之前对比 | `snapshot -D` |
| `snapshot -a -o <路径>` | 注释截图 | `snapshot -a -o /tmp/ann.png` |
| `snapshot -C` | 光标交互 | `snapshot -C` |

### 服务器命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `handoff [消息]` | 用户接管 | `handoff` |
| `resume` | 恢复 AI | `resume` |
| `status` | 健康检查 | `status` |
| `stop` | 关闭 | `stop` |
| `restart` | 重启 | `restart` |

## 使用示例

### 基础使用

```bash
# 启动浏览器
./browse.sh init

# 打开网页
./browse.sh goto https://github.com

# 生成快照
./browse.sh snapshot -i

# 点击登录按钮
./browse.sh click @e1

# 填写表单
./browse.sh fill @e2 "test@example.com"
./browse.sh fill @e3 "password123"

# 截图
./browse.sh screenshot /tmp/result.png
```

### 登录测试

```bash
# 导入 Chrome Cookie
./browse.sh cookie-import-browser chrome

# 打开已登录站点
./browse.sh goto https://github.com

# 截图验证
./browse.sh screenshot /tmp/logged-in.png
```

### 用户交接

```bash
# 打开需要 CAPTCHA 的站点
./browse.sh goto captcha-site.com

# 交接给用户
./browse.sh handoff "请处理验证码"

# 用户完成后恢复
./browse.sh resume
./browse.sh screenshot /tmp/after-captcha.png
```

### 响应式测试

```bash
./browse.sh goto example.com
./browse.sh responsive /tmp/responsive
# 生成:
#   /tmp/responsive-mobile.png
#   /tmp/responsive-tablet.png
#   /tmp/responsive-desktop.png
```

### 断言验证

```bash
./browse.sh goto example.com
./browse.sh is visible ".main-content"
./browse.sh is enabled "#submit-btn"
./browse.sh snapshot -D
```

### Python 服务器直接使用

```python
import asyncio
import aiohttp

async def browse_command(command, *args):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'http://127.0.0.1:18080/command',
            json={'command': command, 'args': list(args)},
            headers={'Authorization': f'Bearer {token}'}
        ) as resp:
            return await resp.text()

# 使用
result = await browse_command('goto', 'https://example.com')
result = await browse_command('screenshot', '/tmp/shot.png')
```

## 架构

```
┌─────────────────────────────────────────────────────────────┐
│                      CyberTeam Browse                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   CLI (browse.sh) ──────────────────────────────────────┐  │
│        │                                                 │  │
│        ▼                                                 │  │
│   HTTP Server ◄────────── State File ────────────────┐   │  │
│   (browse-server.py)  (.cyberteam/browse/state.json) │   │  │
│        │                                              │   │  │
│        ▼                                              │   │  │
│   Playwright ──────────── Chromium ───────────────►   │   │
│   (Browser Control)     (Headless Browser)            │   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 状态文件

- **位置**: `~/.cyberteam/browse/state.json`
- **内容**:
  ```json
  {
    "pid": 12345,
    "port": 18432,
    "token": "uuid-token",
    "startedAt": "2026-03-23T10:00:00Z"
  }
  ```

## 日志文件

- **控制台日志**: `~/.cyberteam/browse/console.log`
- **网络日志**: `~/.cyberteam/browse/network.log`

## 故障排除

### 常见问题

#### 1. Playwright 未安装

```bash
pip install playwright
playwright install chromium
```

#### 2. 端口被占用

杀死旧进程：
```bash
kill $(cat ~/.cyberteam/browse/state.json | jq .pid)
```

#### 3. 浏览器无法启动

检查系统依赖：
```bash
playwright install-deps chromium
```

#### 4. 命令超时

检查网络连接或使用 `wait` 命令：
```bash
./browse.sh goto https://slow-site.com
./browse.sh wait --networkidle
```

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 2.1 | 2026-03-23 | 集成 gstack browse |
| 2.0 | 2026-03-11 | 初始模块创建 |

## 相关链接

- [gstack browse 源仓库](https://github.com/gao-sun/gstack/tree/main/browse)
- [Playwright 文档](https://playwright.dev/)
