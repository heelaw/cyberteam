"""
Alert Manager - 告警管理模块
管理告警的触发、聚合和升级
"""

from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime
import uuid


class AlertLevel(Enum):
    """告警级别枚举"""
    P0_BLOCKER = "p0_blocker"      # 阻塞级 - 需要立即处理
    P1_CRITICAL = "p1_critical"    # 严重级 - 尽快处理
    P2_WARNING = "p2_warning"     # 警告级 - 关注处理
    P3_INFO = "p3_info"           # 信息级 - 记录观察


class Alert:
    """告警对象"""

    def __init__(
        self,
        level: AlertLevel,
        message: str,
        source: str = None,
        metadata: Dict = None
    ):
        self.id = str(uuid.uuid4())[:8]
        self.level = level
        self.message = message
        self.source = source
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
        self.status = "active"
        self.escalation_count = 0

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "level": self.level.value,
            "message": self.message,
            "source": self.source,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
            "escalation_count": self.escalation_count
        }


class AlertManager:
    """告警管理器"""

    def __init__(self):
        self.alerts: List[Alert] = []
        self.escalation_chain = {
            AlertLevel.P3_INFO: AlertLevel.P2_WARNING,
            AlertLevel.P2_WARNING: AlertLevel.P1_CRITICAL,
            AlertLevel.P1_CRITICAL: AlertLevel.P0_BLOCKER,
            AlertLevel.P0_BLOCKER: AlertLevel.P0_BLOCKER  # 最高级不再升级
        }

    def trigger(self, level: AlertLevel, message: str, source: str = None, metadata: Dict = None) -> Alert:
        """
        触发新告警

        Args:
            level: 告警级别
            message: 告警消息
            source: 告警来源
            metadata: 附加元数据

        Returns:
            Alert - 创建的告警对象
        """
        alert = Alert(level=level, message=message, source=source, metadata=metadata)
        self.alerts.append(alert)
        return alert

    def aggregate(self, alerts: List[Alert]) -> List[Alert]:
        """
        聚合相似告警

        Args:
            alerts: 待聚合的告警列表

        Returns:
            List[Alert] - 聚合后的告警列表
        """
        if not alerts:
            return []

        # 按级别和来源分组
        groups: Dict[str, List[Alert]] = {}
        for alert in alerts:
            key = f"{alert.level.value}:{alert.source}"
            if key not in groups:
                groups[key] = []
            groups[key].append(alert)

        # 聚合每个组
        aggregated = []
        for key, group in groups.items():
            if len(group) == 1:
                aggregated.append(group[0])
            else:
                # 多条告警聚合为一条
                first = group[0]
                aggregated.append(Alert(
                    level=first.level,
                    message=f"[聚合{len(group)}条] {first.message}",
                    source=first.source,
                    metadata={
                        **first.metadata,
                        "aggregated_count": len(group),
                        "original_alerts": [a.id for a in group]
                    }
                ))

        return aggregated

    def escalate(self, alert_id: str) -> Optional[Alert]:
        """
        升级告警

        Args:
            alert_id: 告警ID

        Returns:
            Optional[Alert] - 升级后的告警，如果未找到则返回None
        """
        for alert in self.alerts:
            if alert.id == alert_id and alert.status == "active":
                current_level = alert.level
                new_level = self.escalation_chain.get(current_level)

                if new_level and new_level != current_level:
                    alert.level = new_level
                    alert.escalation_count += 1
                    alert.metadata["escalated_at"] = datetime.now().isoformat()
                    return alert
                elif new_level == current_level:
                    # 已达最高级别，标记为需人工介入
                    alert.metadata["requires_manual_intervention"] = True
                    return alert

        return None

    def get_active_alerts(self, min_level: AlertLevel = None) -> List[Alert]:
        """获取活跃告警"""
        active = [a for a in self.alerts if a.status == "active"]
        if min_level:
            active = [a for a in active if a.level.value <= min_level.value]
        return active

    def resolve_alert(self, alert_id: str) -> bool:
        """解决告警"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.status = "resolved"
                alert.metadata["resolved_at"] = datetime.now().isoformat()
                return True
        return False

    def get_alert_summary(self) -> Dict:
        """获取告警摘要"""
        active = self.get_active_alerts()
        by_level = {}
        for level in AlertLevel:
            by_level[level.value] = len([a for a in active if a.level == level])

        return {
            "total_active": len(active),
            "by_level": by_level,
            "requires_escalation": len([a for a in active if a.escalation_count > 0]),
            "requires_manual": len([a for a in active if a.metadata.get("requires_manual_intervention")])
        }