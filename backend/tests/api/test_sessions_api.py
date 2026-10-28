import pytest
from httpx import AsyncClient

ACTIVITY_ID = "a3000000-0000-0000-0000-000000000003"


@pytest.mark.asyncio
async def test_create_session_consent_required(client: AsyncClient):
    payload = {
        "activity_id": ACTIVITY_ID,
        "language_code": "kn-IN",
        "consent_acknowledged": False,
    }
    response = await client.post("/api/v1/sessions", json=payload)
    assert response.status_code == 403
    data = response.json()
    assert "consent" in data["error"]["message"].lower()


@pytest.mark.asyncio
async def test_create_and_get_session_lifecycle(client: AsyncClient):
    payload = {
        "activity_id": ACTIVITY_ID,
        "language_code": "kn-IN",
        "consent_acknowledged": True,
    }
    # 1. Create session
    create_res = await client.post("/api/v1/sessions", json=payload)
    assert create_res.status_code == 201
    created_data = create_res.json()
    session_id = created_data["session_id"]
    token = created_data["session_token"]

    assert session_id is not None
    assert token is not None
    assert created_data["status"] == "active"
    assert created_data["activity"]["id"] == ACTIVITY_ID

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get session without token -> 401
    no_auth_res = await client.get(f"/api/v1/sessions/{session_id}")
    assert no_auth_res.status_code == 401

    # 3. Get session with wrong token -> 401
    bad_auth_res = await client.get(
        f"/api/v1/sessions/{session_id}",
        headers={"Authorization": "Bearer wrong-token-xyz"},
    )
    assert bad_auth_res.status_code == 401

    # 4. Get session with valid token -> 200
    valid_res = await client.get(f"/api/v1/sessions/{session_id}", headers=headers)
    assert valid_res.status_code == 200
    data = valid_res.json()
    assert data["id"] == session_id
    assert data["status"] == "active"
    assert data["consent_acknowledged"] is True

    # 5. Complete session -> 200
    complete_res = await client.post(f"/api/v1/sessions/{session_id}/complete", headers=headers)
    assert complete_res.status_code == 200
    comp_data = complete_res.json()
    assert comp_data["status"] == "completed"

    # 6. Delete session -> 200
    del_res = await client.delete(f"/api/v1/sessions/{session_id}", headers=headers)
    assert del_res.status_code == 200

    # 7. Verify session is gone -> 404
    after_del_res = await client.get(f"/api/v1/sessions/{session_id}", headers=headers)
    assert after_del_res.status_code == 404
