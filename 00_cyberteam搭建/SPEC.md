# CodePilot Desktop 开发规格文档

> **项目名称**: CodePilot Desktop
> **版本**: v1.0
> **编写日期**: 2026-03-31
> **基于技术方案**: CodePilot类软件技术方案.md

---

## 目录

1. [功能详细规格](#1-功能详细规格)
2. [技术详细设计](#2-技术详细设计)
3. [验收标准](#3-验收标准)
4. [依赖清单](#4-依赖清单)

---

## 1. 功能详细规格

### 1.1 P0 功能清单

| 功能 ID | 功能名称 | 优先级 | 描述 |
|---------|----------|--------|------|
| P0-01 | Claude Code 检测 | P0 | 检测用户本地是否已安装 Claude Code CLI |
| P0-02 | Claude Code 安装 | P0 | 提供一键安装向导，引导用户完成安装 |
| P0-03 | 基本对话 | P0 | 发送消息，接收 AI 响应 |
| P0-04 | 流式输出 | P0 | SSE 实时显示 AI 生成内容 |
| P0-05 | 会话管理 | P0 | 创建、切换、删除会话 |
| P0-06 | 工作目录 | P0 | 选择 Claude Code 工作目录 |
| P0-07 | 消息历史 | P0 | 保存和加载历史消息 |

### 1.2 P0-01: Claude Code 检测

#### 1.2.1 功能描述

在应用启动时自动检测用户本地是否已安装 Claude Code CLI，并返回检测结果。

#### 1.2.2 用户交互流程

```
应用启动
    ↓
自动执行检测
    ↓
┌─────────────────────────────────┐
│ 结果 1: 已安装                   │
│  → 显示版本号                    │
│  → 进入主界面                    │
└─────────────────────────────────┘
┌─────────────────────────────────┐
│ 结果 2: 未安装                   │
│  → 显示安装向导                  │
└─────────────────────────────────┘
```

#### 1.2.3 输入/输出定义

**输入**:
- 无（自动检测）

**输出**:
```typescript
interface PrerequisiteCheckResult {
  installed: boolean;
  version?: string;        // 例如 "1.0.12"
  path?: string;          // Claude Code 可执行文件路径
  error?: string;          // 检测失败原因
}
```

#### 1.2.4 边界条件和错误处理

| 场景 | 处理方式 |
|------|----------|
| Claude Code 已安装 | 返回 `installed: true` 和版本信息 |
| Claude Code 未安装 | 返回 `installed: false` |
| 检测命令执行失败 | 返回 `installed: false` 和 `error` 字段 |
| 权限不足 | 返回 `installed: false` 和权限错误提示 |

#### 1.2.5 检测逻辑

```typescript
// 检测优先级:
1. which claude (Unix) / where claude (Windows)
2. 检查 PATH 中的 claude 可执行文件
3. 检查 ~/.claude/bin/claude (macOS/Linux)
4. 检查 %USERPROFILE%\.claude\bin\claude (Windows)
```

---

### 1.3 P0-02: Claude Code 安装向导

#### 1.3.1 功能描述

当检测到 Claude Code 未安装时，显示安装向导引导用户完成安装过程。

#### 1.3.2 用户交互流程

```
步骤 1: 欢迎界面
    ↓
步骤 2: 检测环境 (Node.js 版本、操作系统)
    ↓
步骤 3: 显示安装命令
    ↓
步骤 4: 执行安装
    ↓
步骤 5: 验证安装
    ↓
完成或重试
```

#### 1.3.3 输入/输出定义

**输入**:
```typescript
interface InstallOptions {
  packageManager: 'npm' | 'pnpm' | 'yarn' | 'brew';
  installCommand: string;  // 显示给用户的安装命令
}
```

**输出**:
```typescript
interface InstallResult {
  success: boolean;
  version?: string;
  error?: string;
  logs: string[];  // 安装日志
}
```

#### 1.3.4 安装向导 UI 状态

| 状态 | UI 显示 |
|------|---------|
| `idle` | 显示安装命令，等待用户执行 |
| `installing` | 显示进度指示器 |
| `verifying` | 验证安装结果 |
| `success` | 显示成功消息和"进入应用"按钮 |
| `error` | 显示错误消息和"重试"按钮 |

#### 1.3.5 错误处理

| 错误类型 | 用户提示 |
|----------|----------|
| 网络错误 | "网络连接失败，请检查网络后重试" |
| 权限错误 | "权限不足，请使用 sudo 或手动安装" |
| 安装超时 | "安装超时，请手动运行命令后重试验证" |
| 版本不兼容 | "Node.js 版本过低，请升级后重试" |

---

### 1.4 P0-03: 基本对话

#### 1.4.1 功能描述

用户可以在输入框中输入消息，发送给 Claude Code SDK，接收 AI 响应并显示。

#### 1.4.2 用户交互流程

```
用户输入消息
    ↓
点击发送 / 按下 Enter
    ↓
┌─────────────────────────────────┐
│ 验证: 消息非空、会话有效         │
└─────────────────────────────────┘
    ↓
发送请求到 /api/chat/messages
    ↓
显示 "正在思考..." 状态
    ↓
接收 SSE 流数据
    ↓
实时渲染消息内容
    ↓
消息完成，保存到数据库
```

#### 1.4.3 输入/输出定义

**用户输入**:
```typescript
interface SendMessageInput {
  sessionId: string;       // 会话 ID
  content: string;          // 消息内容
  attachments?: {          // 附件 (P1)
    name: string;
    path: string;
    type: 'file' | 'image';
  }[];
}
```

**API 输出** (SSE 流事件):
```typescript
type SSEEvent =
  | { type: 'text'; content: string }
  | { type: 'tool_use'; id: string; name: string; input: object }
  | { type: 'tool_result'; id: string; content: string }
  | { type: 'permission_request'; id: string; tool: string; input: object }
  | { type: 'status'; value: string }
  | { type: 'error'; error: string }
  | { type: 'done' };
```

#### 1.4.4 边界条件和错误处理

| 场景 | 处理方式 |
|------|----------|
| 空消息 | 禁用发送按钮，不发送请求 |
| 会话不存在 | 创建新会话 |
| SDK 调用失败 | 显示错误消息，保留输入内容 |
| 网络中断 | 显示重连提示 |
| 消息过长 (>100KB) | 截断并提示用户 |

---

### 1.5 P0-04: 流式输出 (SSE)

#### 1.5.1 功能描述

通过 Server-Sent Events (SSE) 实时接收并显示 Claude Code SDK 生成的文本内容。

#### 1.5.2 用户交互流程

```
SDK 开始生成
    ↓
SSE 事件: text
    ↓
实时追加到消息内容
    ↓
渲染更新 (防抖 16ms)
    ↓
SSE 事件: tool_use
    ↓
显示工具调用卡片
    ↓
...
    ↓
SSE 事件: done
    ↓
保存完整消息到数据库
```

#### 1.5.3 SSE 事件类型定义

| 事件类型 | 说明 | 数据结构 |
|----------|------|----------|
| `text` | 文本片段 | `{ type: 'text', content: string }` |
| `tool_use` | 工具调用开始 | `{ type: 'tool_use', id: string, name: string, input: object }` |
| `tool_result` | 工具执行结果 | `{ type: 'tool_result', id: string, content: string }` |
| `tool_output` | 工具 stderr 输出 | `{ type: 'tool_output', id: string, content: string }` |
| `permission_request` | 权限请求 | `{ type: 'permission_request', id: string, tool: string, input: object }` |
| `status` | 状态更新 | `{ type: 'status', value: string }` |
| `error` | 错误信息 | `{ type: 'error', error: string }` |
| `done` | 流结束 | `{ type: 'done' }` |

#### 1.5.4 流处理状态机

```
                    ┌──────────────┐
         ┌─────────│   idle       │
         │         └──────┬───────┘
         │                │ start stream
         │                ↓
         │         ┌──────────────┐
         │  ┌─────│  streaming    │
         │  │     └──────┬───────┘
         │  │ text event │ tool_use event
         │  ↓            ↓
         │ ┌──────────┐ ┌──────────────┐
         │ │ append   │ │ show tool     │
         │ │ text     │ │ card         │
         │ └──────────┘ └──────┬───────┘
         │                      │
         │                tool_result event
         │                      ↓
         │                ┌──────────────┐
         │  ┌─────────────│  tool_done   │
         │  │              └──────┬───────┘
         │  │                     │
         │  │error event         │ done event
         │  ↓                     ↓
         │ ┌──────────┐    ┌──────────────┐
         └─│  error   │    │   complete   │
           └──────────┘    └──────────────┘
```

#### 1.5.5 错误处理

| 场景 | 处理方式 |
|------|----------|
| SSE 连接断开 | 自动重连，最多 3 次 |
| 数据解析错误 | 忽略错误片段，继续处理 |
| 流中断 | 显示 "连接中断，正在重连..." |

---

### 1.6 P0-05: 会话管理

#### 1.6.1 功能描述

管理多个聊天会话，支持创建、切换、删除和重命名会话。

#### 1.6.2 用户交互流程

```
主界面侧边栏
    ↓
┌─────────────────────────────────┐
│ 会话列表                        │
│ ├── 今天                        │
│ │   ├── 会话 A (活动)           │
│ │   └── 会话 B                  │
│ ├── 昨天                        │
│ │   └── 会话 C                  │
│ └── 更早                        │
│     └── 会话 D                  │
└─────────────────────────────────┘
    ↓
点击会话 → 切换到该会话
点击 "+" → 创建新会话
右键会话 → 显示操作菜单
```

#### 1.6.3 输入/输出定义

**会话数据结构**:
```typescript
interface ChatSession {
  id: string;              // UUID
  title: string;           // 会话标题 (自动生成或用户自定义)
  createdAt: number;        // 创建时间戳
  updatedAt: number;        // 更新时间戳
  workingDirectory?: string; // 工作目录
  messageCount: number;     // 消息数量
  lastMessage?: string;    // 最后一条消息摘要
}
```

**API 端点**:

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/sessions` | 获取所有会话列表 |
| POST | `/api/sessions` | 创建新会话 |
| GET | `/api/sessions/:id` | 获取会话详情 |
| PATCH | `/api/sessions/:id` | 更新会话 (标题、目录) |
| DELETE | `/api/sessions/:id` | 删除会话 |

#### 1.6.4 会话自动标题生成规则

```typescript
// 首条用户消息的前 50 个字符作为标题
function generateTitle(firstMessage: string): string {
  const text = firstMessage.replace(/[^\u4e00-\u9fa5a-zA-Z0-9]/g, '').slice(0, 50);
  return text || '新会话';
}
```

#### 1.6.5 边界条件和错误处理

| 场景 | 处理方式 |
|------|----------|
| 无会话 | 显示 "创建第一个会话" 引导 |
| 会话数超过 100 | 显示 "请清理旧会话" 提示 |
| 删除最后会话 | 自动创建新会话 |
| 并发修改 | 使用乐观锁，后写入覆盖 |

---

### 1.7 P0-06: 工作目录

#### 1.7.1 功能描述

允许用户选择 Claude Code 的工作目录，该目录会传递给 SDK 的 `cwd` 参数。

#### 1.7.2 用户交互流程

```
点击工作目录选择器
    ↓
打开系统文件夹选择对话框
    ↓
用户选择文件夹
    ↓
验证文件夹可访问
    ↓
更新会话的 workingDirectory
    ↓
后续对话使用新目录
```

#### 1.7.3 输入/输出定义

**目录验证**:
```typescript
interface DirectoryValidation {
  valid: boolean;
  path: string;
  readable: boolean;
  writable: boolean;
  error?: string;
}
```

**目录选择 API**:
```typescript
// Preload API
window.electronAPI.dialog.openFolder(): Promise<string | null>
// 返回选中的目录路径，用户取消返回 null
```

#### 1.7.4 目录选择器 UI

| 状态 | 显示 |
|------|------|
| 未选择 | "选择工作目录" |
| 已选择 | 文件夹图标 + 路径 (可点击打开) |
| 无效目录 | 红色警告 + "目录不可访问" |

---

### 1.8 P0-07: 消息历史

#### 1.8.1 功能描述

保存和加载聊天消息历史，支持会话切换后恢复上下文。

#### 1.8.2 用户交互流程

```
切换到会话 A
    ↓
加载会话消息 (从数据库)
    ↓
渲染消息列表
    ↓
用户继续对话
    ↓
新消息实时保存
    ↓
切换到会话 B
    ↓
保存会话 A 状态
    ↓
加载会话 B 消息
```

#### 1.8.3 消息数据结构

```typescript
interface Message {
  id: string;              // UUID
  sessionId: string;        // 所属会话
  role: 'user' | 'assistant';
  content: string;          // 消息内容 (支持 Markdown)
  attachments?: Attachment[];
  toolUses?: ToolUse[];     // 工具调用记录
  createdAt: number;        // 创建时间
}

interface Attachment {
  name: string;
  path: string;
  type: 'file' | 'image';
  size: number;
}

interface ToolUse {
  id: string;
  name: string;
  input: object;
  result?: string;
  status: 'pending' | 'approved' | 'rejected' | 'completed';
  createdAt: number;
}
```

#### 1.8.4 消息加载策略

```typescript
// 分页加载策略
const MESSAGE_PAGE_SIZE = 50;

interface LoadMessagesOptions {
  sessionId: string;
  before?: string;    // 消息 ID，用于加载更多
  limit?: number;     // 默认 50
}

// 返回
interface LoadMessagesResult {
  messages: Message[];
  hasMore: boolean;
  nextCursor?: string;
}
```

#### 1.8.5 边界条件和错误处理

| 场景 | 处理方式 |
|------|----------|
| 消息加载失败 | 显示 "加载失败，点击重试" |
| 消息过多 (>10000) | 提示用户清理旧会话 |
| 图片加载失败 | 显示占位符 |

---

## 2. 技术详细设计

### 2.1 API 接口设计 (REST)

#### 2.1.1 基础信息

| 项目 | 值 |
|------|---|
| 基础 URL | `http://localhost:3001/api` |
| 认证方式 | 无 (本地应用) |
| 内容类型 | `application/json` |
| 字符编码 | UTF-8 |

#### 2.1.2 会话管理 API

**GET /api/sessions**

获取所有会话列表。

```typescript
// Response 200
{
  "sessions": ChatSession[];
}
```

**POST /api/sessions**

创建新会话。

```typescript
// Request
{
  "title"?: string;
  "workingDirectory"?: string;
}

// Response 201
{
  "session": ChatSession;
}
```

**GET /api/sessions/:id**

获取会话详情。

```typescript
// Response 200
{
  "session": ChatSession;
}
```

**PATCH /api/sessions/:id**

更新会话。

```typescript
// Request
{
  "title"?: string;
  "workingDirectory"?: string;
}

// Response 200
{
  "session": ChatSession;
}
```

**DELETE /api/sessions/:id**

删除会话。

```typescript
// Response 204 (No Content)
```

#### 2.1.3 消息 API

**GET /api/sessions/:id/messages**

获取会话消息。

```typescript
// Query Parameters
{
  "before"?: string;   // 消息 ID，用于分页
  "limit"?: number;     // 默认 50，最大 100
}

// Response 200
{
  "messages": Message[];
  "hasMore": boolean;
  "nextCursor"?: string;
}
```

**POST /api/chat/messages**

发送消息并启动对话流。

```typescript
// Request
{
  "sessionId": string;
  "content": string;
  "attachments"?: Attachment[];
}

// Response: SSE Stream
// Content-Type: text/event-stream
//
// data: {"type":"text","content":"Hello"}
// data: {"type":"text","content":" world"}
// ...
// data: {"type":"done"}
```

**DELETE /api/sessions/:id/messages**

清空会话消息。

```typescript
// Response 204
```

#### 2.1.4 设置 API

**GET /api/settings**

获取所有设置。

```typescript
// Response 200
{
  "settings": Record<string, string>;
}
```

**PATCH /api/settings**

更新设置。

```typescript
// Request
{
  "key": string;
  "value": string;
}

// Response 200
{
  "setting": { "key": string; "value": string };
}
```

#### 2.1.5 MCP API

**GET /api/mcp/servers**

获取 MCP 服务器列表。

```typescript
// Response 200
{
  "servers": MCPServer[];
}

interface MCPServer {
  id: string;
  name: string;
  enabled: boolean;
  config: MCPServerConfig;
}
```

**POST /api/mcp/servers**

添加 MCP 服务器。

```typescript
// Request
{
  "name": string;
  "transport": 'stdio' | 'sse' | 'http';
  "config": MCPServerConfig;
}

// Response 201
{
  "server": MCPServer;
}
```

**PATCH /api/mcp/servers/:id**

更新 MCP 服务器。

```typescript
// Request
{
  "enabled"?: boolean;
  "config"?: MCPServerConfig;
}

// Response 200
{
  "server": MCPServer;
}
```

**DELETE /api/mcp/servers/:id**

删除 MCP 服务器。

```typescript
// Response 204
```

#### 2.1.6 健康检查 API

**GET /api/health**

```typescript
// Response 200
{
  "status": "ok";
  "claudeInstalled": boolean;
  "claudeVersion"?: string;
}
```

---

### 2.2 数据库设计 (SQLite)

#### 2.2.1 数据库配置

```typescript
// 使用 better-sqlite3，WAL 模式
const db = new Database('codepilot.db');
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');
```

#### 2.2.2 表结构

**chat_sessions** - 聊天会话表

```sql
CREATE TABLE chat_sessions (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL DEFAULT '新会话',
  working_directory TEXT,
  created_at INTEGER NOT NULL DEFAULT (unixepoch()),
  updated_at INTEGER NOT NULL DEFAULT (unixepoch()),
  message_count INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX idx_sessions_updated_at ON chat_sessions(updated_at DESC);
```

**messages** - 消息表

```sql
CREATE TABLE messages (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  attachments TEXT,  -- JSON array
  tool_uses TEXT,    -- JSON array
  created_at INTEGER NOT NULL DEFAULT (unixepoch()),
  FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
);

CREATE INDEX idx_messages_session_id ON messages(session_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
```

**settings** - 设置表

```sql
CREATE TABLE settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at INTEGER NOT NULL DEFAULT (unixepoch())
);
```

**mcp_servers** - MCP 服务器配置表

```sql
CREATE TABLE mcp_servers (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  enabled INTEGER NOT NULL DEFAULT 1,
  transport TEXT NOT NULL CHECK(transport IN ('stdio', 'sse', 'http')),
  config TEXT NOT NULL,  -- JSON
  created_at INTEGER NOT NULL DEFAULT (unixepoch()),
  updated_at INTEGER NOT NULL DEFAULT (unixepoch())
);
```

#### 2.2.3 触发器

```sql
-- 自动更新会话的 updated_at 和 message_count
CREATE TRIGGER update_session_on_message_insert
AFTER INSERT ON messages
BEGIN
  UPDATE chat_sessions
  SET updated_at = unixepoch(),
      message_count = message_count + 1
  WHERE id = NEW.session_id;
END;

CREATE TRIGGER update_session_on_message_delete
AFTER DELETE ON messages
BEGIN
  UPDATE chat_sessions
  SET updated_at = unixepoch(),
      message_count = message_count - 1
  WHERE id = OLD.session_id;
END;
```

---

### 2.3 状态机设计

#### 2.3.1 应用状态机

```
┌─────────────────────────────────────────────────────────────┐
│                      Application States                      │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐
│   launching  │ ← 应用启动
└──────┬───────┘
       │ 检测完成
       ↓
┌──────────────┐
│ checking     │ ← 检查 Claude Code 安装状态
└──────┬───────┘
       │
       ├──────────────────┐
       │                  │
       ↓                  ↓
┌──────────────┐    ┌──────────────┐
│ needs_setup │    │   ready      │
│ (未安装)    │    │ (已安装)     │
└──────┬───────┘    └──────┬───────┘
       │                  │
       │ 安装完成          │ 退出应用
       ↓                  ↓
   [返回 checking]    ┌──────────────┐
                      │   closed     │
                      └──────────────┘
```

#### 2.3.2 对话状态机

```
┌─────────────────────────────────────────────────────────────┐
│                      Chat States                             │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐
│   idle      │ ← 等待用户输入
└──────┬───────┘
       │ 发送消息
       ↓
┌──────────────┐
│  sending    │ ← 请求发送中
└──────┬───────┘
       │
       ├──────────────┬──────────────┐
       ↓              ↓              ↓
┌──────────────┐ ┌──────────┐  ┌──────────────┐
│ streaming   │ │ waiting  │  │    error     │
│ (接收流)    │ │ (权限)   │  │  (错误)      │
└──────┬──────┘ └────┬─────┘  └──────────────┘
       │              │
       │ done          │ 批准/拒绝
       ↓              ↓
   [idle]        [streaming 继续]
```

#### 2.3.3 安装向导状态机

```
┌─────────────────────────────────────────────────────────────┐
│                   Installation Wizard States                 │
└─────────────────────────────────────────────────────────────┘

                    ┌──────────────┐
              ┌─────│   welcome    │
              │     └──────┬───────┘
              │            │ 开始安装
              │            ↓
              │     ┌──────────────┐
              │     │ checking    │ ← 检查环境
              │     └──────┬───────┘
              │            │ 环境就绪
              │            ↓
              │     ┌──────────────┐
              │     │  display_cmd │ ← 显示命令
              │     └──────┬───────┘
              │            │ 用户执行
              │            ↓
              │     ┌──────────────┐
              │ ┌───│ installing  │ ← 安装中
              │ │   └──────┬───────┘
              │ │ 安装完成   │ 超时/失败
              │ │           ↓
              │ │   ┌──────────────┐
              │ └──→│ verifying   │ ← 验证
              │     └──────┬───────┘
              │            │
              │      ┌─────┴─────┐
              │      ↓           ↓
              │ ┌──────────┐ ┌──────────┐
              └──│ success  │ │  error   │
                └──────────┘ └────┬─────┘
                                   │ 重试
                                   ↓
                             [display_cmd]
```

---

### 2.4 目录结构和文件职责

```
codepilot-desktop/
├── electron/                         # Electron 主进程
│   ├── main.ts                       # 主进程入口
│   │   ├── 职责: 窗口管理、IPC 处理器、托盘管理
│   │   └── 导出: createWindow(), setupIPC()
│   │
│   ├── preload.ts                    # Preload 脚本
│   │   ├── 职责: 安全桥接、API 暴露
│   │   └── 导出: electronAPI (shell, dialog, install, terminal)
│   │
│   ├── terminal-manager.ts          # 终端管理
│   │   ├── 职责: PTY 进程管理
│   │   └── 导出: TerminalManager class
│   │
│   └── ipc-handlers.ts               # IPC 处理器注册
│       ├── 职责: 统一注册所有 IPC handlers
│       └── 导出: registerHandlers()
│
├── src/
│   ├── app/                          # Next.js App Router
│   │   ├── api/                      # API 路由
│   │   │   ├── chat/
│   │   │   │   └── messages/
│   │   │   │       └── route.ts     # POST /api/chat/messages
│   │   │   ├── sessions/
│   │   │   │   ├── route.ts         # GET/POST /api/sessions
│   │   │   │   └── [id]/
│   │   │   │       ├── route.ts     # GET/PATCH/DELETE /api/sessions/:id
│   │   │   │       └── messages/
│   │   │   │           └── route.ts # GET/DELETE /api/sessions/:id/messages
│   │   │   ├── settings/
│   │   │   │   └── route.ts         # GET/PATCH /api/settings
│   │   │   ├── mcp/
│   │   │   │   └── servers/
│   │   │   │       ├── route.ts     # GET/POST /api/mcp/servers
│   │   │   │       └── [id]/
│   │   │   │           └── route.ts # PATCH/DELETE /api/mcp/servers/:id
│   │   │   └── health/
│   │   │       └── route.ts         # GET /api/health
│   │   │
│   │   ├── chat/
│   │   │   └── page.tsx             # 聊天页面
│   │   │
│   │   ├── settings/
│   │   │   └── page.tsx             # 设置页面
│   │   │
│   │   ├── layout.tsx               # 根布局
│   │   └── globals.css              # 全局样式
│   │
│   ├── components/                   # React 组件
│   │   ├── ui/                      # 基础 UI 组件
│   │   │   ├── button.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── tabs.tsx
│   │   │   ├── input.tsx
│   │   │   ├── dropdown-menu.tsx
│   │   │   └── scroll-area.tsx
│   │   │
│   │   ├── chat/                    # 聊天相关组件
│   │   │   ├── chat-container.tsx  # 聊天容器
│   │   │   ├── message-list.tsx    # 消息列表
│   │   │   ├── message-item.tsx    # 单条消息
│   │   │   ├── chat-input.tsx      # 输入框
│   │   │   ├── code-block.tsx      # 代码块
│   │   │   ├── tool-call-card.tsx  # 工具调用卡片
│   │   │   └── typing-indicator.tsx
│   │   │
│   │   ├── sidebar/                 # 侧边栏组件
│   │   │   ├── sidebar.tsx
│   │   │   ├── session-list.tsx
│   │   │   └── session-item.tsx
│   │   │
│   │   └── settings/                # 设置组件
│   │       ├── settings-panel.tsx
│   │       ├── provider-config.tsx
│   │       └── mcp-manager.tsx
│   │
│   ├── lib/                         # 核心库
│   │   ├── claude-client.ts        # Claude SDK 封装
│   │   │   ├── 职责: SDK 调用、流处理、错误分类
│   │   │   └── 导出: streamClaude(), resolveProvider()
│   │   │
│   │   ├── stream-session-manager.ts # 流会话管理
│   │   │   ├── 职责: 管理活跃流、快照、终止
│   │   │   └── 导出: StreamSessionManager class
│   │   │
│   │   ├── db.ts                    # 数据库操作
│   │   │   ├── 职责: SQLite 封装、CRUD 操作
│   │   │   └── 导出: db, sessionsDB, messagesDB
│   │   │
│   │   ├── mcp-loader.ts            # MCP 加载器
│   │   │   ├── 职责: MCP 服务器加载、生命周期
│   │   │   └── 导出: MCPLoader class
│   │   │
│   │   └── provider-resolver.ts    # Provider 解析
│   │       ├── 职责: 多 API 提供商支持
│   │       └── 导出: resolveForClaudeCode()
│   │
│   ├── hooks/                       # React Hooks
│   │   ├── useSSEStream.ts          # SSE 流订阅
│   │   ├── useChat.ts               # 对话状态管理
│   │   ├── useSessions.ts           # 会话列表管理
│   │   └── useSettings.ts          # 设置管理
│   │
│   └── types/                        # TypeScript 类型
│       └── index.ts                  # 全局类型定义
│
├── package.json
├── tsconfig.json
├── next.config.js
├── tailwind.config.ts
├── electron-builder.yml
└── SPEC.md                          # 本文档
```

---

### 2.5 关键模块接口定义

#### 2.5.1 Claude Client (claude-client.ts)

```typescript
export interface ClaudeStreamOptions {
  prompt: string;
  provider: ProviderConfig;
  cwd: string;
  mcpServers?: Record<string, MCPServerConfig>;
  permissionMode?: 'bypassPermissions' | 'acceptEdits';
  abortSignal?: AbortSignal;
}

export interface ProviderConfig {
  provider: 'anthropic' | 'openrouter' | 'bedrock';
  apiKey?: string;
  apiBaseUrl?: string;
  model?: string;
}

export type StreamEvent =
  | { type: 'text'; content: string }
  | { type: 'tool_use'; id: string; name: string; input: object }
  | { type: 'tool_result'; id: string; content: string }
  | { type: 'tool_output'; id: string; content: string }
  | { type: 'permission_request'; id: string; tool: string; input: object }
  | { type: 'status'; value: string }
  | { type: 'error'; error: string }
  | { type: 'done' };

export function streamClaude(options: ClaudeStreamOptions): ReadableStream<StreamEvent>;
export function resolveForClaudeCode(provider: ProviderConfig, env: Record<string, string>): ResolvedConfig;
```

#### 2.5.2 Stream Session Manager (stream-session-manager.ts)

```typescript
export interface SessionStreamSnapshot {
  sessionId: string;
  accumulatedText: string;
  toolUses: ToolUseInfo[];
  toolResults: ToolResultInfo[];
  startedAt: number;
  status: 'streaming' | 'waiting_permission' | 'complete' | 'error';
}

export interface ToolUseInfo {
  id: string;
  name: string;
  input: object;
  status: 'pending' | 'approved' | 'rejected';
}

export interface ToolResultInfo {
  id: string;
  content: string;
}

export class StreamSessionManager {
  constructor();
  createStream(sessionId: string, stream: ReadableStream<StreamEvent>): AbortController;
  getSnapshot(sessionId: string): SessionStreamSnapshot | null;
  abortStream(sessionId: string): void;
  abortAll(): void;
  onStreamEvent(sessionId: string, callback: (event: StreamEvent) => void): void;
}
```

---

## 3. 验收标准

### 3.1 P0 功能验收条件

#### P0-01: Claude Code 检测

| 验收条件 | 测试方法 |
|----------|----------|
| 已安装时显示版本号 | 在已安装 Claude Code 的机器上启动应用 |
| 未安装时显示安装向导 | 在未安装 Claude Code 的环境中启动 |
| 检测失败时显示友好错误 | 模拟检测失败场景 |

#### P0-02: Claude Code 安装

| 验收条件 | 测试方法 |
|----------|----------|
| 安装向导显示正确命令 | 验证不同平台 (macOS/Windows/Linux) |
| 安装过程有进度反馈 | 手动执行安装，观察 UI 更新 |
| 安装完成后验证成功 | 安装后返回版本号 |
| 失败时显示错误和重试 | 中断安装，验证错误处理 |

#### P0-03: 基本对话

| 验收条件 | 测试方法 |
|----------|----------|
| 消息发送成功 | 发送 "你好" |
| AI 响应正确显示 | 验证响应内容渲染 |
| 空消息不可发送 | 不输入直接点击发送 |
| 多轮对话连贯 | 连续发送 5 条消息 |

#### P0-04: 流式输出

| 验收条件 | 测试方法 |
|----------|----------|
| 文本实时显示 | 观察 SSE 流文本逐字显示 |
| 工具调用卡片显示 | 发送需要工具的请求 |
| 流中断自动重连 | 断网测试 |
| done 事件触发保存 | 检查数据库消息记录 |

#### P0-05: 会话管理

| 验收条件 | 测试方法 |
|----------|----------|
| 创建新会话 | 点击 "+" 创建 |
| 切换会话 | 点击不同会话 |
| 删除会话 | 右键删除 |
| 会话列表排序 | 按时间分组显示 |
| 会话标题自动生成 | 新会话发送消息后检查标题 |

#### P0-06: 工作目录

| 验收条件 | 测试方法 |
|----------|----------|
| 打开目录选择器 | 点击选择器 |
| 目录显示正确 | 选择后验证路径 |
| 目录切换生效 | 切换目录后发送消息 |

#### P0-07: 消息历史

| 验收条件 | 测试方法 |
|----------|----------|
| 切换会话加载历史 | 切换到有消息的会话 |
| 历史消息渲染正确 | Markdown 代码高亮 |
| 分页加载正常 | 会话消息超过 50 条 |
| 删除后清空历史 | 删除会话验证消息清理 |

---

### 3.2 测试用例

#### 3.2.1 单元测试

```typescript
// db.test.ts
describe('Database Operations', () => {
  describe('sessionsDB', () => {
    it('should create a new session', async () => {
      const session = await sessionsDB.create({ title: 'Test' });
      expect(session.id).toBeDefined();
      expect(session.title).toBe('Test');
    });

    it('should list sessions ordered by updatedAt', async () => {
      const sessions = await sessionsDB.list();
      expect(sessions[0].updatedAt).toBeGreaterThanOrEqual(sessions[1]?.updatedAt ?? 0);
    });

    it('should delete session and its messages', async () => {
      const session = await sessionsDB.create({});
      await messagesDB.create({ sessionId: session.id, role: 'user', content: 'Hi' });
      await sessionsDB.delete(session.id);
      const messages = await messagesDB.list(session.id);
      expect(messages).toHaveLength(0);
    });
  });

  describe('messagesDB', () => {
    it('should create a message with attachments', async () => {
      const message = await messagesDB.create({
        sessionId: 'test-session',
        role: 'user',
        content: 'Check this file',
        attachments: [{ name: 'test.ts', path: '/test.ts', type: 'file', size: 100 }]
      });
      expect(message.attachments).toHaveLength(1);
    });

    it('should paginate messages', async () => {
      const messages = await messagesDB.list('test-session', { limit: 10 });
      expect(messages.length).toBeLessThanOrEqual(10);
    });
  });
});

// claude-client.test.ts
describe('Claude Client', () => {
  it('should resolve provider config correctly', () => {
    const resolved = resolveForClaudeCode({ provider: 'anthropic', apiKey: 'test-key' }, {});
    expect(resolved.apiKey).toBe('test-key');
  });

  it('should sanitize environment variables', () => {
    const env = sanitizeEnv({ PATH: '/usr/bin', HOME: '/home/user' });
    expect(env.ANTHROPIC_API_KEY).toBeUndefined();
  });
});
```

#### 3.2.2 集成测试

```typescript
// chat.integration.test.ts
describe('Chat Flow', () => {
  it('should send message and receive response', async () => {
    // 1. Create session
    const session = await createSession();

    // 2. Send message
    const response = await fetch('/api/chat/messages', {
      method: 'POST',
      body: JSON.stringify({ sessionId: session.id, content: 'Hello' })
    });

    // 3. Verify SSE stream
    expect(response.headers.get('content-type')).toBe('text/event-stream');

    // 4. Collect stream events
    const events = await collectStreamEvents(response);
    expect(events).toContainEqual({ type: 'text', content: expect.any(String) });
    expect(events).toContainEqual({ type: 'done' });

    // 5. Verify message saved
    const messages = await getMessages(session.id);
    expect(messages).toHaveLength(2); // user + assistant
  });
});
```

---

### 3.3 性能要求

| 指标 | 要求 | 说明 |
|------|------|------|
| 应用启动时间 | < 5s | 从点击图标到显示界面 |
| 首次消息响应 | < 3s | 发送后到收到首字节 |
| 消息渲染延迟 | < 100ms | SSE 事件到 UI 更新 |
| 会话切换时间 | < 500ms | 切换会话到显示消息 |
| 数据库查询 | < 50ms | 单次查询响应时间 |
| 内存占用 | < 500MB | 正常使用内存 |
| 包体积 | < 200MB | 安装包大小 |

---

## 4. 依赖清单

### 4.1 NPM 包列表

```json
{
  "dependencies": {
    // Electron
    "electron": "^40.0.0",

    // Next.js
    "next": "^16.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",

    // UI
    "tailwindcss": "^4.0.0",
    "@radix-ui/react-dialog": "^1.1.0",
    "@radix-ui/react-dropdown-menu": "^2.1.0",
    "@radix-ui/react-tabs": "^1.1.0",
    "@radix-ui/react-scroll-area": "^1.2.0",

    // Database
    "better-sqlite3": "^11.0.0",

    // Claude SDK
    "@anthropic-ai/claude-agent-sdk": "^1.0.0",

    // Utilities
    "uuid": "^10.0.0",
    "zod": "^3.23.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.5.0"
  },
  "devDependencies": {
    // TypeScript
    "typescript": "^5.7.0",
    "@types/node": "^22.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "@types/better-sqlite3": "^7.6.0",
    "@types/uuid": "^10.0.0",

    // Build
    "electron-builder": "^25.0.0",
    "electron-rebuild": "^3.2.0",

    // Testing
    "vitest": "^2.0.0",
    "@testing-library/react": "^16.0.0",
    "playwright": "^1.48.0",

    // Linting
    "eslint": "^9.0.0",
    "eslint-config-next": "^16.0.0"
  }
}
```

### 4.2 环境要求

#### 4.2.1 运行时环境

| 项目 | 要求 |
|------|------|
| Node.js | >= 20.0.0 (LTS) |
| npm | >= 10.0.0 |
| 操作系统 | macOS 12+ / Windows 10+ / Ubuntu 20.04+ |
| 架构 | x64 / ARM64 |

#### 4.2.2 Claude Code 要求

| 项目 | 要求 |
|------|------|
| Claude Code CLI | >= 1.0.0 |
| 安装方式 | npm global / brew / direct download |

#### 4.2.3 开发环境

| 项目 | 要求 |
|------|------|
| Node.js | >= 22.0.0 |
| pnpm | >= 9.0.0 |
| Git | >= 2.40.0 |

---

## 附录 A: 错误代码定义

| 错误代码 | 错误类型 | 说明 |
|----------|----------|------|
| `E001` | `CLAUDE_NOT_INSTALLED` | Claude Code 未安装 |
| `E002` | `CLAUDE_VERSION_INCOMPATIBLE` | Claude Code 版本不兼容 |
| `E003` | `INSTALL_FAILED` | 安装失败 |
| `E004` | `INSTALL_TIMEOUT` | 安装超时 |
| `E005` | `DIRECTORY_NOT_ACCESSIBLE` | 目录不可访问 |
| `E006` | `SESSION_NOT_FOUND` | 会话不存在 |
| `E007` | `MESSAGE_SEND_FAILED` | 消息发送失败 |
| `E008` | `STREAM_INTERRUPTED` | 流中断 |
| `E009` | `MCP_SERVER_ERROR` | MCP 服务器错误 |
| `E010` | `PERMISSION_DENIED` | 权限被拒绝 |
| `E011` | `API_KEY_INVALID` | API Key 无效 |
| `E012` | `RATE_LIMIT_EXCEEDED` | 速率限制 |

---

## 附录 B: 版本历史

| 版本 | 日期 | 修改内容 |
|------|------|----------|
| v1.0 | 2026-03-31 | 初始版本，基于技术方案文档 |

---

*文档状态: 草稿 | 审核状态: 待审核*
