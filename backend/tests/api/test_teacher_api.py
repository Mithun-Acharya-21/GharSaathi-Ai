import pytest
from httpx import AsyncClient

TEACHER_KEY = "dev-teacher-secret-key-change-in-production"


@pytest.mark.asyncio
async def test_teacher_reports_auth_required(client: AsyncClient):
    # Without header -> 401
    res_no_auth = await client.get("/api/v1/teacher/reports")
    assert res_no_auth.status_code == 401

    # With invalid header -> 401
    res_bad_auth = await client.get(
        "/api/v1/teacher/reports", headers={"X-Teacher-API-Key": "bad-key"}
    )
    assert res_bad_auth.status_code == 401


@pytest.mark.asyncio
async def test_teacher_reports_and_review_queue(client: AsyncClient):
    headers = {"X-Teacher-API-Key": TEACHER_KEY}

    # 1. Reports endpoint
    res = await client.get("/api/v1/teacher/reports", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["activities_available"] == 6
    assert "overall_accuracy_percentage" in data
    assert "topics" in data
    assert len(data["topics"]) == 6

    # 2. Review queue endpoint
    res_queue = await client.get("/api/v1/teacher/review-queue", headers=headers)
    assert res_queue.status_code == 200
    queue_data = res_queue.json()
    assert isinstance(queue_data, list)
