from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


class AppException(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(code="NOT_FOUND", message=message, status_code=status.HTTP_404_NOT_FOUND)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Authentication required or invalid credentials"):
        super().__init__(
            code="UNAUTHORIZED", message=message, status_code=status.HTTP_401_UNAUTHORIZED
        )


class ForbiddenException(AppException):
    def __init__(self, message: str = "Operation not permitted"):
        super().__init__(code="FORBIDDEN", message=message, status_code=status.HTTP_403_FORBIDDEN)


class ExpiredSessionException(AppException):
    def __init__(self, message: str = "Session has expired"):
        super().__init__(
            code="SESSION_EXPIRED", message=message, status_code=status.HTTP_401_UNAUTHORIZED
        )


class InvalidStateTransitionException(AppException):
    def __init__(self, message: str = "Invalid state transition"):
        super().__init__(
            code="INVALID_STATE", message=message, status_code=status.HTTP_400_BAD_REQUEST
        )


class UnsupportedMediaTypeException(AppException):
    def __init__(self, message: str = "Unsupported media type"):
        super().__init__(
            code="UNSUPPORTED_MEDIA_TYPE",
            message=message,
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )


class PayloadTooLargeException(AppException):
    def __init__(self, message: str = "File size exceeds allowed limit"):
        super().__init__(
            code="PAYLOAD_TOO_LARGE",
            message=message,
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        )


class RateLimitException(AppException):
    def __init__(self, message: str = "Rate limit or transcription quota exceeded"):
        super().__init__(
            code="RATE_LIMIT_EXCEEDED",
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


class UpstreamServiceException(AppException):
    def __init__(self, message: str = "External service integration error"):
        super().__init__(
            code="UPSTREAM_SERVICE_ERROR",
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
        )


class UpstreamTimeoutException(AppException):
    def __init__(self, message: str = "External service timed out"):
        super().__init__(
            code="UPSTREAM_TIMEOUT",
            message=message,
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        )


class ServiceUnavailableException(AppException):
    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(
            code="SERVICE_UNAVAILABLE",
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        req_id = getattr(request.state, "request_id", str(uuid4()))
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "request_id": req_id,
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        req_id = getattr(request.state, "request_id", str(uuid4()))
        # Format human-friendly validation error message
        errors = exc.errors()
        first_msg = errors[0]["msg"] if errors else "Invalid request data."
        loc = " -> ".join(str(part) for part in errors[0]["loc"]) if errors else ""
        detail_msg = f"{loc}: {first_msg}" if loc else first_msg

        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": f"Validation failed: {detail_msg}",
                    "request_id": req_id,
                }
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        req_id = getattr(request.state, "request_id", str(uuid4()))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred. Please try again later.",
                    "request_id": req_id,
                }
            },
        )
