"""initial_schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-10-26 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Activities table
    op.create_table(
        "activities",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("grade", sa.Integer(), nullable=False),
        sa.Column("subject", sa.String(length=50), nullable=False),
        sa.Column("topic", sa.String(length=100), nullable=False),
        sa.Column("learning_objective", sa.Text(), nullable=False),
        sa.Column("language_code", sa.String(length=10), nullable=False),
        sa.Column("estimated_minutes", sa.Integer(), nullable=False),
        sa.Column("materials", sa.JSON(), nullable=False),
        sa.Column("parent_instructions", sa.Text(), nullable=False),
        sa.Column("child_prompt", sa.Text(), nullable=False),
        sa.Column("question_type", sa.String(length=30), nullable=False),
        sa.Column("public_question_config", sa.JSON(), nullable=False),
        sa.Column("evaluator_config", sa.JSON(), nullable=False),
        sa.Column("hints", sa.JSON(), nullable=False),
        sa.Column("content_version", sa.Integer(), nullable=False),
        sa.Column("published", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_activities_grade", "activities", ["grade"])
    op.create_index("ix_activities_language_code", "activities", ["language_code"])
    op.create_index("ix_activities_published", "activities", ["published"])
    op.create_index(
        "ix_activities_grade_lang_pub",
        "activities",
        ["grade", "language_code", "published"],
    )

    # 2. Sessions table
    op.create_table(
        "sessions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("activity_id", sa.String(length=36), nullable=False),
        sa.Column("language_code", sa.String(length=10), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("consent_acknowledged", sa.Boolean(), nullable=False),
        sa.Column("session_token_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["activity_id"], ["activities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sessions_activity_id", "sessions", ["activity_id"])
    op.create_index("ix_sessions_status", "sessions", ["status"])
    op.create_index("ix_sessions_session_token_hash", "sessions", ["session_token_hash"])
    op.create_index("ix_sessions_created_at", "sessions", ["created_at"])
    op.create_index("ix_sessions_expires_at", "sessions", ["expires_at"])
    op.create_index("ix_sessions_token_hash_status", "sessions", ["session_token_hash", "status"])

    # 3. Attempts table
    op.create_table(
        "attempts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("session_id", sa.String(length=36), nullable=False),
        sa.Column("input_mode", sa.String(length=20), nullable=False),
        sa.Column("draft_transcript", sa.Text(), nullable=True),
        sa.Column("confirmed_transcript", sa.Text(), nullable=True),
        sa.Column("confirmed_answer", sa.Text(), nullable=True),
        sa.Column("transcription_status", sa.String(length=20), nullable=False),
        sa.Column("evaluation_status", sa.String(length=30), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=True),
        sa.Column("feedback", sa.Text(), nullable=True),
        sa.Column("hint_used", sa.Integer(), nullable=False),
        sa.Column("provider_request_id", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_attempts_session_id", "attempts", ["session_id"])
    op.create_index("ix_attempts_evaluation_status", "attempts", ["evaluation_status"])
    op.create_index("ix_attempts_is_correct", "attempts", ["is_correct"])
    op.create_index("ix_attempts_created_at", "attempts", ["created_at"])
    op.create_index("ix_attempts_session_created", "attempts", ["session_id", "created_at"])
    op.create_index("ix_attempts_eval_correct", "attempts", ["evaluation_status", "is_correct"])


def downgrade() -> None:
    op.drop_table("attempts")
    op.drop_table("sessions")
    op.drop_table("activities")
