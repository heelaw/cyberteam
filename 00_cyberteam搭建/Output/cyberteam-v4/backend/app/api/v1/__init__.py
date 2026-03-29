"""API v1 路由。"""

from .chat import router as chat_router
from .agents import router as agents_router
from .projects import router as projects_router
from .skills import router as skills_router

__all__ = ["chat_router", "agents_router", "projects_router", "skills_router"]
