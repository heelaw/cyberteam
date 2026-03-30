"""
CyberTeam v5.0 后端主应用
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api import employees, chat, departments, skills

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="CyberTeam v5.0 - 数字军团",
    description="企业级 AI Agent 协作平台",
    version="5.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册路由
app.include_router(employees.router)
app.include_router(chat.router)
app.include_router(departments.router)
app.include_router(skills.router)


# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "5.0.0"}


@app.get("/")
async def root():
    return {
        "message": "CyberTeam v5.0 - 数字军团 API",
        "docs": "/docs",
        "version": "5.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
