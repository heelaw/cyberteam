"""FastAPI main application with lifespan."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket

from app.config import settings
from app.db.database import Base, async_engine, async_sessionmaker
from app.engine import agent_compiler, model_gateway, event_bus, thinking_injector


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Auto-create database tables
    from app.db import models  # noqa: F401 -- ensure all models are registered
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Initialize engine modules
    agent_compiler.get_available_agents()

    # Sync custom agents from DB to compiler cache
    from app.engine.agent_compiler import sync_custom_agents_to_compiler
    from app.db.database import async_sessionmaker
    async with async_sessionmaker() as db:
        count = await sync_custom_agents_to_compiler(db)
        print(f"Synced {count} custom agents to compiler cache")

    yield

    # Shutdown
    print("Shutting down...")
    await async_engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include API v1 routes
from app.api.v1 import chat, agents, projects, skills, sse, auth
# departments/teams/templates - defined inline
from app.api.v1.departments import router as departments_router
from app.api.v1.teams import router as teams_router
from app.api.v1.templates import router as templates_router

app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(skills.router, prefix="/api/v1/skills", tags=["skills"])
app.include_router(sse.router, prefix="/api/v1", tags=["sse"])  # SSE: /api/v1/sse/*
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])  # Auth: /api/v1/auth/*

# Alias routes (without /v1 prefix) for frontend compatibility
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(skills.router, prefix="/api/skills", tags=["skills"])
app.include_router(sse.router, prefix="/api", tags=["sse"])  # /api/sse/*
app.include_router(auth.router, prefix="/api", tags=["auth"])  # /api/auth/*
app.include_router(departments_router, prefix="/api/departments", tags=["departments"])
app.include_router(teams_router, prefix="/api/teams", tags=["teams"])
app.include_router(templates_router, prefix="/api/templates", tags=["templates"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "engines": {
            "agent_compiler": "ready",
            "model_gateway": "ready",
            "event_bus": "ready",
            "thinking_injector": "ready",
        },
    }
