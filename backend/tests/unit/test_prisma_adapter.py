import httpx
import pytest

from app.core.config import Settings
from app.core.errors import (
    AppException,
    RateLimitException,
    ServiceUnavailableException,
    UpstreamServiceException,
)
from app.integrations.gnani_prisma import GnaniPrismaClient


@pytest.mark.asyncio
async def test_prisma_missing_api_key():
    settings = Settings(GNANI_API_KEY="")
    async with httpx.AsyncClient() as http_client:
        client = GnaniPrismaClient(http_client=http_client, settings=settings)
        with pytest.raises(ServiceUnavailableException) as exc:
            await client.transcribe(b"fake audio", "test.wav", "audio/wav")
        assert "GNANI_API_KEY" in str(exc.value.message)


@pytest.mark.asyncio
async def test_prisma_success():
    def mock_handler(request: httpx.Request):
        assert request.headers.get("X-API-Key-ID") == "dummy-key"
        return httpx.Response(
            200,
            json={
                "success": True,
                "request_id": "req-999",
                "transcript": "12",
                "model": "gnani-prisma-v2.5",
            },
        )

    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        settings = Settings(GNANI_API_KEY="dummy-key")
        client = GnaniPrismaClient(http_client=http_client, settings=settings)
        result = await client.transcribe(b"test audio bytes", "audio.wav", "audio/wav", "kn-IN")
        assert result.transcript == "12"
        assert result.request_id == "req-999"
        assert result.model == "gnani-prisma-v2.5"


@pytest.mark.asyncio
async def test_prisma_upstream_errors():
    # 400 Bad Request (invalid audio)
    transport_400 = httpx.MockTransport(
        lambda req: httpx.Response(400, json={"error": "bad audio"})
    )
    async with httpx.AsyncClient(transport=transport_400) as http_client:
        settings = Settings(GNANI_API_KEY="dummy-key")
        client = GnaniPrismaClient(http_client=http_client, settings=settings)
        with pytest.raises(AppException) as exc:
            await client.transcribe(b"bad", "audio.wav", "audio/wav")
        assert exc.value.code == "INVALID_AUDIO_PAYLOAD"

    # 403 Forbidden
    transport_403 = httpx.MockTransport(
        lambda req: httpx.Response(403, json={"error": "forbidden"})
    )
    async with httpx.AsyncClient(transport=transport_403) as http_client:
        client = GnaniPrismaClient(http_client=http_client, settings=settings)
        with pytest.raises(UpstreamServiceException):
            await client.transcribe(b"bad", "audio.wav", "audio/wav")

    # 429 Rate Limit
    transport_429 = httpx.MockTransport(
        lambda req: httpx.Response(429, json={"error": "rate limit"})
    )
    async with httpx.AsyncClient(transport=transport_429) as http_client:
        client = GnaniPrismaClient(http_client=http_client, settings=settings)
        with pytest.raises(RateLimitException):
            await client.transcribe(b"bad", "audio.wav", "audio/wav")
