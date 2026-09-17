from typing import Any

from pydantic import BaseModel, Field


class ErrorBody(BaseModel):
    code: str
    message: str
    request_id: str | None = None
    details: Any | None = None


class ErrorResponse(BaseModel):
    error: ErrorBody


class HealthLiveResponse(BaseModel):
    status: str = "ok"
    service: str = "creatoros-api"


class HealthReadyResponse(BaseModel):
    status: str
    database: str
    redis: str
    request_id: str | None = Field(default=None)
