"""
CyberTeam Execution Monitor Configuration
==========================================
基于 PentAGI Execution Monitoring 设计

配置项说明:
- loop_detection: 循环检测配置
- intervention: 干预器配置
- limits: 工具调用限制配置
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class LoopDetectionConfig:
    """循环检测配置"""
    enabled: bool = True
    max_sequence_length: int = 20  # 跟踪的工具调用序列长度
    similarity_threshold: float = 0.7  # 序列相似度阈值
    min_repeat_count: int = 3  # 最小重复次数触发警告
    window_size: int = 10  # 滑动窗口大小
    check_interval: int = 5  # 每N次调用检查一次
    exact_match_enabled: bool = True  # 启用精确匹配
    fuzzy_match_enabled: bool = True  # 启用模糊匹配


@dataclass
class InterventionConfig:
    """干预器配置"""
    enabled: bool = True
    auto_intervention: bool = True  # 自动干预
    mentor_mode: str = "adviser"  # adviser | aggressive | passive
    max_retries: int = 3  # 最大重试次数
    escalation_timeout: int = 300  # 升级超时(秒)
    suggestion_types: List[str] = field(default_factory=lambda: [
        "diagnose", "alternative", "retry", "escalate", "context_refresh"
    ])
    context_refresh_interval: int = 10  # 上下文刷新间隔


@dataclass
class ToolLimitsConfig:
    """工具调用限制配置"""
    enabled: bool = True
    global_max_calls: int = 1000  # 全局最大调用次数
    per_agent_max_calls: int = 100  # 单个Agent最大调用次数
    per_tool_max_calls: int = 50  # 单个工具最大调用次数
    per_minute_limit: int = 30  # 每分钟最大调用次数
    burst_limit: int = 10  # 突发限制
    warning_threshold: float = 0.8  # 警告阈值(百分比)
    hard_stop_threshold: int = 50  # 硬性停止阈值(调用次数)
    cooldown_period: int = 60  # 冷却期(秒)


@dataclass
class MonitorConfig:
    """监控模块总配置"""
    loop_detection: LoopDetectionConfig = field(default_factory=LoopDetectionConfig)
    intervention: InterventionConfig = field(default_factory=InterventionConfig)
    limits: ToolLimitsConfig = field(default_factory=ToolLimitsConfig)

    # 通用配置
    log_level: str = "INFO"
    metrics_enabled: bool = True
    alert_webhook: Optional[str] = None
    persist_state: bool = True
    state_file: str = ".cyberteam/monitor_state.json"

    @classmethod
    def from_dict(cls, config: Dict) -> 'MonitorConfig':
        """从字典加载配置"""
        return cls(
            loop_detection=LoopDetectionConfig(**config.get('loop_detection', {})),
            intervention=InterventionConfig(**config.get('intervention', {})),
            limits=ToolLimitsConfig(**config.get('limits', {})),
            log_level=config.get('log_level', 'INFO'),
            metrics_enabled=config.get('metrics_enabled', True),
            alert_webhook=config.get('alert_webhook'),
            persist_state=config.get('persist_state', True),
            state_file=config.get('state_file', '.cyberteam/monitor_state.json')
        )

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'loop_detection': self.loop_detection.__dict__,
            'intervention': self.intervention.__dict__,
            'limits': self.limits.__dict__,
            'log_level': self.log_level,
            'metrics_enabled': self.metrics_enabled,
            'alert_webhook': self.alert_webhook,
            'persist_state': self.persist_state,
            'state_file': self.state_file
        }


# 默认配置实例
DEFAULT_CONFIG = MonitorConfig()


def get_config(config_path: Optional[str] = None) -> MonitorConfig:
    """获取配置"""
    if config_path:
        import json
        try:
            with open(config_path, 'r') as f:
                config_dict = json.load(f)
            return MonitorConfig.from_dict(config_dict)
        except Exception as e:
            print(f"Failed to load config from {config_path}: {e}")
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG
