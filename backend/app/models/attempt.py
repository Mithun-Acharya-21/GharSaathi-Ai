from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import EvaluationStatus, InputMode, TranscriptionStatus
from app.models.base import Base, generate_uuid, utc_now

if TYPE_CHECKING:
    from app.models.session import Session


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    input_mode: Mapped[str] = mapped_column(
        String(20), nullable=False, default=InputMode.SPEECH.value
    )
    draft_transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    confirmed_transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    confirmed_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    transcription_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=TranscriptionStatus.PENDING.value
    )
    evaluation_status: Mapped[str] = mapped_column(
        String(30), nullable=False, default=EvaluationStatus.PENDING_CONFIRMATION.value, index=True
    )
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True, index=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    hint_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    provider_request_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )

    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="attempts")

    __table_args__ = (
        Index("ix_attempts_session_created", "session_id", "created_at"),
        Index("ix_attempts_eval_correct", "evaluation_status", "is_correct"),
    )
