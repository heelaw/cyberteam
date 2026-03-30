"""RBAC 权限控制服务 - 抄 Magic。

核心功能：
- 基于角色的访问控制（Role-Based Access Control）
- 权限定义与检查
- 部门级别的访问控制
- CyberTeam 三省六部架构适配

角色层级：
- admin: 超级管理员，拥有所有权限
- user: 普通用户，按部门权限访问
- guest: 访客，只有只读权限
- department_admin: 部门管理员，管理本部门资源

权限定义：
- agent:manage - 管理 Agent
- agent:execute - 执行 Agent
- project:manage - 管理项目
- project:read - 读取项目
- skill:manage - 管理技能
- skill:execute - 执行技能
- department:manage - 管理部门
- config:manage - 管理配置
- budget:manage - 管理预算
"""

from enum import Enum
from typing import Dict, List, Optional, Set
from functools import wraps
import logging

log = logging.getLogger("cyberteam.auth.rbac")


class Permission(str, Enum):
    """权限枚举。"""
    # Agent 权限
    AGENT_MANAGE = "agent:manage"
    AGENT_EXECUTE = "agent:execute"
    AGENT_READ = "agent:read"

    # 项目权限
    PROJECT_MANAGE = "project:manage"
    PROJECT_READ = "project:read"

    # 技能权限
    SKILL_MANAGE = "skill:manage"
    SKILL_EXECUTE = "skill:execute"
    SKILL_READ = "skill:read"

    # 部门权限
    DEPARTMENT_MANAGE = "department:manage"
    DEPARTMENT_READ = "department:read"

    # 系统权限
    CONFIG_MANAGE = "config:manage"
    BUDGET_MANAGE = "budget:manage"
    USER_MANAGE = "user:manage"


class Role(str, Enum):
    """角色枚举。"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
    DEPARTMENT_ADMIN = "department_admin"


# 角色权限映射
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.ADMIN: set(Permission),  # 管理员拥有所有权限
    Role.USER: {
        Permission.AGENT_READ,
        Permission.AGENT_EXECUTE,
        Permission.PROJECT_READ,
        Permission.SKILL_READ,
        Permission.SKILL_EXECUTE,
        Permission.DEPARTMENT_READ,
    },
    Role.DEPARTMENT_ADMIN: {
        Permission.AGENT_READ,
        Permission.AGENT_EXECUTE,
        Permission.AGENT_MANAGE,
        Permission.PROJECT_READ,
        Permission.PROJECT_MANAGE,
        Permission.SKILL_READ,
        Permission.SKILL_EXECUTE,
        Permission.SKILL_MANAGE,
        Permission.DEPARTMENT_READ,
        Permission.BUDGET_MANAGE,
    },
    Role.GUEST: {
        Permission.AGENT_READ,
        Permission.PROJECT_READ,
        Permission.DEPARTMENT_READ,
    },
}


class RBACService:
    """RBAC 权限服务。

    用法:
        rbac = RBACService()
        has_permission = rbac.check(user, Permission.AGENT_MANAGE)
        rbac.require(user, Permission.AGENT_MANAGE)  # 无权限则抛出异常
    """

    def __init__(self):
        self._custom_role_permissions: Dict[str, Set[Permission]] = {}

    def get_role_permissions(self, role: str) -> Set[Permission]:
        """获取角色的所有权限。"""
        try:
            role_enum = Role(role)
        except ValueError:
            return set()

        # 优先检查自定义权限
        if role in self._custom_role_permissions:
            return self._custom_role_permissions[role]

        return ROLE_PERMISSIONS.get(role_enum, set())

    def check(self, user: dict, permission: Permission) -> bool:
        """检查用户是否拥有指定权限。

        Args:
            user: 用户信息字典 {"sub": user_id, "role": role}
            permission: 权限枚举

        Returns:
            是否拥有权限
        """
        if not user:
            return False

        role = user.get("role", "guest")
        permissions = self.get_role_permissions(role)

        return permission in permissions

    def require(self, user: dict, permission: Permission) -> None:
        """要求用户拥有指定权限，无权限则抛出异常。"""
        if not self.check(user, permission):
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission.value}",
            )

    def check_department_access(
        self, user: dict, department_id: str, require_write: bool = False
    ) -> bool:
        """检查用户是否有权访问指定部门。

        Args:
            user: 用户信息字典
            department_id: 部门ID
            require_write: 是否需要写权限

        Returns:
            是否有权访问
        """
        if not user:
            return False

        role = user.get("role", "guest")

        # 管理员可以访问所有部门
        if role == Role.ADMIN.value:
            return True

        # 检查用户所属部门
        user_departments = user.get("departments", [])
        if department_id in user_departments:
            return True

        # 部门管理员可以访问本部门
        if role == Role.DEPARTMENT_ADMIN.value:
            return True

        # 普通用户只有读权限
        if not require_write:
            return True

        return False

    def set_custom_role_permissions(
        self, role: str, permissions: List[Permission]
    ) -> None:
        """为角色设置自定义权限（覆盖默认权限）。"""
        self._custom_role_permissions[role] = set(permissions)
        log.info(f"Custom permissions set for role {role}: {permissions}")


# 全局单例
_rbac_service: Optional[RBACService] = None


def get_rbac_service() -> RBACService:
    """获取 RBAC 服务单例。"""
    global _rbac_service
    if _rbac_service is None:
        _rbac_service = RBACService()
    return _rbac_service


def check_permission(permission: Permission):
    """装饰器：检查权限。

    用法:
        @check_permission(Permission.AGENT_MANAGE)
        async def manage_agent(user: dict = Depends(get_current_user)):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 尝试从 kwargs 或依赖注入获取 user
            user = kwargs.get("user")
            if user is None:
                # 尝试从 Depends 获取
                for key, value in kwargs.items():
                    if isinstance(value, dict) and "sub" in value:
                        user = value
                        break

            rbac = get_rbac_service()
            rbac.require(user or {}, permission)
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_permission(permission: Permission):
    """依赖注入：要求特定权限。"""
    async def dependency(user: dict = None):
        rbac = get_rbac_service()
        rbac.require(user or {}, permission)
        return user
    return dependency
