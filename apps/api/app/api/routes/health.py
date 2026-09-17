from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.api.deps import get_health_service
from app.schemas.health import HealthLiveResponse, HealthReadyResponse
from app.services.health_service import HealthService

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthLiveResponse)
def health(service: HealthService = Depends(get_health_service)) -> HealthLiveResponse:
    return service.liveness()


@router.get("/health/ready", response_model=HealthReadyResponse)
def health_ready(
    request: Request,
    service: HealthService = Depends(get_health_service),
) -> JSONResponse:
    payload, status_code = service.readiness()
    payload.request_id = getattr(request.state, "request_id", None)
    return JSONResponse(status_code=status_code, content=payload.model_dump())
