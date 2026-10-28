from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_teacher_service, verify_teacher_auth
from app.schemas.teacher import ReviewQueueItem, TeacherReportResponse
from app.services.teacher_service import TeacherService

router = APIRouter(
    prefix="/teacher",
    tags=["Teacher Reporting & Review"],
    dependencies=[Depends(verify_teacher_auth)],
)


@router.get(
    "/reports",
    response_model=TeacherReportResponse,
    summary="Get aggregate learning analytics",
)
async def get_teacher_reports(
    teacher_service: Annotated[TeacherService, Depends(get_teacher_service)],
    grade: Annotated[
        int | None, Query(ge=1, le=6, description="Filter reports by grade (1 to 6)")
    ] = None,
):
    """
    Retrieve aggregate statistics on activities, sessions, and mathematically evaluated attempts.
    Contains no personally identifiable student information. Protected by X-Teacher-API-Key.
    """
    return await teacher_service.get_reports(grade=grade)


@router.get(
    "/review-queue",
    response_model=list[ReviewQueueItem],
    summary="Get anonymized review queue",
)
async def get_review_queue(
    teacher_service: Annotated[TeacherService, Depends(get_teacher_service)],
    grade: Annotated[
        int | None, Query(ge=1, le=6, description="Filter queue by grade (1 to 6)")
    ] = None,
):
    """
    Retrieve anonymized attempts requiring human review (ambiguous spoken responses or unexpected inputs).
    Protected by X-Teacher-API-Key.
    """
    return await teacher_service.get_review_queue(grade=grade)
