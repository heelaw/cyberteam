"""Company API 测试."""
import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_company(client):
    resp = await client.post("/api/v1/companies", json={"name": "测试公司"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "测试公司"
    assert data["status"] == "active"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_company_with_description(client):
    resp = await client.post("/api/v1/companies", json={
        "name": "科技公司",
        "description": "一家AI公司",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["description"] == "一家AI公司"


@pytest.mark.asyncio
async def test_list_companies_empty(client):
    resp = await client.get("/api/v1/companies")
    assert resp.status_code == 200
    data = resp.json()
    if isinstance(data, dict):
        assert "items" in data or "total" in data
    else:
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_list_companies_pagination(client):
    for i in range(5):
        await client.post("/api/v1/companies", json={"name": f"公司{i}"})
    resp = await client.get("/api/v1/companies?skip=0&limit=2")
    assert resp.status_code == 200
    data = resp.json()
    if isinstance(data, dict):
        items = data.get("items", data)
        assert len(items) <= 2
    else:
        assert len(data) <= 2


@pytest.mark.asyncio
async def test_list_companies_search(client):
    await client.post("/api/v1/companies", json={"name": "百度科技"})
    await client.post("/api/v1/companies", json={"name": "阿里巴巴"})
    resp = await client.get("/api/v1/companies?q=百度")
    assert resp.status_code == 200
    data = resp.json()
    if isinstance(data, dict):
        data = data.get("items", data)
    assert any("百度" in c["name"] for c in data)


@pytest.mark.asyncio
async def test_get_company(client):
    create_resp = await client.post("/api/v1/companies", json={"name": "腾讯"})
    company_id = create_resp.json()["id"]
    resp = await client.get(f"/api/v1/companies/{company_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "腾讯"


@pytest.mark.asyncio
async def test_get_company_not_found(client):
    resp = await client.get("/api/v1/companies/nonexistent-id")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_company(client):
    create_resp = await client.post("/api/v1/companies", json={"name": "字节"})
    company_id = create_resp.json()["id"]
    resp = await client.put(f"/api/v1/companies/{company_id}", json={"name": "字节跳动"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "字节跳动"


@pytest.mark.asyncio
async def test_update_company_not_found(client):
    resp = await client.put("/api/v1/companies/fake-id", json={"name": "测试"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_company_soft_delete(client):
    create_resp = await client.post("/api/v1/companies", json={"name": "删除公司"})
    company_id = create_resp.json()["id"]
    resp = await client.delete(f"/api/v1/companies/{company_id}")
    assert resp.status_code in (200, 204)
    # 软删除后列表中不应出现
    get_resp = await client.get("/api/v1/companies")
    data = get_resp.json()
    if isinstance(data, dict):
        data = data.get("items", data)
    assert all(c["id"] != company_id for c in data)


@pytest.mark.asyncio
async def test_delete_company_not_found(client):
    resp = await client.delete("/api/v1/companies/fake-id")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_company_departments(client):
    create_resp = await client.post("/api/v1/companies", json={"name": "部门公司"})
    company_id = create_resp.json()["id"]
    resp = await client.get(f"/api/v1/companies/{company_id}/departments")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_company_agents(client):
    create_resp = await client.post("/api/v1/companies", json={"name": "Agent公司"})
    company_id = create_resp.json()["id"]
    resp = await client.get(f"/api/v1/companies/{company_id}/agents")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_company_stats(client):
    create_resp = await client.post("/api/v1/companies", json={"name": "统计公司"})
    company_id = create_resp.json()["id"]
    resp = await client.get(f"/api/v1/companies/{company_id}/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "department_count" in data
    assert "agent_count" in data
