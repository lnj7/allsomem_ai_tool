import uuid

from app.main import app
from fastapi.testclient import TestClient


def test_register_login_me_onboarding() -> None:
    client = TestClient(app)
    email = f"founder-{uuid.uuid4().hex[:8]}@example.com"
    register = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123", "full_name": "Founder"},
    )
    assert register.status_code == 200, register.text
    login = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    assert login.status_code == 200
    me = client.get("/api/v1/auth/me")
    assert me.status_code == 200
    assert me.json()["email"] == email
    saved = client.post(
        "/api/v1/onboarding",
        json={
            "step": 6,
            "complete": True,
            "data": {"name": "Founder", "primary_goal": "grow audience"},
        },
    )
    assert saved.status_code == 200
    assert saved.json()["completed"] is True
    creator = client.get("/api/v1/creators/me")
    assert creator.status_code == 200
    generate = client.post("/api/v1/onboarding/generate-profile")
    assert generate.status_code == 503
    assert "AI provider is not configured" in generate.json()["error"]["message"]
