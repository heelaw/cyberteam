# Contributing to CyberTeam Desktop

感谢你对 CyberTeam Desktop 的贡献！请阅读以下指南确保你的代码符合项目规范。

---

## 📋 目录

- [开发环境](#开发环境)
- [代码规范](#代码规范)
- [Git 提交规范](#git-提交规范)
- [Pull Request 流程](#pull-request-流程)
- [测试](#测试)

---

## 开发环境

### 环境要求

- **Node.js**: `>=20.x`
- **pnpm**: `>=9.x`
- **Electron**: `>=40.x`
- **Rust**: `>=1.75` (仅用于本地调试)
- **macOS**: 推荐使用 macOS 进行开发

### 安装

```bash
# 克隆项目
git clone https://github.com/heelaw/cyberteam.git
cd cyberteam

# 安装依赖
pnpm install

# 启动开发模式
pnpm dev
```

### 可用脚本

| 命令 | 说明 |
|------|------|
| `pnpm dev` | 启动开发服务器 |
| `pnpm build` | 构建生产版本 |
| `pnpm electron:dev` | 启动 Electron 开发模式 |
| `pnpm electron:build` | 构建 Electron 安装包 |
| `pnpm lint` | 运行 ESLint |
| `pnpm typecheck` | 运行 TypeScript 类型检查 |
| `pnpm test` | 运行单元测试 |
| `pnpm test:e2e` | 运行 E2E 测试 |

---

## 代码规范

### TypeScript

- 使用 **TypeScript strict mode**
- 所有组件和函数必须有类型声明
- 禁止使用 `any`，使用 `unknown` 代替
- 使用 `interface` 定义对象类型，`type` 定义联合类型

### React 组件

- 使用 **函数组件** + **Hooks**
- 组件文件使用 **PascalCase**：`ChatRoom.tsx`
- Hooks 使用 **camelCase**：`useChatSession.ts`
- 优先使用 **named exports**，避免 default exports

### 样式

- 使用 **Tailwind CSS** 进行样式开发
- 组件样式写在组件文件内，或使用 CSS modules
- 不要使用内联样式（除动态值外）

### 目录结构

```
src/
├── components/           # 通用 UI 组件
│   ├── ui/             # shadcn/ui 组件
│   └── ...
├── pages/              # 页面组件
│   ├── chat/
│   ├── settings/
│   └── ...
├── hooks/              # 自定义 Hooks
├── stores/             # Zustand stores
├── lib/                # 工具函数
│   ├── db.ts          # SQLite 数据库
│   ├── claude-client.ts # Claude SDK 封装
│   └── ...
├── types/              # TypeScript 类型定义
└── electron/           # Electron 相关（main process）

electron/
├── main.ts            # 主进程入口
├── preload.ts         # Preload 脚本
└── ipc/               # IPC handlers
```

---

## Git 提交规范

### Commit Message 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类别

| Type | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 文档更新 |
| `style` | 代码格式（不影响功能）|
| `refactor` | 重构（不是新功能也不是修复）|
| `perf` | 性能优化 |
| `test` | 添加/修改测试 |
| `chore` | 构建/工具变更 |
| `ci` | CI/CD 配置变更 |

### 示例

```bash
# 新功能
git commit -m "feat(chat): add @mention support with agent picker"

# Bug 修复
git commit -m "fix(session): preserve working_directory when switching tabs"

# 重构
git commit -m "refactor(provider): extract provider resolution to separate module"

# 文档
git commit -m "docs(ARCHITECTURE): add database schema documentation"
```

### Scope 范围

| Scope | 说明 |
|-------|------|
| `chat` | 聊天/消息功能 |
| `provider` | API Provider 配置 |
| `department` | 部门/组织架构 |
| `agent` | Agent 管理 |
| `skill` | Skill 管理 |
| `market` | Agent 市场 |
| `playground` | Playground 看板 |
| `ui` | UI 组件 |
| `electron` | Electron 主进程 |
| `ci` | CI/CD |
| `docs` | 文档 |

---

## Pull Request 流程

### 1. 创建分支

```bash
# 从 main 创建功能分支
git checkout main
git pull origin main
git checkout -b feat/your-feature-name

# 从 main 创建修复分支
git checkout -b fix/issue-description
```

### 2. 提交 PR

- PR 标题必须符合 Commit Message 格式
- 填写 PR 模板中的所有项
- 确保 CI 所有检查通过
- 代码审查必须至少 1 人 approval

### 3. PR 模板

```markdown
## 描述
[简要描述这个 PR 的内容]

## 类型
- [ ] 新功能 (feat)
- [ ] Bug 修复 (fix)
- [ ] 重构 (refactor)
- [ ] 文档 (docs)
- [ ] 其他

## 影响的范围
[这个 PR 影响到哪些模块]

## 测试
- [ ] 单元测试通过
- [ ] E2E 测试通过
- [ ] 手动测试通过

## 截图（UI 变更）
[如有 UI 变更，添加截图]

## Checklist
- [ ] 代码符合 TypeScript strict mode
- [ ] 没有 ESLint 错误
- [ ] 类型检查通过
- [ ] 提交信息符合规范
```

---

## 测试

### 单元测试

```bash
# 运行所有测试
pnpm test

# 监听模式
pnpm test:watch

# 覆盖率
pnpm test:coverage
```

### E2E 测试

```bash
# 启动开发服务器
pnpm dev

# 运行 E2E 测试
pnpm test:e2e
```

### 测试规范

- 所有新功能必须包含测试
- 所有 Bug 修复必须包含回归测试
- 测试文件与源文件同名，后缀 `.test.ts` 或 `.spec.ts`

---

## 问题反馈

使用 GitHub Issues 反馈问题时，请包含：

1. **问题描述** — 清晰描述问题
2. **复现步骤** — 如何复现问题
3. **预期行为** — 期望的行为
4. **实际行为** — 实际发生的行为
5. **环境信息**:
   - 操作系统版本
   - Node.js 版本
   - pnpm 版本
   - Electron 版本（如果是桌面应用问题）
6. **截图** — 如果有 UI 问题

---

## 许可证

提交代码即表示你同意你的代码按照项目的 MIT 许可证条款授权。
