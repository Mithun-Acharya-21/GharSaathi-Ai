from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.enums import EvaluationStatus, InputMode, TranscriptionStatus
from app.schemas.common import BaseSchema


class AttemptTranscribeResponse(BaseModel):
    attempt_id: str
    transcription_status: TranscriptionStatus
    evaluation_status: EvaluationStatus
    transcript: str
    language_code: str
    provider: str
    request_id: str | None = None


class AttemptTextCreateRequest(BaseModel):
    answer: str = Field(..., min_length=1, max_length=1000, description="Typed answer text")


class AttemptTextResponse(BaseModel):
    attempt_id: str
    input_mode: InputMode = InputMode.TEXT
    transcription_status: TranscriptionStatus = TranscriptionStatus.NOT_APPLICABLE
    evaluation_status: EvaluationStatus = EvaluationStatus.PENDING_CONFIRMATION
    draft_answer: str
    message: str = "Typed answer recorded. Please review and confirm."


class AttemptConfirmRequest(BaseModel):
    confirmed_answer: str = Field(
        ..., min_length=1, max_length=1000, description="Parent-confirmed final answer"
    )
    corrected_transcript: str | None = Field(
        default=None, max_length=2000, description="Optional parent-corrected transcript"
    )
    confirmation_status: str = Field(default="confirmed", description="Confirmation status flag")


class AttemptConfirmResponse(BaseModel):
    attempt_id: str
    evaluation_status: EvaluationStatus
    confirmed_answer: str
    confirmed_transcript: str | None = None


class AttemptEvaluateResponse(BaseModel):
    attempt_id: str
    evaluation_status: EvaluationStatus
    is_correct: bool | None
    feedback: str
    next_hint: str | None = None
    review_required: bool = False


class AttemptSummary(BaseSchema):
    id: str
    input_mode: str
    draft_transcript: str | None = None
    confirmed_transcript: str | None = None
    confirmed_answer: str | None = None
    transcription_status: str
    evaluation_status: str
    is_correct: bool | None = None
    feedback: str | None = None
    created_at: datetime
