from fastapi import APIRouter

from app.api.routes import activities, attempts, sessions, speech, teacher

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(activities.router)
api_router.include_router(sessions.router)
api_router.include_router(attempts.router)
api_router.include_router(speech.router)
api_router.include_router(teacher.router)
