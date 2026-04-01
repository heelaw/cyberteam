"""Skill API 测试."""
import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_skill(client):
    resp = await client.post("/api/v1/skills", json={
        "name": "用户增长",
        "code": "user-growth",
        "category": "growth",
        "difficulty": "medium",
        "trigger_keywords": ["增长", "用户"],
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["code"] == "user-growth"
    assert data["name"] == "用户增长"
    assert data["category"] == "growth"


@pytest.mark.asyncio
async def test_list_skills(client):
    await client.post("/api/v1/skills", json={"name": "技能A", "code": "skill-a", "category": "tech"})
    await client.post("/api/v1/skills", json={"name": "技能B", "code": "skill-b", "category": "growth"})
    resp = await client.get("/api/v1/skills")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_list_skills_filter_category(client):
    await client.post("/api/v1/skills", json={"name": "技术技能", "code": "tech-skill", "category": "tech"})
    await client.post("/api/v1/skills", json={"name": "运营技能", "code": "growth-skill", "category": "growth"})
    resp = await client.get("/api/v1/skills?category=tech")
    data = resp.json()
    assert all(s["category"] == "tech" for s in data)


@pytest.mark.asyncio
async def test_list_skills_filter_difficulty(client):
    await client.post("/api/v1/skills", json={"name": "困难技能", "code": "hard-skill", "difficulty": "hard"})
    await client.post("/api/v1/skills", json={"name": "简单技能", "code": "easy-skill", "difficulty": "easy"})
    resp = await client.get("/api/v1/skills?difficulty=hard")
    data = resp.json()
    assert all(s["difficulty"] == "hard" for s in data)


@pytest.mark.asyncio
async def test_get_skill(client):
    await client.post("/api/v1/skills", json={"name": "详情技能", "code": "detail-skill"})
    resp = await client.get("/api/v1/skills/detail-skill")
    assert resp.status_code == 200
    assert resp.json()["code"] == "detail-skill"


@pytest.mark.asyncio
async def test_get_skill_not_found(client):
    resp = await client.get("/api/v1/skills/nonexistent")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_skill(client):
    await client.post("/api/v1/skills", json={"name": "旧名称", "code": "update-skill"})
    resp = await client.put("/api/v1/skills/update-skill", json={"name": "新名称"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "新名称"


@pytest.mark.asyncio
async def test_delete_skill(client):
    await client.post("/api/v1/skills", json={"name": "删除技能", "code": "delete-skill"})
    resp = await client.delete("/api/v1/skills/delete-skill")
    assert resp.status_code == 200
    get_resp = await client.get("/api/v1/skills/delete-skill")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_skill_agent_count(client):
    # 创建skill
    await client.post("/api/v1/skills", json={"name": "计数技能", "code": "count-skill"})
    # 创建agent并绑定
    await client.post("/api/v1/agents", json={
        "name": "计数Agent",
        "code": "count-agent",
        "skills": ["count-skill"],
    })
    resp = await client.get("/api/v1/skills/count-skill")
    assert resp.status_code == 200
    assert resp.json()["agent_count"] >= 1


@pytest.mark.asyncio
async def test_get_skill_categories(client):
    await client.post("/api/v1/skills", json={"name": "分类A", "code": "cat-a", "category": "tech"})
    await client.post("/api/v1/skills", json={"name": "分类B", "code": "cat-b", "category": "growth"})
    resp = await client.get("/api/v1/skills/categories")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_execute_skill(client):
    await client.post("/api/v1/skills", json={"name": "执行技能", "code": "exec-skill"})
    resp = await client.post("/api/v1/skills/exec-skill/execute", json={
        "input": "测试输入",
        "context": {"user_id": "123"},
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"
    assert "execution_id" in data


@pytest.mark.asyncio
async def test_execute_skill_not_found(client):
    resp = await client.post("/api/v1/skills/fake-skill/execute", json={"input": "test"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_skill_code_pattern_validation(client):
    """skill code 必须符合 [a-z0-9_-]+ 格式"""
    resp = await client.post("/api/v1/skills", json={
        "name": "错误代码",
        "code": "Invalid Code!",  # 非法字符
    })
    # Pydantic 应该在请求层面拒绝
    assert resp.status_code in [400, 422]


@pytest.mark.asyncio
async def test_skill_trigger_keywords(client):
    resp = await client.post("/api/v1/skills", json={
        "name": "关键词技能",
        "code": "keyword-skill",
        "trigger_keywords": ["营销", "推广", "增长"],
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "营销" in data["trigger_keywords"]
    assert "增长" in data["trigger_keywords"]
