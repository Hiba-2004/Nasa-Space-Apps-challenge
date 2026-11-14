"""Create the initial persistent schema.

Revision ID: 0001
Revises: None
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "astronauts",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("mission_role", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "alerts",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("astronaut_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("detail", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.ForeignKeyConstraint(["astronaut_id"], ["astronauts.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_alerts_astronaut_id", "alerts", ["astronaut_id"])
    op.create_index("ix_alerts_created_at", "alerts", ["created_at"])
    op.create_table(
        "assessments",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("astronaut_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("findings", sa.JSON(), nullable=False),
        sa.Column("guidance_actions", sa.JSON(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["astronaut_id"], ["astronauts.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_assessments_astronaut_id", "assessments", ["astronaut_id"])
    op.create_index("ix_assessments_created_at", "assessments", ["created_at"])
    op.create_table(
        "checkins",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("astronaut_id", sa.String(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("mood", sa.Integer(), nullable=True),
        sa.Column("fatigue", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["astronaut_id"], ["astronauts.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("astronaut_id", "recorded_at", name="uq_checkin_observation"),
    )
    op.create_index("ix_checkins_astronaut_id", "checkins", ["astronaut_id"])
    op.create_index("ix_checkins_recorded_at", "checkins", ["recorded_at"])
    op.create_table(
        "measurements",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("astronaut_id", sa.String(), nullable=False),
        sa.Column("measured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metric", sa.String(length=50), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(length=20), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(["astronaut_id"], ["astronauts.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "astronaut_id", "measured_at", "metric", name="uq_measurement_observation"
        ),
    )
    op.create_index("ix_measurements_astronaut_id", "measurements", ["astronaut_id"])
    op.create_index("ix_measurements_measured_at", "measurements", ["measured_at"])


def downgrade() -> None:
    op.drop_table("measurements")
    op.drop_table("checkins")
    op.drop_table("assessments")
    op.drop_table("alerts")
    op.drop_table("astronauts")

