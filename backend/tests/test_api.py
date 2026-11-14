from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base, get_db
from backend.app.main import app
from backend.app.models import AlertRecord, AstronautRecord, MeasurementRecord
from backend.app.services.simulation import seed_synthetic_scenario


@pytest.fixture
def session_factory(tmp_path: Path):
    database_path = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{database_path}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    yield factory
    engine.dispose()


@pytest.fixture
def client(session_factory):
    def override_db():
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def create_astronaut(client: TestClient, name: str = "Synthetic Test Crew") -> dict:
    response = client.post("/api/v1/astronauts", json={"display_name": name})
    assert response.status_code == 201
    return response.json()


def measurement_payload(timestamp: str, metric: str = "sleep_hours") -> dict:
    units = {"sleep_hours": "h", "resting_heart_rate": "bpm"}
    return {
        "measured_at": timestamp,
        "metric": metric,
        "value": 7.2 if metric == "sleep_hours" else 62,
        "unit": units[metric],
        "source": "synthetic fixture",
    }


def test_health_and_mission_context(client: TestClient):
    assert client.get("/api/v1/health").json() == {"status": "ok", "api_version": "v1"}
    assert client.get("/api/v1/mission-context").json()["is_synthetic"] is True


def test_create_read_and_persist_across_sessions(client: TestClient, session_factory):
    astronaut = create_astronaut(client)
    response = client.post(
        f"/api/v1/astronauts/{astronaut['id']}/measurements",
        json=measurement_payload("2026-10-01T08:00:00Z"),
    )
    assert response.status_code == 201
    with session_factory() as reopened_session:
        stored = reopened_session.get(AstronautRecord, astronaut["id"])
        assert stored is not None
        assert stored.display_name == "Synthetic Test Crew"
        count = reopened_session.scalar(select(func.count()).select_from(MeasurementRecord))
        assert count == 1


def test_rejects_invalid_inputs(client: TestClient):
    astronaut = create_astronaut(client)
    response = client.post(
        f"/api/v1/astronauts/{astronaut['id']}/measurements",
        json={
            "measured_at": "2026-10-01T08:00:00",
            "metric": "sleep_hours",
            "value": 7.2,
            "unit": "hours",
        },
    )
    assert response.status_code == 422
    assert client.get("/api/v1/astronauts?limit=0").status_code == 422


def test_unknown_astronaut_returns_404(client: TestClient):
    unknown = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
    assert client.get(f"/api/v1/astronauts/{unknown}").status_code == 404
    assert client.get(f"/api/v1/astronauts/{unknown}/measurements").status_code == 404
    assert client.get(f"/api/v1/astronauts/{unknown}/alerts").status_code == 404


def test_measurement_filtering_ordering_and_pagination(client: TestClient):
    astronaut = create_astronaut(client)
    base = f"/api/v1/astronauts/{astronaut['id']}/measurements"
    payloads = [
        measurement_payload("2026-10-03T08:00:00Z"),
        measurement_payload("2026-10-01T08:00:00Z", "resting_heart_rate"),
        measurement_payload("2026-10-02T08:00:00Z"),
    ]
    for payload in payloads:
        assert client.post(base, json=payload).status_code == 201
    response = client.get(
        base,
        params={
            "metric": "sleep_hours",
            "from_time": "2026-10-02T00:00:00Z",
            "limit": 1,
        },
    )
    assert response.status_code == 200
    assert [item["measured_at"] for item in response.json()] == ["2026-10-02T08:00:00Z"]
    assert client.get(
        base,
        params={"from_time": "2026-10-03T00:00:00Z", "to_time": "2026-10-01T00:00:00Z"},
    ).status_code == 422


def test_duplicate_measurement_and_checkin_return_409(client: TestClient):
    astronaut = create_astronaut(client)
    measurements = f"/api/v1/astronauts/{astronaut['id']}/measurements"
    payload = measurement_payload("2026-10-01T08:00:00Z")
    assert client.post(measurements, json=payload).status_code == 201
    assert client.post(measurements, json=payload).status_code == 409
    checkins = f"/api/v1/astronauts/{astronaut['id']}/checkins"
    checkin = {"recorded_at": "2026-10-01T18:00:00Z", "mood": 4}
    assert client.post(checkins, json=checkin).status_code == 201
    assert client.post(checkins, json=checkin).status_code == 409


def test_repeatable_simulation_is_idempotent(session_factory):
    with session_factory() as session:
        first = seed_synthetic_scenario(session)
        second = seed_synthetic_scenario(session)
        assert first.measurements_created == 5
        assert second.astronauts_created == 0
        assert second.measurements_created == 0
        assert second.checkins_created == 0
        assert session.scalar(select(func.count()).select_from(MeasurementRecord)) == 5


def test_foreign_keys_reject_orphan_records(session_factory):
    with session_factory() as session:
        session.add(
            MeasurementRecord(
                astronaut_id="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
                measured_at=datetime(2026, 10, 1, tzinfo=UTC),
                metric="sleep_hours",
                value=7.0,
                unit="h",
                source="synthetic fixture",
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()


def test_persisted_alerts_are_returned_and_filterable(client: TestClient, session_factory):
    astronaut = create_astronaut(client)
    with session_factory() as session:
        session.add(
            AlertRecord(
                astronaut_id=astronaut["id"],
                created_at=datetime(2026, 10, 2, tzinfo=UTC),
                title="Synthetic review marker",
                detail="Synthetic test record; not a clinical alert.",
                status="open",
            )
        )
        session.commit()
    response = client.get(
        f"/api/v1/astronauts/{astronaut['id']}/alerts", params={"status": "open"}
    )
    assert response.status_code == 200
    assert response.json()[0]["title"] == "Synthetic review marker"


def test_assessment_integrates_and_persists_package_outputs(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
):
    astronaut = create_astronaut(client)
    calls: dict[str, object] = {}

    def fake_analyze(history, baseline, context):
        calls.update(history=history, baseline=baseline, context=context)
        return [{
            "code": "test_finding",
            "title": "Synthetic finding",
            "detail": "Adapter test",
            "evidence": ["synthetic:test"],
            "data_status": "observed",
        }]

    def fake_guidance(findings, checkin, context):
        calls.update(findings=findings, checkin=checkin)
        return [{
            "id": "test-action",
            "title": "Review synthetic data",
            "rationale": "Adapter test",
            "evidence_links": ["finding:test_finding"],
            "urgency": "routine",
        }]

    monkeypatch.setattr("backend.app.services.assessments.analyze_health", fake_analyze)
    monkeypatch.setattr("backend.app.services.assessments.generate_guidance", fake_guidance)
    response = client.post(f"/api/v1/astronauts/{astronaut['id']}/assessments")
    assert response.status_code == 201
    assert response.json()["findings"][0]["code"] == "test_finding"
    assert calls["baseline"] is None
    listed = client.get(f"/api/v1/astronauts/{astronaut['id']}/assessments").json()
    assert len(listed) == 1

