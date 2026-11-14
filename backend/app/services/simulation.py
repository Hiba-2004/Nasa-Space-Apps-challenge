from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import NAMESPACE_URL, uuid5

from sqlalchemy.orm import Session

from backend.app.models import AstronautRecord, CheckInRecord, MeasurementRecord

SCENARIO_KEY = "astravital:synthetic:starter:v1"


@dataclass(frozen=True)
class SeedResult:
    astronaut_id: str
    astronauts_created: int
    measurements_created: int
    checkins_created: int


def deterministic_id(kind: str, key: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"{SCENARIO_KEY}:{kind}:{key}"))


def seed_synthetic_scenario(db: Session) -> SeedResult:
    """Insert a deterministic fictional scenario; repeated calls create nothing."""
    astronaut_id = deterministic_id("astronaut", "crew-a")
    astronauts_created = 0
    measurements_created = 0
    checkins_created = 0
    if db.get(AstronautRecord, astronaut_id) is None:
        db.add(
            AstronautRecord(
                id=astronaut_id,
                display_name="Synthetic Crew A",
                mission_role="Synthetic flight engineer",
                created_at=datetime(2026, 10, 1, 7, 30, tzinfo=UTC),
            )
        )
        astronauts_created = 1

    observations = [
        ("resting_heart_rate", 62.0, "bpm"),
        ("sleep_hours", 7.2, "h"),
        ("body_temperature", 36.7, "Cel"),
        ("blood_pressure_systolic", 118.0, "mmHg"),
        ("blood_pressure_diastolic", 76.0, "mmHg"),
    ]
    measured_at = datetime(2026, 10, 1, 8, 0, tzinfo=UTC)
    for metric, value, unit in observations:
        record_id = deterministic_id("measurement", f"{measured_at.isoformat()}:{metric}")
        if db.get(MeasurementRecord, record_id) is None:
            db.add(
                MeasurementRecord(
                    id=record_id,
                    astronaut_id=astronaut_id,
                    measured_at=measured_at,
                    metric=metric,
                    value=value,
                    unit=unit,
                    source="synthetic seeded scenario",
                )
            )
            measurements_created += 1

    checkin_at = measured_at + timedelta(hours=10)
    checkin_id = deterministic_id("checkin", checkin_at.isoformat())
    if db.get(CheckInRecord, checkin_id) is None:
        db.add(
            CheckInRecord(
                id=checkin_id,
                astronaut_id=astronaut_id,
                recorded_at=checkin_at,
                mood=4,
                fatigue=None,
                notes="Synthetic scenario; fatigue was not reported.",
            )
        )
        checkins_created = 1

    db.commit()
    return SeedResult(
        astronaut_id=astronaut_id,
        astronauts_created=astronauts_created,
        measurements_created=measurements_created,
        checkins_created=checkins_created,
    )

