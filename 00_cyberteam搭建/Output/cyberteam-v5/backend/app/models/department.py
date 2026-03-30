"""
部门数据模型

定义公司组织架构中的部门
"""
from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass
class Department:
    """部门"""
    id: str
    name: str  # 部门名称
    code: str  # 部门代码，如 "tech", "product"
    parent_id: Optional[str] = None  # 父部门ID
    level: int = 1  # 层级：1=决策层，2=协调层，3=执行层
    description: str = ""
    manager_role: str = ""  # 负责人角色，如 "技术总监"
    skills: list[str] = field(default_factory=list)  # 部门专属技能
    status: str = "active"  # active, inactive
    order: int = 0  # 排序

    @staticmethod
    def create(
        name: str,
        code: str,
        level: int = 1,
        parent_id: Optional[str] = None,
        description: str = "",
        manager_role: str = "",
        skills: list[str] = None
    ) -> "Department":
        """创建新部门"""
        return Department(
            id=f"dept_{code}_{uuid.uuid4().hex[:8]}",
            name=name,
            code=code,
            parent_id=parent_id,
            level=level,
            description=description,
            manager_role=manager_role,
            skills=skills or [],
            order=level * 100
        )


# 默认部门模板
DEFAULT_DEPARTMENTS = [
    Department(
        id="dept_ceo",
        name="董事会",
        code="ceo",
        level=1,
        description="公司最高决策层",
        manager_role="CEO",
        skills=["战略规划", "团队管理", "决策分析"],
        order=100
    ),
    Department(
        id="dept_coo",
        name="运营中心",
        code="coo",
        level=1,
        description="运营管理中心",
        manager_role="COO",
        skills=["运营管理", "流程优化", "资源调度"],
        order=200
    ),
    Department(
        id="dept_tech",
        name="技术研发部",
        code="tech",
        level=2,
        parent_id="dept_coo",
        description="技术开发和架构设计",
        manager_role="技术总监",
        skills=["架构设计", "代码审查", "技术选型", "开发管理"],
        order=301
    ),
    Department(
        id="dept_product",
        name="产品研发部",
        code="product",
        level=2,
        parent_id="dept_coo",
        description="产品规划和需求管理",
        manager_role="产品总监",
        skills=["需求分析", "产品规划", "用户体验", "数据分析"],
        order=302
    ),
    Department(
        id="dept_growth",
        name="增长营销部",
        code="growth",
        level=2,
        parent_id="dept_coo",
        description="用户增长和营销策略",
        manager_role="增长总监",
        skills=["用户增长", "营销策略", "数据分析", "渠道运营"],
        order=303
    ),
    Department(
        id="dept_finance",
        name="财务部",
        code="finance",
        level=3,
        parent_id="dept_coo",
        description="财务管理和预算控制",
        manager_role="财务总监",
        skills=["预算管理", "成本控制", "财务分析"],
        order=401
    ),
    Department(
        id="dept_hr",
        name="人力资源部",
        code="hr",
        level=3,
        parent_id="dept_coo",
        description="人才招聘和团队建设",
        manager_role="HR总监",
        skills=["招聘", "培训", "绩效考核", "团队建设"],
        order=402
    ),
]


class DepartmentRegistry:
    """部门注册表"""

    def __init__(self):
        self.departments: dict[str, Department] = {}
        self._init_defaults()

    def _init_defaults(self):
        """初始化默认部门"""
        for dept in DEFAULT_DEPARTMENTS:
            self.departments[dept.id] = dept

    def register(self, dept: Department):
        """注册部门"""
        self.departments[dept.id] = dept

    def get(self, dept_id: str) -> Optional[Department]:
        """获取部门"""
        return self.departments.get(dept_id)

    def get_by_code(self, code: str) -> Optional[Department]:
        """通过代码获取部门"""
        for dept in self.departments.values():
            if dept.code == code:
                return dept
        return None

    def list_all(self) -> list[Department]:
        """列出所有部门"""
        return sorted(self.departments.values(), key=lambda x: x.order)

    def list_by_level(self, level: int) -> list[Department]:
        """按层级列出部门"""
        return [d for d in self.departments.values() if d.level == level]

    def list_children(self, parent_id: str) -> list[Department]:
        """列出子部门"""
        return [d for d in self.departments.values() if d.parent_id == parent_id]

    def update(self, dept_id: str, **kwargs) -> Optional[Department]:
        """更新部门"""
        dept = self.departments.get(dept_id)
        if not dept:
            return None

        for key, value in kwargs.items():
            if hasattr(dept, key):
                setattr(dept, key, value)

        return dept

    def delete(self, dept_id: str) -> bool:
        """删除部门"""
        if dept_id in self.departments:
            del self.departments[dept_id]
            return True
        return False

    def get_tree(self) -> list[dict]:
        """获取部门树"""
        result = []
        root_depts = [d for d in self.departments.values() if d.level == 1]

        def build_tree(dept: Department) -> dict:
            children = self.list_children(dept.id)
            node = {
                "id": dept.id,
                "name": dept.name,
                "code": dept.code,
                "level": dept.level,
                "manager_role": dept.manager_role,
                "description": dept.description,
                "children": [build_tree(c) for c in children]
            }
            return node

        for root in sorted(root_depts, key=lambda x: x.order):
            result.append(build_tree(root))

        return result
