from typing import Annotated

from fastapi import APIRouter, Depends, Response

from app.api.dependencies import get_activity_service, get_timbre_client
from app.core.errors import AppException
from app.integrations.gnani_timbre import TimbreClientProtocol
from app.schemas.speech import SpeechSynthesizeRequest
from app.services.activity_service import ActivityService

router = APIRouter(prefix="/speech", tags=["Speech Synthesis"])


@router.post(
    "/synthesize",
    summary="Synthesize spoken instructions via Gnani Timbre",
    responses={
        200: {
            "content": {"audio/wav": {}},
            "description": "Synthesized audio bytes in WAV format.",
        },
        503: {
            "description": "Timbre TTS service is disabled or unconfigured in this deployment.",
        },
    },
)
async def synthesize_speech(
    req: SpeechSynthesizeRequest,
    activity_service: Annotated[ActivityService, Depends(get_activity_service)],
    timbre_client: Annotated[TimbreClientProtocol, Depends(get_timbre_client)],
):
    """
    Synthesize approved activity instructions or prompts using Gnani Timbre.
    If Timbre is disabled in configuration, returns 503 so the frontend displays approved text fallback.
    """
    activity = await activity_service.get_activity_public(req.activity_id)

    if req.text_type == "prompt":
        text_to_speak = activity.child_prompt
    elif req.text_type == "instructions":
        text_to_speak = activity.parent_instructions
    else:
        raise AppException(
            "INVALID_TEXT_TYPE", "text_type must be 'instructions' or 'prompt'", status_code=400
        )

    audio_bytes = await timbre_client.synthesize(
        text=text_to_speak,
        language_code=req.language_code or activity.language_code,
    )

    return Response(content=audio_bytes, media_type="audio/wav")
