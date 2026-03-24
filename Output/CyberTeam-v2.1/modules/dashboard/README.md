# CyberTeam Dashboard

CyberTeam Web Dashboard 原型，基于 PentAGI 前端设计。

## 技术栈

- React 18 + TypeScript
- Vite
- Tailwind CSS
- Radix UI
- Zustand (状态管理)
- React Router DOM
- Lucide React (图标)

## 功能

- 📊 **概览页面**: 统计卡片、Agent 状态、消息流
- 📋 **看板视图**: 拖拽式任务管理
- 🤖 **Agent 监控**: 实时查看 Agent 状态
- 💬 **消息流**: 团队消息通知
- ⚙️ **设置**: 基本配置

## 开始使用

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

## 项目结构

```
src/
├── components/
│   ├── agents/      # Agent 状态组件
│   ├── kanban/      # 看板组件
│   ├── layout/      # 布局组件
│   ├── messages/    # 消息组件
│   ├── tasks/      # 任务统计组件
│   └── ui/          # 基础 UI 组件
├── lib/             # 工具函数
├── pages/           # 页面组件
├── store/           # Zustand 状态管理
└── types/           # TypeScript 类型定义
```

## 页面路由

- `/` - 概览
- `/kanban` - 任务看板
- `/agents` - Agent 状态
- `/messages` - 消息流
- `/settings` - 设置
