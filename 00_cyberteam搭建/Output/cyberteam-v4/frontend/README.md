# CyberTeam V4 Frontend

V4 前端控制台 - 直接在浏览器中打开 `index.html` 即可使用。

## 功能

- 📊 任务统计面板
- 🧠 14个思维专家展示
- 🏢 6个执行部门展示
- ✅ 创建新任务
- 📋 任务列表实时刷新

## 启动

### 方式1: 直接打开
```bash
# 直接在浏览器中打开
open frontend/index.html
# 或使用 Python HTTP 服务器
cd frontend && python3 -m http.server 8081
```

### 方式2: 后端 + 前端
```bash
# 1. 启动后端
cd backend && uvicorn app.main:app --reload --port 8080

# 2. 启动前端服务器
cd frontend && python3 -m http.server 8081

# 3. 访问 http://localhost:8081
```

## API 依赖

前端需要后端 API 服务运行在 `http://localhost:8080`：
- `/api/tasks` - 任务管理
- `/api/agents` - Agent 列表
- `/api/tasks/stats` - 任务统计
