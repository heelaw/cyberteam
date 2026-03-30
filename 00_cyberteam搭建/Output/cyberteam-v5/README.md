# CyberTeam v5.0 - 数字军团

## 项目状态：研发中

### 核心功能

1. **Claude Code CLI 集成** - 真正调用 AI 执行任务
2. **数字员工市场** - 可视化管理 Agent 团队
3. **任务执行引擎** - 工作流驱动 Agent 协作
4. **MCP 工具扩展** - 连接外部服务

### 快速开始

```bash
# 后端
cd backend
uvicorn app.main:app --reload --port 8000

# 前端
cd frontend
npm run dev
```

### 技术栈

- **前端**: React + Vite + Ant Design
- **后端**: FastAPI + Python 3.12
- **Agent 引擎**: 基于 Magic agentlang 框架
- **核心集成**: Claude Code CLI (subprocess)
