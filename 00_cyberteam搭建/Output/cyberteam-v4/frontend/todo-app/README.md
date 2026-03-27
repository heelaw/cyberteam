# TODO 应用

一个简单而功能完整的待办事项应用，支持本地存储和 API 集成。

## 功能特性

- ✅ 添加、编辑、删除待办事项
- 🔘 标记任务完成/未完成
- 🎯 三级优先级（高/中/低）
- 🔍 筛选（全部/待完成/已完成）
- 📊 排序（创建时间/优先级/标题）
- 📱 响应式设计，支持移动端
- 💾 本地存储持久化
- 🔌 可选后端 API 集成

## 快速开始

### 方式 1: 直接打开（本地存储模式）

```bash
# 在浏览器中打开
open frontend/todo-app/index.html

# 或使用 HTTP 服务器
cd frontend/todo-app
python3 -m http.server 8082
# 访问 http://localhost:8082
```

### 方式 2: 启用后端 API

1. 修改 `js/app.js` 中的配置：
```javascript
this.useApi = true;  // 启用 API 模式
```

2. 启动后端服务器（确保运行在 `http://localhost:8080`）

3. 打开前端应用

## 目录结构

```
todo-app/
├── index.html      # 主页面
├── css/
│   └── style.css   # 样式文件
├── js/
│   └── app.js      # 客户端逻辑
└── README.md       # 说明文档
```

## API 接口（可选）

当启用 API 模式时，应用将调用以下接口：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/todos` | 获取所有待办事项 |
| POST | `/api/todos` | 创建新的待办事项 |
| PATCH | `/api/todos/:id` | 更新待办事项 |
| DELETE | `/api/todos/:id` | 删除待办事项 |

## 浏览器兼容性

- Chrome/Edge (推荐)
- Firefox
- Safari
- 移动端浏览器

## 技术栈

- 原生 HTML5
- 原生 CSS3 (Flexbox + CSS Grid)
- 原生 JavaScript (ES6+)
- LocalStorage API
- Fetch API
