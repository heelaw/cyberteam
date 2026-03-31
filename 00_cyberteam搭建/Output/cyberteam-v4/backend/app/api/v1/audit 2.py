"""审计日志中间件 - 记录所有关键操作。

提供内存审计日志功能，用于追踪：
- 公司操作（创建/更新/删除/绑定）
- 部门操作
- Agent操作
- Skill操作
- 团队操作
"""

from datetime import datetime
import uuid

# 内存审计日志存储（保留最近1000条）
_audit_logs: list[dict] = []


def record_audit(
    company_id: str = None,
    user_id: str = None,
    action: str = None,
    resource_type: str = None,
    resource_id: str = None,
    resource_name: str = None,
    detail: dict = None,
    ip_address: str = None,
) -> str:
    """记录审计日志。

    Args:
        company_id: 公司ID
        user_id: 用户ID
        action: 操作类型（CREATE/UPDATE/DELETE/BIND/UNBIND）
        resource_type: 资源类型（company/department/agent/skill/team）
        resource_id: 资源ID
        resource_name: 资源名称
        detail: 详细信息（dict格式）
        ip_address: IP地址

    Returns:
        审计日志ID
    """
    log_id = str(uuid.uuid4())
    _audit_logs.append({
        "id": log_id,
        "company_id": company_id,
        "user_id": user_id,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "resource_name": resource_name,
        "detail": detail,
        "ip_address": ip_address,
        "created_at": datetime.utcnow().isoformat(),
    })

    # 保留最近1000条
    if len(_audit_logs) > 1000:
        _audit_logs[:] = _audit_logs[-1000:]

    return log_id


def get_audit_logs(
    company_id: str = None,
    resource_type: str = None,
    action: str = None,
    limit: int = 100,
) -> list[dict]:
    """获取审计日志。

    Args:
        company_id: 公司ID（可选，筛选该公司日志）
        resource_type: 资源类型（可选）
        action: 操作类型（可选）
        limit: 返回数量限制（默认100）

    Returns:
        审计日志列表
    """
    filtered = _audit_logs

    if company_id:
        filtered = [l for l in filtered if l.get("company_id") == company_id]
    if resource_type:
        filtered = [l for l in filtered if l.get("resource_type") == resource_type]
    if action:
        filtered = [l for l in filtered if l.get("action") == action]

    return filtered[-limit:]


def clear_audit_logs():
    """清除所有审计日志（仅用于测试）。"""
    global _audit_logs
    _audit_logs.clear()