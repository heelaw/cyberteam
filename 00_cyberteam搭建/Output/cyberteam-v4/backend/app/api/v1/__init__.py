"""API v1 路由。"""

from .chat import router as chat_router
from .agents import router as agents_router
from .projects import router as projects_router
from .skills import router as skills_router
from .expert_agents import router as expert_agents_router
from .playground import router as playground_router
from .companies import router as companies_router
from .spawn_api import router as spawn_router
from .organization import router as organization_router
from .departments import router as departments_router
from .teams import router as teams_router

__all__ = ["chat_router", "agents_router", "projects_router", "skills_router", "expert_agents_router", "playground_router", "companies_router", "spawn_router", "organization_router", "departments_router", "teams_router"]