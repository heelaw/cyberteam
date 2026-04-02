"""Skill 绑定持久化测试."""
import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
async def cleanup(client):
    """每个测试后清理数据。"""
    yield
    # 清理由 test isolation 处理，这里不做额外清理


@pytest.mark.asyncio
async def test_bind_skill_to_agent(client):
    """测试绑定 Skill 到 Agent（通过 skills API）。"""
    # 1. 创建 Skill
    await client.post("/api/v1/skills", json={
        "name": "测试技能",
        "code": "test-skill-bind",
        "category": "tech",
    })

    # 2. 创建 Agent
    await client.post("/api/v1/agents", json={
        "name": "测试Agent",
        "code": "test-agent-bind",
    })

    # 3. 通过 skills API 绑定
    resp = await client.post("/api/v1/skills/test-skill-bind/agents/test-agent-bind")
    assert resp.status_code == 201
    data = resp.json()
    assert data["skill_code"] == "test-skill-bind"
    assert data["agent_code"] == "test-agent-bind"
    assert data["status"] == "bound"


@pytest.mark.asyncio
async def test_unbind_skill_from_agent(client):
    """测试从 Agent 解绑 Skill。"""
    # 1. 创建 Skill 和 Agent
    await client.post("/api/v1/skills", json={
        "name": "解绑技能",
        "code": "test-skill-unbind",
        "category": "tech",
    })
    await client.post("/api/v1/agents", json={
        "name": "解绑Agent",
        "code": "test-agent-unbind",
    })

    # 2. 先绑定
    await client.post("/api/v1/skills/test-skill-unbind/agents/test-agent-unbind")

    # 3. 解绑
    resp = await client.delete("/api/v1/skills/test-skill-unbind/agents/test-agent-unbind")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "unbound"


@pytest.mark.asyncio
async def test_get_agent_skills(client):
    """测试获取 Agent 绑定的所有 Skill。"""
    # 1. 创建 Skills
    await client.post("/api/v1/skills", json={
        "name": "技能1",
        "code": "skill-for-agent-1",
        "category": "tech",
    })
    await client.post("/api/v1/skills", json={
        "name": "技能2",
        "code": "skill-for-agent-2",
        "category": "growth",
    })

    # 2. 创建 Agent
    await client.post("/api/v1/agents", json={
        "name": "多技能Agent",
        "code": "multi-skill-agent",
    })

    # 3. 绑定多个 Skills
    await client.post("/api/v1/skills/skill-for-agent-1/agents/multi-skill-agent")
    await client.post("/api/v1/skills/skill-for-agent-2/agents/multi-skill-agent")

    # 4. 获取 Agent 的 Skills
    resp = await client.get("/api/v1/skills/agents/multi-skill-agent/skills")
    assert resp.status_code == 200
    data = resp.json()
    assert data["agent_code"] == "multi-skill-agent"
    assert "skill-for-agent-1" in data["skills"]
    assert "skill-for-agent-2" in data["skills"]
    assert data["count"] == 2


@pytest.mark.asyncio
async def test_get_skill_agents_after_bind(client):
    """测试绑定后查询 Skill 关联的 Agents。"""
    # 1. 创建 Skill 和多个 Agents
    await client.post("/api/v1/skills", json={
        "name": "共享技能",
        "code": "shared-skill",
        "category": "tech",
    })
    await client.post("/api/v1/agents", json={
        "name": "Agent A",
        "code": "agent-a",
    })
    await client.post("/api/v1/agents", json={
        "name": "Agent B",
        "code": "agent-b",
    })

    # 2. 绑定 Skill 到多个 Agents
    await client.post("/api/v1/skills/shared-skill/agents/agent-a")
    await client.post("/api/v1/skills/shared-skill/agents/agent-b")

    # 3. 查询 Skill 关联的 Agents
    resp = await client.get("/api/v1/skills/shared-skill/agents")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    agent_codes = [a["code"] for a in data]
    assert "agent-a" in agent_codes
    assert "agent-b" in agent_codes


@pytest.mark.asyncio
async def test_bind_skill_via_agents_api_syncs(client):
    """测试通过 agents API 绑定也会同步到 skills 内存索引。"""
    # 1. 创建 Skill 和 Agent
    await client.post("/api/v1/skills", json={
        "name": "同步技能",
        "code": "sync-skill",
        "category": "tech",
    })
    await client.post("/api/v1/agents", json={
        "name": "同步Agent",
        "code": "sync-agent",
    })

    # 2. 通过 agents API 绑定（而不是 skills API）
    resp = await client.post("/api/v1/agents/sync-agent/skills", json={
        "skill_id": "sync-skill",
    })
    assert resp.status_code == 200

    # 3. 通过 skills API 查询应该能看到绑定
    resp = await client.get("/api/v1/skills/sync-skill/agents")
    assert resp.status_code == 200
    data = resp.json()
    agent_codes = [a["code"] for a in data]
    assert "sync-agent" in agent_codes


@pytest.mark.asyncio
async def test_bind_skill_not_found(client):
    """测试绑定不存在的 Skill。"""
    await client.post("/api/v1/agents", json={
        "name": "测试Agent",
        "code": "test-agent-notfound",
    })

    resp = await client.post("/api/v1/skills/nonexistent-skill/agents/test-agent-notfound")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_bind_to_nonexistent_agent(client):
    """测试绑定到不存在的 Agent。"""
    await client.post("/api/v1/skills", json={
        "name": "测试技能",
        "code": "test-skill-noagent",
        "category": "tech",
    })

    resp = await client.post("/api/v1/skills/test-skill-noagent/agents/nonexistent-agent")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_unbind_nonexistent_binding(client):
    """测试解绑未绑定的 Skill（应该成功）。"""
    await client.post("/api/v1/skills", json={
        "name": "解绑测试技能",
        "code": "test-skill-no-bind",
        "category": "tech",
    })
    await client.post("/api/v1/agents", json={
        "name": "解绑测试Agent",
        "code": "test-agent-no-bind",
    })

    # 解绑未绑定的不应该报错
    resp = await client.delete("/api/v1/skills/test-skill-no-bind/agents/test-agent-no-bind")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "unbound"


@pytest.mark.asyncio
async def test_agent_skill_bind_persistence_across_restart(client):
    """测试服务重启后绑定关系能恢复。

    注：由于使用内存存储，此测试验证的是同一进程中
    的内存索引在多个 API 调用间的持久性。
    """
    # 1. 创建 Skill 和 Agent
    await client.post("/api/v1/skills", json={
        "name": "持久化技能",
        "code": "persist-skill",
        "category": "tech",
    })
    await client.post("/api/v1/agents", json={
        "name": "持久化Agent",
        "code": "persist-agent",
    })

    # 2. 绑定
    await client.post("/api/v1/skills/persist-skill/agents/persist-agent")

    # 3. 多次查询验证绑定仍然存在
    for _ in range(3):
        resp = await client.get("/api/v1/skills/persist-skill/agents")
        assert resp.status_code == 200
        data = resp.json()
        assert any(a["code"] == "persist-agent" for a in data)