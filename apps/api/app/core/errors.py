from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import Settings
from app.schemas.health import ErrorBody, ErrorResponse


def register_exception_handlers(app: FastAPI, settings: Settings) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None) or str(uuid4())
        payload = ErrorResponse(
            error=ErrorBody(
                code="VALIDATION_ERROR",
                message="Request validation failed.",
                request_id=request_id,
                details=None if settings.is_production else exc.errors(),
            )
        )
        return JSONResponse(status_code=422, content=payload.model_dump())

    @app.exception_handler(StarletteHTTPException)
    async def http_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None) or str(uuid4())
        payload = ErrorResponse(
            error=ErrorBody(
                code="HTTP_ERROR",
                message=str(exc.detail),
                request_id=request_id,
            )
        )
        return JSONResponse(status_code=exc.status_code, content=payload.model_dump())

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, _exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None) or str(uuid4())
        message = "An unexpected error occurred."
        payload = ErrorResponse(
            error=ErrorBody(
                code="INTERNAL_ERROR",
                message=message,
                request_id=request_id,
            )
        )
        return JSONResponse(status_code=500, content=payload.model_dump())
