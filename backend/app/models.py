from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


def new_id() -> str:
    return str(uuid4())


class AstronautRecord(Base):
    __tablename__ = "astronauts"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    display_name: Mapped[str] = mapped_column(String(100))
    mission_role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    measurements: Mapped[list["MeasurementRecord"]] = relationship(back_populates="astronaut")
    checkins: Mapped[list["CheckInRecord"]] = relationship(back_populates="astronaut")
    assessments: Mapped[list["AssessmentRecord"]] = relationship(back_populates="astronaut")
    alerts: Mapped[list["AlertRecord"]] = relationship(back_populates="astronaut")


class MeasurementRecord(Base):
    __tablename__ = "measurements"
    __table_args__ = (
        UniqueConstraint("astronaut_id", "measured_at", "metric", name="uq_measurement_observation"),
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    astronaut_id: Mapped[str] = mapped_column(
        ForeignKey("astronauts.id", ondelete="RESTRICT"), index=True
    )
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    metric: Mapped[str] = mapped_column(String(50))
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(20))
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    astronaut: Mapped[AstronautRecord] = relationship(back_populates="measurements")


class CheckInRecord(Base):
    __tablename__ = "checkins"
    __table_args__ = (
        UniqueConstraint("astronaut_id", "recorded_at", name="uq_checkin_observation"),
    )
    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    astronaut_id: Mapped[str] = mapped_column(
        ForeignKey("astronauts.id", ondelete="RESTRICT"), index=True
    )
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    mood: Mapped[int | None] = mapped_column(nullable=True)
    fatigue: Mapped[int | None] = mapped_column(nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    astronaut: Mapped[AstronautRecord] = relationship(back_populates="checkins")


class AssessmentRecord(Base):
    __tablename__ = "assessments"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    astronaut_id: Mapped[str] = mapped_column(
        ForeignKey("astronauts.id", ondelete="RESTRICT"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    findings: Mapped[list] = mapped_column(JSON)
    guidance_actions: Mapped[list] = mapped_column(JSON)
    summary: Mapped[str] = mapped_column(Text)
    astronaut: Mapped[AstronautRecord] = relationship(back_populates="assessments")


class AlertRecord(Base):
    __tablename__ = "alerts"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    astronaut_id: Mapped[str] = mapped_column(
        ForeignKey("astronauts.id", ondelete="RESTRICT"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    title: Mapped[str] = mapped_column(String(200))
    detail: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30))
    astronaut: Mapped[AstronautRecord] = relationship(back_populates="alerts")

