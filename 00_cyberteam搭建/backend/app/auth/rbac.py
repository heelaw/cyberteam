"""RBAC permission system for CyberTeam."""
from typing import Optional
from enum import Enum


class Department(str, Enum):
    """Three Departments (三省)."""
    STRATEGY = "strategy"       # 战略省
    EXECUTION = "execution"     # 执行省
    MANAGEMENT = "management"  # 管理省


class Action(str, Enum):
    """Actions that can be performed."""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"


# Six Ministries permission matrix (三省六部权限矩阵)
DEPARTMENT_PERMISSIONS: dict[str, dict[str, list[str]]] = {
    # 三省
    "strategy": {
        "policy": ["read", "write", "execute"],
        "planning": ["read", "write", "execute"],
        "investor": ["read"],
        "framework": ["read", "write"],
    },
    "execution": {
        "engineering": ["read", "write", "execute"],
        "design": ["read", "write", "execute"],
        "marketing": ["read", "write", "execute"],
        "operations": ["read", "write", "execute"],
    },
    "management": {
        "hr": ["read", "write", "execute"],
        "finance": ["read", "write", "execute"],
        "ops": ["read", "write", "execute"],
        "product": ["read", "write", "execute"],
    },
    # 六部
    "吏部": ["read", "write", "execute", "admin"],      # 人力资源
    "户部": ["read", "write", "execute", "admin"],      # 财务
    "礼部": ["read", "write", "execute", "admin"],      # 外交/品牌
    "兵部": ["read", "write", "execute", "admin"],      # 运营
    "刑部": ["read", "write", "execute", "admin"],      # 法务
    "工部": ["read", "write", "execute", "admin"],      # 工程
}

# Role to department mapping
ROLE_DEPARTMENTS: dict[str, str] = {
    "ceo": "strategy",
    "coo": "strategy",
    "cfo": "management",
    "cto": "execution",
    "cmo": "execution",
    "agent": "execution",
    "expert": "strategy",
}


class RBAC:
    """RBAC permission checker."""

    @staticmethod
    def check_permission(
        user: dict,
        department: str,
        action: str,
        resource: Optional[str] = None,
    ) -> bool:
        """Check if user has permission for action on department.

        Args:
            user: User dict with 'role' and 'departments' keys
            department: Target department name
            action: Action to perform (read/write/execute/admin)
            resource: Optional specific resource within department

        Returns:
            True if permission granted, False otherwise
        """
        user_role = user.get("role", "guest")
        user_departments = user.get("departments", [])

        # Admin role has all permissions
        if user_role == "admin":
            return True

        # Map role to department if direct mapping exists
        if user_role in ROLE_DEPARTMENTS:
            mapped_dept = ROLE_DEPARTMENTS[user_role]
            if mapped_dept == department:
                return action in DEPARTMENT_PERMISSIONS.get(mapped_dept, {}).get(resource or department, [])

        # Check if user's departments include target department
        if department in user_departments or user_role in user_departments:
            dept_perms = DEPARTMENT_PERMISSIONS.get(department, {})
            if resource and resource in dept_perms:
                return action in dept_perms[resource]
            elif resource is None:
                # Check if any resource in department allows action
                for res_perms in dept_perms.values():
                    if action in res_perms:
                        return True

        return False

    @staticmethod
    def get_user_departments(user: dict) -> list[str]:
        """Get all departments a user has access to."""
        user_role = user.get("role", "guest")
        user_departments = user.get("departments", [])

        # Add role-based department
        if user_role in ROLE_DEPARTMENTS:
            role_dept = ROLE_DEPARTMENTS[user_role]
            if role_dept not in user_departments:
                user_departments = [role_dept] + user_departments

        return user_departments

    @staticmethod
    def require_permission(department: str, action: str, resource: Optional[str] = None):
        """Decorator to enforce RBAC on endpoint functions."""
        def decorator(func):
            func._required_permission = {
                "department": department,
                "action": action,
                "resource": resource,
            }
            return func
        return decorator
