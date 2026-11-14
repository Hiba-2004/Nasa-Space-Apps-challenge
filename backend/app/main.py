from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.config import get_settings
from backend.app.database import Base, engine, get_db
from backend.app.models import (
    AlertRecord,
    AssessmentRecord,
    AstronautRecord,
    CheckInRecord,
    MeasurementRecord,
)
from backend.app.schemas import (
    Alert,
    Astronaut,
    AstronautCreate,
    AstronautReport,
    CheckIn,
    CheckInCreate,
    HealthAssessment,
    HealthMeasurement,
    HealthMeasurementCreate,
    HealthResponse,
    MeasurementMetric,
    MissionContext,
    utc_now,
)
from backend.app.services.assessments import build_assessment

DbSession = Annotated[Session, Depends(get_db)]
PageOffset = Annotated[int, Query(ge=0, description="Number of records to skip")]
PageLimit = Annotated[int, Query(ge=1, le=500, description="Maximum records to return")]


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="ASTRAVITAL API",
    version="1.0.0",
    description=(
        "Offline-first astronaut health decision-support prototype. Synthetic examples only; "
        "not a medical device or diagnostic system."
    ),
    lifespan=lifespan,
)
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def require_astronaut(db: Session, astronaut_id: UUID) -> AstronautRecord:
    record = db.get(AstronautRecord, str(astronaut_id))
    if record is None:
        raise HTTPException(status_code=404, detail="Astronaut not found")
    return record


def as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value


def commit_or_conflict(db: Session, detail: str) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail) from exc


def validate_date_range(from_time: datetime | None, to_time: datetime | None) -> None:
    for name, value in (("from_time", from_time), ("to_time", to_time)):
        if value is not None and (value.tzinfo is None or value.utcoffset() != UTC.utcoffset(value)):
            raise HTTPException(status_code=422, detail=f"{name} must be an ISO-8601 UTC timestamp")
    if from_time is not None and to_time is not None and from_time > to_time:
        raise HTTPException(status_code=422, detail="from_time must be before or equal to to_time")


def astronaut_schema(record: AstronautRecord) -> Astronaut:
    return Astronaut(id=record.id, display_name=record.display_name,
                     mission_role=record.mission_role, created_at=as_utc(record.created_at))


def measurement_schema(record: MeasurementRecord) -> HealthMeasurement:
    return HealthMeasurement(id=record.id, astronaut_id=record.astronaut_id,
                             measured_at=as_utc(record.measured_at), metric=record.metric,
                             value=record.value, unit=record.unit, source=record.source)


def checkin_schema(record: CheckInRecord) -> CheckIn:
    return CheckIn(id=record.id, astronaut_id=record.astronaut_id,
                   recorded_at=as_utc(record.recorded_at), mood=record.mood,
                   fatigue=record.fatigue, notes=record.notes)


def assessment_schema(record: AssessmentRecord) -> HealthAssessment:
    return HealthAssessment(id=record.id, astronaut_id=record.astronaut_id,
                            created_at=as_utc(record.created_at), findings=record.findings,
                            guidance_actions=record.guidance_actions, summary=record.summary)


def alert_schema(record: AlertRecord) -> Alert:
    return Alert(
        id=record.id,
        astronaut_id=record.astronaut_id,
        created_at=as_utc(record.created_at),
        title=record.title,
        detail=record.detail,
        status=record.status,
    )


@app.get("/api/v1/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    return HealthResponse()


@app.get("/api/v1/astronauts", response_model=list[Astronaut], tags=["astronauts"])
def list_astronauts(
    db: DbSession, offset: PageOffset = 0, limit: PageLimit = 100
) -> list[Astronaut]:
    query = select(AstronautRecord).order_by(
        AstronautRecord.created_at, AstronautRecord.id
    ).offset(offset).limit(limit)
    records = db.scalars(query).all()
    return [astronaut_schema(item) for item in records]


@app.post("/api/v1/astronauts", response_model=Astronaut,
          status_code=status.HTTP_201_CREATED, tags=["astronauts"])
def create_astronaut(payload: AstronautCreate, db: DbSession) -> Astronaut:
    record = AstronautRecord(**payload.model_dump(), created_at=utc_now())
    db.add(record)
    commit_or_conflict(db, "Astronaut conflicts with an existing record")
    return astronaut_schema(record)


@app.get("/api/v1/astronauts/{astronaut_id}", response_model=Astronaut, tags=["astronauts"])
def get_astronaut(astronaut_id: UUID, db: DbSession) -> Astronaut:
    return astronaut_schema(require_astronaut(db, astronaut_id))


@app.get("/api/v1/astronauts/{astronaut_id}/measurements",
         response_model=list[HealthMeasurement], tags=["measurements"])
def list_measurements(
    astronaut_id: UUID,
    db: DbSession,
    offset: PageOffset = 0,
    limit: PageLimit = 100,
    metric: Annotated[MeasurementMetric | None, Query(description="Exact measurement metric")] = None,
    from_time: Annotated[datetime | None, Query(description="Inclusive UTC lower bound")] = None,
    to_time: Annotated[datetime | None, Query(description="Inclusive UTC upper bound")] = None,
) -> list[HealthMeasurement]:
    require_astronaut(db, astronaut_id)
    validate_date_range(from_time, to_time)
    query = select(MeasurementRecord).where(
        MeasurementRecord.astronaut_id == str(astronaut_id)
    )
    if metric is not None:
        query = query.where(MeasurementRecord.metric == metric.value)
    if from_time is not None:
        query = query.where(MeasurementRecord.measured_at >= from_time)
    if to_time is not None:
        query = query.where(MeasurementRecord.measured_at <= to_time)
    query = query.order_by(MeasurementRecord.measured_at, MeasurementRecord.id).offset(
        offset
    ).limit(limit)
    return [measurement_schema(item) for item in db.scalars(query).all()]


@app.post("/api/v1/astronauts/{astronaut_id}/measurements",
          response_model=HealthMeasurement, status_code=201, tags=["measurements"])
def create_measurement(astronaut_id: UUID, payload: HealthMeasurementCreate,
                       db: DbSession) -> HealthMeasurement:
    require_astronaut(db, astronaut_id)
    record = MeasurementRecord(astronaut_id=str(astronaut_id), **payload.model_dump())
    db.add(record)
    commit_or_conflict(db, "A measurement for this metric and timestamp already exists")
    return measurement_schema(record)


@app.get("/api/v1/astronauts/{astronaut_id}/checkins",
         response_model=list[CheckIn], tags=["check-ins"])
def list_checkins(
    astronaut_id: UUID,
    db: DbSession,
    offset: PageOffset = 0,
    limit: PageLimit = 100,
    from_time: Annotated[datetime | None, Query(description="Inclusive UTC lower bound")] = None,
    to_time: Annotated[datetime | None, Query(description="Inclusive UTC upper bound")] = None,
) -> list[CheckIn]:
    require_astronaut(db, astronaut_id)
    validate_date_range(from_time, to_time)
    query = select(CheckInRecord).where(
        CheckInRecord.astronaut_id == str(astronaut_id)
    )
    if from_time is not None:
        query = query.where(CheckInRecord.recorded_at >= from_time)
    if to_time is not None:
        query = query.where(CheckInRecord.recorded_at <= to_time)
    query = query.order_by(CheckInRecord.recorded_at, CheckInRecord.id).offset(offset).limit(limit)
    return [checkin_schema(item) for item in db.scalars(query).all()]


@app.post("/api/v1/astronauts/{astronaut_id}/checkins", response_model=CheckIn,
          status_code=201, tags=["check-ins"])
def create_checkin(astronaut_id: UUID, payload: CheckInCreate,
                   db: DbSession) -> CheckIn:
    require_astronaut(db, astronaut_id)
    record = CheckInRecord(astronaut_id=str(astronaut_id), **payload.model_dump())
    db.add(record)
    commit_or_conflict(db, "A check-in for this timestamp already exists")
    return checkin_schema(record)


@app.post("/api/v1/astronauts/{astronaut_id}/assessments",
          response_model=HealthAssessment, status_code=201, tags=["assessments"])
def create_assessment(astronaut_id: UUID, db: DbSession) -> HealthAssessment:
    require_astronaut(db, astronaut_id)
    measurements = list_measurements(astronaut_id, db, limit=500)
    checkins = list_checkins(astronaut_id, db, limit=500)
    context = mission_context().model_dump()
    history = [item.model_dump(mode="json") for item in measurements]
    last_checkin = checkins[-1].model_dump(mode="json") if checkins else None
    record = build_assessment(str(astronaut_id), history, last_checkin, context)
    db.add(record)
    db.commit()
    return assessment_schema(record)


@app.get("/api/v1/astronauts/{astronaut_id}/assessments",
         response_model=list[HealthAssessment], tags=["assessments"])
def list_assessments(
    astronaut_id: UUID,
    db: DbSession,
    offset: PageOffset = 0,
    limit: PageLimit = 100,
) -> list[HealthAssessment]:
    require_astronaut(db, astronaut_id)
    query = select(AssessmentRecord).where(
        AssessmentRecord.astronaut_id == str(astronaut_id)
    ).order_by(AssessmentRecord.created_at, AssessmentRecord.id).offset(offset).limit(limit)
    return [assessment_schema(item) for item in db.scalars(query).all()]


@app.get("/api/v1/astronauts/{astronaut_id}/alerts", response_model=list[Alert],
         tags=["alerts"], description="Reserved MVP endpoint; no clinical alert rules are defined.")
def list_alerts(
    astronaut_id: UUID,
    db: DbSession,
    offset: PageOffset = 0,
    limit: PageLimit = 100,
    alert_status: Annotated[str | None, Query(alias="status")] = None,
) -> list[Alert]:
    require_astronaut(db, astronaut_id)
    query = select(AlertRecord).where(AlertRecord.astronaut_id == str(astronaut_id))
    if alert_status is not None:
        query = query.where(AlertRecord.status == alert_status)
    query = query.order_by(AlertRecord.created_at, AlertRecord.id).offset(offset).limit(limit)
    return [alert_schema(item) for item in db.scalars(query).all()]


@app.get("/api/v1/astronauts/{astronaut_id}/report",
         response_model=AstronautReport, tags=["reports"])
def get_report(astronaut_id: UUID, db: DbSession) -> AstronautReport:
    return AstronautReport(
        astronaut=astronaut_schema(require_astronaut(db, astronaut_id)),
        measurements=list_measurements(astronaut_id, db, limit=500),
        checkins=list_checkins(astronaut_id, db, limit=500),
        assessments=list_assessments(astronaut_id, db, limit=500),
    )


@app.get("/api/v1/mission-context", response_model=MissionContext, tags=["mission"])
def mission_context() -> MissionContext:
    return MissionContext(
        mission_name=settings.mission_name,
        mission_day=settings.mission_day,
        communication_delay_minutes=settings.communication_delay_minutes,
    )

