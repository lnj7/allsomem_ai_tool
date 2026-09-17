from app.api.deps import get_health_service
from app.main import app
from app.schemas.health import HealthLiveResponse, HealthReadyResponse
from app.services.health_service import HealthService
from fastapi.testclient import TestClient


class StubHealthService(HealthService):
    def __init__(self, ready: bool = True) -> None:
        self.ready = ready

    def liveness(self) -> HealthLiveResponse:
        return HealthLiveResponse()

    def readiness(self) -> tuple[HealthReadyResponse, int]:
        if self.ready:
            return HealthReadyResponse(status="ready", database="ok", redis="ok"), 200
        return HealthReadyResponse(status="not_ready", database="unavailable", redis="ok"), 503


def test_health_ok() -> None:
    app.dependency_overrides[get_health_service] = lambda: StubHealthService()
    client = TestClient(app)
    response = client.get("/health")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "creatoros-api"}


def test_ready_ok() -> None:
    app.dependency_overrides[get_health_service] = lambda: StubHealthService(ready=True)
    client = TestClient(app)
    response = client.get("/health/ready")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["database"] == "ok"
    assert body["redis"] == "ok"


def test_ready_unavailable() -> None:
    app.dependency_overrides[get_health_service] = lambda: StubHealthService(ready=False)
    client = TestClient(app)
    response = client.get("/health/ready")
    app.dependency_overrides.clear()
    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"
