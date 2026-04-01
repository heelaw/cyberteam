"""Teams API 测试."""
import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_team(client):
    resp = await client.post("/api/v1/teams", json={"name": "技术团队"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "技术团队"
    assert data["member_count"] == 0
    assert "id" in data


@pytest.mark.asyncio
async def test_create_team_with_members(client):
    resp = await client.post("/api/v1/teams", json={
        "name": "产品团队",
        "members": ["agent-1", "agent-2"],
    })
    assert resp.status_code == 201
    data = resp.json()
    assert len(data["members"]) == 2
    assert data["member_count"] == 2


@pytest.mark.asyncio
async def test_list_teams_empty(client):
    resp = await client.get("/api/v1/teams")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_list_teams_filter_by_company(client):
    await client.post("/api/v1/teams", json={"name": "A公司团队", "company_id": "company-a"})
    await client.post("/api/v1/teams", json={"name": "B公司团队", "company_id": "company-b"})
    resp = await client.get("/api/v1/teams?company_id=company-a")
    data = resp.json()
    assert all(t["company_id"] == "company-a" for t in data)


@pytest.mark.asyncio
async def test_get_team(client):
    create_resp = await client.post("/api/v1/teams", json={"name": "查询团队"})
    team_id = create_resp.json()["id"]
    resp = await client.get(f"/api/v1/teams/{team_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "查询团队"


@pytest.mark.asyncio
async def test_get_team_not_found(client):
    resp = await client.get("/api/v1/teams/fake-id")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_team(client):
    create_resp = await client.post("/api/v1/teams", json={"name": "旧名称"})
    team_id = create_resp.json()["id"]
    resp = await client.put(f"/api/v1/teams/{team_id}", json={"name": "新名称"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "新名称"


@pytest.mark.asyncio
async def test_delete_team(client):
    create_resp = await client.post("/api/v1/teams", json={"name": "删除团队"})
    team_id = create_resp.json()["id"]
    resp = await client.delete(f"/api/v1/teams/{team_id}")
    assert resp.status_code == 204
    get_resp = await client.get(f"/api/v1/teams/{team_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_add_member(client):
    create_resp = await client.post("/api/v1/teams", json={"name": "成员团队"})
    team_id = create_resp.json()["id"]
    resp = await client.post(f"/api/v1/teams/{team_id}/members", json={"member_id": "agent-x"})
    assert resp.status_code == 200
    assert "agent-x" in resp.json()["members"]


@pytest.mark.asyncio
async def test_add_duplicate_member(client):
    create_resp = await client.post("/api/v1/teams", json={"name": "重复成员团队", "members": ["agent-x"]})
    team_id = create_resp.json()["id"]
    resp = await client.post(f"/api/v1/teams/{team_id}/members", json={"member_id": "agent-x"})
    # 应该成功但不增加重复
    assert resp.status_code == 200
    assert resp.json()["members"].count("agent-x") == 1


@pytest.mark.asyncio
async def test_remove_member(client):
    create_resp = await client.post("/api/v1/teams", json={"name": "移除成员团队", "members": ["agent-y"]})
    team_id = create_resp.json()["id"]
    resp = await client.delete(f"/api/v1/teams/{team_id}/members/agent-y")
    assert resp.status_code == 200
    assert "agent-y" not in resp.json()["members"]


@pytest.mark.asyncio
async def test_remove_nonexistent_member(client):
    create_resp = await client.post("/api/v1/teams", json={"name": "无成员团队"})
    team_id = create_resp.json()["id"]
    resp = await client.delete(f"/api/v1/teams/{team_id}/members/nonexistent")
    assert resp.status_code == 200  # 应该成功（幂等）


@pytest.mark.asyncio
async def test_team_pagination(client):
    for i in range(5):
        await client.post("/api/v1/teams", json={"name": f"团队{i}"})
    resp = await client.get("/api/v1/teams?skip=2&limit=2")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
