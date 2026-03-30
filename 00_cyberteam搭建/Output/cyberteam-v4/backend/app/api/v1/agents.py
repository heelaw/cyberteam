"""Agent 管理 API v1 - 真实化实现。

核心功能：
- Agent CRUD 操作（多租户支持）
- Agent ↔ Skill 绑定管理
- Agent 执行历史

API 路由：
- GET /api/v1/agents - 列出所有 Agent（支持 company_id/skills 过滤）
- GET /api/v1/agents/{code} - 获取 Agent 详情（含绑定的 Skill 列表）
- POST /api/v1/agents - 创建自定义 Agent
- PUT /api/v1/agents/{code} - 更新 Agent
- DELETE /api/v1/agents/{code} - 删除 Agent（软删除）
- POST /api/v1/agents/{code}/skills - 绑定 Skill 到 Agent
- DELETE /api/v1/agents/{code}/skills/{skill_id} - 解绑 Skill
- GET /api/v1/agents/{code}/executions - Agent 执行历史
"""

import threading
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/agents", tags=["agents v1"])


# === In-Memory Store ===

class AgentStore:
    """内存存储 - Agent 数据存储（线程安全）"""

    def __init__(self):
        self._lock = threading.RLock()
        self._agents: dict[str, dict] = {}  # code -> agent data
        self._executions: dict[str, list] = {}  # agent_code -> execution list

    def list_agents(
        self,
        company_id: Optional[str] = None,
        skill_ids: Optional[List[str]] = None,
    ) -> List[dict]:
        """列出 Agent（支持过滤）"""
        with self._lock:
            result = []
            for code, agent in self._agents.items():
                if agent.get("is_deleted"):
                    continue
                if company_id and agent.get("company_id") != company_id:
                    continue
                if skill_ids:
                    agent_skill_ids = set(agent.get("skills", []))
                    if not agent_skill_ids.intersection(set(skill_ids)):
                        continue
                result.append(self._format_agent(code, agent))
            return result

    def get_agent(self, code: str) -> Optional[dict]:
        """获取 Agent 详情"""
        with self._lock:
            agent = self._agents.get(code)
            if not agent or agent.get("is_deleted"):
                return None
            return self._format_agent(code, agent)

    def create_agent(self, data: dict) -> dict:
        """创建 Agent"""
        with self._lock:
            code = data["code"]
            if code in self._agents:
                raise ValueError(f"Agent {code} 已存在")
            now = datetime.utcnow()
            agent = {
                "id": str(uuid.uuid4()),
                "code": code,
                "name": data["name"],
                "agent_type": data.get("agent_type", "custom"),
                "description": data.get("description"),
                "company_id": data.get("company_id"),
                "skills": data.get("skills", []),
                "config": data.get("config", {}),
                "is_active": True,
                "is_deleted": False,
                "created_at": now,
                "updated_at": now,
            }
            self._agents[code] = agent
            self._executions[code] = []
            return self._format_agent(code, agent)

    def update_agent(self, code: str, data: dict) -> Optional[dict]:
        """更新 Agent"""
        with self._lock:
            agent = self._agents.get(code)
            if not agent or agent.get("is_deleted"):
                return None
            for key in ["name", "description", "skills", "config", "is_active"]:
                if key in data and data[key] is not None:
                    agent[key] = data[key]
            agent["updated_at"] = datetime.utcnow()
            return self._format_agent(code, agent)

    def delete_agent(self, code: str) -> bool:
        """软删除 Agent"""
        with self._lock:
            agent = self._agents.get(code)
            if not agent or agent.get("is_deleted"):
                return False
            agent["is_deleted"] = True
            agent["updated_at"] = datetime.utcnow()
            return True

    def add_skill(self, agent_code: str, skill_id: str) -> Optional[dict]:
        """绑定 Skill 到 Agent"""
        with self._lock:
            agent = self._agents.get(agent_code)
            if not agent or agent.get("is_deleted"):
                return None
            skills = agent.get("skills", [])
            if skill_id not in skills:
                skills.append(skill_id)
                agent["skills"] = skills
                agent["updated_at"] = datetime.utcnow()
            return self._format_agent(agent_code, agent)

    def remove_skill(self, agent_code: str, skill_id: str) -> Optional[dict]:
        """解绑 Skill"""
        with self._lock:
            agent = self._agents.get(agent_code)
            if not agent or agent.get("is_deleted"):
                return None
            skills = agent.get("skills", [])
            if skill_id in skills:
                skills.remove(skill_id)
                agent["skills"] = skills
                agent["updated_at"] = datetime.utcnow()
            return self._format_agent(agent_code, agent)

    def get_executions(self, agent_code: str, limit: int = 50, offset: int = 0) -> List[dict]:
        """获取执行历史"""
        with self._lock:
            executions = self._executions.get(agent_code, [])
            return executions[offset:offset + limit]

    def add_execution(self, agent_code: str, execution: dict) -> None:
        """添加执行记录"""
        with self._lock:
            if agent_code not in self._executions:
                self._executions[agent_code] = []
            self._executions[agent_code].insert(0, execution)
            # 只保留最近 1000 条
            self._executions[agent_code] = self._executions[agent_code][:1000]

    def _format_agent(self, code: str, agent: dict) -> dict:
        """格式化 Agent 输出"""
        return {
            "id": agent["id"],
            "code": code,
            "name": agent["name"],
            "agent_type": agent.get("agent_type", "custom"),
            "description": agent.get("description"),
            "company_id": agent.get("company_id"),
            "skills": agent.get("skills", []),
            "skill_count": len(agent.get("skills", [])),
            "status": "active" if agent.get("is_active") else "inactive",
            "is_active": agent.get("is_active", True),
            "config": agent.get("config", {}),
            "created_at": agent["created_at"],
            "updated_at": agent["updated_at"],
        }


# 全局单例
_agent_store = AgentStore()


def get_agent_store() -> AgentStore:
    """获取 Agent 存储实例"""
    return _agent_store


# === Skill Store（供 Agent API 调用） ===

class SkillStore:
    """Skill 内存存储（被 Agent API 引用）"""

    def __init__(self):
        self._lock = threading.RLock()
        self._skills: dict[str, dict] = {}

    def get_skill(self, skill_id: str) -> Optional[dict]:
        """根据 ID 获取 Skill"""
        with self._lock:
            skill = self._skills.get(skill_id)
            if not skill or skill.get("is_deleted"):
                return None
            return self._format_skill(skill_id, skill)

    def list_skills(self) -> List[dict]:
        """列出所有 Skill"""
        with self._lock:
            return [
                self._format_skill(sid, s)
                for sid, s in self._skills.items()
                if not s.get("is_deleted")
            ]

    def create_skill(self, data: dict) -> dict:
        """创建 Skill"""
        with self._lock:
            skill_id = data["code"]
            if skill_id in self._skills:
                raise ValueError(f"Skill {skill_id} 已存在")
            now = datetime.utcnow()
            skill = {
                "id": str(uuid.uuid4()),
                "code": skill_id,
                "name": data["name"],
                "description": data.get("description"),
                "category": data.get("category", "custom"),
                "difficulty": data.get("difficulty", "medium"),
                "trigger_keywords": data.get("trigger_keywords", []),
                "success_metrics": data.get("success_metrics", {}),
                "config": data.get("config", {}),
                "is_deleted": False,
                "created_at": now,
                "updated_at": now,
            }
            self._skills[skill_id] = skill
            return self._format_skill(skill_id, skill)

    def update_skill(self, skill_code: str, data: dict) -> Optional[dict]:
        """更新 Skill"""
        with self._lock:
            skill = self._skills.get(skill_code)
            if not skill or skill.get("is_deleted"):
                return None
            for key in ["name", "description", "category", "difficulty",
                        "trigger_keywords", "success_metrics", "config"]:
                if key in data and data[key] is not None:
                    skill[key] = data[key]
            skill["updated_at"] = datetime.utcnow()
            return self._format_skill(skill_code, skill)

    def delete_skill(self, skill_code: str) -> bool:
        """软删除 Skill"""
        with self._lock:
            skill = self._skills.get(skill_code)
            if not skill or skill.get("is_deleted"):
                return False
            skill["is_deleted"] = True
            skill["updated_at"] = datetime.utcnow()
            return True

    def _format_skill(self, skill_id: str, skill: dict) -> dict:
        """格式化 Skill 输出"""
        return {
            "id": skill["id"],
            "code": skill_id,
            "name": skill["name"],
            "description": skill.get("description"),
            "category": skill.get("category", "custom"),
            "difficulty": skill.get("difficulty", "medium"),
            "trigger_keywords": skill.get("trigger_keywords", []),
            "success_metrics": skill.get("success_metrics", {}),
            "agent_count": 0,
            "config": skill.get("config", {}),
            "created_at": skill["created_at"],
            "updated_at": skill["updated_at"],
        }


# 全局 Skill Store（供 Agent API 使用）
_skill_store = SkillStore()


def get_skill_store() -> SkillStore:
    """获取 Skill 存储实例"""
    return _skill_store


# === Request/Response Models ===

class AgentCreate(BaseModel):
    """创建 Agent 请求"""
    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., pattern=r"^[a-z0-9_-]+$")
    agent_type: str = "custom"
    description: Optional[str] = None
    company_id: Optional[str] = None
    skills: List[str] = []
    config: Optional[dict] = {}


class AgentUpdate(BaseModel):
    """更新 Agent 请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    skills: Optional[List[str]] = None
    config: Optional[dict] = None
    is_active: Optional[bool] = None


class AgentOut(BaseModel):
    """Agent 响应"""
    id: str
    code: str
    name: str
    agent_type: str
    description: Optional[str]
    company_id: Optional[str]
    skills: List[str]
    skill_count: int
    status: str
    is_active: bool
    config: dict
    created_at: datetime
    updated_at: datetime


class SkillBindRequest(BaseModel):
    """绑定 Skill 请求"""
    skill_id: str


class ExecutionOut(BaseModel):
    """执行记录响应"""
    id: str
    agent_code: str
    status: str
    input_text: Optional[str]
    output_text: Optional[str]
    duration_ms: int
    created_at: datetime


# === Routes ===

@router.get("", response_model=List[AgentOut])
async def list_agents(
    company_id: Optional[str] = None,
    skill_ids: Optional[str] = None,  # comma-separated
):
    """列出所有 Agent（支持 company_id/skills 过滤）"""
    store = get_agent_store()
    skill_list = skill_ids.split(",") if skill_ids else None
    agents = store.list_agents(company_id=company_id, skill_ids=skill_list)
    return agents


@router.get("/{code}", response_model=AgentOut)
async def get_agent(code: str):
    """获取 Agent 详情（含绑定的 Skill 列表）"""
    store = get_agent_store()
    agent = store.get_agent(code)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {code} 不存在",
        )
    return agent


@router.post("", response_model=AgentOut, status_code=status.HTTP_201_CREATED)
async def create_agent(request: AgentCreate):
    """创建自定义 Agent"""
    store = get_agent_store()
    try:
        agent = store.create_agent(request.model_dump())
        return agent
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{code}", response_model=AgentOut)
async def update_agent(code: str, request: AgentUpdate):
    """更新 Agent"""
    store = get_agent_store()
    agent = store.update_agent(code, request.model_dump(exclude_unset=True))
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {code} 不存在",
        )
    return agent


@router.delete("/{code}")
async def delete_agent(code: str):
    """删除 Agent（软删除）"""
    store = get_agent_store()
    success = store.delete_agent(code)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {code} 不存在",
        )
    return {"status": "ok", "code": code}


@router.post("/{code}/skills", response_model=AgentOut)
async def bind_skill(code: str, request: SkillBindRequest):
    """绑定 Skill 到 Agent"""
    store = get_agent_store()
    skill_store = get_skill_store()

    # 验证 Skill 存在
    skill = skill_store.get_skill(request.skill_id)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill {request.skill_id} 不存在",
        )

    agent = store.add_skill(code, request.skill_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {code} 不存在",
        )
    return agent


@router.delete("/{code}/skills/{skill_id}", response_model=AgentOut)
async def unbind_skill(code: str, skill_id: str):
    """解绑 Skill"""
    store = get_agent_store()
    agent = store.remove_skill(code, skill_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {code} 或 Skill {skill_id} 不存在",
        )
    return agent


@router.get("/{code}/executions", response_model=List[ExecutionOut])
async def get_agent_executions(
    code: str,
    limit: int = 50,
    offset: int = 0,
):
    """获取 Agent 执行历史"""
    store = get_agent_store()

    # 验证 Agent 存在
    agent = store.get_agent(code)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {code} 不存在",
        )

    executions = store.get_executions(code, limit=limit, offset=offset)
    return executions


# === 辅助函数：记录执行（供其他模块调用） ===

def record_agent_execution(
    agent_code: str,
    status: str,
    input_text: Optional[str] = None,
    output_text: Optional[str] = None,
    duration_ms: int = 0,
) -> str:
    """记录 Agent 执行（供外部调用）"""
    store = get_agent_store()
    execution_id = str(uuid.uuid4())
    execution = {
        "id": execution_id,
        "agent_code": agent_code,
        "status": status,
        "input_text": input_text,
        "output_text": output_text,
        "duration_ms": duration_ms,
        "created_at": datetime.utcnow(),
    }
    store.add_execution(agent_code, execution)
    return execution_id
