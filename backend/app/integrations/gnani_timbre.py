import logging
from typing import Protocol

import httpx

from app.core.config import Settings
from app.core.errors import (
    AppException,
    RateLimitException,
    ServiceUnavailableException,
    UpstreamServiceException,
    UpstreamTimeoutException,
)

logger = logging.getLogger(__name__)


class TimbreClientProtocol(Protocol):
    async def synthesize(
        self,
        text: str,
        language_code: str = "kn-IN",
    ) -> bytes: ...


class GnaniTimbreClient:
    """Official Gnani Timbre Text-to-Speech integration adapter."""

    def __init__(self, http_client: httpx.AsyncClient, settings: Settings):
        self.http_client = http_client
        self.settings = settings

    async def synthesize(
        self,
        text: str,
        language_code: str = "kn-IN",
    ) -> bytes:
        if not self.settings.GNANI_TTS_ENABLED:
            raise ServiceUnavailableException(
                "Text-to-speech audio synthesis is currently disabled in configuration."
            )

        if not self.settings.GNANI_API_KEY or not self.settings.GNANI_API_KEY.strip():
            logger.warning("Gnani TTS requested but GNANI_API_KEY is not configured.")
            raise ServiceUnavailableException(
                "Text-to-speech service is not configured. Please supply a valid GNANI_API_KEY."
            )

        if len(text) > 1000:
            raise AppException(
                "TEXT_TOO_LONG", "Text exceeds maximum supported synthesis length.", status_code=400
            )

        # Select model-verified voice for language
        voice = (
            self.settings.GNANI_TTS_VOICE_KN
            if language_code == "kn-IN"
            else self.settings.GNANI_TTS_VOICE_EN
        )

        headers = {
            "Content-Type": "application/json",
            "X-API-Key-ID": self.settings.GNANI_API_KEY.strip(),
        }

        payload = {
            "text": text,
            "voice": voice,
            "model": self.settings.GNANI_TTS_MODEL,
            "language": language_code,
            "speed": 1.0,
            "audio_config": {
                "sample_rate": 48000,
                "num_channels": 1,
                "sample_width": 2,
                "encoding": "linear_pcm",
                "container": "wav",
            },
        }

        try:
            response = await self.http_client.post(
                self.settings.GNANI_TTS_URL,
                headers=headers,
                json=payload,
                timeout=self.settings.GNANI_TTS_TIMEOUT_SECONDS,
            )
        except httpx.TimeoutException as exc:
            logger.error("Timeout calling Gnani Timbre TTS at %s", self.settings.GNANI_TTS_URL)
            raise UpstreamTimeoutException("Text-to-speech synthesis service timed out.") from exc
        except httpx.RequestError as exc:
            logger.error("Network error communicating with Gnani Timbre TTS: %s", str(exc))
            raise UpstreamServiceException("Unable to reach the text-to-speech service.") from exc

        if response.status_code == 200:
            return response.content
        elif response.status_code == 400:
            logger.warning("Gnani TTS returned 400: %s", response.text[:200])
            raise AppException(
                "INVALID_TTS_REQUEST",
                "Invalid voice or text parameters for TTS synthesis.",
                status_code=400,
            )
        elif response.status_code in (401, 403):
            logger.error(
                "Gnani TTS authentication or quota failure (HTTP %d)", response.status_code
            )
            raise UpstreamServiceException(
                "Text-to-speech authentication failed or quota exhausted."
            )
        elif response.status_code == 429:
            raise RateLimitException(
                "Upstream text-to-speech rate limit exceeded. Please retry shortly."
            )
        else:
            logger.error("Gnani TTS error HTTP %d: %s", response.status_code, response.text[:200])
            raise UpstreamServiceException(
                f"Text-to-speech service error (HTTP {response.status_code})."
            )
