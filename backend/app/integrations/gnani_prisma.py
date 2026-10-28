import logging
from typing import Protocol

import httpx
from pydantic import BaseModel

from app.core.config import Settings
from app.core.errors import (
    AppException,
    RateLimitException,
    ServiceUnavailableException,
    UpstreamServiceException,
    UpstreamTimeoutException,
)

logger = logging.getLogger(__name__)


class TranscriptionResult(BaseModel):
    transcript: str
    request_id: str | None = None
    model: str = "gnani-prisma-v2.5"
    language_code: str = "kn-IN"


class PrismaClientProtocol(Protocol):
    async def transcribe(
        self,
        audio_bytes: bytes,
        filename: str,
        content_type: str,
        language_code: str = "kn-IN",
    ) -> TranscriptionResult: ...


class GnaniPrismaClient:
    """Official Gnani Prisma v2.5 Speech-to-Text integration adapter."""

    def __init__(self, http_client: httpx.AsyncClient, settings: Settings):
        self.http_client = http_client
        self.settings = settings

    async def transcribe(
        self,
        audio_bytes: bytes,
        filename: str,
        content_type: str,
        language_code: str = "kn-IN",
    ) -> TranscriptionResult:
        if not self.settings.GNANI_API_KEY or not self.settings.GNANI_API_KEY.strip():
            logger.warning("Gnani STT transcription attempted but GNANI_API_KEY is not configured.")
            raise ServiceUnavailableException(
                "Speech recognition service is not configured. Please supply a valid GNANI_API_KEY."
            )

        headers = {
            "X-API-Key-ID": self.settings.GNANI_API_KEY.strip(),
        }

        # Prepare multipart/form-data payload
        files = {
            "audio_file": (filename, audio_bytes, content_type),
        }
        data = {
            "language_code": language_code,
            "format": self.settings.GNANI_STT_FORMAT,
        }

        try:
            response = await self.http_client.post(
                self.settings.GNANI_STT_URL,
                headers=headers,
                files=files,
                data=data,
                timeout=self.settings.GNANI_STT_TIMEOUT_SECONDS,
            )
        except httpx.TimeoutException as exc:
            logger.error("Timeout calling Gnani Prisma STT API at %s", self.settings.GNANI_STT_URL)
            raise UpstreamTimeoutException("Speech transcription service timed out.") from exc
        except httpx.RequestError as exc:
            logger.error("Network error communicating with Gnani Prisma STT: %s", str(exc))
            raise UpstreamServiceException(
                "Unable to reach the speech transcription service."
            ) from exc

        # Handle upstream response codes
        if response.status_code == 200:
            try:
                res_json = response.json()
            except Exception as exc:
                logger.error(
                    "Failed to parse JSON response from Gnani STT: %s", response.text[:200]
                )
                raise UpstreamServiceException(
                    "Malformed response received from speech recognition provider."
                ) from exc

            transcript = res_json.get("transcript", "").strip()
            request_id = res_json.get("request_id")
            model = res_json.get("model", "gnani-prisma-v2.5")

            return TranscriptionResult(
                transcript=transcript,
                request_id=request_id,
                model=model,
                language_code=language_code,
            )

        elif response.status_code == 400:
            err_msg = "Invalid audio format or audio duration exceeds 60 seconds."
            logger.warning("Gnani STT returned 400: %s", response.text[:200])
            raise AppException("INVALID_AUDIO_PAYLOAD", err_msg, status_code=400)

        elif response.status_code in (401, 403):
            logger.error(
                "Gnani STT authentication or quota failure (HTTP %d)", response.status_code
            )
            raise UpstreamServiceException(
                "Speech recognition authentication failed or account quota is exhausted."
            )

        elif response.status_code == 429:
            logger.warning("Gnani STT rate limit exceeded (HTTP 429)")
            raise RateLimitException(
                "Upstream speech recognition rate limit exceeded. Please retry shortly."
            )

        else:
            logger.error(
                "Gnani STT failed with upstream HTTP %d: %s",
                response.status_code,
                response.text[:200],
            )
            raise UpstreamServiceException(
                f"Speech recognition service returned an error (HTTP {response.status_code})."
            )
