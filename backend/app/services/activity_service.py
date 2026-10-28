from typing import Any

from app.core.errors import NotFoundException
from app.repositories.activity_repository import ActivityRepository
from app.schemas.activity import (
    ActivityListResponse,
    ActivityPublic,
    ActivitySummary,
    GradeInfo,
    GradeListResponse,
)

GRADE_DEFINITIONS: list[dict[str, Any]] = [
    {"grade": 1, "name": "Grade 1", "description": "Counting, concrete addition and subtraction"},
    {"grade": 2, "name": "Grade 2", "description": "Place value, tens and ones grouping"},
    {
        "grade": 3,
        "name": "Grade 3",
        "description": "Multiplication as equal groups and repeated addition",
    },
    {"grade": 4, "name": "Grade 4", "description": "Geometry, shapes, measurement and perimeter"},
    {"grade": 5, "name": "Grade 5", "description": "Decimals, currency comparison and operations"},
    {"grade": 6, "name": "Grade 6", "description": "Ratios, proportions and rate applications"},
]


class ActivityService:
    def __init__(self, activity_repo: ActivityRepository):
        self.activity_repo = activity_repo

    def get_supported_grades(self) -> GradeListResponse:
        return GradeListResponse(grades=[GradeInfo(**g) for g in GRADE_DEFINITIONS])

    async def list_activities(
        self, grade: int | None = None, language_code: str | None = None
    ) -> ActivityListResponse:
        activities = await self.activity_repo.list_by_filter(
            grade=grade, language_code=language_code, published_only=True
        )
        summaries = [ActivitySummary.model_validate(act) for act in activities]
        return ActivityListResponse(activities=summaries, total=len(summaries))

    async def get_activity_public(self, activity_id: str) -> ActivityPublic:
        activity = await self.activity_repo.get_by_id(activity_id, published_only=True)
        if not activity:
            raise NotFoundException(f"Activity with ID '{activity_id}' not found or not published.")
        return ActivityPublic.model_validate(activity)
