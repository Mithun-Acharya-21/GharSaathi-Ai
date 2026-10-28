from datetime import timedelta

from app.core.config import get_settings
from app.core.errors import (
    ExpiredSessionException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
)
from app.core.security import generate_session_token, hash_token, verify_token
from app.domain.enums import SessionStatus
from app.domain.state_transitions import validate_session_transition
from app.models.base import ensure_utc, utc_now
from app.models.session import Session
from app.repositories.activity_repository import ActivityRepository
from app.repositories.session_repository import SessionRepository
from app.schemas.activity import ActivitySummary
from app.schemas.attempt import AttemptSummary
from app.schemas.session import (
    SessionCompleteResponse,
    SessionCreateRequest,
    SessionCreateResponse,
    SessionDetailResponse,
)


class SessionService:
    def __init__(
        self,
        session_repo: SessionRepository,
        activity_repo: ActivityRepository,
    ):
        self.session_repo = session_repo
        self.activity_repo = activity_repo
        self.settings = get_settings()

    async def create_session(self, req: SessionCreateRequest) -> SessionCreateResponse:
        activity = await self.activity_repo.get_by_id(req.activity_id, published_only=True)
        if not activity:
            raise NotFoundException(f"Activity '{req.activity_id}' not found or not published.")

        if not req.consent_acknowledged:
            raise ForbiddenException(
                "Guardian consent acknowledgement is required before initiating a voice learning session."
            )

        plain_token = generate_session_token()
        hashed_token = hash_token(plain_token)

        now = utc_now()
        expires_at = now + timedelta(hours=self.settings.SESSION_TOKEN_TTL_HOURS)

        session_obj = Session(
            activity_id=activity.id,
            language_code=req.language_code,
            status=SessionStatus.ACTIVE.value,
            consent_acknowledged=req.consent_acknowledged,
            session_token_hash=hashed_token,
            created_at=now,
            expires_at=expires_at,
        )

        created = await self.session_repo.create(session_obj)

        return SessionCreateResponse(
            session_id=created.id,
            session_token=plain_token,
            activity=ActivitySummary.model_validate(activity),
            status=SessionStatus(created.status),
            created_at=created.created_at,
            expires_at=created.expires_at,
        )

    async def get_and_authorize_session(self, session_id: str, bearer_token: str) -> Session:
        session_obj = await self.session_repo.get_by_id(session_id)
        if not session_obj:
            raise NotFoundException(f"Session '{session_id}' not found.")

        # Constant-time token verification
        if not verify_token(bearer_token, session_obj.session_token_hash):
            raise UnauthorizedException(
                "Invalid session credentials or session ownership mismatch."
            )

        # Expiry check
        if ensure_utc(session_obj.expires_at) < utc_now():
            session_obj.status = SessionStatus.EXPIRED.value
            raise ExpiredSessionException(
                "This learning session has expired. Please start a new session."
            )

        return session_obj

    async def get_session_detail(self, session_id: str, bearer_token: str) -> SessionDetailResponse:
        await self.get_and_authorize_session(session_id, bearer_token)
        # Fetch with attempts loaded
        session_with_attempts = await self.session_repo.get_by_id_with_attempts(session_id)
        if not session_with_attempts:
            raise NotFoundException(f"Session '{session_id}' not found.")

        attempt_summaries = [
            AttemptSummary.model_validate(att) for att in session_with_attempts.attempts
        ]

        return SessionDetailResponse(
            id=session_with_attempts.id,
            activity_id=session_with_attempts.activity_id,
            language_code=session_with_attempts.language_code,
            status=SessionStatus(session_with_attempts.status),
            consent_acknowledged=session_with_attempts.consent_acknowledged,
            created_at=session_with_attempts.created_at,
            completed_at=session_with_attempts.completed_at,
            expires_at=session_with_attempts.expires_at,
            attempts=attempt_summaries,
        )

    async def complete_session(self, session_id: str, bearer_token: str) -> SessionCompleteResponse:
        session_obj = await self.get_and_authorize_session(session_id, bearer_token)
        validate_session_transition(SessionStatus(session_obj.status), SessionStatus.COMPLETED)

        now = utc_now()
        session_obj.status = SessionStatus.COMPLETED.value
        session_obj.completed_at = now
        await self.session_repo.session.commit()

        return SessionCompleteResponse(
            session_id=session_obj.id,
            status=SessionStatus.COMPLETED,
            completed_at=now,
            message="Session successfully completed.",
        )

    async def delete_session(self, session_id: str, bearer_token: str) -> None:
        session_obj = await self.get_and_authorize_session(session_id, bearer_token)
        await self.session_repo.delete(session_obj)
