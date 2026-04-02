"""动态部门管理器 - 支持运行时添加、修改、删除自定义部门。

功能：
- 动态注册新部门
- 更新现有部门 Metadata
- 删除自定义部门（内置部门受保护）
- 从数据库加载自定义部门
- 将自定义部门持久化到数据库
"""

import logging
from typing import Dict, List, Optional, Any, Set

from app.engine.ceo_metadata import (
    CEORouter,
    DEPARTMENT_METADATA,
    DepartmentMetadata,
    SkillDefinition,
    RoutingRule,
    LeaderConfig,
    ExecutorConfig,
)

logger = logging.getLogger(__name__)

# 内置部门 ID 集合（不可删除）
BUILTIN_DEPARTMENT_IDS: Set[str] = {
    "ceo", "product", "engineering", "design",
    "operations", "marketing", "finance", "hr",
}


class DepartmentRegistry:
    """动态部门注册表 - 管理所有部门（包括内置和自定义）。

    支持：
    - register_department(): 注册新部门
    - update_department(): 更新部门 Metadata
    - unregister_department(): 注销自定义部门
    - get_department(): 获取部门 Metadata
    - list_departments(): 列出所有部门
    - is_builtin(): 判断是否为内置部门
    """

    def __init__(self, db_session=None):
        """初始化部门注册表。

        Args:
            db_session: 可选的数据库会话，用于持久化自定义部门
        """
        self._departments: Dict[str, DepartmentMetadata] = dict(DEPARTMENT_METADATA)
        self._custom_department_ids: Set[str] = set()  # 追踪自定义部门
        self._db_session = db_session
        self._router: Optional[CEORouter] = None

    @property
    def router(self) -> CEORouter:
        """获取路由引擎（延迟初始化）。"""
        if self._router is None:
            self._router = CEORouter()
        return self._router

    def register_department(
        self,
        department_id: str,
        name: str,
        description: str,
        responsibility: str,
        skills: List[Dict[str, Any]] = None,
        routing_rules: List[Dict[str, Any]] = None,
        leader_role: str = "部门负责人",
        leader_skills: List[str] = None,
        executor_role: str = "部门专家",
        executor_skills: List[str] = None,
        parent_id: Optional[str] = None,
        price_tier: str = "免费",
        tags: List[str] = None,
    ) -> DepartmentMetadata:
        """注册新部门。

        Args:
            department_id: 部门唯一标识（英文）
            name: 部门中文名称
            description: 部门描述
            responsibility: 核心职责
            skills: 技能列表，格式：[{"skill_id": "xxx", "name": "技能名", "level": 1}]
            routing_rules: 路由规则，格式：[{"keywords": ["关键词1", "关键词2"], "weight": 1.0}]
            leader_role: Leader 角色名称
            leader_skills: Leader 所需技能列表
            executor_role: 执行器角色名称
            executor_skills: 执行器所需技能列表
            parent_id: 上级部门 ID
            price_tier: 价格层级
            tags: 标签列表

        Returns:
            创建的 DepartmentMetadata 对象

        Raises:
            ValueError: 如果部门 ID 已存在
        """
        if department_id in self._departments:
            raise ValueError(f"部门 {department_id} 已存在，请使用 update_department() 更新")

        if department_id in BUILTIN_DEPARTMENT_IDS:
            raise ValueError(f"部门 {department_id} 是内置部门，无法注册同名部门")

        # 构建技能列表
        skill_defs = []
        for s in (skills or []):
            skill_defs.append(SkillDefinition(
                skill_id=s.get("skill_id", ""),
                name=s.get("name", ""),
                level=s.get("level", 3),
                description=s.get("description", ""),
            ))

        # 构建路由规则
        routing_rule_defs = []
        for r in (routing_rules or []):
            routing_rule_defs.append(RoutingRule(
                keywords=r.get("keywords", []),
                weight=r.get("weight", 1.0),
                description=r.get("description", ""),
            ))

        # 构建 Leader 配置
        leader = LeaderConfig(
            role=leader_role,
            skills=leader_skills or [],
            decision_making="collaborative",
        )

        # 构建 Executor 配置
        executor = ExecutorConfig(
            role=executor_role,
            skills=executor_skills or [],
            output_format="markdown",
            review_required=True,
        )

        # 创建部门 Metadata
        metadata = DepartmentMetadata(
            department_id=department_id,
            name=name,
            description=description,
            responsibility=responsibility,
            skills=skill_defs,
            routing_rules=routing_rule_defs,
            leader=leader,
            executor=executor,
            parent_id=parent_id,
            price_tier=price_tier,
            tags=tags or [],
        )

        # 注册到内存
        self._departments[department_id] = metadata
        self._custom_department_ids.add(department_id)

        # TODO: 持久化到数据库（当 db_session 可用时）
        # if self._db_session:
        #     await self._save_to_db(metadata)

        logger.info(f"注册新部门: {department_id} ({name})")
        return metadata

    def update_department(
        self,
        department_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        responsibility: Optional[str] = None,
        skills: Optional[List[Dict[str, Any]]] = None,
        routing_rules: Optional[List[Dict[str, Any]]] = None,
        leader_role: Optional[str] = None,
        leader_skills: Optional[List[str]] = None,
        executor_role: Optional[str] = None,
        executor_skills: Optional[List[str]] = None,
        parent_id: Optional[str] = None,
        price_tier: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Optional[DepartmentMetadata]:
        """更新部门 Metadata。

        Args:
            department_id: 部门 ID
            其他参数同 register_department()

        Returns:
            更新后的 DepartmentMetadata 对象，如果部门不存在则返回 None
        """
        if department_id not in self._departments:
            logger.warning(f"部门 {department_id} 不存在")
            return None

        metadata = self._departments[department_id]

        # 更新字段
        if name is not None:
            metadata.name = name
        if description is not None:
            metadata.description = description
        if responsibility is not None:
            metadata.responsibility = responsibility
        if parent_id is not None:
            metadata.parent_id = parent_id
        if price_tier is not None:
            metadata.price_tier = price_tier
        if tags is not None:
            metadata.tags = tags

        if skills is not None:
            metadata.skills = [
                SkillDefinition(
                    skill_id=s.get("skill_id", ""),
                    name=s.get("name", ""),
                    level=s.get("level", 3),
                    description=s.get("description", ""),
                )
                for s in skills
            ]

        if routing_rules is not None:
            metadata.routing_rules = [
                RoutingRule(
                    keywords=r.get("keywords", []),
                    weight=r.get("weight", 1.0),
                    description=r.get("description", ""),
                )
                for r in routing_rules
            ]

        if leader_role is not None:
            metadata.leader.role = leader_role
        if leader_skills is not None:
            metadata.leader.skills = leader_skills

        if executor_role is not None:
            metadata.executor.role = executor_role
        if executor_skills is not None:
            metadata.executor.skills = executor_skills

        logger.info(f"更新部门: {department_id}")
        return metadata

    def unregister_department(self, department_id: str) -> bool:
        """注销自定义部门。

        Args:
            department_id: 部门 ID

        Returns:
            True 如果注销成功，False 如果部门不存在或为内置部门
        """
        if department_id in BUILTIN_DEPARTMENT_IDS:
            logger.warning(f"无法注销内置部门: {department_id}")
            return False

        if department_id not in self._departments:
            logger.warning(f"部门不存在: {department_id}")
            return False

        # 从内存移除
        del self._departments[department_id]
        self._custom_department_ids.discard(department_id)

        # TODO: 从数据库删除（当 db_session 可用时）

        logger.info(f"注销部门: {department_id}")
        return True

    def get_department(self, department_id: str) -> Optional[DepartmentMetadata]:
        """获取部门 Metadata。"""
        return self._departments.get(department_id)

    def list_departments(
        self,
        include_builtin: bool = True,
        include_custom: bool = True,
    ) -> List[DepartmentMetadata]:
        """列出部门。

        Args:
            include_builtin: 是否包含内置部门
            include_custom: 是否包含自定义部门

        Returns:
            部门 Metadata 列表
        """
        result = []

        if include_builtin:
            for dept_id in BUILTIN_DEPARTMENT_IDS:
                if dept_id in self._departments:
                    result.append(self._departments[dept_id])

        if include_custom:
            for dept_id in self._custom_department_ids:
                if dept_id in self._departments:
                    result.append(self._departments[dept_id])

        return result

    def list_department_ids(
        self,
        include_builtin: bool = True,
        include_custom: bool = True,
    ) -> List[str]:
        """列出部门 ID。"""
        result = []

        if include_builtin:
            result.extend(sorted(BUILTIN_DEPARTMENT_IDS & set(self._departments.keys())))

        if include_custom:
            result.extend(sorted(self._custom_department_ids))

        return result

    def is_builtin(self, department_id: str) -> bool:
        """判断是否为内置部门。"""
        return department_id in BUILTIN_DEPARTMENT_IDS

    def is_custom(self, department_id: str) -> bool:
        """判断是否为自定义部门。"""
        return department_id in self._custom_department_ids

    def get_statistics(self) -> Dict[str, Any]:
        """获取部门统计信息。"""
        return {
            "total_count": len(self._departments),
            "builtin_count": len(BUILTIN_DEPARTMENT_IDS & set(self._departments.keys())),
            "custom_count": len(self._custom_department_ids & set(self._departments.keys())),
            "builtin_departments": sorted(BUILTIN_DEPARTMENT_IDS & set(self._departments.keys())),
            "custom_departments": sorted(self._custom_department_ids),
        }

    def export_config(self) -> Dict[str, Any]:
        """导出所有部门的配置（用于保存或传输）。"""
        return {
            "builtin_count": len(BUILTIN_DEPARTMENT_IDS),
            "custom_departments": [
                self.get_department(dept_id).to_dict()
                for dept_id in sorted(self._custom_department_ids)
                if dept_id in self._departments
            ],
        }

    def import_config(self, config: Dict[str, Any]) -> int:
        """导入部门配置。

        Args:
            config: 导出的配置字典

        Returns:
            成功导入的部门数量
        """
        imported = 0
        for dept_config in config.get("custom_departments", []):
            try:
                self.register_department(
                    department_id=dept_config["department_id"],
                    name=dept_config["name"],
                    description=dept_config["description"],
                    responsibility=dept_config["responsibility"],
                    skills=dept_config.get("skills", []),
                    routing_rules=dept_config.get("routing_rules", []),
                    leader_role=dept_config.get("leader", {}).get("role", "部门负责人"),
                    leader_skills=dept_config.get("leader", {}).get("skills", []),
                    executor_role=dept_config.get("executor", {}).get("role", "部门专家"),
                    executor_skills=dept_config.get("executor", {}).get("skills", []),
                    parent_id=dept_config.get("parent_id"),
                    price_tier=dept_config.get("price_tier", "免费"),
                    tags=dept_config.get("tags", []),
                )
                imported += 1
            except ValueError as e:
                logger.warning(f"导入部门失败: {e}")

        return imported


# 全局单例实例
_department_registry: Optional[DepartmentRegistry] = None


def get_department_registry() -> DepartmentRegistry:
    """获取全局部门注册表单例。"""
    global _department_registry
    if _department_registry is None:
        _department_registry = DepartmentRegistry()
    return _department_registry


def reset_department_registry() -> None:
    """重置全局部门注册表（主要用于测试）。"""
    global _department_registry
    _department_registry = None
