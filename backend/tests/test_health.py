from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_returns_healthy():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "ai-studymate-backend",
    }


def test_generate_rejects_empty_notes():
    response = client.post("/generate", json={"notes": ""})

    assert response.status_code == 422


def test_generate_rejects_short_notes():
    response = client.post("/generate", json={"notes": "too short"})

    assert response.status_code == 422
