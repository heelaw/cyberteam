"""部门注册表测试 - 验证动态部门管理功能。"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app.engine.department_registry import (
    DepartmentRegistry,
    get_department_registry,
    reset_department_registry,
    BUILTIN_DEPARTMENT_IDS,
)


class TestDepartmentRegistry:
    """测试 DepartmentRegistry 的所有方法。"""

    def setup_method(self):
        """每个测试前重置注册表。"""
        reset_department_registry()
        self.registry = DepartmentRegistry()

    def teardown_method(self):
        """每个测试后重置注册表。"""
        reset_department_registry()

    def test_get_builtin_departments(self):
        """测试获取内置部门。"""
        depts = self.registry.list_departments(include_builtin=True, include_custom=False)
        assert len(depts) == len(BUILTIN_DEPARTMENT_IDS)

        for dept in depts:
            assert dept.department_id in BUILTIN_DEPARTMENT_IDS

    def test_get_custom_departments_empty(self):
        """测试获取自定义部门（初始为空）。"""
        depts = self.registry.list_departments(include_builtin=False, include_custom=True)
        assert len(depts) == 0

    def test_register_new_department(self):
        """测试注册新部门。"""
        dept = self.registry.register_department(
            department_id="new_dept",
            name="新部门",
            description="这是一个测试部门",
            responsibility="负责测试任务",
            skills=[
                {"skill_id": "test_skill", "name": "测试技能", "level": 2},
            ],
            routing_rules=[
                {"keywords": ["测试", "实验"], "weight": 1.0, "description": "测试任务"},
            ],
            tags=["测试", "新部门"],
        )

        assert dept.department_id == "new_dept"
        assert dept.name == "新部门"
        assert len(dept.skills) == 1
        assert dept.skills[0].skill_id == "test_skill"

    def test_register_duplicate_department_fails(self):
        """测试注册重复部门会失败。"""
        self.registry.register_department(
            department_id="test_dept",
            name="测试部门",
            description="测试",
            responsibility="测试",
        )

        with pytest.raises(ValueError, match="已存在"):
            self.registry.register_department(
                department_id="test_dept",
                name="另一个测试部门",
                description="测试",
                responsibility="测试",
            )

    def test_register_builtin_name_fails(self):
        """测试注册与内置部门同名的部门会失败。"""
        with pytest.raises(ValueError, match="已存在"):
            self.registry.register_department(
                department_id="marketing",
                name="市场部",
                description="测试",
                responsibility="测试",
            )

    def test_update_department(self):
        """测试更新部门。"""
        self.registry.register_department(
            department_id="update_test",
            name="原名称",
            description="原描述",
            responsibility="原职责",
        )

        updated = self.registry.update_department(
            "update_test",
            name="新名称",
            description="新描述",
        )

        assert updated is not None
        assert updated.name == "新名称"
        assert updated.description == "新描述"
        assert updated.responsibility == "原职责"  # 未更新的字段保持不变

    def test_update_nonexistent_department(self):
        """测试更新不存在的部门返回 None。"""
        result = self.registry.update_department("nonexistent", name="新名称")
        assert result is None

    def test_unregister_custom_department(self):
        """测试注销自定义部门。"""
        self.registry.register_department(
            department_id="to_delete",
            name="待删除部门",
            description="测试",
            responsibility="测试",
        )

        success = self.registry.unregister_department("to_delete")
        assert success is True
        assert self.registry.get_department("to_delete") is None

    def test_unregister_builtin_department_fails(self):
        """测试注销内置部门会失败。"""
        success = self.registry.unregister_department("marketing")
        assert success is False

        # 内置部门仍然存在
        assert self.registry.get_department("marketing") is not None

    def test_get_department(self):
        """测试获取单个部门。"""
        self.registry.register_department(
            department_id="get_test",
            name="获取测试",
            description="测试",
            responsibility="测试",
        )

        dept = self.registry.get_department("get_test")
        assert dept is not None
        assert dept.department_id == "get_test"

        # 获取不存在的部门
        nonexistent = self.registry.get_department("nonexistent")
        assert nonexistent is None

    def test_is_builtin(self):
        """测试判断是否为内置部门。"""
        assert self.registry.is_builtin("marketing") is True
        assert self.registry.is_builtin("ceo") is True
        assert self.registry.is_builtin("hr") is True

        self.registry.register_department(
            department_id="custom_test",
            name="自定义",
            description="测试",
            responsibility="测试",
        )
        assert self.registry.is_builtin("custom_test") is False

    def test_is_custom(self):
        """测试判断是否为自定义部门。"""
        assert self.registry.is_custom("marketing") is False

        self.registry.register_department(
            department_id="custom_check",
            name="自定义检查",
            description="测试",
            responsibility="测试",
        )
        assert self.registry.is_custom("custom_check") is True

    def test_get_statistics(self):
        """测试获取统计信息。"""
        self.registry.register_department(
            department_id="stats_test1",
            name="统计测试1",
            description="测试",
            responsibility="测试",
        )
        self.registry.register_department(
            department_id="stats_test2",
            name="统计测试2",
            description="测试",
            responsibility="测试",
        )

        stats = self.registry.get_statistics()

        assert stats["total_count"] == len(BUILTIN_DEPARTMENT_IDS) + 2
        assert stats["builtin_count"] == len(BUILTIN_DEPARTMENT_IDS)
        assert stats["custom_count"] == 2
        assert "stats_test1" in stats["custom_departments"]
        assert "stats_test2" in stats["custom_departments"]

    def test_export_config(self):
        """测试导出配置。"""
        self.registry.register_department(
            department_id="export_test",
            name="导出测试",
            description="测试描述",
            responsibility="测试职责",
            skills=[{"skill_id": "s1", "name": "技能1", "level": 1}],
            routing_rules=[{"keywords": ["导出"], "weight": 1.0}],
            tags=["导出", "测试"],
        )

        config = self.registry.export_config()

        assert config["builtin_count"] == len(BUILTIN_DEPARTMENT_IDS)
        assert len(config["custom_departments"]) >= 1

        # 找到我们添加的部门
        export_dept = next(
            (d for d in config["custom_departments"] if d["department_id"] == "export_test"),
            None,
        )
        assert export_dept is not None
        assert export_dept["name"] == "导出测试"
        assert len(export_dept["skills"]) == 1

    def test_import_config(self):
        """测试导入配置。"""
        config = {
            "custom_departments": [
                {
                    "department_id": "import_dept1",
                    "name": "导入部门1",
                    "description": "导入描述1",
                    "responsibility": "导入职责1",
                    "skills": [{"skill_id": "i1", "name": "导入技能1", "level": 2}],
                    "routing_rules": [{"keywords": ["导入"], "weight": 1.0}],
                    "leader": {"role": "导入负责人", "skills": ["导入技能"]},
                    "executor": {"role": "导入执行者", "skills": ["导入技能"]},
                    "parent_id": None,
                    "price_tier": "专业",
                    "tags": ["导入"],
                },
                {
                    "department_id": "import_dept2",
                    "name": "导入部门2",
                    "description": "导入描述2",
                    "responsibility": "导入职责2",
                    "skills": [],
                    "routing_rules": [],
                    "parent_id": None,
                    "price_tier": "免费",
                    "tags": [],
                },
            ]
        }

        imported = self.registry.import_config(config)
        assert imported == 2

        # 验证导入成功
        dept1 = self.registry.get_department("import_dept1")
        assert dept1 is not None
        assert dept1.name == "导入部门1"

        dept2 = self.registry.get_department("import_dept2")
        assert dept2 is not None
        assert dept2.description == "导入描述2"

    def test_import_duplicate_skipped(self):
        """测试导入重复部门会被跳过。"""
        self.registry.register_department(
            department_id="dup_import",
            name="原始部门",
            description="原始",
            responsibility="原始",
        )

        config = {
            "custom_departments": [
                {
                    "department_id": "dup_import",
                    "name": "导入重复",
                    "description": "导入",
                    "responsibility": "导入",
                    "skills": [],
                    "routing_rules": [],
                },
            ]
        }

        imported = self.registry.import_config(config)
        assert imported == 0  # 应该跳过重复的

        # 原有部门名称不变
        dept = self.registry.get_department("dup_import")
        assert dept.name == "原始部门"


class TestGlobalRegistry:
    """测试全局注册表单例。"""

    def setup_method(self):
        reset_department_registry()

    def teardown_method(self):
        reset_department_registry()

    def test_get_department_registry(self):
        """测试获取全局单例。"""
        registry1 = get_department_registry()
        registry2 = get_department_registry()
        assert registry1 is registry2  # 应该是同一个实例

    def test_reset_department_registry(self):
        """测试重置全局注册表。"""
        registry1 = get_department_registry()
        registry1.register_department(
            department_id="before_reset",
            name="重置前",
            description="测试",
            responsibility="测试",
        )

        reset_department_registry()

        registry2 = get_department_registry()
        assert registry2 is not registry1  # 应该是新实例
        assert registry2.get_department("before_reset") is None  # 数据应该被清除


@pytest.mark.parametrize("dept_id", list(BUILTIN_DEPARTMENT_IDS))
def test_all_builtin_departments_accessible(dept_id):
    """参数化测试：所有内置部门都应该可以访问。"""
    registry = DepartmentRegistry()
    dept = registry.get_department(dept_id)
    assert dept is not None
    assert dept.department_id == dept_id


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
