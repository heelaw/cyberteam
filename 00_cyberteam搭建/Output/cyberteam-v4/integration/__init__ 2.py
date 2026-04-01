"""CyberTeam Adapter - Engine 层与底层 cyberteam 模块的适配层

职责：
1. 封装 cyberteam 底层模块的复杂接口
2. 提供简洁的 API 给 engine 层调用
3. 解耦 engine 层与底层实现，便于 ClawTeam 升级

升级策略：
- 如果 ClawTeam 升级，只需更新此适配层
- engine 层无需改动
"""

from integration.cyberteam_adapter import CyberTeamAdapter

__all__ = ["CyberTeamAdapter"]
