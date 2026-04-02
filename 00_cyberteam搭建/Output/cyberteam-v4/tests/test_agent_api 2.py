"""Agent API 测试."""
import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_agent(client):
    resp = await client.post("/api/v1/agents", json={
        "name": "运营Agent",
        "code": "ops-agent",
        "agent_type": "custom",
        "company_id": "company-1",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["code"] == "ops-agent"
    assert data["name"] == "运营Agent"
    assert data["agent_type"] == "custom"


@pytest.mark.asyncio
async def test_create_agent_with_skills(client):
    # 先创建 skill
    await client.post("/api/v1/skills", json={"name": "增长技能", "code": "growth-skill"})
    resp = await client.post("/api/v1/agents", json={
        "name": "增长Agent",
        "code": "growth-agent",
        "skills": ["growth-skill"],
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "growth-skill" in data["skills"]


@pytest.mark.asyncio
async def test_list_agents(client):
    await client.post("/api/v1/agents", json={"name": "Agent-A", "code": "agent-a"})
    resp = await client.get("/api/v1/agents")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_list_agents_filter_company(client):
    await client.post("/api/v1/agents", json={"name": "A公司Agent", "code": "a-agent", "company_id": "c-a"})
    await client.post("/api/v1/agents", json={"name": "B公司Agent", "code": "b-agent", "company_id": "c-b"})
    resp = await client.get("/api/v1/agents?company_id=c-a")
    data = resp.json()
    assert all(a.get("company_id") == "c-a" for a in data)


@pytest.mark.asyncio
async def test_get_agent(client):
    await client.post("/api/v1/agents", json={"name": "详情Agent", "code": "detail-agent"})
    resp = await client.get("/api/v1/agents/detail-agent")
    assert resp.status_code == 200
    assert resp.json()["code"] == "detail-agent"


@pytest.mark.asyncio
async def test_get_agent_not_found(client):
    resp = await client.get("/api/v1/agents/fake-agent")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_agent(client):
    await client.post("/api/v1/agents", json={"name": "旧名称", "code": "update-agent"})
    resp = await client.put("/api/v1/agents/update-agent", json={"name": "新名称"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "新名称"


@pytest.mark.asyncio
async def test_delete_agent(client):
    await client.post("/api/v1/agents", json={"name": "删除Agent", "code": "delete-agent"})
    resp = await client.delete("/api/v1/agents/delete-agent")
    assert resp.status_code == 200
    get_resp = await client.get("/api/v1/agents/delete-agent")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_bind_skill_to_agent(client):
    await client.post("/api/v1/skills", json={"name": "绑定技能", "code": "bind-skill"})
    await client.post("/api/v1/agents", json={"name": "绑定Agent", "code": "bind-agent"})
    resp = await client.post("/api/v1/agents/bind-agent/skills", json={"skill_id": "bind-skill"})
    assert resp.status_code == 200
    data = resp.json()
    assert "bind-skill" in data["skills"]


@pytest.mark.asyncio
async def test_unbind_skill_from_agent(client):
    await client.post("/api/v1/skills", json={"name": "解绑技能", "code": "unbind-skill"})
    await client.post("/api/v1/agents", json={
        "name": "解绑Agent",
        "code": "unbind-agent",
        "skills": ["unbind-skill"],
    })
    resp = await client.delete("/api/v1/agents/unbind-agent/skills/unbind-skill")
    assert resp.status_code == 200
    data = resp.json()
    assert "unbind-skill" not in data["skills"]


@pytest.mark.asyncio
async def test_agent_skill_count(client):
    import uuid
    uid = uuid.uuid4().hex[:8]
    await client.post("/api/v1/skills", json={"name": f"计数技能A-{uid}", "code": f"ca-{uid}"})
    await client.post("/api/v1/skills", json={"name": f"计数技能B-{uid}", "code": f"cb-{uid}"})
    resp = await client.post("/api/v1/agents", json={
        "name": f"计数Agent-{uid}",
        "code": f"cagent-{uid}",
        "skills": [f"ca-{uid}", f"cb-{uid}"],
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["skill_count"] == 2


@pytest.mark.asyncio
async def test_agent_code_pattern_validation(client):
    resp = await client.post("/api/v1/agents", json={
        "name": "非法代码",
        "code": "Invalid Code!",
    })
    assert resp.status_code in [400, 422]


@pytest.mark.asyncio
async def test_agent_execution_history(client):
    import uuid
    uid = uuid.uuid4().hex[:8]
    await client.post("/api/v1/agents", json={"name": f"历史Agent-{uid}", "code": f"hist-{uid}"})
    resp = await client.get(f"/api/v1/agents/hist-{uid}/executions")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_list_agents_filter_skills(client):
    import uuid
    uid = uuid.uuid4().hex[:8]
    await client.post("/api/v1/skills", json={"name": f"筛选技能-{uid}", "code": f"fs-{uid}"})
    await client.post("/api/v1/agents", json={
        "name": f"有技能Agent-{uid}",
        "code": f"hskill-{uid}",
        "skills": [f"fs-{uid}"],
    })
    await client.post("/api/v1/agents", json={"name": f"无技能Agent-{uid}", "code": f"nsk-{uid}"})
    resp = await client.get(f"/api/v1/agents?skill_ids=fs-{uid}")
    data = resp.json()
    # 过滤后所有agent都应该有该skill
    assert len(data) >= 1
    assert all(f"fs-{uid}" in a.get("skills", []) for a in data)


@pytest.mark.asyncio
async def test_duplicate_agent_code(client):
    import uuid
    uid = uuid.uuid4().hex[:8]
    await client.post("/api/v1/agents", json={"name": f"Original-{uid}", "code": f"dup-{uid}"})
    resp = await client.post("/api/v1/agents", json={"name": f"Duplicate-{uid}", "code": f"dup-{uid}"})
    assert resp.status_code in [400, 409]
