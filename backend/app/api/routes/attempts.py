from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status

from app.api.dependencies import get_attempt_service, get_bearer_token
from app.schemas.attempt import (
    AttemptConfirmRequest,
    AttemptConfirmResponse,
    AttemptEvaluateResponse,
    AttemptTextCreateRequest,
    AttemptTextResponse,
    AttemptTranscribeResponse,
)
from app.services.attempt_service import AttemptService

router = APIRouter(prefix="", tags=["Attempts"])


@router.post(
    "/sessions/{session_id}/attempts/transcribe",
    response_model=AttemptTranscribeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Transcribe spoken answer via Gnani Prisma",
)
async def transcribe_spoken_answer(
    session_id: str,
    bearer_token: Annotated[str, Depends(get_bearer_token)],
    attempt_service: Annotated[AttemptService, Depends(get_attempt_service)],
    audio_file: Annotated[
        UploadFile, File(description="Spoken audio file (WAV, MP3, OGG, FLAC, AAC, M4A)")
    ],
):
    """
    Upload a spoken child answer for real-time transcription via Gnani Prisma STT v3.
    The raw audio is processed strictly in-memory without persistent disk storage.
    Returns a draft transcript for parent review before mathematical evaluation.
    """
    audio_bytes = await audio_file.read()
    return await attempt_service.transcribe_speech(
        session_id=session_id,
        bearer_token=bearer_token,
        filename=audio_file.filename or "recording.wav",
        content_type=audio_file.content_type or "audio/wav",
        audio_bytes=audio_bytes,
    )


@router.post(
    "/sessions/{session_id}/attempts/text",
    response_model=AttemptTextResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit typed-answer fallback",
)
async def submit_typed_answer(
    session_id: str,
    req: AttemptTextCreateRequest,
    bearer_token: Annotated[str, Depends(get_bearer_token)],
    attempt_service: Annotated[AttemptService, Depends(get_attempt_service)],
):
    """Fallback text submission when speech recognition or audio capture is unavailable."""
    return await attempt_service.create_text_attempt(
        session_id=session_id, bearer_token=bearer_token, req=req
    )


@router.patch(
    "/attempts/{attempt_id}/confirm",
    response_model=AttemptConfirmResponse,
    summary="Review and confirm transcript / answer",
)
async def confirm_answer(
    attempt_id: str,
    req: AttemptConfirmRequest,
    bearer_token: Annotated[str, Depends(get_bearer_token)],
    attempt_service: Annotated[AttemptService, Depends(get_attempt_service)],
):
    """
    Allows a parent to review, correct any misheard speech-to-text words,
    and explicitly confirm the child's final answer before mathematical evaluation.
    """
    return await attempt_service.confirm_attempt(
        attempt_id=attempt_id, bearer_token=bearer_token, req=req
    )


@router.post(
    "/attempts/{attempt_id}/evaluate",
    response_model=AttemptEvaluateResponse,
    summary="Evaluate confirmed answer",
)
async def evaluate_answer(
    attempt_id: str,
    bearer_token: Annotated[str, Depends(get_bearer_token)],
    attempt_service: Annotated[AttemptService, Depends(get_attempt_service)],
):
    """
    Deterministically evaluates the confirmed mathematical answer against the server-side
    activity specifications. Returns pedagogical feedback and progressive hints.
    """
    return await attempt_service.evaluate_attempt(attempt_id=attempt_id, bearer_token=bearer_token)
