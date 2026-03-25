"""CyberTeam V4 配置管理。"""

import os
from functools import lru_cache


class Settings:
    """应用配置。"""

    # 服务配置
    port: int = int(os.getenv("PORT", "8080"))
    host: str = os.getenv("HOST", "0.0.0.0")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # 数据库配置
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./cyberteam.db"
    )

    # 存储配置
    workspace_root: str = os.getenv(
        "WORKSPACE_ROOT",
        "~/.cyberteam/workspace"
    )

    # 专家配置
    expert_timeout: int = int(os.getenv("EXPERT_TIMEOUT", "120"))
    debate_rounds: int = int(os.getenv("DEBATE_ROUNDS", "5"))
    convergence_threshold: float = float(os.getenv("CONVERGENCE_THRESHOLD", "0.3"))

    # 评分配置
    score_threshold: float = float(os.getenv("SCORE_THRESHOLD", "50"))
    quality_gate_l1: float = float(os.getenv("QUALITY_GATE_L1", "70"))
    quality_gate_l3: float = float(os.getenv("QUALITY_GATE_L3", "70"))
    quality_gate_l4: float = float(os.getenv("QUALITY_GATE_L4", "75"))

    # OpenAI 配置
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4")

    # Redis 配置（用于事件总线）
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例。"""
    return Settings()