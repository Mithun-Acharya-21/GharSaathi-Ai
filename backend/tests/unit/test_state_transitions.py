import pytest

from app.core.errors import InvalidStateTransitionException
from app.domain.enums import EvaluationStatus, SessionStatus
from app.domain.state_transitions import validate_evaluation_transition, validate_session_transition


def test_valid_session_transitions():
    validate_session_transition(SessionStatus.ACTIVE, SessionStatus.COMPLETED)
    validate_session_transition(SessionStatus.ACTIVE, SessionStatus.EXPIRED)
    validate_session_transition(SessionStatus.ACTIVE, SessionStatus.ABANDONED)
    validate_session_transition(SessionStatus.ACTIVE, SessionStatus.ACTIVE)


def test_invalid_session_transitions():
    with pytest.raises(InvalidStateTransitionException):
        validate_session_transition(SessionStatus.COMPLETED, SessionStatus.ACTIVE)

    with pytest.raises(InvalidStateTransitionException):
        validate_session_transition(SessionStatus.EXPIRED, SessionStatus.ACTIVE)


def test_valid_evaluation_transitions():
    validate_evaluation_transition(
        EvaluationStatus.PENDING_CONFIRMATION, EvaluationStatus.CONFIRMED
    )
    validate_evaluation_transition(EvaluationStatus.CONFIRMED, EvaluationStatus.EVALUATED)
    validate_evaluation_transition(EvaluationStatus.CONFIRMED, EvaluationStatus.REVIEW_REQUIRED)


def test_invalid_evaluation_transitions():
    with pytest.raises(InvalidStateTransitionException):
        validate_evaluation_transition(
            EvaluationStatus.PENDING_CONFIRMATION, EvaluationStatus.EVALUATED
        )
