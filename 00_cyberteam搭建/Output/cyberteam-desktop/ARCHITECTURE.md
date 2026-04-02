# CyberTeam Desktop - 完整技术方案

> 基于 4 个研究 Agent 对 **CodePilot-0.43.1**、**Magic**、**CyberTeam V4**、**ClawTeam**、**聊天界面最佳实践** 的深度研究综合产出

---

## 一、项目定位

**CyberTeam Desktop** 是一个 macOS 桌面应用，定位为「AI 军团工作台」：

1. **自定义公司架构** — 部门 + Agent（员工）+ Skill（能力）
2. **多 Agent 协作** — 群聊讨论、@提及、任务分配、CEO 审核
3. **对话即工作** — Claude Code CLI 驱动真实 AI 执行
4. **Playground 输出** — 交互式看板 + 会议纪要 + CEO 审核报告

---

## 二、技术架构决策

### 2.1 为什么选 Electron（不是 Tauri）

| 维度 | Tauri (Rust) | Electron (Node.js) |
|------|:---:|:---:|
| 二次开发门槛 | 要学 Rust | 会 JS 就行 |
| Claude Code SDK | 不支持（需 Node.js） | @anthropic-ai/claude-agent-sdk 直连 |
| 数据库 | JSON / Rust crate | better-sqlite3（成熟） |
| 调试 | Rust 报错难懂 | Chrome DevTools |
| 打包 | 限制多 | electron-builder 成熟 |
| **实际验证** | ❌ | ✅ CodePilot 0.43.1 稳定运行 |

### 2.2 技术栈

```
┌──────────────────────────────────────────────────────────────┐
│  Electron 40                                                 │
│  ├── main process: Node.js (SQLite + Claude SDK + IPC)    │
│  ├── preload: contextBridge (安全 API 暴露)                  │
│  └── renderer: React 19 + Vite                              │
├──────────────────────────────────────────────────────────────┤
│  前端 (React 19)                                             │
│  ├── Zustand — 状态管理                                      │
│  ├── TipTap + @mention — 输入框 @ 触发（Magic 1200ms 窗口） │
│  ├── Tailwind CSS 4 + shadcn/ui — UI 组件                   │
│  ├── react-markdown + Shiki — Markdown 渲染                 │
│  └── @tanstack/react-virtual — 虚拟滚动                      │
├──────────────────────────────────────────────────────────────┤
│  后端 (Electron main process)                                │
│  ├── better-sqlite3 — 数据库（12 张表，CodePilot 方案）      │
│  ├── @anthropic-ai/claude-agent-sdk — Claude Code CLI       │
│  ├── node-pty — 终端模拟器                                   │
│  └── electron-builder — 打包 .dmg                            │
└──────────────────────────────────────────────────────────────┘
```

---

## 三、数据库设计

### 3.1 核心表（CodePilot 方案 + CyberTeam 扩展）

```sql
-- ============ CodePilot 原有表（直接复用） ============

CREATE TABLE api_providers (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  provider_type TEXT NOT NULL DEFAULT 'anthropic',
  protocol TEXT NOT NULL DEFAULT '',
  base_url TEXT NOT NULL DEFAULT '',
  api_key TEXT NOT NULL DEFAULT '',
  is_active INTEGER NOT NULL DEFAULT 0,
  sort_order INTEGER NOT NULL DEFAULT 0,
  extra_env TEXT NOT NULL DEFAULT '{}',
  headers_json TEXT NOT NULL DEFAULT '{}',
  role_models_json TEXT NOT NULL DEFAULT '{}',
  notes TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE chat_sessions (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL DEFAULT 'New Chat',
  working_directory TEXT NOT NULL DEFAULT '',
  provider_id TEXT NOT NULL DEFAULT '',
  model TEXT NOT NULL DEFAULT '',
  system_prompt TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  status TEXT NOT NULL DEFAULT 'active',
  -- CyberTeam 扩展
  conversation_type TEXT NOT NULL DEFAULT 'single',  -- single/group/department
  department_id TEXT,
  project_id TEXT,
  review_status TEXT NOT NULL DEFAULT 'pending'  -- pending/approved/rejected
);

CREATE TABLE messages (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
  content TEXT NOT NULL,
  sender_id TEXT NOT NULL DEFAULT '',
  sender_name TEXT NOT NULL DEFAULT '',
  sender_avatar TEXT NOT NULL DEFAULT '',
  metadata TEXT NOT NULL DEFAULT '{}',  -- {mentions: [{id, name, type}], reply_to: ''}
  token_usage TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
);

CREATE TABLE settings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  key TEXT NOT NULL UNIQUE,
  value TEXT NOT NULL
);

-- ============ CyberTeam 新增表 ============

-- 项目（独立项目概念）
CREATE TABLE projects (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  working_directory TEXT NOT NULL DEFAULT '',
  department_id TEXT,
  status TEXT NOT NULL DEFAULT 'active',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 部门
CREATE TABLE departments (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  icon TEXT NOT NULL DEFAULT '',
  parent_id TEXT,
  description TEXT NOT NULL DEFAULT '',
  sort_order INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (parent_id) REFERENCES departments(id)
);

-- Agent 定义
CREATE TABLE agents (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  avatar TEXT NOT NULL DEFAULT '',
  role TEXT NOT NULL DEFAULT 'expert',  -- ceo/manager/expert/executor
  department_id TEXT NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  soul_content TEXT NOT NULL DEFAULT '',  -- SOUL.md 内容
  status TEXT NOT NULL DEFAULT 'offline',  -- online/offline/busy
  capabilities TEXT NOT NULL DEFAULT '[]',  -- 能力标签
  config TEXT NOT NULL DEFAULT '{}',  -- 模型/温度等
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- 技能定义
CREATE TABLE skills (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT NOT NULL DEFAULT '',
  description TEXT NOT NULL DEFAULT '',
  content TEXT NOT NULL DEFAULT '',  -- SKILL.md 内容
  trigger_keywords TEXT NOT NULL DEFAULT '[]',
  enabled INTEGER NOT NULL DEFAULT 1,
  source TEXT NOT NULL DEFAULT 'custom',  -- builtin/custom/market
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Agent-Skill 绑定
CREATE TABLE agent_skills (
  id TEXT PRIMARY KEY,
  agent_id TEXT NOT NULL,
  skill_id TEXT NOT NULL,
  enabled INTEGER NOT NULL DEFAULT 1,
  FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
  FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

-- 部门市场（参考 Magic）
CREATE TABLE agent_market (
  id TEXT PRIMARY KEY,
  agent_code TEXT NOT NULL UNIQUE,
  name_i18n TEXT NOT NULL DEFAULT '{}',  -- {zh, en}
  role_i18n TEXT NOT NULL DEFAULT '{}',
  description_i18n TEXT NOT NULL DEFAULT '{}',
  icon TEXT,
  prompt TEXT,
  skills TEXT NOT NULL DEFAULT '[]',
  features TEXT NOT NULL DEFAULT '[]',
  source_type TEXT NOT NULL DEFAULT 'LOCAL_CREATE',
  category_id TEXT,
  is_added INTEGER NOT NULL DEFAULT 0,
  allow_delete INTEGER NOT NULL DEFAULT 1,
  publisher_type TEXT NOT NULL DEFAULT 'USER',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 会议纪要
CREATE TABLE meeting_minutes (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  meeting_type TEXT NOT NULL,  -- ceo_coo/strategy/risk/ceo_report
  title TEXT NOT NULL,
  content TEXT NOT NULL DEFAULT '',
  review_status TEXT NOT NULL DEFAULT 'pending',
  attachments TEXT NOT NULL DEFAULT '[]',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- 团队模板（参考 Magic Crew）
CREATE TABLE crew_templates (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  members TEXT NOT NULL DEFAULT '[]',
  departments TEXT NOT NULL DEFAULT '[]',
  is_preset INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

### 3.2 数据存储位置

```
~/Library/Application Support/CyberTeam/
├── cyberteam.db              # SQLite 数据库
├── cyberteam.db-wal          # WAL 日志
├── avatars/                  # Agent 头像
├── projects/                 # 项目文件
└── config.json               # 应用配置
```

---

## 四、功能模块设计

### 4.1 模块总览

```
CyberTeam Desktop
├── 1. 启动页 — 仿 CodePilot 初始化
├── 2. 设置页 — API Provider 管理（7种协议）
├── 3. 部门管理 — 组织架构编辑器
├── 4. Agent 市场 — 浏览/安装/配置
├── 5. Skill 管理 — 技能 CRUD + 启停
├── 6. 对话页 — 微信风格聊天 + @mention + 流式响应
├── 7. 项目管理 — 独立项目 + Playground
└── 8. 任务看板 — ClawTeam 风格任务管理
```

### 4.2 对话页详细设计（核心功能）

```
┌─────────────────────────────────────────────────────────────┐
│  CyberTeam Desktop                                  _ □ × │
├──────────┬──────────────────────────────────────────────┤
│          │  聊天标题栏                                    │
│  搜索框  │  「增长部门群」| 5 位成员在线 | ⚙️             │
│          ├──────────────────────────────────────────────┤
│  部门树  │                                              │
│  ├ CEO   │  ┌─────────────────────────────────────┐   │
│  ├ COO   │  │ 🟢 运营总监                    10:30 │   │
│  ├ 增长部│  │    根据数据分析，小红书的曝光量     │   │
│  │├增长总监│    需要提升 30%...                    │   │
│  │└SEO专员│  └─────────────────────────────────────┘   │
│  ├ 产品部│                                              │
│  ├ 运营部│  ┌─────────────────────────────────────┐   │
│  └ 质量部│  │ 🔵 CEO（你）                    10:31 │   │
│          │  │    @增长总监 请给出具体的执行方案    │   │
│  ──────  │  └─────────────────────────────────────┘   │
│  会话列表│                                              │
│  ├ 💬增长部│  ┌─────────────────────────────────────┐   │
│  │  群聊  │  │ 🟡 增长总监 ▸typing...              │   │
│  ├ 💬1:1  │  │                                     │   │
│  │  COO   │  └─────────────────────────────────────┘   │
│  └ 💬产品部│                                              │
│     群聊  │  ┌─────────────────────────────────────┐   │
│          │  │  @  [发送]                           │   │
│  ──────  │  │  ┌──────────────┐                    │   │
│  + 新建群│  │  │ 🟢 运营总监  │                    │   │
│          │  │  │ 🟢 增长总监  │ ← @mention 下拉    │   │
│          │  │  │ 🟢 产品总监  │                    │   │
│          │  │  └──────────────┘                    │   │
│          │  └─────────────────────────────────────┘   │
└──────────┴──────────────────────────────────────────────┘
```

### 4.3 会话类型

| 类型 | 说明 | 创建方式 |
|------|------|---------|
| **单聊** | 用户 ↔ 单个 Agent | 点击 Agent 头像 |
| **群聊** | 用户 + 多个 Agent | 新建群聊 → 选择 Agent |
| **部门群** | 用户 + 整个部门 | 点击部门「发起部门会议」 |
| **Crew 团队** | 预设模板团队 | 从团队模板一键创建 |

### 4.4 @mention 机制（照搬 Magic，1200ms 窗口）

```typescript
// 触发字符 + 1200ms 激活窗口
const MENTION_INPUT_ACTIVATION_WINDOW_MS = 1200

// 触发条件
const lastAtInputAt = editor.storage.mention?.lastAtInputAt ?? 0
const isInActivationWindow =
  Date.now() - lastAtInputAt <= MENTION_INPUT_ACTIVATION_WINDOW_MS

// Mention 类型
enum MentionItemType {
  AGENT = "agent",
  SKILL = "skill",
  DEPARTMENT = "department",
  FILE = "project_file",
}

// Mention 节点数据结构
interface MentionNode {
  type: 'mention'
  attrs: {
    id: string
    name: string
    avatar: string
    department: string
    role: string
    data: AgentMentionData | SkillMentionData
  }
}
```

**可复制文件**（来自 Magic）：
| 文件 | 功能 |
|------|------|
| `MentionExtension.ts` | TipTap @mention 扩展（1200ms 窗口）|
| `suggestion.ts` | 触发配置 |
| `MentionNodeView.tsx` | 节点渲染 |
| `MentionPanelRenderer.tsx` | 下拉选择器 |
| `types.ts` | 类型定义 |

### 4.5 流式响应（照搬 Magic）

```typescript
// 打字机效果
const { content: typedContent, typing, add, start, done } = useTyping(content)

useUpdateEffect(() => {
  if (content) {
    add(content.substring(lastContentRef.current.length))
    lastContentRef.current = content
    if (!typing && isStreaming) start()
  }
}, [content])

// 流式光标管理
useStreamCursor(isStreaming || typing, typedContent, markdownRef)
```

**可复制文件**（来自 Magic）：
| 文件 | 功能 |
|------|------|
| `EnhanceMarkdown/index.tsx` | Markdown + typing 效果 |
| `useTyping.tsx` | 打字机实现 |
| `useStreamCursor.ts` | 流式光标 |
| `StreamingPlaceholder/index.tsx` | 加载占位符 |

---

## 五、项目/工作目录管理

### 5.1 独立项目概念（修复 CodePilot bug）

| 问题 | CodePilot | CyberTeam 修复 |
|------|-----------|----------------|
| 无项目抽象 | 只有 session | 新增 `projects` 表 |
| 目录切换清空 sdk_session_id | 有 bug | 修复：保留除非跨盘符 |
| 目录不存在静默失败 | 有 bug | 主动验证 + 提示 |

### 5.2 目录验证链

```
用户选择目录
    ↓
validate_directory(path) — fs.statSync().isDirectory()
    ↓
POST /api/chat/sessions → session.working_directory = path
    ↓
localStorage.setItem("cyberteam:last-working-directory", path)
    ↓
刷新 → localStorage → validate → 恢复会话
```

### 5.3 可复制文件（来自 CodePilot）

| 文件 | 功能 |
|------|------|
| `src/lib/db.ts` (createSession) | 会话创建 + 目录存储 |
| `src/lib/working-directory.ts` | isExistingDirectory + resolveWorkingDirectory |
| `src/components/chat/FolderPicker.tsx` | 目录浏览 UI |
| `src/hooks/useNativeFolderPicker.ts` | Electron 原生对话框 Hook |
| `electron/preload.ts` | dialog.openFolder IPC 暴露 |

---

## 六、部门 + Agent 市场（参考 Magic）

### 6.1 市场 API 设计

```typescript
// 获取市场分类
GET /api/market/categories

// 获取 Agent 列表
POST /api/market/agents
Body: { page, page_size, keyword, category_id }

// 雇佣 Agent
POST /api/market/agents/:code/hire

// 解雇 Agent
DELETE /api/market/agents/:code

// 我的 Agent 列表
GET /api/agents
```

### 6.2 Crew 团队模板（参考 Magic，7 步骤）

```typescript
const CREW_EDIT_STEP = {
  Identity: "identity",           // 身份定义
  KnowledgeBase: "knowledge-base", // 知识库
  Skills: "skills",               // 技能绑定
  RunAndDebug: "run-and-debug",   // 运行调试
  Publishing: "publishing",       // 发布
  Playbook: "playbook",           // 场景配置
  BuiltinSkills: "builtin-skills" // 内置技能
}
```

### 6.3 可复制文件（来自 Magic）

| 功能 | 文件路径 |
|------|---------|
| 市场 Store | `employee-market/stores/store-crew/index.ts` |
| 市场页面 | `EmployeeMarketDesktop.tsx` |
| Agent 卡片 | `EmployeeCard.tsx` |
| CrewEdit Store | `CrewEdit/store/root-store.ts` |

---

## 七、CEO 审核 + 会议纪要（CyberTeam 独有）

### 7.1 四层对话体系

```
第一层：CEO → COO（战略对齐）
  └── 目标/约束/风险偏好/资源配置

第二层：COO → 专家团队（策略制定）
  └── 卖点/场景/渠道/转化

第三层：专家团队内部分歧讨论
  └── 风险预案/保底措施/多轮迭代

第四层：COO → CEO（汇报 + 审核）
  └── 审核批准/修改/打回
```

### 7.2 CEO 审核状态机

```typescript
enum ReviewStatus {
  PENDING = 'pending',    // 待审核
  APPROVED = 'approved',  // 已批准
  REJECTED = 'rejected',  // 已打回
  REVISION = 'revision',  // 需修改后重审
}
```

### 7.3 会议纪要格式

```markdown
# 对话记录 #[序号] - [类型]

**会议ID**: mtg_[日期]_[类型]_[序号]
**日期**: YYYY-MM-DD
**类型**: CEO-COO对齐/策略讨论/风险预案/CEO汇报
**主持人**: [主持人]
**参与人**: [参与者列表]

---

## 一、会议议程
[必须讨论的议题]

## 二、讨论内容
[按议题记录讨论过程 + 质疑者追问]

## 三、共识结论
| 结论项 | 内容 | 证据 |
|--------|------|------|

## 四、质疑者审查报告
| 维度 | 评分 |
|------|------|
| 数据来源 | /10 |
| 逻辑推理 | /10 |
| 假设验证 | /10 |
| 完整性 | /10 |
| **总分** | /40 (≥32通过) |

## 五、后续动作
- [ ] [动作项] — 负责人 — 截止日期
```

### 7.4 Playground 看板（7 Tab）

| Tab | 功能 | 数据来源 |
|-----|------|---------|
| **概览** | 项目核心指标卡片 | metadata.yaml |
| **公式** | CEO 思维模型/收入公式拆解 | 对话_02_策略讨论 |
| **漏斗** | 转化漏斗图（与模拟器同步） | 对话_04_CEO汇报 |
| **时段** | 时间轴/里程碑 | 项目计划 |
| **风险** | 风险矩阵/预警机制 | 对话_03_风险预案 |
| **预算** | 预算分配表 | metadata.yaml |
| **模拟** | 可调参数的实时模拟器 | 漏斗参数 |

### 7.5 质疑者机制

**触发时机**：

| 讨论阶段 | 质疑者动作 |
|---------|-----------|
| 讨论开始前 | 检查 context/ 是否有真实数据 |
| 专家发言后 | 追问数据来源和假设依据 |
| 方案形成前 | 要求说明"风险是什么" |
| 结论产出前 | 要求提供"3个可能的反例" |
| 讨论结束时 | 输出"未解决问题清单" |

**绝对禁止**：
- ❌ 接受无法溯源的结论
- ❌ 接受"应该是"或"大概"
- ❌ 跳过对假设的质疑

**可复制文件**（来自 CyberTeam V4）：
| 文件 | 功能 |
|------|------|
| `AGENTS/socratic-questioner/*/AGENT.md` | Agent 定义 |
| `AGENTS/socratic-questioner/*/SOUL.md` | 灵魂定义 |
| `projects/_template/05_Playground/活动看板_v8.html` | Playground HTML |
| `projects/_template/01_Agent会议纪要/对话记录/对话记录模板.md` | 纪要模板 |

---

## 八、Claude Code CLI 集成（照搬 CodePilot）

### 8.1 调用方式

```typescript
import { query } from '@anthropic-ai/claude-agent-sdk'

export async function streamClaudeResponse(
  sessionId: string,
  message: string,
  options: {
    workingDirectory: string
    model: string
    provider: ApiProvider
    onProgress: (event: SSEEvent) => void
  }
) {
  const resolved = resolveForClaudeCode(options.provider)

  const result = await query({
    query: message,
    cwd: options.workingDirectory,
    model: resolved.modelId,
    env: {
      ...process.env,
      ...resolved.envOverrides,
    },
    onProgress: (event) => options.onProgress(event),
  })

  return result
}
```

### 8.2 Provider 解析（7 种协议）

| 协议 | 说明 | 环境变量 |
|------|------|---------|
| `anthropic` | Anthropic Messages API | ANTHROPIC_API_KEY |
| `openai-compatible` | OpenAI 兼容接口 | API_KEY + BASE_URL |
| `openrouter` | OpenRouter | OPENROUTER_API_KEY |
| `bedrock` | AWS Bedrock | AWS credentials |
| `vertex` | Google Vertex AI | GCP credentials |
| `google` | Google AI Studio | GOOGLE_API_KEY |
| `minimax` | MiniMax | ANTHROPIC_AUTH_TOKEN + ANTHROPIC_BASE_URL |

### 8.3 可复制文件（来自 CodePilot）

| 文件 | 功能 |
|------|------|
| `src/lib/claude-client.ts` | Claude SDK 封装 |
| `src/lib/provider-resolver.ts` | Provider 解析 |
| `src/lib/provider-catalog.ts` | Provider 目录 |
| `src/lib/provider-doctor.ts` | Provider 诊断 |

---

## 九、开发路线图（Phase 0-9）

| Phase | 模块 | 天数 | 核心交付 |
|-------|------|------|----------|
| **0** | 项目初始化 | 1 | Electron + React + Vite 脚手架 |
| **1** | 设置 + Provider | 2 | API Provider 管理 UI |
| **2** | 项目 + 目录 | 2 | projects 表 + FolderPicker |
| **3** | 对话核心 | 3 | Claude SDK + SSE 流式响应 |
| **4** | 聊天界面 | 3 | 微信风格 + @mention + typing 效果 |
| **5** | 部门 + Agent 市场 | 2 | 市场页 + Crew 模板 |
| **6** | Skill 管理 | 1 | Skill CRUD + 启用/停用 |
| **7** | 多 Agent 协作 + CEO 审核 | 3 | CEO 路由 + 群聊 + 审核 UI |
| **8** | Playground + 会议纪要 | 2 | 7 Tab 看板 + 纪要模板 |
| **9** | 打包发布 | 1 | .dmg 安装包 |
| | **总计** | **~19天** | |

---

## 十、可复用资源清单

### 10.1 直接复制（CodePilot）

| 文件 | 功能 |
|------|------|
| `electron/main.ts` | Electron 主进程框架 |
| `electron/preload.ts` | contextBridge API 暴露 |
| `src/lib/db.ts` | SQLite CRUD |
| `src/lib/claude-client.ts` | Claude SDK 封装 |
| `src/lib/provider-resolver.ts` | Provider 解析 |
| `src/lib/provider-catalog.ts` | Provider 目录 |
| `src/lib/files.ts` | 文件操作 |
| `src/lib/working-directory.ts` | 目录验证 |

### 10.2 直接复制（Magic）

| 文件 | 功能 |
|------|------|
| `MentionExtension.ts` | TipTap @mention 扩展 |
| `suggestion.ts` | @触发配置（1200ms 窗口）|
| `MentionNodeView.tsx` | Mention 节点渲染 |
| `MentionPanelRenderer.tsx` | 下拉选择器 |
| `EnhanceMarkdown/index.tsx` | Markdown + typing 效果 |
| `useTyping.tsx` | 打字机实现 |
| `useStreamCursor.ts` | 流式光标 |
| `EmployeeMarketDesktop.tsx` | 市场页面 |
| `CrewEdit/store/root-store.ts` | Crew 编辑 Store |

### 10.3 直接复制（CyberTeam V4）

| 文件 | 功能 |
|------|------|
| `AGENTS/socratic-questioner/*` | 质疑者 Agent |
| `projects/_template/05_Playground/*.html` | Playground HTML |
| `projects/_template/01_Agent会议纪要/对话记录/*.md` | 纪要模板 |

---

## 十一、关键设计决策

### 11.1 策略：照搬底层，重写 UI

```
Layer 0: Electron 框架     → 照搬 CodePilot
Layer 1: Node.js 后端      → 照搬 CodePilot (db/sdk/provider)
Layer 2: Claude Code 集成  → 照搬 CodePilot (claude-client)
Layer 3: 前端 UI           → CyberTeam 自定义（微信风格）
Layer 4: 业务逻辑          → CyberTeam 独有（CEO路由/三省六部/Playground）
```

**不重新发明的部分**：
- ✅ Electron 主进程框架
- ✅ SQLite 数据库操作
- ✅ Claude Code SDK 调用
- ✅ Provider 管理系统
- ✅ SSE 流式响应
- ✅ 文件系统操作
- ✅ TipTap @mention 机制
- ✅ 流式打字机效果

** CyberTeam 自己做的部分**：
- 🎨 微信风格聊天界面
- 🏢 部门/Agent/Skill 管理 UI
- 🧠 CEO 路由引擎
- 📊 Playground 看板
- 📝 会议纪要系统
- 🔍 质疑者机制

### 11.2 已知 bug（参考 CodePilot）

| Bug | 位置 | 修复方案 |
|-----|------|---------|
| 目录切换清空 sdk_session_id | CodePilot db.ts | CyberTeam 保留 session_id，除非跨盘符 |
| 目录不存在静默失败 | CodePilot 多处 | 主动验证 + 提示用户 |

---

*文档版本：v2.0 | 创建日期：2026-03-31 | 基于 4 个研究 Agent 综合产出*
