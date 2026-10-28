from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import SessionStatus
from app.models.base import Base, generate_uuid, utc_now

if TYPE_CHECKING:
    from app.models.activity import Activity
    from app.models.attempt import Attempt


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    activity_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("activities.id", ondelete="CASCADE"), nullable=False, index=True
    )
    language_code: Mapped[str] = mapped_column(String(10), nullable=False, default="kn-IN")
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=SessionStatus.ACTIVE.value, index=True
    )
    consent_acknowledged: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    session_token_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, index=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    # Relationships
    activity: Mapped["Activity"] = relationship("Activity", back_populates="sessions")
    attempts: Mapped[list["Attempt"]] = relationship(
        "Attempt", back_populates="session", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_sessions_token_hash_status", "session_token_hash", "status"),)
