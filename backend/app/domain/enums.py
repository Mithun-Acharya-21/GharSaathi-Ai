from enum import StrEnum


class QuestionType(StrEnum):
    INTEGER = "integer"
    DECIMAL = "decimal"
    MULTIPLE_CHOICE = "multiple_choice"
    STEP_BY_STEP = "step_by_step"


class SessionStatus(StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"
    ABANDONED = "abandoned"


class InputMode(StrEnum):
    SPEECH = "speech"
    TEXT = "text"


class TranscriptionStatus(StrEnum):
    NOT_APPLICABLE = "not_applicable"
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class EvaluationStatus(StrEnum):
    PENDING_CONFIRMATION = "pending_confirmation"
    CONFIRMED = "confirmed"
    EVALUATED = "evaluated"
    REVIEW_REQUIRED = "review_required"
