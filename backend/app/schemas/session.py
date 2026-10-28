from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.enums import SessionStatus
from app.schemas.activity import ActivitySummary
from app.schemas.attempt import AttemptSummary
from app.schemas.common import BaseSchema


class SessionCreateRequest(BaseModel):
    activity_id: str = Field(..., description="ID of the activity to start")
    language_code: str = Field(default="kn-IN", description="Language code for the session")
    consent_acknowledged: bool = Field(
        ...,
        description="Explicit guardian consent acknowledgement for voice learning participation",
    )


class SessionCreateResponse(BaseModel):
    session_id: str
    session_token: str = Field(
        ...,
        description="Secret bearer token. Returned only once upon creation; store securely on the client.",
    )
    activity: ActivitySummary
    status: SessionStatus
    created_at: datetime
    expires_at: datetime


class SessionDetailResponse(BaseSchema):
    id: str
    activity_id: str
    language_code: str
    status: SessionStatus
    consent_acknowledged: bool
    created_at: datetime
    completed_at: datetime | None = None
    expires_at: datetime
    attempts: list[AttemptSummary] = Field(default_factory=list)


class SessionCompleteResponse(BaseModel):
    session_id: str
    status: SessionStatus
    completed_at: datetime
    message: str = "Session successfully completed."
