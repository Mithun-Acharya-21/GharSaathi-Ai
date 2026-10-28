from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_activity_service
from app.core.errors import AppException
from app.schemas.activity import ActivityListResponse, ActivityPublic, GradeListResponse
from app.services.activity_service import ActivityService

router = APIRouter(prefix="", tags=["Activities"])


@router.get(
    "/grades",
    response_model=GradeListResponse,
    summary="List supported grades",
)
async def get_grades(
    activity_service: Annotated[ActivityService, Depends(get_activity_service)],
):
    """Retrieve supported mathematics grades (Grades 1 to 6)."""
    return activity_service.get_supported_grades()


@router.get(
    "/activities",
    response_model=ActivityListResponse,
    summary="List published activities",
)
async def list_activities(
    activity_service: Annotated[ActivityService, Depends(get_activity_service)],
    grade: Annotated[int | None, Query(ge=1, le=6, description="Filter by grade (1 to 6)")] = None,
    language_code: Annotated[
        str | None, Query(description="Filter by language code (e.g. kn-IN)")
    ] = None,
):
    """List teacher-reviewed published mathematics activities filtered by grade and language."""
    if grade is not None and (grade < 1 or grade > 6):
        raise AppException("INVALID_GRADE", "Grade must be between 1 and 6.", status_code=400)

    return await activity_service.list_activities(grade=grade, language_code=language_code)


@router.get(
    "/activities/{activity_id}",
    response_model=ActivityPublic,
    summary="Get public activity definition",
)
async def get_activity(
    activity_id: str,
    activity_service: Annotated[ActivityService, Depends(get_activity_service)],
):
    """
    Retrieve the public learning activity definition, materials, parent instructions,
    and progressive hints. Internal answer keys and evaluator configs are strictly excluded.
    """
    return await activity_service.get_activity_public(activity_id=activity_id)
