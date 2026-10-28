from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.schemas.common import BaseSchema


class GradeInfo(BaseModel):
    grade: int
    name: str
    description: str


class GradeListResponse(BaseModel):
    grades: list[GradeInfo]


class ActivitySummary(BaseSchema):
    id: str
    grade: int
    subject: str
    topic: str
    learning_objective: str
    language_code: str
    estimated_minutes: int
    question_type: str


class ActivityPublic(BaseSchema):
    id: str
    grade: int
    subject: str
    topic: str
    learning_objective: str
    language_code: str
    estimated_minutes: int
    materials: list[str]
    parent_instructions: str
    child_prompt: str
    question_type: str
    public_question_config: dict[str, Any]
    hints: list[str]
    content_version: int
    created_at: datetime
    # evaluator_config is strictly omitted here!


class ActivityListResponse(BaseModel):
    activities: list[ActivitySummary]
    total: int
