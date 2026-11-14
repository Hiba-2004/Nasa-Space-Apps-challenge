from typing import Any

from pydantic import TypeAdapter

from analytics import analyze_health
from backend.app.models import AssessmentRecord
from backend.app.schemas import Finding, GuidanceAction, utc_now
from health_assistant import generate_guidance

findings_adapter = TypeAdapter(list[Finding])
actions_adapter = TypeAdapter(list[GuidanceAction])


def build_assessment(
    astronaut_id: str,
    history: list[dict[str, Any]],
    latest_checkin: dict[str, Any] | None,
    context: dict[str, Any],
) -> AssessmentRecord:
    """Call team-owned interfaces and validate their output at the backend boundary."""
    findings = findings_adapter.validate_python(
        analyze_health(history, baseline=None, context=context)
    )
    actions = actions_adapter.validate_python(
        generate_guidance(
            [item.model_dump(mode="json") for item in findings], latest_checkin, context
        )
    )
    return AssessmentRecord(
        astronaut_id=astronaut_id,
        created_at=utc_now(),
        findings=[item.model_dump(mode="json") for item in findings],
        guidance_actions=[item.model_dump(mode="json") for item in actions],
        summary="A transparent descriptive review of available synthetic observations.",
    )

