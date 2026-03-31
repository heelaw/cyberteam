# CyberTeam Desktop — 项目路线图

> 版本：v1.0.0 | 制定日期：2026-03-31 | 技术栈：Tauri 2.x + React 18 + Vite 6 + TypeScript 5 + Rust

---

## 一、项目愿景

打造一款 macOS 原生桌面应用（类 CodePilot），深度集成 Claude Code CLI（`/opt/homebrew/bin/claude`），为 CyberTeam Agent 系统提供本地执行环境。应用需支持 Settings（API/CLI 配置）、Skills（技能管理）、Agents（数字员工管理）、Chat（实时对话）等完整功能，并通过 Tauri 实现 native 级别的性能与系统集成。

**对标产品**：GitHub Copilot Desktop、CodePilot（Electron 版）
**差异化**：CyberTeam Desktop 是 CyberTeam Agent 系统的本地入口，而非通用 AI 聊天工具。

---

## 二、技术决策（Architectural Decisions）

### 2.1 核心架构

```
┌─────────────────────────────────────────────────────────┐
│                    Tauri WebView                         │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              React + Vite + TypeScript               │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────┐  │ │
│  │  │  Chat    │ │ Settings │ │  Skills  │ │Agents │  │ │
│  │  │  Module  │ │  Module  │ │  Module  │ │Module │  │ │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └───┬───┘  │ │
│  │       └────────────┴────────────┴────────────┘       │ │
│  │                      │                               │ │
│  │              ┌──────┴──────┐                        │ │
│  │              │  API Client │                        │ │
│  │              │  (Tauri IPC)│                        │ │
│  │              └──────┬──────┘                        │ │
│  └─────────────────────┼───────────────────────────────┘ │
│                         │                                  │
│  ┌──────────────────────┼───────────────────────────────┐ │
│  │            Rust Tauri Backend                        │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌───────────────┐  │ │
│  │  │ Claude Code │ │  SQLite DB  │ │ File System   │  │ │
│  │  │  CLI Spawn  │ │  (Settings) │ │  (Projects)   │  │ │
│  │  └─────────────┘ └─────────────┘ └───────────────┘  │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

### 2.2 关键技术选型

| 层级 | 技术选型 | 理由 |
|------|----------|------|
| **桌面框架** | Tauri 2.x | 比 Electron 更小（~10MB vs ~150MB）、更快、更安全 |
| **前端框架** | React 18 + Vite 6 | HMR 快，生态成熟 |
| **类型系统** | TypeScript 5 | 严格模式保证代码质量 |
| **UI 组件库** | Ant Design 5 或 shadcn/ui | 参照 cyberteam-v5 用 Ant Design |
| **状态管理** | Zustand | 轻量、无 boilerplate |
| **路由** | React Router v6 | 标准 SPA 路由 |
| **CLI 集成** | `claude --dangerously-skip-permissions` | 跳过权限确认实现自动化 |
| **数据持久化** | SQLite via `rusqlite` | Tauri 原生支持，存储 Settings/Agents |
| **进程管理** | Rust `tokio::process` | Claude Code CLI 的 spawn/interrupt |
| **IPC** | Tauri Commands (Rust ↔ JS) | 类型安全的双向通信 |
| **样式** | Tailwind CSS 4 | 快速开发响应式 UI |

### 2.3 Claude Code CLI 集成方案

**CLI 路径**：`/opt/homebrew/bin/claude`（macOS Homebrew 安装路径）

**集成模式**：
1. **Spawn 模式**（Phase 1）：通过 Rust 后端 `Command::new("claude")` spawn 子进程，stdin/stdout 通过 Tauri IPC流传回前端
2. **Message Protocol**：使用 Claude Code 的 JSON message protocol（stdin 输入 JSON，stdout 输出 SSE-like 格式）
3. **Session 管理**：每个 Chat Session 对应一个 Claude Code subprocess，支持 interrupt（Ctrl+C）和 restart
4. **权限模式**：`--dangerously-skip-permissions` flag 实现无打扰自动化

**参考代码**：直接复用 `codepilot-desktop/src/lib/claude-client.ts` 中的 `streamClaude()` 逻辑，迁移到 Rust 侧实现

### 2.4 数据库 Schema（SQLite）

```sql
-- Settings 表
CREATE TABLE settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at INTEGER NOT NULL
);

-- Agents 表
CREATE TABLE agents (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  role TEXT NOT NULL,
  soul_md TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

-- Sessions 表（Chat 历史）
CREATE TABLE sessions (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

-- Messages 表
CREATE TABLE messages (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  role TEXT NOT NULL,  -- 'user' | 'assistant'
  content TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  FOREIGN KEY (session_id) REFERENCES sessions(id)
);
```

---

## 三、项目阶段划分

### Phase 0 · 脚手架 & 基础设施（预估 1 周）

**目标**：建立 Tauri + React 项目，配置开发环境，验证 Claude Code CLI 调用通路。

#### 任务清单

- [ ] **T0-1** 初始化 Tauri 2.x 项目，使用 `npm create tauri-app` 选择 React + TypeScript 模板
- [ ] **T0-2** 配置 Vite 6 + TypeScript 5 + Tailwind CSS 4
- [ ] **T0-3** 配置项目目录结构（参照 cyberteam-v5 frontend 结构）
  ```
  src/
  ├── components/    # 通用 UI 组件
  ├── pages/         # Chat / Settings / Skills / Agents
  ├── stores/        # Zustand stores
  ├── hooks/         # 自定义 hooks（含 SSE stream hook）
  ├── lib/           # API client、Tauri IPC 调用
  └── types/         # TypeScript 类型定义
  ```
- [ ] **T0-4** 配置 ESLint + Prettier + Husky pre-commit
- [ ] **T0-5** Rust 后端基础：Cargo.toml 依赖（`rusqlite`、`tokio`、`serde`、`tauri`）
- [ ] **T0-6** 验证 Claude Code CLI 可执行：`tauri dev` 中调用 `/opt/homebrew/bin/claude --version`
- [ ] **T0-7** 配置 `codepilot-desktop` 中已有组件的迁移路径（保留可复用部分）

#### 里程碑（M0）
> ✅ `tauri dev` 能启动应用窗口，且 Rust 后端能成功 spawn Claude Code CLI 子进程

---

### Phase 1 · 核心对话功能（预估 2 周）

**目标**：实现 Chat 模块，具备与 Claude Code CLI 的实时对话能力。

#### 任务清单

- [ ] **T1-1** Rust：`claude_code_spawn` command — 创建 Claude Code subprocess，返回 session_id
- [ ] **T1-2** Rust：`claude_code_send` command — 向 subprocess 发送 JSON 消息
- [ ] **T1-3** Rust：`claude_code_interrupt` command — 发送 interrupt 信号（SIGINT）
- [ ] **T1-4** Rust：`claude_code_resume` command — resume 已中断的 session
- [ ] **T1-5** Rust：`claude_code_destroy` command — 销毁 subprocess
- [ ] **T1-6** 前端：`useChat` hook — 管理当前 session 的消息状态（Zustand store）
- [ ] **T1-7** 前端：`useSSEStream` hook — 消费 Tauri event stream，渲染增量文本
- [ ] **T1-8** 前端：Chat 页面布局（参照 cyberteam-v5 `ChatRoom.tsx`）
- [ ] **T1-9** 前端：消息气泡组件（user / assistant 区分，支持 markdown 渲染）
- [ ] **T1-10** 前端：工具调用卡片渲染（tool_use / tool_result 展示）
- [ ] **T1-11** 前端：Interrupt 按钮（中止当前生成）
- [ ] **T1-12** 前端：Session 列表侧边栏（历史会话）
- [ ] **T1-13** SQLite：Sessions / Messages 表的持久化 CRUD
- [ ] **T1-14** 前端：Chat 页面从 SQLite 加载历史记录

#### 里程碑（M1）
> ✅ 用户可以在桌面应用中与 Claude Code CLI 对话，看到实时流式输出，能中断生成，历史会话自动保存

---

### Phase 2 · 配置与权限管理（预估 1.5 周）

**目标**：实现 Settings 模块，支持 API Key、CLI 路径、Permission Mode 等配置。

#### 任务清单

- [ ] **T2-1** SQLite：`settings` 表的 Rust CRUD commands
- [ ] **T2-2** 前端：`useSettings` hook — 读取/写入 settings store
- [ ] **T2-3** 前端：Settings 页面 UI（配置分组）
  - **API 配置**：ANTHROPIC_API_KEY（密钥脱敏展示）
  - **CLI 配置**：`claude` 路径（默认 `/opt/homebrew/bin/claude`）
  - **权限模式**：Bypass Permissions 开关
  - **主题**：Dark / Light / System
- [ ] **T2-4** Rust：启动时从 SQLite 加载 Settings，注入 Claude Code subprocess env
- [ ] **T2-5** 前端：Permission Mode 实时切换（Bypass / AcceptEdits）
- [ ] **T2-6** 前端：设置变更时自动重启当前 Claude Code session（提示用户）

#### 里程碑（M2）
> ✅ 用户可在 Settings 中配置 API Key、CLI 路径、权限模式，配置自动持久化并生效

---

### Phase 3 · Skills 管理模块（预估 1.5 周）

**目标**：实现 Skills 模块，支持 Skill 的查看、安装、配置、启用/停用。

#### 任务清单

- [ ] **T3-1** SQLite：`skills` 表 schema（含 skill_id、name、description、trigger、workflow_md、enabled）
- [ ] **T3-2** Rust：`skills_list` / `skills_get` / `skills_enable` / `skills_disable` commands
- [ ] **T3-3** 前端：`useSkills` hook + Zustand store
- [ ] **T3-4** 前端：Skills 页面布局（卡片网格 / 列表视图切换）
- [ ] **T3-5** 前端：Skill 详情抽屉（trigger 条件、workflow 预览、配置项）
- [ ] **T3-6** 前端：Skill 安装功能（从本地 `.claude/skills/` 目录扫描导入，或从 URL 安装）
- [ ] **T3-7** 前端：Skill 启用/停用切换（影响 Chat 中 Skill 的可用性）
- [ ] **T3-8** 前端：Skill 市场tab（browse 内置 + 用户上传的 Skills）

#### 里程碑（M3）
> ✅ 用户可浏览、安装、配置、启用/停用 Skills，Skills 配置影响对话行为

---

### Phase 4 · Agents 管理模块（预估 1.5 周）

**目标**：实现 Agents 模块，支持 Agent 的查看、创建、编辑、删除。

#### 任务清单

- [ ] **T4-1** SQLite：`agents` 表 schema（含 id、name、role、soul_md、metadata）
- [ ] **T4-2** Rust：`agents_list` / `agents_get` / `agents_create` / `agents_update` / `agents_delete` commands
- [ ] **T4-3** 前端：`useAgents` hook + Zustand store
- [ ] **T4-4** 前端：Agents 页面布局（卡片网格，展示 Avatar / Name / Role）
- [ ] **T4-5** 前端：Agent 详情页（SOUL.md 编辑器，含实时预览）
- [ ] **T4-6** 前端：Agent 创建向导（name → role → SOUL.md）
- [ ] **T4-7** 前端：Agent Marketplace tab（浏览系统内置 Agents）
- [ ] **T4-8** 前端：Agent 与 Chat 的联动（选择 Agent 后以其角色身份开始对话）

#### 里程碑（M4）
> ✅ 用户可完整管理 Agents（CRUD），Agent 配置后可在 Chat 中以其身份进行对话

---

### Phase 5 · 系统集成 & 打包（预估 1 周）

**目标**：完善 macOS 原生集成，通过 Tauri 生成可分发 .app 文件。

#### 任务清单

- [ ] **T5-1** macOS 菜单栏（Native Menu）：File / Edit / View / Session / Help
- [ ] **T5-2** macOS 系统托盘（System Tray）：最小化到托盘、Quick Chat shortcut
- [ ] **T5-3** 全局快捷键：例如 `Cmd+Shift+C` 快速唤起应用窗口
- [ ] **T5-4** 文件拖拽上传：Chat 中支持拖拽文件到窗口，自动附加到 prompt
- [ ] **T5-5** 窗口管理：记住窗口位置/大小、多窗口支持（Chat 窗口 + Agent Editor）
- [ ] **T5-6** Tauri Build 配置：`appId`、`signing`、`entitlements`（Camera/Microphone 等权限）
- [ ] **T5-7** 构建验证：`tauri build` 生成 `.app` 并在真机上运行测试
- [ ] **T5-8** Auto-Update 机制（可选，Phase 6）：Tauri updater plugin

#### 里程碑（M5）
> ✅ `tauri build` 成功生成 macOS .app，可分发给用户安装使用

---

### Phase 6 · 增强功能 & 稳定性（预估 1 周）

**目标**：补齐高级功能，提升稳定性和用户体验。

#### 任务清单

- [ ] **T6-1** 多 Session 并行：同时运行多个 Claude Code subprocess（Tab 页）
- [ ] **T6-2** MCP Server 管理（参照 codepilot-desktop `src/app/api/mcp/servers/`）：在 Settings 中配置 MCP Servers
- [ ] **T6-3** 项目目录管理：指定工作目录（cwd），支持多项目切换
- [ ] **T6-4** 对话导出：Markdown / JSON 格式导出对话记录
- [ ] **T6-5** 性能优化：Virtual list 渲染长对话、WebView 内存优化
- [ ] **T6-6** 错误处理增强：Claude Code 退出的错误码解析、自动 resume 逻辑
- [ ] **T6-7** 日志系统：Rust 侧 `tracing` + 前端 error boundary
- [ ] **T6-8** 国际化（i18n）：预留 i18n 框架（中文/English）

#### 里程碑（M6）
> ✅ 应用具备完整的企业级功能集，可作为 CyberTeam 系统的正式桌面客户端发布

---

## 四、完整任务总表

| Phase | 任务 ID | 描述 | 优先级 | 预估工时 |
|-------|---------|------|--------|----------|
| 0 | T0-1 | 初始化 Tauri 项目 | P0 | 1h |
| 0 | T0-2 | 配置 Vite + TS + Tailwind | P0 | 1h |
| 0 | T0-3 | 目录结构与 ESLint | P1 | 1h |
| 0 | T0-4 | Rust 基础依赖 | P0 | 0.5h |
| 0 | T0-5 | CLI 路径验证 | P0 | 0.5h |
| 1 | T1-1 | claude_code_spawn | P0 | 2h |
| 1 | T1-2 | claude_code_send | P0 | 1h |
| 1 | T1-3 | claude_code_interrupt | P0 | 1h |
| 1 | T1-4 | claude_code_destroy | P0 | 1h |
| 1 | T1-5 | 前端 useChat hook | P0 | 2h |
| 1 | T1-6 | 前端 Chat 页面 | P0 | 4h |
| 1 | T1-7 | Session 持久化 | P1 | 2h |
| 2 | T2-1 | Settings Rust CRUD | P0 | 2h |
| 2 | T2-2 | 前端 Settings 页面 | P0 | 3h |
| 2 | T2-3 | Permission Mode 切换 | P1 | 1h |
| 3 | T3-1 | Skills Rust CRUD | P0 | 2h |
| 3 | T3-2 | 前端 Skills 页面 | P0 | 4h |
| 3 | T3-3 | Skill 安装/导入 | P1 | 2h |
| 4 | T4-1 | Agents Rust CRUD | P0 | 2h |
| 4 | T4-2 | 前端 Agents 页面 | P0 | 4h |
| 4 | T4-3 | Agent SOUL.md 编辑器 | P1 | 3h |
| 5 | T5-1 | macOS 菜单栏 | P1 | 2h |
| 5 | T5-2 | System Tray | P1 | 2h |
| 5 | T5-3 | 全局快捷键 | P1 | 1h |
| 5 | T5-4 | 文件拖拽 | P1 | 1h |
| 5 | T5-5 | Tauri Build 打包 | P0 | 2h |
| 6 | T6-1 | 多 Session Tab | P2 | 3h |
| 6 | T6-2 | MCP Server 管理 | P1 | 2h |
| 6 | T6-3 | 对话导出 | P2 | 1h |
| 6 | T6-4 | 性能优化 | P2 | 2h |

---

## 五、里程碑汇总

| 里程碑 | 完成条件 | 对应 Phase |
|--------|----------|------------|
| **M0** 脚手架完成 | `tauri dev` 启动 + CLI 调用验证 | Phase 0 |
| **M1** 核心对话完成 | 能与 Claude Code 对话、流式输出、持久化 | Phase 1 |
| **M2** 配置模块完成 | Settings 全功能 + 权限模式切换 | Phase 2 |
| **M3** Skills 管理完成 | Skill CRUD + 启用/停用 + 安装 | Phase 3 |
| **M4** Agents 管理完成 | Agent CRUD + SOUL.md 编辑 + Chat 联动 | Phase 4 |
| **M5** 可打包发布 | `tauri build` 生成 .app 并验证运行 | Phase 5 |
| **M6** 企业级功能集 | 多 Session、MCP、项目管理、性能优化 | Phase 6 |

---

## 六、技术风险与对策

| 风险 | 影响 | 对策 |
|------|------|------|
| Claude Code CLI 协议变更 | CLI 集成失效 | 封装 `claude --print-format json` 协议层，版本检测降级 |
| Tauri IPC 性能瓶颈 | 流式输出延迟 | 使用 Tauri event 而非 request/response，批量 flush |
| SQLite 并发写入 | 多 session 写冲突 | Rust 侧使用 `rusqlite` 线程安全模式 + WAL |
| macOS 权限沙盒 | Claude Code 无法访问文件 | 申请 `com.apple.security.files.user-selected.read-write` entitlement |
| Claude Code 内存泄漏 | 长时间运行 OOM | Session 超时自动 destroy，定期检测 subprocess 内存 |

---

## 七、依赖关系图

```
Phase 0 (T0-*)
    │
    ▼
Phase 1 (T1-*)  ← 依赖 T0-5（CLI 验证）
    │
    ▼
Phase 2 (T2-*)  ← 可与 Phase 1 并行（数据层独立）
Phase 3 (T3-*)  ← 可与 Phase 2 并行
Phase 4 (T4-*)  ← 可与 Phase 3 并行
    │
    └──────────────────────────────┐
                                   ▼
                              Phase 5 (T5-*)  ← 依赖 Phase 1-4
                                   │
                                   ▼
                              Phase 6 (T6-*)  ← 依赖 Phase 5
```

---

## 八、目录结构（目标状态）

```
Output/cyberteam-desktop/
├── src/                          # React 前端
│   ├── components/
│   │   ├── ui/                   # 基础 UI 组件（Button/Input/Dialog/Tabs）
│   │   ├── chat/                 # Chat 相关组件
│   │   │   ├── ChatBubble.tsx
│   │   │   ├── ToolCard.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   └── SessionList.tsx
│   │   ├── settings/
│   │   └── agents/
│   ├── pages/
│   │   ├── Chat.tsx              # 主 Chat 页面
│   │   ├── Settings.tsx
│   │   ├── Skills.tsx
│   │   └── Agents.tsx
│   ├── stores/
│   │   ├── chatStore.ts          # Zustand: 当前会话状态
│   │   ├── settingsStore.ts
│   │   ├── skillsStore.ts
│   │   └── agentsStore.ts
│   ├── hooks/
│   │   ├── useChat.ts
│   │   ├── useSSEStream.ts
│   │   ├── useSettings.ts
│   │   └── useAgents.ts
│   ├── lib/
│   │   └── tauri.ts              # Tauri IPC 调用封装
│   └── types/
│       └── index.ts
├── src-tauri/                    # Rust 后端
│   ├── src/
│   │   ├── main.rs               # Tauri entry
│   │   ├── lib.rs
│   │   ├── commands/
│   │   │   ├── mod.rs
│   │   │   ├── claude.rs         # Claude Code CLI commands
│   │   │   ├── settings.rs       # Settings CRUD
│   │   │   ├── skills.rs         # Skills CRUD
│   │   │   └── agents.rs         # Agents CRUD
│   │   ├── db/
│   │   │   ├── mod.rs
│   │   │   └── schema.rs         # SQLite schema
│   │   └── process/
│   │       ├── mod.rs
│   │       └── session.rs        # Claude Code subprocess 管理
│   ├── Cargo.toml
│   └── tauri.conf.json
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.ts
├── ROADMAP.md
└── README.md
```
