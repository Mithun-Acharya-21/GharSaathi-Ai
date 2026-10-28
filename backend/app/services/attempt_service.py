import logging

from app.core.config import get_settings
from app.core.errors import (
    AppException,
    NotFoundException,
    PayloadTooLargeException,
    RateLimitException,
    UnsupportedMediaTypeException,
)
from app.domain.enums import (
    EvaluationStatus,
    InputMode,
    SessionStatus,
    TranscriptionStatus,
)
from app.domain.evaluation import Evaluator
from app.domain.state_transitions import validate_evaluation_transition
from app.integrations.gnani_prisma import PrismaClientProtocol
from app.models.attempt import Attempt
from app.models.base import utc_now
from app.repositories.activity_repository import ActivityRepository
from app.repositories.attempt_repository import AttemptRepository
from app.repositories.session_repository import SessionRepository
from app.schemas.attempt import (
    AttemptConfirmRequest,
    AttemptConfirmResponse,
    AttemptEvaluateResponse,
    AttemptTextCreateRequest,
    AttemptTextResponse,
    AttemptTranscribeResponse,
)
from app.services.session_service import SessionService

logger = logging.getLogger(__name__)

SUPPORTED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".ogg", ".flac", ".aac", ".m4a"}
SUPPORTED_MIME_PREFIXES = {"audio/", "application/ogg", "application/octet-stream"}


class AttemptService:
    def __init__(
        self,
        attempt_repo: AttemptRepository,
        session_repo: SessionRepository,
        activity_repo: ActivityRepository,
        session_service: SessionService,
        prisma_client: PrismaClientProtocol,
    ):
        self.attempt_repo = attempt_repo
        self.session_repo = session_repo
        self.activity_repo = activity_repo
        self.session_service = session_service
        self.prisma_client = prisma_client
        self.settings = get_settings()

    async def transcribe_speech(
        self,
        session_id: str,
        bearer_token: str,
        filename: str,
        content_type: str,
        audio_bytes: bytes,
    ) -> AttemptTranscribeResponse:
        session_obj = await self.session_service.get_and_authorize_session(session_id, bearer_token)
        if session_obj.status != SessionStatus.ACTIVE.value:
            raise AppException(
                "SESSION_NOT_ACTIVE", "Cannot submit audio to an inactive session.", status_code=400
            )

        # 1. Check max transcription quota per session
        attempt_count = await self.attempt_repo.count_for_session(session_id)
        if attempt_count >= self.settings.MAX_TRANSCRIPTIONS_PER_SESSION:
            raise RateLimitException(
                f"Maximum transcriptions limit ({self.settings.MAX_TRANSCRIPTIONS_PER_SESSION}) reached for this session."
            )

        # 2. Validate file size (10 MB limit)
        max_bytes = self.settings.MAX_AUDIO_SIZE_MB * 1024 * 1024
        if len(audio_bytes) > max_bytes:
            raise PayloadTooLargeException(
                f"Audio file size exceeds the allowed limit of {self.settings.MAX_AUDIO_SIZE_MB}MB."
            )

        # 3. Validate audio format
        lower_fn = filename.lower() if filename else ""
        has_valid_ext = any(lower_fn.endswith(ext) for ext in SUPPORTED_AUDIO_EXTENSIONS)
        has_valid_mime = (
            any(content_type.startswith(p) for p in SUPPORTED_MIME_PREFIXES)
            if content_type
            else False
        )

        if not has_valid_ext and not has_valid_mime:
            raise UnsupportedMediaTypeException(
                f"Unsupported audio format '{content_type or lower_fn}'. Supported formats: WAV, MP3, OGG, FLAC, AAC, M4A."
            )

        # 4. Call Gnani Prisma adapter
        transcription_res = await self.prisma_client.transcribe(
            audio_bytes=audio_bytes,
            filename=filename or "audio.wav",
            content_type=content_type or "audio/wav",
            language_code=session_obj.language_code,
        )

        # 5. Persist Attempt
        attempt_obj = Attempt(
            session_id=session_obj.id,
            input_mode=InputMode.SPEECH.value,
            draft_transcript=transcription_res.transcript,
            transcription_status=TranscriptionStatus.COMPLETED.value,
            evaluation_status=EvaluationStatus.PENDING_CONFIRMATION.value,
            provider_request_id=transcription_res.request_id,
            created_at=utc_now(),
        )
        saved = await self.attempt_repo.create(attempt_obj)

        return AttemptTranscribeResponse(
            attempt_id=saved.id,
            transcription_status=TranscriptionStatus.COMPLETED,
            evaluation_status=EvaluationStatus.PENDING_CONFIRMATION,
            transcript=saved.draft_transcript or "",
            language_code=session_obj.language_code,
            provider=transcription_res.model,
            request_id=transcription_res.request_id,
        )

    async def create_text_attempt(
        self,
        session_id: str,
        bearer_token: str,
        req: AttemptTextCreateRequest,
    ) -> AttemptTextResponse:
        session_obj = await self.session_service.get_and_authorize_session(session_id, bearer_token)
        if session_obj.status != SessionStatus.ACTIVE.value:
            raise AppException(
                "SESSION_NOT_ACTIVE",
                "Cannot submit answer to an inactive session.",
                status_code=400,
            )

        attempt_obj = Attempt(
            session_id=session_obj.id,
            input_mode=InputMode.TEXT.value,
            draft_transcript=req.answer.strip(),
            confirmed_answer=req.answer.strip(),
            transcription_status=TranscriptionStatus.NOT_APPLICABLE.value,
            evaluation_status=EvaluationStatus.PENDING_CONFIRMATION.value,
            created_at=utc_now(),
        )
        saved = await self.attempt_repo.create(attempt_obj)

        return AttemptTextResponse(
            attempt_id=saved.id,
            input_mode=InputMode.TEXT,
            transcription_status=TranscriptionStatus.NOT_APPLICABLE,
            evaluation_status=EvaluationStatus.PENDING_CONFIRMATION,
            draft_answer=saved.draft_transcript or "",
            message="Typed answer recorded. Please confirm your answer for evaluation.",
        )

    async def confirm_attempt(
        self,
        attempt_id: str,
        bearer_token: str,
        req: AttemptConfirmRequest,
    ) -> AttemptConfirmResponse:
        attempt = await self.attempt_repo.get_by_id(attempt_id)
        if not attempt:
            raise NotFoundException(f"Attempt '{attempt_id}' not found.")

        # Verify session ownership
        await self.session_service.get_and_authorize_session(attempt.session_id, bearer_token)

        # Validate state transition
        validate_evaluation_transition(
            EvaluationStatus(attempt.evaluation_status), EvaluationStatus.CONFIRMED
        )

        attempt.confirmed_answer = req.confirmed_answer.strip()
        if req.corrected_transcript:
            attempt.confirmed_transcript = req.corrected_transcript.strip()
        elif attempt.draft_transcript:
            attempt.confirmed_transcript = attempt.draft_transcript

        attempt.evaluation_status = EvaluationStatus.CONFIRMED.value
        attempt.updated_at = utc_now()
        await self.attempt_repo.session.commit()

        return AttemptConfirmResponse(
            attempt_id=attempt.id,
            evaluation_status=EvaluationStatus.CONFIRMED,
            confirmed_answer=attempt.confirmed_answer,
            confirmed_transcript=attempt.confirmed_transcript,
        )

    async def evaluate_attempt(
        self,
        attempt_id: str,
        bearer_token: str,
    ) -> AttemptEvaluateResponse:
        attempt = await self.attempt_repo.get_by_id(attempt_id)
        if not attempt:
            raise NotFoundException(f"Attempt '{attempt_id}' not found.")

        # Verify session ownership
        session_obj = await self.session_service.get_and_authorize_session(
            attempt.session_id, bearer_token
        )

        # Check state: must be confirmed before evaluation
        if attempt.evaluation_status not in (
            EvaluationStatus.CONFIRMED.value,
            EvaluationStatus.REVIEW_REQUIRED.value,
        ):
            raise AppException(
                "ATTEMPT_NOT_CONFIRMED",
                "Answers must be reviewed and confirmed before evaluation.",
                status_code=400,
            )

        activity = session_obj.activity
        if not activity:
            activity = await self.activity_repo.get_by_id(
                session_obj.activity_id, published_only=False
            )

        eval_result = Evaluator.evaluate(
            question_type=activity.question_type,
            confirmed_answer=attempt.confirmed_answer,
            evaluator_config=activity.evaluator_config,
            hints=activity.hints,
            hint_index=attempt.hint_used,
        )

        if eval_result.review_required:
            attempt.evaluation_status = EvaluationStatus.REVIEW_REQUIRED.value
            attempt.is_correct = None
        else:
            attempt.evaluation_status = EvaluationStatus.EVALUATED.value
            attempt.is_correct = eval_result.is_correct

        attempt.feedback = eval_result.feedback
        if not eval_result.is_correct and eval_result.next_hint:
            attempt.hint_used += 1

        attempt.updated_at = utc_now()
        await self.attempt_repo.session.commit()

        return AttemptEvaluateResponse(
            attempt_id=attempt.id,
            evaluation_status=EvaluationStatus(attempt.evaluation_status),
            is_correct=attempt.is_correct,
            feedback=eval_result.feedback,
            next_hint=eval_result.next_hint,
            review_required=eval_result.review_required,
        )
