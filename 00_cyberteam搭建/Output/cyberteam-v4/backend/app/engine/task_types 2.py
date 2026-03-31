"""任务调度值对象和枚举"""
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


class TaskStatus(Enum):
    """任务状态枚举"""
    UNKNOWN = 0
    PENDING = 1      # 创建/等待执行
    RUNNING = 2      # 执行中
    SUCCESS = 3      # 成功完成
    FAILED = 4       # 失败
    CANCELLED = 5    # 取消
    TIMEOUT = 6      # 超时
    RETRY = 7        # 重试中


class TaskType(Enum):
    """任务类型枚举"""
    IMMEDIATE = 1   # 即时任务
    SCHEDULED = 2   # 定时任务
    CRON = 3        # Cron 任务


@dataclass
class TaskResult:
    """任务执行结果值对象"""
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    cost_time_ms: float = 0.0
    retry_count: int = 0
