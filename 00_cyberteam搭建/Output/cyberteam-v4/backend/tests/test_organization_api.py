"""组织架构 API 测试 - 验证自定义组织架构功能。

测试覆盖：
- 组织结构 CRUD 操作
- 节点管理（创建/更新/删除）
- Agent 绑定
- 节点排序
- 配置快照保存/加载
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import app
from app.api.v1.organization import reset_org_store, get_org_store
from app.models.organization import (
    OrgNodeType,
    OrgNode,
    OrgStructure,
    DEFAULT_STRUCTURE,
)


@pytest.fixture(scope="function")
def client():
    """每个测试使用独立的客户端和存储"""
    reset_org_store()
    yield TestClient(app)
    reset_org_store()


class TestGetStructure:
    """测试获取组织结构"""

    def test_get_default_structure(self, client):
        """测试获取默认公司组织结构"""
        response = client.get("/api/v1/organization/structure/default")
        assert response.status_code == 200
        data = response.json()
        assert data["company_id"] == "default"
        assert data["ceo_node"]["name"] == "CEO（总指挥）"
        assert data["ceo_node"]["node_type"] == "ceo"

    def test_get_new_company_creates_default(self, client):
        """测试获取新公司时会创建默认结构"""
        response = client.get("/api/v1/organization/structure/new_company")
        assert response.status_code == 200
        data = response.json()
        assert data["company_id"] == "new_company"
        assert data["ceo_node"]["id"] == "ceo-new_company"

    def test_get_structure_contains_layers(self, client):
        """测试组织结构包含讨论层和执行层"""
        response = client.get("/api/v1/organization/structure/default")
        assert response.status_code == 200
        data = response.json()
        assert len(data["discussion_teams"]) >= 1
        assert len(data["execution_departments"]) >= 1


class TestUpdateStructure:
    """测试更新组织结构"""

    def test_update_structure_success(self, client):
        """测试成功更新组织结构"""
        # 先获取当前结构
        response = client.get("/api/v1/organization/structure/test_company")
        structure = response.json()

        # 修改讨论层名称
        structure["discussion_teams"][0]["name"] = "策略讨论组"
        structure["updated_at"] = datetime.utcnow().isoformat()

        response = client.put(
            "/api/v1/organization/structure/test_company",
            json=structure,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["discussion_teams"][0]["name"] == "策略讨论组"

    def test_update_structure_mismatched_company_id(self, client):
        """测试 company_id 不匹配时返回错误"""
        response = client.get("/api/v1/organization/structure/test_company")
        structure = response.json()
        structure["company_id"] = "different_company"

        response = client.put(
            "/api/v1/organization/structure/test_company",
            json=structure,
        )
        assert response.status_code == 400


class TestNodeOperations:
    """测试节点操作"""

    def test_create_node_success(self, client):
        """测试成功创建节点"""
        response = client.post(
            "/api/v1/organization/nodes",
            json={
                "parent_id": "ceo-root",
                "node_type": "team",
                "name": "战略讨论组",
                "icon": "🎯",
                "color": "#3b82f6",
                "description": "负责战略规划",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "战略讨论组"
        assert data["node_type"] == "team"
        assert data["parent_id"] == "ceo-root"

    def test_create_node_invalid_parent(self, client):
        """测试父节点不存在时创建失败"""
        response = client.post(
            "/api/v1/organization/nodes",
            json={
                "parent_id": "nonexistent_parent",
                "node_type": "team",
                "name": "测试团队",
            },
        )
        assert response.status_code == 404

    def test_get_node_success(self, client):
        """测试获取节点详情"""
        # 先创建一个节点
        create_response = client.post(
            "/api/v1/organization/nodes",
            json={
                "parent_id": "ceo-root",
                "node_type": "department",
                "name": "技术部",
            },
        )
        node_id = create_response.json()["id"]

        # 获取节点
        response = client.get(f"/api/v1/organization/nodes/{node_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "技术部"

    def test_get_node_not_found(self, client):
        """测试获取不存在的节点"""
        response = client.get("/api/v1/organization/nodes/nonexistent")
        assert response.status_code == 404

    def test_update_node_success(self, client):
        """测试更新节点"""
        # 创建节点
        create_response = client.post(
            "/api/v1/organization/nodes",
            json={
                "parent_id": "ceo-root",
                "node_type": "team",
                "name": "原名称",
            },
        )
        node_id = create_response.json()["id"]

        # 更新节点
        response = client.put(
            f"/api/v1/organization/nodes/{node_id}",
            json={
                "name": "新名称",
                "icon": "✨",
                "description": "更新后的描述",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "新名称"
        assert data["icon"] == "✨"

    def test_delete_node_success(self, client):
        """测试删除节点"""
        # 创建节点
        create_response = client.post(
            "/api/v1/organization/nodes",
            json={
                "parent_id": "ceo-root",
                "node_type": "team",
                "name": "待删除团队",
            },
        )
        node_id = create_response.json()["id"]

        # 删除节点
        response = client.delete(f"/api/v1/organization/nodes/{node_id}")
        assert response.status_code == 200

        # 验证删除
        get_response = client.get(f"/api/v1/organization/nodes/{node_id}")
        assert get_response.status_code == 404

    def test_delete_ceo_fails(self, client):
        """测试不能删除 CEO 节点"""
        response = client.delete("/api/v1/organization/nodes/ceo-root")
        assert response.status_code == 400


class TestAgentBinding:
    """测试 Agent 绑定"""

    def test_bind_agents_success(self, client):
        """测试成功绑定 Agent"""
        # 创建节点
        create_response = client.post(
            "/api/v1/organization/nodes",
            json={
                "parent_id": "ceo-root",
                "node_type": "team",
                "name": "运营团队",
            },
        )
        node_id = create_response.json()["id"]

        # 绑定 Agent
        response = client.put(
            f"/api/v1/organization/nodes/{node_id}/agents",
            json={"agent_ids": ["agent-001", "agent-002"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["agent_ids"]) == 2
        assert "agent-001" in data["agent_ids"]
        assert "agent-002" in data["agent_ids"]

    def test_bind_agents_replace_existing(self, client):
        """测试绑定会替换原有 Agent"""
        # 创建节点
        create_response = client.post(
            "/api/v1/organization/nodes",
            json={
                "parent_id": "ceo-root",
                "node_type": "team",
                "name": "测试团队",
            },
        )
        node_id = create_response.json()["id"]

        # 第一次绑定
        client.put(
            f"/api/v1/organization/nodes/{node_id}/agents",
            json={"agent_ids": ["agent-001"]},
        )

        # 第二次绑定（替换）
        response = client.put(
            f"/api/v1/organization/nodes/{node_id}/agents",
            json={"agent_ids": ["agent-003"]},
        )
        data = response.json()
        assert data["agent_ids"] == ["agent-003"]

    def test_bind_agents_node_not_found(self, client):
        """测试绑定到不存在的节点"""
        response = client.put(
            "/api/v1/organization/nodes/nonexistent/agents",
            json={"agent_ids": ["agent-001"]},
        )
        assert response.status_code == 404


class TestNodeReorder:
    """测试节点排序"""

    def test_reorder_node_success(self, client):
        """测试成功调整节点顺序"""
        # 创建一个父节点（讨论层下的团队）
        parent_node = client.post(
            "/api/v1/organization/nodes",
            json={
                "parent_id": "discussion-default",
                "node_type": "team",
                "name": "父团队",
            },
        ).json()

        # 创建一个子节点（也在讨论层下）
        child_node = client.post(
            "/api/v1/organization/nodes",
            json={
                "parent_id": "discussion-default",
                "node_type": "team",
                "name": "子团队",
            },
        ).json()

        # 重新排序：将子节点移到父节点下
        response = client.post(
            "/api/v1/organization/nodes/reorder",
            json={
                "node_id": child_node["id"],
                "new_parent_id": parent_node["id"],
                "new_order": 0,
            },
        )
        assert response.status_code == 200

        # 验证子节点已被移动到父节点下
        get_response = client.get(f"/api/v1/organization/nodes/{child_node['id']}")
        assert get_response.json()["parent_id"] == parent_node["id"]


class TestConfigSnapshots:
    """测试配置快照"""

    def test_save_config_success(self, client):
        """测试保存配置快照"""
        # 获取当前结构
        structure_response = client.get("/api/v1/organization/structure/snapshot_test")
        structure = structure_response.json()

        # 保存配置
        response = client.post(
            "/api/v1/organization/configs/snapshot_test",
            json={
                "name": "我的配置v1",
                "structure": structure,
                "is_default": True,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "我的配置v1"
        assert data["is_default"] is True

    def test_list_configs(self, client):
        """测试列出配置"""
        structure_response = client.get("/api/v1/organization/structure/list_test")
        structure = structure_response.json()

        # 保存多个配置
        client.post(
            "/api/v1/organization/configs/list_test",
            json={"name": "配置1", "structure": structure},
        )
        client.post(
            "/api/v1/organization/configs/list_test",
            json={"name": "配置2", "structure": structure},
        )

        # 列出配置
        response = client.get("/api/v1/organization/configs/list_test")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_load_config_success(self, client):
        """测试加载配置"""
        structure_response = client.get("/api/v1/organization/structure/load_test")
        structure = structure_response.json()

        # 保存配置
        save_response = client.post(
            "/api/v1/organization/configs/load_test",
            json={"name": "待加载配置", "structure": structure},
        )
        config_id = save_response.json()["id"]

        # 加载配置
        response = client.get(
            f"/api/v1/organization/configs/load_test/{config_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["company_id"] == "load_test"

    def test_load_config_not_found(self, client):
        """测试加载不存在的配置"""
        response = client.get(
            "/api/v1/organization/configs/company/nonexistent_config"
        )
        assert response.status_code == 404

    def test_delete_config_success(self, client):
        """测试删除配置"""
        structure_response = client.get("/api/v1/organization/structure/delete_test")
        structure = structure_response.json()

        # 保存配置
        save_response = client.post(
            "/api/v1/organization/configs/delete_test",
            json={"name": "待删除配置", "structure": structure},
        )
        config_id = save_response.json()["id"]

        # 删除配置
        response = client.delete(
            f"/api/v1/organization/configs/delete_test/{config_id}"
        )
        assert response.status_code == 200

        # 验证删除
        load_response = client.get(
            f"/api/v1/organization/configs/delete_test/{config_id}"
        )
        assert load_response.status_code == 404


class TestNodeTypes:
    """测试节点类型"""

    def test_create_team_node(self, client):
        """测试创建团队节点"""
        response = client.post(
            "/api/v1/organization/nodes",
            json={
                "parent_id": "ceo-root",
                "node_type": "team",
                "name": "市场团队",
            },
        )
        assert response.status_code == 201
        assert response.json()["node_type"] == "team"

    def test_create_department_node(self, client):
        """测试创建部门节点"""
        response = client.post(
            "/api/v1/organization/nodes",
            json={
                "parent_id": "ceo-root",
                "node_type": "department",
                "name": "研发部门",
            },
        )
        assert response.status_code == 201
        assert response.json()["node_type"] == "department"

    def test_create_layer_nodes(self, client):
        """测试创建层级节点"""
        # 讨论层
        response = client.post(
            "/api/v1/organization/nodes",
            json={
                "parent_id": "ceo-root",
                "node_type": "discussion_layer",
                "name": "战略讨论组",
            },
        )
        assert response.status_code == 201

        # 执行层
        response = client.post(
            "/api/v1/organization/nodes",
            json={
                "parent_id": "ceo-root",
                "node_type": "execution_layer",
                "name": "执行组",
            },
        )
        assert response.status_code == 201


class TestDefaultStructure:
    """测试默认组织结构"""

    def test_default_ceo_node(self, client):
        """测试默认 CEO 节点"""
        response = client.get("/api/v1/organization/structure/default")
        data = response.json()

        assert data["ceo_node"]["id"] == "ceo-root"
        assert data["ceo_node"]["node_type"] == "ceo"
        assert data["ceo_node"]["icon"] == "👑"
        assert data["ceo_node"]["color"] == "#f59e0b"

    def test_default_discussion_layer(self, client):
        """测试默认讨论层"""
        response = client.get("/api/v1/organization/structure/default")
        data = response.json()

        assert len(data["discussion_teams"]) >= 1
        discussion = data["discussion_teams"][0]
        assert discussion["node_type"] == "discussion_layer"
        assert discussion["icon"] == "💭"

    def test_default_execution_layer(self, client):
        """测试默认执行层"""
        response = client.get("/api/v1/organization/structure/default")
        data = response.json()

        assert len(data["execution_departments"]) >= 1
        execution = data["execution_departments"][0]
        assert execution["node_type"] == "execution_layer"
        assert execution["icon"] == "⚙️"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
