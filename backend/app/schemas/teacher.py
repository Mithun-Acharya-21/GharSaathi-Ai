from datetime import datetime

from pydantic import BaseModel, Field


class TopicMetric(BaseModel):
    grade: int
    topic: str
    sessions_started: int
    sessions_completed: int
    attempts_evaluated: int
    correct_attempts: int
    accuracy_percentage: float = Field(
        ...,
        description="Percentage of evaluated attempts that are correct (0.0 if no evaluated attempts)",
    )
    review_required_count: int


class TeacherReportResponse(BaseModel):
    grade: int | None
    activities_available: int
    sessions_started: int
    sessions_completed: int
    attempts_evaluated: int
    correct_evaluated_attempts: int
    incorrect_evaluated_attempts: int
    overall_accuracy_percentage: float
    review_required_count: int
    topics: list[TopicMetric]


class ReviewQueueItem(BaseModel):
    attempt_id: str
    grade: int
    topic: str
    child_prompt: str
    input_mode: str
    draft_transcript: str | None = None
    confirmed_transcript: str | None = None
    confirmed_answer: str | None = None
    evaluation_status: str
    feedback: str | None = None
    created_at: datetime
