from typing import Annotated

import httpx
from fastapi import Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.errors import UnauthorizedException
from app.core.security import verify_teacher_key
from app.db.session import get_db
from app.integrations.gnani_prisma import GnaniPrismaClient, PrismaClientProtocol
from app.integrations.gnani_timbre import GnaniTimbreClient, TimbreClientProtocol
from app.repositories.activity_repository import ActivityRepository
from app.repositories.attempt_repository import AttemptRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.teacher_repository import TeacherRepository
from app.services.activity_service import ActivityService
from app.services.attempt_service import AttemptService
from app.services.session_service import SessionService
from app.services.teacher_service import TeacherService


def get_shared_http_client(request: Request) -> httpx.AsyncClient:
    client = getattr(request.app.state, "http_client", None)
    if client is None:
        # Fallback if accessed outside lifespan (e.g. standalone test)
        client = httpx.AsyncClient()
    return client


def get_bearer_token(
    authorization: Annotated[str | None, Header(description="Bearer <session_token>")] = None,
) -> str:
    if not authorization:
        raise UnauthorizedException("Authorization header with Bearer token is required.")

    parts = authorization.strip().split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedException("Invalid Authorization format. Expected 'Bearer <token>'.")

    token = parts[1].strip()
    if not token:
        raise UnauthorizedException("Session bearer token cannot be empty.")

    return token


def verify_teacher_auth(
    x_teacher_api_key: Annotated[str | None, Header(alias="X-Teacher-API-Key")] = None,
    settings: Annotated[Settings, Depends(get_settings)] = None,
) -> None:
    if not verify_teacher_key(x_teacher_api_key, settings.TEACHER_API_KEY):
        raise UnauthorizedException("Missing or invalid X-Teacher-API-Key.")


# Provider dependencies (overridable in tests via app.dependency_overrides)
def get_prisma_client(
    http_client: Annotated[httpx.AsyncClient, Depends(get_shared_http_client)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> PrismaClientProtocol:
    return GnaniPrismaClient(http_client=http_client, settings=settings)


def get_timbre_client(
    http_client: Annotated[httpx.AsyncClient, Depends(get_shared_http_client)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TimbreClientProtocol:
    return GnaniTimbreClient(http_client=http_client, settings=settings)


# Repository dependencies
def get_activity_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ActivityRepository:
    return ActivityRepository(db)


def get_session_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SessionRepository:
    return SessionRepository(db)


def get_attempt_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AttemptRepository:
    return AttemptRepository(db)


def get_teacher_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TeacherRepository:
    return TeacherRepository(db)


# Service dependencies
def get_activity_service(
    activity_repo: Annotated[ActivityRepository, Depends(get_activity_repository)],
) -> ActivityService:
    return ActivityService(activity_repo)


def get_session_service(
    session_repo: Annotated[SessionRepository, Depends(get_session_repository)],
    activity_repo: Annotated[ActivityRepository, Depends(get_activity_repository)],
) -> SessionService:
    return SessionService(session_repo, activity_repo)


def get_attempt_service(
    attempt_repo: Annotated[AttemptRepository, Depends(get_attempt_repository)],
    session_repo: Annotated[SessionRepository, Depends(get_session_repository)],
    activity_repo: Annotated[ActivityRepository, Depends(get_activity_repository)],
    session_service: Annotated[SessionService, Depends(get_session_service)],
    prisma_client: Annotated[PrismaClientProtocol, Depends(get_prisma_client)],
) -> AttemptService:
    return AttemptService(
        attempt_repo=attempt_repo,
        session_repo=session_repo,
        activity_repo=activity_repo,
        session_service=session_service,
        prisma_client=prisma_client,
    )


def get_teacher_service(
    teacher_repo: Annotated[TeacherRepository, Depends(get_teacher_repository)],
    attempt_repo: Annotated[AttemptRepository, Depends(get_attempt_repository)],
) -> TeacherService:
    return TeacherService(teacher_repo, attempt_repo)
