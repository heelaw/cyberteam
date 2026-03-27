---
name: browse
description: |
  持久无头浏览器 — Playwright守护进程，支持真实浏览器交互、Cookie管理、用户交接。
  首次启动~3秒，之后~100ms/命令。
version: "2.1"
owner: CyberTeam QA专家
agent: browse-agent
trigger: "用户需要: 浏览器交互/网页抓取/表单填写/截图/登录测试"
---

# Browse - 持久无头浏览器

## 身份定位

```
┌─────────────────────────────────────────────────────────────┐
│  🌐 Browse - 持久无头浏览器                                │
│  用途: Playwright守护进程，真实浏览器交互                  │
│  性能: 首次3秒 → 之后100ms/命令                         │
└─────────────────────────────────────────────────────────────┘
```

## 核心能力

### 1. 持久浏览器
- 守护进程模式，首次启动后持久运行
- 状态保持（登录、cookies、session）
- ~100ms/命令（vs 新建30秒）

### 2. 智能定位器 (Ref系统)
- @e1, @e2 等替代CSS选择器
- 跨会话记住元素
- 更稳定的定位方式

### 3. Cookie管理
- 从真实浏览器导入Cookie
- 支持: Chrome/Arc/Brave/Edge
- Keychain安全访问

### 4. 用户交接
- handoff: 打开可见浏览器
- 手动处理CAPTCHA/MFA
- resume: 恢复AI控制

## 命令参考

### 导航
| 命令 | 功能 | 示例 |
|------|------|------|
| goto | 打开URL | goto https://example.com |
| back | 后退 | back |
| forward | 前进 | forward |
| reload | 刷新 | reload |
| url | 打印当前URL | url |

### 读取
| 命令 | 功能 | 示例 |
|------|------|------|
| text | 页面文本 | text |
| html | HTML内容 | html #content |
| links | 所有链接 | links |
| forms | 表单字段JSON | forms |
| accessibility | ARIA树 | accessibility |

### 交互
| 命令 | 功能 | 示例 |
|------|------|------|
| click | 点击元素 | click @e1 |
| fill | 填写输入 | fill @e2 "hello" |
| select | 下拉选择 | select @e3 "option1" |
| hover | 悬停 | hover @e1 |
| type | 输入文本 | type "hello" |
| press | 按键 | press Enter |
| scroll | 滚动 | scroll @e1 |
| wait | 等待 | wait @e1 |
| upload | 文件上传 | upload @e1 /path/file.pdf |
| viewport | 视口大小 | viewport 1280x720 |

### 检查
| 命令 | 功能 | 示例 |
|------|------|------|
| js | 执行JS | js "document.title" |
| css | CSS值 | css @e1 "color" |
| attrs | 元素属性 | attrs @e1 |
| is | 状态检查 | is visible @e1 |
| console | 控制台日志 | console --errors |
| network | 网络请求 | network |
| cookies | 所有Cookie | cookies |
| storage | 存储数据 | storage |

### 可视化
| 命令 | 功能 | 示例 |
|------|------|------|
| screenshot | 截图 | screenshot /tmp/shot.png |
| pdf | 生成PDF | pdf /tmp/page.pdf |
| responsive | 响应式截图 | responsive /tmp/layout |
| diff | 页面对比 | diff url1 url2 |

### 快照
| 命令 | 功能 | 示例 |
|------|------|------|
| snapshot | 生成快照 | snapshot -i |
| snapshot -i | 仅交互元素 | snapshot -i |
| snapshot -D | 与之前对比 | snapshot -D |
| snapshot -a | 带注释截图 | snapshot -a -o /tmp/ann.png |
| snapshot -C | 光标交互元素 | snapshot -C |

### 服务器
| 命令 | 功能 | 示例 |
|------|------|------|
| handoff | 用户接管 | handoff |
| resume | 恢复AI | resume |
| status | 健康检查 | status |
| stop | 关闭服务器 | stop |
| restart | 重启服务器 | restart |

## 使用示例

### 基础使用
```
> goto github.com
> snapshot -i
> click @登录
> fill @用户名 "test@example.com"
> fill @密码 "password123"
> click @提交
> screenshot /tmp/result.png
```

### 登录测试
```
> cookie-import-browser chrome
> goto github.com
> screenshot /tmp/logged-in.png
```

### 用户交接
```
> goto captcha-site.com
> handoff  # 打开可见浏览器
> # 手动输入验证码
> resume   # 恢复AI控制
> screenshot /tmp/after-captcha.png
```

### 响应式测试
```
> goto example.com
> responsive /tmp/responsive
> # 生成 mobile.png, tablet.png, desktop.png
```

### 断言验证
```
> goto example.com
> is visible ".main-content"
> is enabled "#submit-btn"
> snapshot -D
```

---

**版本**: v2.1 | **来源**: gstack browse | **日期**: 2026-03-23
