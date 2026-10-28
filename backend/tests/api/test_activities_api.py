import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_grades(client: AsyncClient):
    response = await client.get("/api/v1/grades")
    assert response.status_code == 200
    data = response.json()
    assert "grades" in data
    assert len(data["grades"]) == 6
    grade_nums = [g["grade"] for g in data["grades"]]
    assert grade_nums == [1, 2, 3, 4, 5, 6]


@pytest.mark.asyncio
async def test_list_activities_all(client: AsyncClient):
    response = await client.get("/api/v1/activities")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 6
    assert len(data["activities"]) == 6


@pytest.mark.asyncio
async def test_list_activities_by_grade(client: AsyncClient):
    # Grade 3 vertical slice
    response = await client.get("/api/v1/activities?grade=3")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    act = data["activities"][0]
    assert act["grade"] == 3
    assert "Multiplication" in act["topic"]


@pytest.mark.asyncio
async def test_get_activity_detail_protects_answer_key(client: AsyncClient):
    act_id = "a3000000-0000-0000-0000-000000000003"
    response = await client.get(f"/api/v1/activities/{act_id}")
    assert response.status_code == 200
    data = response.json()

    # Verify public fields are present
    assert data["id"] == act_id
    assert data["grade"] == 3
    assert "parent_instructions" in data
    assert "child_prompt" in data
    assert "hints" in data
    assert len(data["hints"]) >= 2
    assert "materials" in data

    # Critical security requirement: private evaluator configuration and expected values must NEVER be exposed
    assert "evaluator_config" not in data
    assert "expected_value" not in data


@pytest.mark.asyncio
async def test_invalid_grade_filter(client: AsyncClient):
    response = await client.get("/api/v1/activities?grade=99")
    assert response.status_code in (400, 422)
