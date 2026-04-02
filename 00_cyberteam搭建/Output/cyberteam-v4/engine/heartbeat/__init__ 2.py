"""
Heartbeat Engine - Paperclip心跳机制实现
来源: paperclip/heartbeats/
功能: Agent长时间运行时的"心跳"保障，防止死循环
"""
import threading
import time
import logging
from datetime import datetime
from typing import Dict, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class HeartbeatStatus(Enum):
    """心跳状态"""
    ALIVE = "alive"
    WARNING = "warning"
    DEAD = "dead"
    STOPPED = "stopped"


@dataclass
class HeartbeatRecord:
    """心跳记录"""
    name: str
    registered_at: datetime
    last_pulse: datetime
    timeout: int = 60
    max_missed: int = 3
    status: HeartbeatStatus = HeartbeatStatus.ALIVE
    missed_count: int = 0
    callback: Optional[Callable] = None


class HeartbeatEngine:
    """
    心跳引擎 - Paperclip Heartbeats实现

    功能:
    1. 注册Agent心跳
    2. 定期发送心跳
    3. 检测超时自动回调
    4. 防止死循环

    使用示例:
    >>> hb = HeartbeatEngine()
    >>> hb.register("ceo", timeout=60, callback=my_callback)
    >>> hb.pulse("ceo")  # 在任务执行中定期调用
    >>> hb.unregister("ceo")  # 任务完成时调用
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._records: Dict[str, HeartbeatRecord] = {}
        self._monitor_thread: Optional[threading.Thread] = None
        self._running = False
        self._interval = 10  # 每10秒检查一次
        self._initialized = True

        logger.info("HeartbeatEngine 初始化完成")

    def register(
        self,
        name: str,
        timeout: int = 60,
        max_missed: int = 3,
        callback: Optional[Callable] = None
    ) -> bool:
        """
        注册心跳

        Args:
            name: Agent名称
            timeout: 超时时间（秒）
            max_missed: 最大错过心跳次数
            callback: 超时回调函数

        Returns:
            bool: 注册是否成功
        """
        if name in self._records:
            logger.warning(f"Heartbeat {name} 已注册，更新配置")
            self.unregister(name)

        now = datetime.now()
        self._records[name] = HeartbeatRecord(
            name=name,
            registered_at=now,
            last_pulse=now,
            timeout=timeout,
            max_missed=max_missed,
            callback=callback
        )

        # 启动监控线程
        if not self._running:
            self._start_monitor()

        logger.info(f"Heartbeat 注册成功: {name} (timeout={timeout}s)")
        return True

    def pulse(self, name: str) -> bool:
        """
        发送心跳

        Args:
            name: Agent名称

        Returns:
            bool: 心跳是否成功
        """
        if name not in self._records:
            logger.warning(f"Heartbeat {name} 未注册，自动注册")
            self.register(name)

        record = self._records[name]
        record.last_pulse = datetime.now()
        record.missed_count = 0
        record.status = HeartbeatStatus.ALIVE

        logger.debug(f"Heartbeat pulse: {name}")
        return True

    def check(self, name: str) -> HeartbeatStatus:
        """
        检查心跳状态

        Args:
            name: Agent名称

        Returns:
            HeartbeatStatus: 当前状态
        """
        if name not in self._records:
            return HeartbeatStatus.STOPPED

        record = self._records[name]
        elapsed = (datetime.now() - record.last_pulse).total_seconds()

        if elapsed > record.timeout:
            if record.missed_count >= record.max_missed:
                record.status = HeartbeatStatus.DEAD
            else:
                record.status = HeartbeatStatus.WARNING
                record.missed_count += 1

        return record.status

    def unregister(self, name: str) -> bool:
        """
        注销心跳

        Args:
            name: Agent名称

        Returns:
            bool: 注销是否成功
        """
        if name in self._records:
            del self._records[name]
            logger.info(f"Heartbeat 注销: {name}")
            return True
        return False

    def get_status(self, name: str) -> Optional[Dict]:
        """
        获取心跳状态详情

        Args:
            name: Agent名称

        Returns:
            Dict: 状态详情
        """
        if name not in self._records:
            return None

        record = self._records[name]
        return {
            "name": record.name,
            "status": record.status.value,
            "registered_at": record.registered_at.isoformat(),
            "last_pulse": record.last_pulse.isoformat(),
            "timeout": record.timeout,
            "missed_count": record.missed_count,
            "elapsed_seconds": (datetime.now() - record.last_pulse).total_seconds()
        }

    def list_all(self) -> Dict[str, HeartbeatStatus]:
        """
        列出所有注册的心跳

        Returns:
            Dict[str, HeartbeatStatus]: 所有心跳状态
        """
        return {name: self.check(name) for name in self._records}

    def _start_monitor(self):
        """启动监控线程"""
        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("Heartbeat 监控线程启动")

    def _monitor_loop(self):
        """监控循环"""
        while self._running:
            try:
                for name in list(self._records.keys()):
                    status = self.check(name)
                    if status == HeartbeatStatus.WARNING:
                        logger.warning(f"Heartbeat 警告: {name} 超过 {self._records[name].timeout}s 未响应")
                    elif status == HeartbeatStatus.DEAD:
                        logger.error(f"Heartbeat 死亡: {name}")
                        record = self._records[name]
                        if record.callback:
                            try:
                                record.callback(name)
                            except Exception as e:
                                logger.error(f"Heartbeat 回调失败: {e}")
                        # 死亡后自动注销
                        self.unregister(name)
            except Exception as e:
                logger.error(f"Heartbeat 监控异常: {e}")

            time.sleep(self._interval)

    def stop(self):
        """停止心跳引擎"""
        self._running = False
        self._records.clear()
        logger.info("HeartbeatEngine 停止")

    def __del__(self):
        """析构函数"""
        self.stop()


# 全局实例
HEARTBEAT = HeartbeatEngine()
