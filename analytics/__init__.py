"""Transparent analysis interface for ASTRAVITAL."""

from typing import Any


def analyze_health(
    history: list[dict[str, Any]], baseline: dict[str, Any] | None, context: dict[str, Any]
) -> list[dict[str, Any]]:
    """Return descriptive findings without clinical thresholds or diagnosis."""
    if not history:
        return [{
            "code": "insufficient_history",
            "title": "More history is needed",
            "detail": "No measurements were available for this assessment.",
            "evidence": [],
            "data_status": "insufficient_data",
        }]
    metrics = sorted({str(item["metric"]) for item in history if item.get("metric")})
    return [{
        "code": "history_summarized",
        "title": "Measurement history available",
        "detail": f"Reviewed {len(history)} measurement(s) across {len(metrics)} metric(s).",
        "evidence": [f"metrics: {', '.join(metrics)}"],
        "data_status": "observed",
    }]


__all__ = ["analyze_health"]

