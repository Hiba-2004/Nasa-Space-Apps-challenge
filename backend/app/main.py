from contextlib import asynccontextmanager
from datetime import UTC
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from analytics import analyze_health
from backend.app.config import get_settings
from backend.app.database import Base, engine, get_db
from backend.app.models import (
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
    MissionContext,
    utc_now,
)
from health_assistant import generate_guidance


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


def as_utc(value):
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value


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


@app.get("/api/v1/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    return HealthResponse()


@app.get("/api/v1/astronauts", response_model=list[Astronaut], tags=["astronauts"])
def list_astronauts(db: Session = Depends(get_db)) -> list[Astronaut]:
    records = db.scalars(select(AstronautRecord).order_by(AstronautRecord.created_at)).all()
    return [astronaut_schema(item) for item in records]


@app.post("/api/v1/astronauts", response_model=Astronaut,
          status_code=status.HTTP_201_CREATED, tags=["astronauts"])
def create_astronaut(payload: AstronautCreate, db: Session = Depends(get_db)) -> Astronaut:
    record = AstronautRecord(**payload.model_dump(), created_at=utc_now())
    db.add(record)
    db.commit()
    return astronaut_schema(record)


@app.get("/api/v1/astronauts/{astronaut_id}", response_model=Astronaut, tags=["astronauts"])
def get_astronaut(astronaut_id: UUID, db: Session = Depends(get_db)) -> Astronaut:
    return astronaut_schema(require_astronaut(db, astronaut_id))


@app.get("/api/v1/astronauts/{astronaut_id}/measurements",
         response_model=list[HealthMeasurement], tags=["measurements"])
def list_measurements(astronaut_id: UUID, db: Session = Depends(get_db)) -> list[HealthMeasurement]:
    require_astronaut(db, astronaut_id)
    query = select(MeasurementRecord).where(
        MeasurementRecord.astronaut_id == str(astronaut_id)
    ).order_by(MeasurementRecord.measured_at)
    return [measurement_schema(item) for item in db.scalars(query).all()]


@app.post("/api/v1/astronauts/{astronaut_id}/measurements",
          response_model=HealthMeasurement, status_code=201, tags=["measurements"])
def create_measurement(astronaut_id: UUID, payload: HealthMeasurementCreate,
                       db: Session = Depends(get_db)) -> HealthMeasurement:
    require_astronaut(db, astronaut_id)
    record = MeasurementRecord(astronaut_id=str(astronaut_id), **payload.model_dump())
    db.add(record)
    db.commit()
    return measurement_schema(record)


@app.get("/api/v1/astronauts/{astronaut_id}/checkins",
         response_model=list[CheckIn], tags=["check-ins"])
def list_checkins(astronaut_id: UUID, db: Session = Depends(get_db)) -> list[CheckIn]:
    require_astronaut(db, astronaut_id)
    query = select(CheckInRecord).where(
        CheckInRecord.astronaut_id == str(astronaut_id)
    ).order_by(CheckInRecord.recorded_at)
    return [checkin_schema(item) for item in db.scalars(query).all()]


@app.post("/api/v1/astronauts/{astronaut_id}/checkins", response_model=CheckIn,
          status_code=201, tags=["check-ins"])
def create_checkin(astronaut_id: UUID, payload: CheckInCreate,
                   db: Session = Depends(get_db)) -> CheckIn:
    require_astronaut(db, astronaut_id)
    record = CheckInRecord(astronaut_id=str(astronaut_id), **payload.model_dump())
    db.add(record)
    db.commit()
    return checkin_schema(record)


@app.post("/api/v1/astronauts/{astronaut_id}/assessments",
          response_model=HealthAssessment, status_code=201, tags=["assessments"])
def create_assessment(astronaut_id: UUID, db: Session = Depends(get_db)) -> HealthAssessment:
    require_astronaut(db, astronaut_id)
    measurements = list_measurements(astronaut_id, db)
    checkins = list_checkins(astronaut_id, db)
    context = mission_context().model_dump()
    history = [item.model_dump(mode="json") for item in measurements]
    findings = analyze_health(history, baseline=None, context=context)
    last_checkin = checkins[-1].model_dump(mode="json") if checkins else None
    actions = generate_guidance(findings, last_checkin, context)
    record = AssessmentRecord(
        astronaut_id=str(astronaut_id), created_at=utc_now(), findings=findings,
        guidance_actions=actions,
        summary="A transparent descriptive review of available synthetic observations.",
    )
    db.add(record)
    db.commit()
    return assessment_schema(record)


@app.get("/api/v1/astronauts/{astronaut_id}/assessments",
         response_model=list[HealthAssessment], tags=["assessments"])
def list_assessments(astronaut_id: UUID, db: Session = Depends(get_db)) -> list[HealthAssessment]:
    require_astronaut(db, astronaut_id)
    query = select(AssessmentRecord).where(
        AssessmentRecord.astronaut_id == str(astronaut_id)
    ).order_by(AssessmentRecord.created_at)
    return [assessment_schema(item) for item in db.scalars(query).all()]


@app.get("/api/v1/astronauts/{astronaut_id}/alerts", response_model=list[Alert],
         tags=["alerts"], description="Reserved MVP endpoint; no clinical alert rules are defined.")
def list_alerts(astronaut_id: UUID, db: Session = Depends(get_db)) -> list[Alert]:
    require_astronaut(db, astronaut_id)
    return []


@app.get("/api/v1/astronauts/{astronaut_id}/report",
         response_model=AstronautReport, tags=["reports"])
def get_report(astronaut_id: UUID, db: Session = Depends(get_db)) -> AstronautReport:
    return AstronautReport(
        astronaut=astronaut_schema(require_astronaut(db, astronaut_id)),
        measurements=list_measurements(astronaut_id, db),
        checkins=list_checkins(astronaut_id, db),
        assessments=list_assessments(astronaut_id, db),
    )


@app.get("/api/v1/mission-context", response_model=MissionContext, tags=["mission"])
def mission_context() -> MissionContext:
    return MissionContext(
        mission_name=settings.mission_name,
        mission_day=settings.mission_day,
        communication_delay_minutes=settings.communication_delay_minutes,
    )

