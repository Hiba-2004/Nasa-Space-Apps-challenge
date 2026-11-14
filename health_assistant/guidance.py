"""Rule-based, evidence-linked guidance for ASTRAVITAL.

Output follows the shared GuidanceAction schema: only
id, title, rationale, evidence_links, urgency.
This is traceable data-collection guidance, not clinical advice.
"""

from typing import Any

URGENCY_ROUTINE = "routine"


def generate_guidance(
    findings: list[dict[str, Any]],
    checkin: dict[str, Any] | None,
    context: dict[str, Any],
) -> list[dict[str, Any]]:
    """Generate traceable guidance actions from analytics findings."""
    if any(item.get("data_status") == "insufficient_data" for item in findings):
        return [{
            "id": "collect-routine-measurements",
            "title": "Collect routine measurements",
            "rationale": "Additional observations are needed before describing patterns.",
            "evidence_links": ["finding:insufficient_history"],
            "urgency": URGENCY_ROUTINE,
        }]
    return [{
        "id": "review-observations",
        "title": "Review the recorded observations",
        "rationale": "The assessment summarizes available data without applying clinical thresholds.",
        "evidence_links": [f"finding:{item['code']}" for item in findings],
        "urgency": URGENCY_ROUTINE,
    }]


__all__ = ["generate_guidance"]
