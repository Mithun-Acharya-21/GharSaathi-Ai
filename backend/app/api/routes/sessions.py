from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_bearer_token, get_session_service
from app.schemas.common import MessageResponse
from app.schemas.session import (
    SessionCompleteResponse,
    SessionCreateRequest,
    SessionCreateResponse,
    SessionDetailResponse,
)
from app.services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post(
    "",
    response_model=SessionCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create anonymous learning session",
)
async def create_session(
    req: SessionCreateRequest,
    session_service: Annotated[SessionService, Depends(get_session_service)],
):
    """
    Create a new anonymous learning session with guardian consent acknowledgement.
    Generates a secure bearer token returned only once in this response.
    """
    return await session_service.create_session(req)


@router.get(
    "/{session_id}",
    response_model=SessionDetailResponse,
    summary="Get current session state",
)
async def get_session(
    session_id: str,
    bearer_token: Annotated[str, Depends(get_bearer_token)],
    session_service: Annotated[SessionService, Depends(get_session_service)],
):
    """Retrieve session state and previous attempt results after validating ownership with the bearer token."""
    return await session_service.get_session_detail(
        session_id=session_id, bearer_token=bearer_token
    )


@router.post(
    "/{session_id}/complete",
    response_model=SessionCompleteResponse,
    summary="Complete learning session",
)
async def complete_session(
    session_id: str,
    bearer_token: Annotated[str, Depends(get_bearer_token)],
    session_service: Annotated[SessionService, Depends(get_session_service)],
):
    """Mark the session as completed after all activities and attempts are evaluated."""
    return await session_service.complete_session(session_id=session_id, bearer_token=bearer_token)


@router.delete(
    "/{session_id}",
    response_model=MessageResponse,
    summary="Delete learning session and attempt data",
)
async def delete_session(
    session_id: str,
    bearer_token: Annotated[str, Depends(get_bearer_token)],
    session_service: Annotated[SessionService, Depends(get_session_service)],
):
    """Delete the caller's session and all related attempts from the database for data privacy compliance."""
    await session_service.delete_session(session_id=session_id, bearer_token=bearer_token)
    return MessageResponse(message="Session and associated attempt data successfully deleted.")
