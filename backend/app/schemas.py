from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


def utc_now() -> datetime:
    return datetime.now(UTC)


class ApiModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")


class MeasurementMetric(StrEnum):
    RESTING_HEART_RATE = "resting_heart_rate"
    SLEEP_HOURS = "sleep_hours"
    BODY_TEMPERATURE = "body_temperature"
    BLOOD_PRESSURE_SYSTOLIC = "blood_pressure_systolic"
    BLOOD_PRESSURE_DIASTOLIC = "blood_pressure_diastolic"


EXPECTED_UNITS = {
    MeasurementMetric.RESTING_HEART_RATE: "bpm",
    MeasurementMetric.SLEEP_HOURS: "h",
    MeasurementMetric.BODY_TEMPERATURE: "Cel",
    MeasurementMetric.BLOOD_PRESSURE_SYSTOLIC: "mmHg",
    MeasurementMetric.BLOOD_PRESSURE_DIASTOLIC: "mmHg",
}


class AstronautCreate(ApiModel):
    display_name: Annotated[str, Field(min_length=1, max_length=100, examples=["Synthetic Crew A"])]
    mission_role: Annotated[str | None, Field(max_length=100)] = None


class Astronaut(AstronautCreate):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=utc_now)


class HealthMeasurementCreate(ApiModel):
    measured_at: datetime = Field(examples=["2026-10-01T08:00:00Z"])
    metric: MeasurementMetric
    value: float = Field(examples=[62.0])
    unit: str = Field(min_length=1, max_length=20, examples=["bpm"])
    source: Annotated[str | None, Field(max_length=100)] = None

    @model_validator(mode="after")
    def validate_timestamp_and_unit(self):
        if self.measured_at.tzinfo is None or self.measured_at.utcoffset() is None:
            raise ValueError("measured_at must include a UTC offset")
        if self.measured_at.utcoffset().total_seconds() != 0:
            raise ValueError("measured_at must be UTC")
        expected = EXPECTED_UNITS[self.metric]
        if self.unit != expected:
            raise ValueError(f"unit for {self.metric.value} must be {expected}")
        return self


class HealthMeasurement(HealthMeasurementCreate):
    id: UUID = Field(default_factory=uuid4)
    astronaut_id: UUID


class CheckInCreate(ApiModel):
    recorded_at: datetime
    mood: Annotated[int | None, Field(ge=1, le=5, description="Self-reported 1–5 scale")] = None
    fatigue: Annotated[int | None, Field(ge=1, le=5, description="Self-reported 1–5 scale")] = None
    notes: Annotated[str | None, Field(max_length=1000)] = None

    @model_validator(mode="after")
    def validate_checkin(self):
        if self.recorded_at.tzinfo is None or self.recorded_at.utcoffset() is None:
            raise ValueError("recorded_at must include a UTC offset")
        if self.recorded_at.utcoffset().total_seconds() != 0:
            raise ValueError("recorded_at must be UTC")
        if self.mood is None and self.fatigue is None and self.notes is None:
            raise ValueError("at least one check-in field must be supplied")
        return self


class CheckIn(CheckInCreate):
    id: UUID = Field(default_factory=uuid4)
    astronaut_id: UUID


class Finding(ApiModel):
    code: str
    title: str
    detail: str
    evidence: list[str] = Field(default_factory=list)
    data_status: str = Field(description="observed, insufficient_data, or unavailable")


class GuidanceAction(ApiModel):
    id: str
    title: str
    rationale: str
    evidence_links: list[str] = Field(default_factory=list)
    urgency: str = "routine"


class HealthAssessment(ApiModel):
    id: UUID = Field(default_factory=uuid4)
    astronaut_id: UUID
    created_at: datetime = Field(default_factory=utc_now)
    findings: list[Finding]
    guidance_actions: list[GuidanceAction]
    summary: str
    disclaimer: str = "Decision support only; not a diagnosis or validated risk prediction."


class Alert(ApiModel):
    id: UUID
    astronaut_id: UUID
    created_at: datetime
    title: str
    detail: str
    status: str


class MissionContext(ApiModel):
    mission_name: str
    mission_day: int = Field(ge=0)
    communication_delay_minutes: float = Field(ge=0)
    environment: str = "simulated"
    is_synthetic: bool = True


class AstronautReport(ApiModel):
    astronaut: Astronaut
    measurements: list[HealthMeasurement]
    checkins: list[CheckIn]
    assessments: list[HealthAssessment]
    generated_at: datetime = Field(default_factory=utc_now)
    data_notice: str = "Missing values are omitted, never interpreted as normal."


class HealthResponse(ApiModel):
    status: str = "ok"
    api_version: str = "v1"

