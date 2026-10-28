from app.core.errors import InvalidStateTransitionException
from app.domain.enums import EvaluationStatus, SessionStatus

VALID_SESSION_TRANSITIONS: dict[SessionStatus, set[SessionStatus]] = {
    SessionStatus.ACTIVE: {SessionStatus.COMPLETED, SessionStatus.EXPIRED, SessionStatus.ABANDONED},
    SessionStatus.COMPLETED: set(),
    SessionStatus.EXPIRED: set(),
    SessionStatus.ABANDONED: set(),
}

VALID_EVALUATION_TRANSITIONS: dict[EvaluationStatus, set[EvaluationStatus]] = {
    EvaluationStatus.PENDING_CONFIRMATION: {
        EvaluationStatus.CONFIRMED,
        EvaluationStatus.REVIEW_REQUIRED,
    },
    EvaluationStatus.CONFIRMED: {
        EvaluationStatus.EVALUATED,
        EvaluationStatus.REVIEW_REQUIRED,
    },
    EvaluationStatus.EVALUATED: set(),
    EvaluationStatus.REVIEW_REQUIRED: {EvaluationStatus.CONFIRMED},
}


def validate_session_transition(current: SessionStatus, target: SessionStatus) -> None:
    if current == target:
        return
    allowed = VALID_SESSION_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise InvalidStateTransitionException(
            f"Cannot transition session from '{current.value}' to '{target.value}'"
        )


def validate_evaluation_transition(current: EvaluationStatus, target: EvaluationStatus) -> None:
    if current == target:
        return
    allowed = VALID_EVALUATION_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise InvalidStateTransitionException(
            f"Cannot transition attempt evaluation from '{current.value}' to '{target.value}'"
        )
