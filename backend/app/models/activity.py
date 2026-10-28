from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Boolean, DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, generate_uuid, utc_now

if TYPE_CHECKING:
    from app.models.session import Session


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    grade: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    subject: Mapped[str] = mapped_column(String(50), nullable=False, default="maths")
    topic: Mapped[str] = mapped_column(String(100), nullable=False)
    learning_objective: Mapped[str] = mapped_column(Text, nullable=False)
    language_code: Mapped[str] = mapped_column(
        String(10), nullable=False, default="kn-IN", index=True
    )
    estimated_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    materials: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    parent_instructions: Mapped[str] = mapped_column(Text, nullable=False)
    child_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(30), nullable=False)
    public_question_config: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, default=dict
    )
    evaluator_config: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    hints: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    content_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )

    # Relationships
    sessions: Mapped[list["Session"]] = relationship(
        "Session", back_populates="activity", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_activities_grade_lang_pub", "grade", "language_code", "published"),)
