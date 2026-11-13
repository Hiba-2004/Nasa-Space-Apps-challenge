"""Rule-based, evidence-linked guidance interface for ASTRAVITAL."""

from typing import Any


def generate_guidance(
    findings: list[dict[str, Any]], checkin: dict[str, Any] | None, context: dict[str, Any]
) -> list[dict[str, Any]]:
    """Generate traceable data-collection guidance, not clinical advice."""
    if any(item.get("data_status") == "insufficient_data" for item in findings):
        return [{
            "id": "collect-routine-measurements",
            "title": "Collect routine measurements",
            "rationale": "Additional observations are needed before describing patterns.",
            "evidence_links": ["finding:insufficient_history"],
            "urgency": "routine",
        }]
    return [{
        "id": "review-observations",
        "title": "Review the recorded observations",
        "rationale": "The assessment summarizes available data without applying clinical thresholds.",
        "evidence_links": [f"finding:{item['code']}" for item in findings],
        "urgency": "routine",
    }]


__all__ = ["generate_guidance"]

