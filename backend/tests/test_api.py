from fastapi.testclient import TestClient

from backend.app.main import app


def test_health_and_mission_context():
    with TestClient(app) as client:
        assert client.get("/api/v1/health").json() == {"status": "ok", "api_version": "v1"}
        context = client.get("/api/v1/mission-context").json()
        assert context["is_synthetic"] is True


def test_create_astronaut_and_measurement():
    with TestClient(app) as client:
        astronaut = client.post(
            "/api/v1/astronauts", json={"display_name": "Synthetic Test Crew"}
        ).json()
        response = client.post(
            f"/api/v1/astronauts/{astronaut['id']}/measurements",
            json={"measured_at": "2026-10-01T08:00:00Z", "metric": "sleep_hours",
                  "value": 7.2, "unit": "h", "source": "synthetic fixture"},
        )
        assert response.status_code == 201
        assert response.json()["unit"] == "h"


def test_rejects_wrong_unit_and_naive_timestamp():
    with TestClient(app) as client:
        astronaut = client.post("/api/v1/astronauts", json={"display_name": "Synthetic"}).json()
        response = client.post(
            f"/api/v1/astronauts/{astronaut['id']}/measurements",
            json={"measured_at": "2026-10-01T08:00:00", "metric": "sleep_hours",
                  "value": 7.2, "unit": "hours"},
        )
        assert response.status_code == 422

