"""CyberTeam V4 常量定义

包含所有全局常量、路径常量和配置常量。
"""

import os
from pathlib import Path
from typing import Dict

# =============================================================================
# 版本信息
# =============================================================================

VERSION = "4.0.0"
VERSION_INFO = tuple(int(x) for x in VERSION.split("."))

# =============================================================================
# 路径常量
# =============================================================================

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# CyberTeam 根目录
CYBERTEAM_ROOT = Path(__file__).parent

# 配置目录
CONFIG_DIR = CYBERTEAM_ROOT / "config"

# 数据目录
DATA_DIR = CYBERTEAM_ROOT / "data"

# 日志目录
LOG_DIR = CYBERTEAM_ROOT / "logs"

# 模板目录
TEMPLATES_DIR = CYBERTEAM_ROOT / "templates"

# 缓存目录
CACHE_DIR = CYBERTEAM_ROOT / ".cache"

# 工作区目录
WORKSPACE_DIR = PROJECT_ROOT / "workspace"

# =============================================================================
# 默认配置
# =============================================================================

# 默认团队配置
DEFAULT_TEAM_CONFIG = {
    "name": "default",
    "max_members": 10,
    "timeout": 300,
}

# 默认代理配置
DEFAULT_AGENT_PROFILES = {
    "claude": {
        "name": "Claude",
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 8192,
    },
    "codex": {
        "name": "Codex",
        "model": "gpt-4",
        "max_tokens": 4096,
    },
    "gemini": {
        "name": "Gemini",
        "model": "gemini-pro",
        "max_tokens": 8192,
    },
    "kimi": {
        "name": "Kimi",
        "model": "moonshot-v1-128k",
        "max_tokens": 128 * 1024,
    },
}

# =============================================================================
# 消息常量
# =============================================================================

# 消息类型
MESSAGE_TYPE_TEXT = "text"
MESSAGE_TYPE_JSON = "json"
MESSAGE_TYPE_FILE = "file"

# 消息状态
MESSAGE_STATUS_PENDING = "pending"
MESSAGE_STATUS_SENT = "sent"
MESSAGE_STATUS_DELIVERED = "delivered"
MESSAGE_STATUS_READ = "read"
MESSAGE_STATUS_FAILED = "failed"

# =============================================================================
# 任务常量
# =============================================================================

# 任务状态
TASK_STATUS_PENDING = "pending"
TASK_STATUS_RUNNING = "running"
TASK_STATUS_COMPLETED = "completed"
TASK_STATUS_FAILED = "failed"
TASK_STATUS_CANCELLED = "cancelled"

# 任务优先级
TASK_PRIORITY_LOW = 1
TASK_PRIORITY_NORMAL = 5
TASK_PRIORITY_HIGH = 10
TASK_PRIORITY_CRITICAL = 20

# =============================================================================
# 团队常量
# =============================================================================

# 团队角色
TEAM_ROLE_LEADER = "leader"
TEAM_ROLE_MEMBER = "member"
TEAM_ROLE_OBSERVER = "observer"

# 团队状态
TEAM_STATUS_ACTIVE = "active"
TEAM_STATUS_INACTIVE = "inactive"
TEAM_STATUS_DISSOLVED = "dissolved"

# =============================================================================
# MCP 协议常量
# =============================================================================

# MCP 服务器状态
MCP_SERVER_STATUS_STOPPED = "stopped"
MCP_SERVER_STATUS_STARTING = "starting"
MCP_SERVER_STATUS_RUNNING = "running"
MCP_SERVER_STATUS_ERROR = "error"

# MCP 工具类型
MCP_TOOL_TYPE_LOCAL = "local"
MCP_TOOL_TYPE_MCP = "mcp"
MCP_TOOL_TYPE_CUSTOM = "custom"

# =============================================================================
# 通信常量
# =============================================================================

# 默认端口
DEFAULT_API_PORT = 8000
DEFAULT_BOARD_PORT = 8080
DEFAULT_MCP_PORT = 8765

# 超时设置（秒）
DEFAULT_TIMEOUT = 30
LONG_TIMEOUT = 300
SHORT_TIMEOUT = 5

# 重试配置
MAX_RETRIES = 3
RETRY_DELAY = 1

# =============================================================================
# 日志常量
# =============================================================================

# 日志级别
LOG_LEVEL_DEBUG = "DEBUG"
LOG_LEVEL_INFO = "INFO"
LOG_LEVEL_WARNING = "WARNING"
LOG_LEVEL_ERROR = "ERROR"
LOG_LEVEL_CRITICAL = "CRITICAL"

# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# =============================================================================
# 文件传输常量
# =============================================================================

# 最大文件大小（字节）
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# 支持的文件类型
ALLOWED_FILE_EXTENSIONS = [
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".json", ".yaml", ".yml", ".toml",
    ".md", ".txt", ".rst",
    ".sh", ".bash", ".zsh",
    ".html", ".css",
]

# =============================================================================
# 工作区常量
# =============================================================================

# Git 配置
DEFAULT_BRANCH = "main"
AGENT_BRANCH_PREFIX = "agent/"

# 冲突标记
CONFLICT_START_MARKER = "<<<<<<<"
CONFLICT_SEPARATOR = "======="
CONFLICT_END_MARKER = ">>>>>>>"

# =============================================================================
# 进程管理常量
# =============================================================================

# 后端类型
BACKEND_TYPE_SUBPROCESS = "subprocess"
BACKEND_TYPE_TMUX = "tmux"

# 进程状态
PROCESS_STATUS_RUNNING = "running"
PROCESS_STATUS_STOPPED = "stopped"
PROCESS_STATUS_ZOMBIE = "zombie"

# =============================================================================
# 环境变量
# =============================================================================

# CyberTeam 专用环境变量
ENV_CYBERTEAM_HOME = "CYBERTEAM_HOME"
ENV_CYBERTEAM_CONFIG = "CYBERTEAM_CONFIG"
ENV_CYBERTEAM_DATA = "CYBERTEAM_DATA"
ENV_CYBERTEAM_LOG_LEVEL = "CYBERTEAM_LOG_LEVEL"
ENV_CYBERTEAM_DEBUG = "CYBERTEAM_DEBUG"

# =============================================================================
# 导出所有常量
# =============================================================================

__all__ = [
    # 版本
    "VERSION",
    "VERSION_INFO",
    # 路径
    "PROJECT_ROOT",
    "CYBERTEAM_ROOT",
    "CONFIG_DIR",
    "DATA_DIR",
    "LOG_DIR",
    "TEMPLATES_DIR",
    "CACHE_DIR",
    "WORKSPACE_DIR",
    # 配置
    "DEFAULT_TEAM_CONFIG",
    "DEFAULT_AGENT_PROFILES",
    # 消息
    "MESSAGE_TYPE_TEXT",
    "MESSAGE_TYPE_JSON",
    "MESSAGE_TYPE_FILE",
    "MESSAGE_STATUS_PENDING",
    "MESSAGE_STATUS_SENT",
    "MESSAGE_STATUS_DELIVERED",
    "MESSAGE_STATUS_READ",
    "MESSAGE_STATUS_FAILED",
    # 任务
    "TASK_STATUS_PENDING",
    "TASK_STATUS_RUNNING",
    "TASK_STATUS_COMPLETED",
    "TASK_STATUS_FAILED",
    "TASK_STATUS_CANCELLED",
    "TASK_PRIORITY_LOW",
    "TASK_PRIORITY_NORMAL",
    "TASK_PRIORITY_HIGH",
    "TASK_PRIORITY_CRITICAL",
    # 团队
    "TEAM_ROLE_LEADER",
    "TEAM_ROLE_MEMBER",
    "TEAM_ROLE_OBSERVER",
    "TEAM_STATUS_ACTIVE",
    "TEAM_STATUS_INACTIVE",
    "TEAM_STATUS_DISSOLVED",
    # MCP
    "MCP_SERVER_STATUS_STOPPED",
    "MCP_SERVER_STATUS_STARTING",
    "MCP_SERVER_STATUS_RUNNING",
    "MCP_SERVER_STATUS_ERROR",
    "MCP_TOOL_TYPE_LOCAL",
    "MCP_TOOL_TYPE_MCP",
    "MCP_TOOL_TYPE_CUSTOM",
    # 通信
    "DEFAULT_API_PORT",
    "DEFAULT_BOARD_PORT",
    "DEFAULT_MCP_PORT",
    "DEFAULT_TIMEOUT",
    "LONG_TIMEOUT",
    "SHORT_TIMEOUT",
    "MAX_RETRIES",
    "RETRY_DELAY",
    # 日志
    "LOG_LEVEL_DEBUG",
    "LOG_LEVEL_INFO",
    "LOG_LEVEL_WARNING",
    "LOG_LEVEL_ERROR",
    "LOG_LEVEL_CRITICAL",
    "LOG_FORMAT",
    "LOG_DATE_FORMAT",
    # 文件
    "MAX_FILE_SIZE",
    "ALLOWED_FILE_EXTENSIONS",
    # 工作区
    "DEFAULT_BRANCH",
    "AGENT_BRANCH_PREFIX",
    "CONFLICT_START_MARKER",
    "CONFLICT_SEPARATOR",
    "CONFLICT_END_MARKER",
    # 进程
    "BACKEND_TYPE_SUBPROCESS",
    "BACKEND_TYPE_TMUX",
    "PROCESS_STATUS_RUNNING",
    "PROCESS_STATUS_STOPPED",
    "PROCESS_STATUS_ZOMBIE",
    # 环境变量
    "ENV_CYBERTEAM_HOME",
    "ENV_CYBERTEAM_CONFIG",
    "ENV_CYBERTEAM_DATA",
    "ENV_CYBERTEAM_LOG_LEVEL",
    "ENV_CYBERTEAM_DEBUG",
]