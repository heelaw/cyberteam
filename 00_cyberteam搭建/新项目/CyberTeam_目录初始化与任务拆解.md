# CyberTeam 目录初始化与任务拆解

## 1. 初始化目标

建立一个干净的新项目目录，用于承载 CyberTeam 的第一版 macOS 桌面端实现。第一版只做一个可跑的最小闭环，但目录必须为未来扩展预留空间。
## 2. 推荐目录结构

```bash
cyberteam/
├── apps/
│   ├── desktop/                 # Electron 主进程
│   └── renderer/                # Next.js 前端
├── packages/
│   ├── core/                    # 核心编排
│   ├── claude/                  # Claude Code 接入
│   ├── team/                    # 公司/部门/Agent
│   ├── chat/                    # 聊天/群聊/消息
│   ├── skill/                   # Skill 系统
│   ├── playground/              # 输出与审核
│   ├── market/                  # 模板市场
│   ├── db/                      # SQLite
│   └── ui/                      # 通用 UI
├── resources/
│   ├── templates/
│   ├── avatars/
│   ├── prompts/
│   └── icons/
├── docs/
│   ├── architecture.md
│   ├── product.md
│   ├── roadmap.md
│   └── decisions/
├── tests/
└── package.json
```

## 3. 第一阶段开发任务拆解

### 任务 1：桌面壳搭建
- 初始化 Electron
- 打开主窗口
- 支持 macOS
- 配置菜单栏
- 建立应用启动与退出流程
### 任务 2：前端骨架
- 初始化 Next.js
- 建立布局
- 建立 Chat / Organization / Playground / Settings 页面
- 统一页面导航结构
### 任务 3：Claude Code 接入
- 检测本地 Claude Code
- 读取用户配置
- 建立基础会话连接

### 任务 4：数据库层
- 设计 SQLite schema
- 实现 Company / Department / Agent / Conversation / Message 表
- 实现基础 CRUD
- 支持 Playground 与审核记录
### 任务 5：聊天功能
- 单聊
- 流式输出
- 历史记录

### 任务 6：组织功能
- 公司创建
- 部门创建
- Agent 创建
- 绑定关系

### 任务 7：群聊与协作
- 创建群聊
- @Agent
- 多 Agent 回复
- 群聊摘要

### 任务 8：Playground
- 会议记录
- 摘要生成
- CEO 审核
- 导出 Markdown

## 4. 第一版页面优先级

### P0
Chat 页面、Organization 页面。

### P1
Playground 页面、Settings 页面。

### P2
Market 页面、模板市场、更多高级面板。

## 5. 开发顺序建议

1. 桌面壳
2. Claude Code 接入
3. SQLite
4. Chat
5. Organization
6. 群聊
7. Playground
8. Market

## 6. 成功标准

- 项目可启动
- 可创建公司
- 可创建 Agent
- 可私聊
- 可群聊
- 可生成 Playground
- 可导出结果

## 7. 备注

第一版不要追求完美，先追求完整闭环和真实可用。
