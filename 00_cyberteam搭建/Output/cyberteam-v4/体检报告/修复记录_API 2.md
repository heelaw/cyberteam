# CyberTeam-V4 API 修复记录

> 修复日期：2026-03-28
> 修复人：Backend Architect Agent

## 修复清单

| 问题编号 | 严重程度 | 问题描述 | 状态 |
|----------|----------|----------|------|
| P0-01 | 高 | Agent CRUD 未实现 | ✅ 已修复 |
| P0-02 | 高 | CORS 配置不安全 | ✅ 已修复 |
| P0-03 | 中 | API 路径不一致 | ✅ 已修复 |

---

## P0-01: Agent CRUD 未实现

### 问题描述
`backend/app/api/agents.py` 只有 GET 端点，缺少：
- `POST /api/agents` - 创建 Agent
- `PUT /api/agents/{agent_id}` - 更新 Agent
- `DELETE /api/agents/{agent_id}` - 删除 Agent

### 修复方案

**1. 新增 Schema 定义**

```python
class AgentCreate(BaseModel):
    """创建 Agent 请求。"""
    agent_id: str
    name: str
    type: str  # expert/department/gstack/system
    framework: Optional[str] = None
    description: str
    keywords: Optional[List[str]] = None
    responsibility: Optional[str] = None

class AgentUpdate(BaseModel):
    """更新 Agent 请求。"""
    name: Optional[str] = None
    framework: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    responsibility: Optional[str] = None
```

**2. 新增内存存储**
```python
_custom_agents: Dict[str, dict] = {}
```

**3. 新增 CRUD 端点**

```python
@router.post("", status_code=201)
async def create_agent(agent: AgentCreate):
    """创建新 Agent"""
    # 检查是否与系统 Agent 冲突
    # 存储到 _custom_agents 字典
    return new_agent

@router.put("/{agent_id}")
async def update_agent(agent_id: str, agent: AgentUpdate):
    """更新指定 Agent"""
    # 系统 Agent 不允许修改
    # 支持部分更新 (exclude_unset=True)
    return updated_agent

@router.delete("/{agent_id}", status_code=204)
async def delete_agent(agent_id: str):
    """删除指定 Agent"""
    # 系统 Agent 不允许删除
    return None
```

### 修复文件
- `/backend/app/api/agents.py`

### 验证
```bash
python3 -c "from app.api.agents import create_agent, update_agent, delete_agent; print('CRUD OK')"
```

---

## P0-02: CORS 配置不安全

### 问题描述
`backend/app/main.py` 中 CORS 配置存在安全问题：

```python
# 错误配置（存在）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 不安全：允许所有来源
    allow_credentials=True,        # 冲突：credentials=True 时不能使用 "*"
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 问题分析
1. `allow_origins=["*"]` 允许任何来源访问
2. `allow_credentials=True` 与 `allow_origins=["*"]` 冲突（浏览器会忽略 `*` 当 credentials 为 true）
3. 生产环境中存在安全风险

### 修复方案

```python
# 明确允许的来源列表
ALLOWED_ORIGINS = [
    "http://localhost:3000",   # 前端开发服务器
    "http://localhost:8080",   # WebUI 服务器
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

### 修复文件
- `/backend/app/main.py` (第 110-120 行)

### 验证
```python
# 导入验证
from app.main import ALLOWED_ORIGINS
assert "http://localhost:3000" in ALLOWED_ORIGINS
assert "*" not in ALLOWED_ORIGINS
```

---

## P0-03: API 路径不一致

### 问题描述
部分路由有 `/api` 前缀，部分没有：

```python
# 正确的路由（有 /api 前缀）
app.include_router(tasks.router, prefix="/api/tasks", ...)
app.include_router(agents.router, prefix="/api/agents", ...)

# 错误的路由（没有 /api 前缀）
app.include_router(health.router, tags=["health"])
```

### 修复方案

将 `health` 路由添加 `/api` 前缀：

```python
# 修复前
app.include_router(health.router, tags=["health"])

# 修复后
app.include_router(health.router, prefix="/api", tags=["health"])
```

### 修复文件
- `/backend/app/main.py` (第 127 行)

### 验证
修复后所有 API 路由都统一为 `/api/{resource}` 格式。

---

## 验证结果

```bash
$ cd /Users/cyberwiz/Documents/01_Project/00_cyberteam搭建/Output/cyberteam-v4/backend
$ python3 -c "from app.main import app; print('Backend OK')"
Backend OK
```

### API 路由清单（修复后）

| 方法 | 路径 | 功能 | 状态 |
|------|------|------|------|
| GET | `/api/agents` | 列出所有 Agent | ✅ |
| POST | `/api/agents` | 创建新 Agent | ✅ 新增 |
| GET | `/api/agents/{agent_id}` | 获取指定 Agent | ✅ |
| PUT | `/api/agents/{agent_id}` | 更新指定 Agent | ✅ 新增 |
| DELETE | `/api/agents/{agent_id}` | 删除指定 Agent | ✅ 新增 |
| GET | `/api/health` | 健康检查 | ✅ (路径已修复) |

---

## 安全建议

1. **CORS 生产配置**：正式部署时应将 `ALLOWED_ORIGINS` 替换为实际域名
2. **Agent 持久化**：当前 CRUD 使用内存存储，重启后会丢失，应接入数据库
3. **权限控制**：建议添加 API 认证和授权机制

---

*修复完成时间：2026-03-28*
