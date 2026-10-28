import pytest
from httpx import AsyncClient

ACTIVITY_ID = "a3000000-0000-0000-0000-000000000003"


@pytest.mark.asyncio
async def test_speech_synthesize_endpoint(client: AsyncClient):
    payload = {
        "activity_id": ACTIVITY_ID,
        "text_type": "instructions",
        "language_code": "kn-IN",
    }
    response = await client.post("/api/v1/speech/synthesize", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/wav"
    assert len(response.content) > 0


@pytest.mark.asyncio
async def test_speech_synthesize_invalid_type(client: AsyncClient):
    payload = {
        "activity_id": ACTIVITY_ID,
        "text_type": "invalid_type",
    }
    response = await client.post("/api/v1/speech/synthesize", json=payload)
    assert response.status_code == 400
