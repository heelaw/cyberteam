"""CyberTeam Adaptors - ClawTeam 融合适配层

该模块提供 CyberTeam V4 与外部 ClawTeam v0.2.0 的无缝融合能力。

主要功能:
- ClawTeam 接口兼容层
- 配置统一管理（支持双数据目录）
- 环境变量兼容（CLAWTEAM_* -> CYBERTEAM_*）
- 消息传递桥接
"""

from cyberteam.adaptors.clawteam_compat import ClawTeamCompat
from cyberteam.adaptors.config_unifier import ConfigUnifier

__all__ = [
    "ClawTeamCompat",
    "ConfigUnifier",
]
