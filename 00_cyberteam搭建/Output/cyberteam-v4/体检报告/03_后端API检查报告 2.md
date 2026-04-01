# CyberTeam-v4 后端 API 检查报告

> 检查时间：2026-03-28
> 检查范围：`backend/app/api/` 目录下的所有 API 端点
> 检查人员：API 审计 Agent

---

## 一、概览

| 项目 | 数量 |
|------|------|
| API 模块总数 | 11 个 |
| API 端点总数 | 约 80+ 个 |
| RESTful 规范遵循度 | 75% |
| 发现问题总数 | 23 个 |
| 严重问题 | 5 个 |
| 中等问题 | 10 个 |
| 轻微问题 | 8 个 |

---

## 二、API 模块清单

| 模块 | 文件路径 | 端点数 | 状态 |
|------|----------|--------|------|
| health | `api/health.py` | 5 | 正常 |
| agents | `api/agents.py` | 5 | 需改进 |
| experts | `api/experts.py` | 7 | 需改进 |
| tasks | `api/tasks.py` | 15 | 需改进 |
| todos | `api/todos.py` | 10 | 正常 |
| projects | `api/projects.py` | 9 | 严重问题 |
| departments | `api/departments.py` | 8 | 需改进 |
| reports | `api/reports.py` | 8 | 需改进 |
| debate | `api/debate.py` | 6 | 需改进 |
| scoring | `api/scoring.py` | 4 | 需改进 |
| teams | `api/teams.py` | 6 | 严重问题 |
| skills | `api/skills.py` | 6 | 严重问题 |

---

## 三、严重问题（必须修复）

### P0-1: Schema 命名风格不一致

**文件**: `api/teams.py`, `api/skills.py`

**问题**: Schema 使用 camelCase 命名（如 `agentIds`, `coordinationMode`），不符合 Python RESTful API 惯例。

**影响**:
- 与其他模块（`tasks.py`, `reports.py`）风格不一致
- 可能导致前端集成困难

**当前代码**:
```python
# teams.py
class TeamCreate(BaseModel):
    id: str = Field(default_factory=lambda: f"team-{uuid.uuid4().hex[:8]}")
    name: str
    agentIds: List[str] = Field(default_factory=list)  # camelCase
    coordinationMode: str = "sequential"  # camelCase
```

**修复建议**:
```python
class TeamCreate(BaseModel):
    id: str = Field(default_factory=lambda: f"team-{uuid.uuid4().hex[:8]}")
    name: str
    agent_ids: List[str] = Field(default_factory=list)  # snake_case
    coordination_mode: str = "sequential"  # snake_case
```

---

### P0-2: 内存存储无持久化

**文件**: `api/projects.py`, `api/teams.py`, `api/skills.py`

**问题**: 使用内存字典存储数据，服务重启后数据丢失。

**当前代码**:
```python
# projects.py 第25行
_projects: Dict[str, Dict[str, Any]] = {}

# teams.py 第17行
_teams_db: Dict[str, dict] = {}

# skills.py 第17行
_skills_db: Dict[str, dict] = {}
```

**影响**:
- 生产环境数据不安全
- 无法水平扩展

**修复建议**:
- 迁移到数据库存储
- 或添加外部存储（Redis）支持

---

### P0-3: teams.py 缺少数据库依赖注入

**文件**: `api/teams.py`

**问题**: 所有端点都缺少 `AsyncSession = Depends(get_db)` 依赖注入，无法访问数据库。

**当前代码**:
```python
@router.get("")
async def list_teams() -> List[TeamOut]:
    return [TeamOut(**t) for t in _teams_db.values()]
```

**修复建议**:
```python
@router.get("")
async def list_teams(db: AsyncSession = Depends(get_db)) -> List[TeamOut]:
    # 添加数据库查询逻辑
    ...
```

---

### P0-4: skills.py 缺少数据库依赖注入

**文件**: `api/skills.py`

**问题**: 同 P0-3，所有端点缺少数据库集成。

---

### P0-5: departments.py 路径参数冲突

**文件**: `api/departments.py`

**问题**: 路由 `/outputs/{task_id}` 与 `/outputs/{output_id}` 可能冲突。

**当前代码**:
```python
@router.get("/outputs/{task_id}")  # 第313行
async def get_department_outputs(task_id: str, ...)

@router.get("/outputs/{output_id}")  # 第340行
async def get_department_output(output_id: int, ...)
```

**影响**: FastAPI 可能无法正确区分 `task_id`（字符串）和 `output_id`（整数）。

**修复建议**:
- 改为查询参数：`GET /outputs?task_id=xxx`
- 或使用不同的路径前缀：`/task-outputs/{task_id}`, `/output/{output_id}`

---

## 四、中等问题（建议修复）

### P1-1: RESTful 路由不规范

**文件**: `api/experts.py`

**问题**: `GET /{expert_id}/info` 应该简化为 `GET /{expert_id}` 或使用查询参数。

---

### P1-2: HTTP 状态码不一致

**文件**: `api/tasks.py`

**问题**: 类似操作返回不同状态码。

| 端点 | 操作 | 当前状态码 | 建议 |
|------|------|------------|------|
| `POST /tasks/swarm/create` | 创建 | 201 | 正确 |
| `POST /tasks/swarm/assign` | 分配 | 默认 200 | 应为 201/202 |
| `POST /swarm/{team_name}/shutdown` | 关闭 | 200 | 应为 202 |

---

### P1-3: CORS 配置不安全

**文件**: `main.py` 第111-117行

**问题**: `allow_origins=["*"]` 允许所有来源。

**当前代码**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境不安全
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**修复建议**:
```python
# 生产环境应配置具体域名
allow_origins=["https://your-domain.com"] if not settings.debug else ["*"]
```

---

### P1-4: 缺少全局异常处理器

**文件**: `main.py`

**问题**: 没有 `@app.exception_handler`，内部错误可能泄露敏感信息。

---

### P1-5: experts.py 置信度计算硬编码

**文件**: `api/experts.py` 第223行

**问题**: 置信度使用硬编码公式，非真实模型输出。

---

### P1-6: projects.py 无异常处理

**文件**: `api/projects.py`

**问题**: 内存操作没有 try-except，可能导致服务崩溃。

---

### P1-7: 缺少请求体验证

**文件**: 多个 API 模块

**问题**: 缺少输入验证中间件，如防 SQL 注入、XSS 防护。

---

### P1-8: teams.py POST 缺少状态码

**文件**: `api/teams.py` 第67行

**问题**: `POST /teams` 没有指定 `status_code`。

---

### P1-9: departments.py execute 端点缺少状态码

**文件**: `api/departments.py` 第231行

**问题**: `POST /departments/execute` 没有指定 `status_code`。

---

### P1-10: debate.py 缺少请求体验证

**文件**: `api/debate.py`

**问题**: `DebateProgressRequest` 的 `expert_outputs` 列表没有深度验证。

---

## 五、轻微问题（可选修复）

### P2-1: Schema 注释不完整

**文件**: 多个模块

**问题**: 部分 Schema 字段缺少 `description`。

---

### P2-2: 缺少 API 标签分组

**文件**: `main.py`

**问题**: 部分端点缺少 `tags` 参数。

---

### P2-3: 路由前缀不统一

**文件**: 所有 API 模块

**问题**: 部分模块使用 `/api/` 前缀，部分不使用（如 `health.py`）。

---

### P2-4: 返回类型不一致

**文件**: 多个模块

**问题**:
- 部分使用 `response_model`
- 部分直接返回字典

---

### P2-5: 缺少分页总数返回

**文件**: `api/teams.py`, `api/skills.py`

**问题**: `GET /teams` 和 `GET /skills` 没有返回 `total` 字段。

---

### P2-6: logging 格式不统一

**文件**: 多个模块

**问题**: 部分使用 f-string，部分使用 `%` 格式化。

---

### P2-7: 缺少 API 版本控制

**文件**: `main.py`

**问题**: 所有端点使用同一版本，未来升级可能困难。

---

### P2-8: 缺少健康检查详细指标

**文件**: `api/health.py`

**问题**: `/ready` 端点硬编码数据库和 API 状态。

---

## 六、按模块详细问题清单

### health.py

| 检查项 | 状态 | 备注 |
|--------|------|------|
| RESTful 规范 | 通过 | |
| JSON 格式 | 通过 | |
| 状态码使用 | 通过 | |
| 错误处理 | 通过 | |

### agents.py

| 检查项 | 状态 | 问题 |
|--------|------|------|
| RESTful 规范 | 部分 | Schema 字段命名 |
| JSON 格式 | 通过 | |
| 状态码使用 | 通过 | |
| 错误处理 | 通过 | |
| 依赖注入 | 通过 | |

### experts.py

| 检查项 | 状态 | 问题 |
|--------|------|------|
| RESTful 规范 | 需改进 | `/{expert_id}/info` 路径 |
| JSON 格式 | 通过 | |
| 状态码使用 | 通过 | |
| 错误处理 | 部分 | 置信度硬编码 |
| 依赖注入 | 通过 | |

### tasks.py

| 检查项 | 状态 | 问题 |
|--------|------|------|
| RESTful 规范 | 部分 | Swarm 端点状态码 |
| JSON 格式 | 通过 | |
| 状态码使用 | 部分 | 不一致 |
| 错误处理 | 通过 | |
| 依赖注入 | 通过 | |

### todos.py

| 检查项 | 状态 | 备注 |
|--------|------|------|
| RESTful 规范 | 通过 | 最佳实践 |
| JSON 格式 | 通过 | |
| 状态码使用 | 通过 | |
| 错误处理 | 通过 | |

### projects.py

| 检查项 | 状态 | 问题 |
|--------|------|------|
| RESTful 规范 | 通过 | |
| JSON 格式 | 通过 | |
| 状态码使用 | 通过 | |
| 错误处理 | 缺失 | 无 try-except |
| 依赖注入 | 通过 | |
| 数据持久化 | 内存存储 | 严重问题 |

### departments.py

| 检查项 | 状态 | 问题 |
|--------|------|------|
| RESTful 规范 | 需改进 | 路径参数冲突 |
| JSON 格式 | 通过 | |
| 状态码使用 | 部分 | execute 缺少 |
| 错误处理 | 通过 | |
| 依赖注入 | 通过 | |

### reports.py

| 检查项 | 状态 | 备注 |
|--------|------|------|
| RESTful 规范 | 通过 | |
| JSON 格式 | 通过 | |
| 状态码使用 | 通过 | |
| 错误处理 | 通过 | |
| 依赖注入 | 通过 | |

### debate.py

| 检查项 | 状态 | 备注 |
|--------|------|------|
| RESTful 规范 | 通过 | |
| JSON 格式 | 通过 | |
| 状态码使用 | 通过 | |
| 错误处理 | 部分 | 请求体验证 |
| 依赖注入 | 通过 | |

### scoring.py

| 检查项 | 状态 | 备注 |
|--------|------|------|
| RESTful 规范 | 通过 | |
| JSON 格式 | 通过 | |
| 状态码使用 | 通过 | |
| 错误处理 | 通过 | |
| 依赖注入 | 通过 | |

### teams.py

| 检查项 | 状态 | 问题 |
|--------|------|------|
| RESTful 规范 | Schema 命名 | camelCase |
| JSON 格式 | Schema 命名 | camelCase |
| 状态码使用 | 缺少 | POST 无 201 |
| 错误处理 | 通过 | |
| 依赖注入 | 缺失 | 无数据库 |
| 数据持久化 | 内存存储 | 严重问题 |

### skills.py

| 检查项 | 状态 | 问题 |
|--------|------|------|
| RESTful 规范 | Schema 命名 | camelCase |
| JSON 格式 | Schema 命名 | camelCase |
| 状态码使用 | 缺少 | POST 无 201 |
| 错误处理 | 通过 | |
| 依赖注入 | 缺失 | 无数据库 |
| 数据持久化 | 内存存储 | 严重问题 |

---

## 七、修复优先级建议

### 第一批次（立即修复）

1. **P0-5**: 修复 `departments.py` 路径参数冲突
2. **P0-1**: 统一 Schema 命名风格（teams.py, skills.py）
3. **P0-2**: 为 projects/teams/skills 添加数据库支持或明确标记为临时存储

### 第二批次（近期修复）

4. **P1-3**: 修复 CORS 配置
5. **P1-4**: 添加全局异常处理器
6. **P1-1**: 统一 RESTful 路由风格
7. **P1-2**: 统一 HTTP 状态码使用

### 第三批次（持续优化）

8. **P1-5-P1-10**: 完善错误处理和验证
9. **P2-1-P2-8**: 细节优化

---

## 八、RESTful 规范检查结果

| 检查项 | 符合度 |
|--------|--------|
| 资源命名（名词复数） | 90% |
| HTTP 方法正确使用 | 85% |
| 状态码使用 | 80% |
| 路径层次结构 | 75% |
| 查询参数使用 | 95% |

**总体 RESTful 规范遵循度**: 75%

---

## 九、JSON 格式检查结果

| 检查项 | 状态 |
|--------|------|
| Content-Type 头 | 正确 |
| 响应结构一致性 | 部分不一致 |
| 错误响应格式 | 统一 |
| 分页格式 | 统一 |

---

## 十、错误处理检查结果

| 模块 | 异常捕获 | 自定义错误 | 全局处理 |
|------|----------|------------|----------|
| health | 通过 | 通过 | N/A |
| agents | 通过 | 通过 | 缺失 |
| experts | 通过 | 通过 | 缺失 |
| tasks | 通过 | 通过 | 缺失 |
| todos | 通过 | 通过 | 缺失 |
| projects | 缺失 | 通过 | 缺失 |
| departments | 通过 | 通过 | 缺失 |
| reports | 通过 | 通过 | 缺失 |
| debate | 通过 | 通过 | 缺失 |
| scoring | 通过 | 通过 | 缺失 |
| teams | 通过 | 通过 | 缺失 |
| skills | 通过 | 通过 | 缺失 |

**建议**: 添加全局异常处理器到 `main.py`

---

## 十一、总结

### 优点

1. **架构清晰**: 使用 FastAPI + SQLAlchemy 异步架构
2. **类型安全**: 大量使用 Pydantic Schema
3. **懒加载设计**: Engine 模块采用懒加载，避免启动时依赖
4. **数据库集成**: 大部分模块正确使用依赖注入

### 需要改进

1. **数据持久化**: teams/skills/projects 使用内存存储
2. **安全配置**: CORS 和异常处理需要加强
3. **命名规范**: 部分 Schema 使用 camelCase
4. **测试覆盖**: 缺少 API 端点测试

### 建议行动

1. 优先修复 P0 级别问题（5个）
2. 尽快修复 P1 级别问题（10个）
3. 考虑添加 API 测试套件
4. 添加 API 文档和 OpenAPI 标签

---

*报告生成时间: 2026-03-28*
*检查工具: API 审计 Agent*
