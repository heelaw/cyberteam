# CodePilot 类桌面应用技术方案

> 参考项目：CodePilot-0.41.0
> 编写日期：2026-03-31
> 版本：v1.0

---

## 一、项目概述

### 1.1 项目定位

开发一款类似 CodePilot 的桌面应用，核心功能：
1. 通过 `@anthropic-ai/claude-agent-sdk` 调用用户本地的 Claude Code CLI
2. 提供 Chat UI 界面
3. 支持 MCP 工具扩展

### 1.2 参考项目分析

**CodePilot** 是目前最成熟的 Claude Code 桌面客户端，基于 Electron + Next.js 构建，提供了完整的对话、工具集成、权限管理方案。

---

## 二、技术栈选型

### 2.1 核心技术栈

| 层级 | 技术选型 | 备选方案 | 选择理由 |
|------|----------|----------|----------|
| **桌面外壳** | Electron 40+ | Tauri | Claude Agent SDK 需要 Node.js 环境，Tauri 无法直接使用 |
| **前端框架** | Next.js 16 (App Router) | React + Vite | CodePilot 验证可行，生态成熟 |
| **UI 组件** | Tailwind CSS 4 + Radix UI | shadcn/ui | 与 Tailwind 配合良好，CodePilot 在用 |
| **状态管理** | React Context + Hooks | Zustand / Redux | 轻量级方案足够 |
| **数据库** | better-sqlite3 (WAL) | sql.js / Dexie | CodePilot 验证可行，原生性能好 |
| **AI 集成** | @anthropic-ai/claude-agent-sdk | 直接调用 CLI | SDK 提供会话管理、权限控制等高级功能 |
| **构建工具** | electron-builder | electron-forge | CodePilot 在用，社区活跃 |

### 2.2 技术选型权衡

| 权衡点 | Electron | Tauri |
|--------|----------|-------|
| **Claude SDK 兼容性** | 原生支持 Node.js | 需要额外桥接 |
| **包体积** | ~150MB | ~20MB |
| **启动速度** | 较慢 | 更快 |
| **原生能力** | 一般 | 优秀（Rust） |
| **社区生态** | 成熟 | 增长中 |

**决策：选择 Electron**，原因：
1. `@anthropic-ai/claude-agent-sdk` 是 Node.js SDK
2. CodePilot 已验证 Electron 可行
3. MCP 工具生态多基于 Node.js

---

## 三、系统架构设计

### 3.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        Electron Main Process                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ Window Mgmt  │  │ IPC Handlers │  │ Utility Process      │ │
│  │ - 创建窗口   │  │ - install:*  │  │ (Next.js Server)     │ │
│  │ - 托盘管理   │  │ - shell:*    │  │                      │ │
│  │ - 生命周期   │  │ - dialog:*   │  │                      │ │
│  │              │  │ - terminal:* │  │                      │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │ IPC (contextBridge)
┌────────────────────────────┴────────────────────────────────────┐
│                      Electron Renderer Process                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Next.js 16 App Router                  │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │   │
│  │  │   /chat     │  │  /settings  │  │   /plugins      │  │   │
│  │  │  (主界面)   │  │  (设置页)   │  │  (MCP管理)      │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  │   │
│  │  ┌─────────────────────────────────────────────────────┐  │   │
│  │  │                    React Components                  │  │   │
│  │  │  ChatInput | MessageList | CodeBlock | ToolUse     │  │   │
│  │  └─────────────────────────────────────────────────────┘  │   │
│  │  ┌─────────────────────────────────────────────────────┐  │   │
│  │  │                    Core Libraries                    │  │   │
│  │  │  claude-client.ts | stream-session-manager.ts      │  │   │
│  │  │  db.ts | provider-resolver.ts | mcp-loader.ts      │  │   │
│  │  └─────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 进程模型

```
┌─────────────────────────────────────────────────────────────┐
│                     Main Process (Node.js)                   │
│  • BrowserWindow 管理                                          │
│  • IPC 消息路由                                                │
│  • Native 对话框                                              │
│  • 托盘图标                                                    │
│  • Shell 命令执行                                              │
└─────────────────────────────────────────────────────────────┘
                              │
                    IPC (contextBridge)
                              │
┌─────────────────────────────────────────────────────────────┐
│              Renderer Process (Chromium + Next.js)            │
│  • React UI 渲染                                              │
│  • SSE 流处理                                                 │
│  • Claude SDK 调用                                            │
│  • SQLite 访问 (通过 IPC)                                      │
└─────────────────────────────────────────────────────────────┘
                              │
                    IPC (stdin/stdout)
                              │
┌─────────────────────────────────────────────────────────────┐
│              Utility Process (Next.js Server)                │
│  • REST API 端点                                             │
│  • 数据库操作                                                 │
│  • Claude SDK 子进程                                          │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 关键设计决策

| 决策 | 方案 | 理由 |
|------|------|------|
| **Next.js 位置** | 运行在 Utility Process | 避免主进程崩溃，隔离性好 |
| **数据库访问** | 通过 IPC 调用 Utility Process | better-sqlite3 是原生模块 |
| **SDK 调用** | 直接在 Renderer 调用 | SDK 支持在 Node 环境运行 |
| **MCP 管理** | 统一配置存储 + 动态加载 | 支持用户自定义 MCP 服务器 |

---

## 四、核心模块划分

### 4.1 Electron 主进程模块 (electron/main.ts)

| 功能 | 职责 |
|------|------|
| **窗口管理** | 创建 BrowserWindow，处理窗口事件 |
| **IPC 处理器** | install:*, shell:*, dialog:*, terminal:* |
| **安装向导** | Claude Code 检测和安装流程 |
| **托盘管理** | 背景运行时的系统托盘图标 |
| **环境加载** | 从用户 shell 加载环境变量 |

### 4.2 Preload 桥接模块 (electron/preload.ts)

```typescript
// 暴露的 API
window.electronAPI = {
  versions: { electron, node, chrome, platform },
  shell: { openPath },
  dialog: { openFolder },
  install: { checkPrerequisites, start, cancel, getLogs, onProgress },
  bridge: { isActive },
  terminal: { create, write, resize, kill, onData, onExit }
}
```

### 4.3 Claude SDK 封装 (claude-client.ts)

| 功能 | 职责 |
|------|------|
| **会话管理** | 创建/恢复 SDK 会话 |
| **流处理** | SSE 流解析和转换 |
| **工具调用** | MCP 工具注册和权限处理 |
| **错误分类** | 16 类结构化错误 |
| **提供者解析** | 多 API 提供商支持 |

### 4.4 流管理模块 (stream-session-manager.ts)

```typescript
interface ActiveStream {
  sessionId: string;
  abortController: AbortController;
  snapshot: SessionStreamSnapshot;
  accumulatedText: string;
  toolUsesArray: ToolUseInfo[];
  toolResultsArray: ToolResultInfo[];
}
```

### 4.5 数据库模块 (db.ts)

| 表 | 用途 |
|----|------|
| `chat_sessions` | 聊天会话元数据 |
| `messages` | 消息内容 (JSON 数组) |
| `settings` | 键值设置 |
| `tasks` | TodoWrite 任务项 |
| `api_providers` | API 提供商配置 |
| `mcp_servers` | MCP 服务器配置 |

### 4.6 MCP 工具模块

| 文件 | 用途 |
|------|------|
| `mcp-loader.ts` | MCP 服务器加载和生命周期 |
| `cli-tools-mcp.ts` | CLI 工具管理 |
| `image-gen-mcp.ts` | 图片生成工具 |
| `media-import-mcp.ts` | 媒体导入工具 |
| `widget-guidelines.ts` | 可视化组件规范 |

---

## 五、数据流设计

### 5.1 对话流程

```
用户输入 → MessageInput 组件
         → POST /api/chat/messages
         → claude-client.ts (创建 SDK conversation)
         → Claude Agent SDK SSE 流
         → stream-session-manager.ts 管理流
         → useSSEStream hook 订阅
         → MessageList 渲染
         → db.ts 持久化到 SQLite
```

### 5.2 SSE 事件类型

| 事件类型 | 用途 |
|----------|------|
| `text` | 实时文本流 |
| `tool_use` | 工具调用请求 |
| `tool_result` | 工具执行结果 |
| `tool_output` | 工具 stderr 输出 |
| `permission_request` | 权限请求 |
| `status` | 状态更新 |
| `result` | 最终结果 |
| `error` | 错误信息 |
| `done` | 流结束 |

### 5.3 MCP 配置转换

```typescript
function toSdkMcpConfig(servers: Record<string, MCPServerConfig>): Record<string, McpServerConfig> {
  // 支持三种传输类型:
  // - stdio: { command, args, env }
  // - sse: { url, headers? }
  // - http: { url, headers? }
}
```

---

## 六、MVP 功能范围

### 6.1 核心功能 (P0)

| 功能 | 描述 | 优先级 |
|------|------|--------|
| Claude Code 检测 | 检测用户是否安装 Claude Code | P0 |
| Claude Code 安装 | 提供一键安装向导 | P0 |
| 基本对话 | 发送消息，接收 AI 响应 | P0 |
| 流式输出 | SSE 实时显示 AI 生成内容 | P0 |
| 会话管理 | 创建、切换、删除会话 | P0 |
| 工作目录 | 选择 Claude Code 工作目录 | P0 |
| 消息历史 | 保存和加载历史消息 | P0 |

### 6.2 扩展功能 (P1)

| 功能 | 描述 | 优先级 |
|------|------|--------|
| MCP 服务器管理 | 添加、配置、启用/禁用 MCP | P1 |
| 权限请求处理 | 工具调用权限审批 | P1 |
| 文件上传 | 支持代码文件作为附件 | P1 |
| 代码高亮 | 消息中的代码块语法高亮 | P1 |
| 主题切换 | 深色/浅色主题 | P1 |
| 设置面板 | API Provider 配置 | P1 |

### 6.3 高级功能 (P2)

| 功能 | 描述 | 优先级 |
|------|------|--------|
| 多 Provider | 支持 Anthropic/OpenRouter/Bedrock | P2 |
| 远程 Bridge | Telegram/飞书控制 | P2 |
| 插件系统 | 扩展功能插件 | P2 |
| 图片生成 | 调用图片生成模型 | P2 |

---

## 七、开发工作量估算

### 7.1 模块分解

| 模块 | 功能点 | 预估人天 |
|------|--------|----------|
| **Electron 基础** | | |
| 项目初始化 | 脚手架、构建配置 | 1 |
| 主进程 | 窗口、IPC、托盘 | 2 |
| Preload | API 暴露 | 1 |
| **Next.js 基础** | | |
| App Router | 路由、布局 | 1 |
| UI 组件库 | Button、Dialog、Tabs | 2 |
| 样式系统 | Tailwind + 主题 | 1 |
| **核心对话** | | |
| Claude SDK 集成 | claude-client | 3 |
| 流管理 | stream-session-manager | 2 |
| 对话 UI | ChatInput、MessageList | 2 |
| 会话管理 | CRUD + SQLite | 2 |
| **MCP 集成** | | |
| MCP 管理 UI | 添加/配置服务器 | 2 |
| MCP 加载器 | 动态加载 | 2 |
| 权限处理 | 请求/批准流程 | 2 |
| **其他** | | |
| 安装向导 | Claude Code 检测/安装 | 2 |
| 设置面板 | Provider 配置 | 2 |
| 错误处理 | 错误分类、提示 | 1 |
| **集成测试** | | |
| E2E 测试 | Playwright | 2 |
| **合计** | | **28 人天** |

### 7.2 里程碑

| 阶段 | 内容 | 周期 |
|------|------|------|
| M1 | Electron + Next.js 骨架跑通 | 1 周 |
| M2 | 基本对话功能可用 | 1.5 周 |
| M3 | MCP 工具支持 | 1 周 |
| M4 | 完善和 Bug 修复 | 0.5 周 |

---

## 八、关键风险点和解决方案

### 8.1 技术风险

| 风险 | 影响 | 概率 | 缓解方案 |
|------|------|------|----------|
| **Claude SDK 版本升级** | API 变更 | 中 | 固定版本号，定期升级测试 |
| **Electron 渲染崩溃** | UI 无响应 | 低 | Utility Process 隔离 |
| **Native 模块 ABI** | better-sqlite3 不兼容 | 中 | electron-rebuild 自动编译 |
| **MCP 服务器不稳定** | 工具调用失败 | 中 | 超时控制，错误重试 |

### 8.2 安全风险

| 风险 | 影响 | 缓解方案 |
|------|------|----------|
| **API Key 泄露** | 数据安全 | 仅本地存储，不上传 |
| **恶意 MCP 工具** | 系统安全 | 权限确认机制 |
| **代码执行** | 系统安全 | 沙箱环境，权限控制 |

### 8.3 兼容性风险

| 风险 | 影响 | 缓解方案 |
|------|------|----------|
| **macOS/Windows/Linux** | 平台差异 | 条件编译，测试覆盖 |
| **Node.js 版本** | SDK 依赖 | 锁定 LTS 版本 |
| **Claude CLI 版本** | 功能差异 | 版本检测，降级提示 |

---

## 九、项目结构

```
codepilot-desktop/
├── electron/
│   ├── main.ts              # 主进程入口
│   ├── preload.ts           # Preload 脚本
│   └── terminal-manager.ts  # 终端管理
├── src/
│   ├── app/
│   │   ├── api/             # API 路由
│   │   │   ├── chat/
│   │   │   │   └── messages/
│   │   │   │       └── route.ts
│   │   │   └── health/
│   │   │       └── route.ts
│   │   ├── chat/
│   │   │   └── page.tsx     # 聊天页面
│   │   ├── settings/
│   │   │   └── page.tsx     # 设置页面
│   │   └── layout.tsx       # 根布局
│   ├── components/
│   │   ├── ui/              # 基础 UI
│   │   ├── chat/            # 聊天组件
│   │   └── settings/        # 设置组件
│   ├── lib/
│   │   ├── claude-client.ts # SDK 封装
│   │   ├── stream-session-manager.ts
│   │   ├── db.ts            # 数据库
│   │   ├── mcp-loader.ts    # MCP 加载
│   │   └── provider-resolver.ts
│   ├── hooks/
│   │   ├── useSSEStream.ts
│   │   └── useChat.ts
│   └── types/
│       └── index.ts
├── package.json
├── next.config.js
├── tailwind.config.ts
├── electron-builder.yml
└── tsconfig.json
```

---

## 十、参考文档

| 文档 | 地址 |
|------|------|
| CodePilot ARCHITECTURE.md | `CodePilot-0.41.0/ARCHITECTURE.md` |
| Claude Agent SDK | `@anthropic-ai/claude-agent-sdk` |
| Electron 文档 | https://electronjs.org/docs |
| Next.js 文档 | https://nextjs.org/docs |
| electron-builder | https://www.electron.build |

---

## 附录 A：CodePilot 核心代码分析

### A.1 claude-client.ts 关键设计

```typescript
// SDK 调用核心模式
export function streamClaude(options: ClaudeStreamOptions): ReadableStream<string> {
  return new ReadableStream<string>({
    async start(controller) {
      // 1. 解析 Provider 配置
      const resolved = resolveForClaudeCode(options.provider, {...});

      // 2. 构建环境变量
      const sdkEnv = {...sanitizeEnv(process.env)};
      Object.assign(sdkEnv, resolvedEnv);

      // 3. 构建 Query Options
      const queryOptions: Options = {
        cwd: resolvedWorkingDirectory.path,
        abortController,
        permissionMode: skipPermissions ? 'bypassPermissions' : 'acceptEdits',
        env: sanitizeEnv(sdkEnv),
        // MCP 配置转换
        mcpServers: toSdkMcpConfig(mcpServers),
      };

      // 4. 启动对话
      const conversation = query({prompt, options: queryOptions});

      // 5. 处理流事件
      for await (const message of conversation) {
        switch (message.type) {
          case 'assistant': // 工具调用
          case 'user': // 工具结果
          case 'stream_event': // 文本流
          case 'result': // 最终结果
        }
      }
    }
  });
}
```

### A.2 Electron IPC 模式

```typescript
// Main Process
ipcMain.handle('install:check-prerequisites', async () => {
  // 检测 Claude Code 安装状态
  const expandedPath = getExpandedShellPath();
  // ... 返回检测结果
});

ipcMain.handle('install:start', () => {
  // 启动安装流程
});

// Renderer Process (Preload)
contextBridge.exposeInMainWorld('electronAPI', {
  install: {
    checkPrerequisites: () => ipcRenderer.invoke('install:check-prerequisites'),
    start: () => ipcRenderer.invoke('install:start'),
    onProgress: (callback) => {...}
  }
});
```

---

*文档版本：v1.0 | 编写人：Software Architect Agent | 审核状态：待审核*
