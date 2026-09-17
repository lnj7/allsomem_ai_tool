import os

import pytest
from app.main import app
from fastapi.testclient import TestClient


@pytest.mark.skipif(os.getenv("RUN_INTEGRATION") != "1", reason="Requires local Postgres and Redis")
def test_ready_against_live_dependencies() -> None:
    client = TestClient(app)
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["database"] == "ok"
    assert response.json()["redis"] == "ok"
