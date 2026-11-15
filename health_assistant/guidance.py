"""Rule-based, evidence-linked guidance for ASTRAVITAL.

Output follows the shared GuidanceAction schema: only
id, title, rationale, evidence_links, urgency.
This is traceable guidance, not clinical advice or diagnosis.
"""

from typing import Any

URGENCY_ROUTINE = "routine"
URGENCY_FOLLOW_UP = "follow_up"

# Finding codes produced by analytics (Member 3).
COLLECT_CODES = {
    "insufficient_history",
    "insufficient_baseline",
    "insufficient_variability",
}


def _metric_from(finding: dict[str, Any]) -> str | None:
    """Read the metric name from the finding's evidence list, if present."""
    for line in finding.get("evidence") or []:
        if isinstance(line, str) and line.startswith("metric: "):
            return line[len("metric: "):].strip()
    return None


def _slug(code: str, metric: str | None) -> str:
    base = code.replace("_", "-")
    return f"{base}-{metric.replace('_', '-')}" if metric else base


def _action(finding: dict[str, Any]) -> dict[str, Any] | None:
    code = str(finding.get("code", "unknown"))
    status = finding.get("data_status")
    metric = _metric_from(finding)
    label = metric or "the measurements"
    link = [f"finding:{code}"]

    # Missing data: ask for more observations, never conclude.
    if code in COLLECT_CODES or status in ("insufficient_data", "unavailable"):
        return {
            "id": f"collect-{_slug(code, metric)}",
            "title": f"Collect more data for {label}",
            "rationale": (
                "There is not enough data to describe a pattern, "
                "so no conclusion is drawn."
            ),
            "evidence_links": link,
            "urgency": URGENCY_ROUTINE,
        }

    # Summary only: nothing to act on.
    if code == "history_summarized":
        return None

    if code == "unusual_change":
        return {
            "id": f"review-{_slug(code, metric)}",
            "title": f"Review the recent change in {label}",
            "rationale": (
                "The latest value differs statistically from the personal "
                "history. This is not a diagnosis. Repeat the measurement "
                "and share it with the crew medical officer if it persists."
            ),
            "evidence_links": link,
            "urgency": URGENCY_FOLLOW_UP,
        }

    # Unknown code: generic, never an error.
    return {
        "id": f"review-{_slug(code, metric)}",
        "title": "Review the recorded observations",
        "rationale": (
            "The assessment summarizes available data without applying "
            "clinical thresholds."
        ),
        "evidence_links": link,
        "urgency": URGENCY_ROUTINE,
    }


def generate_guidance(
    findings: list[dict[str, Any]],
    checkin: dict[str, Any] | None,
    context: dict[str, Any],
) -> list[dict[str, Any]]:
    """Generate traceable guidance actions from analytics findings."""
    actions: list[dict[str, Any]] = []
    seen: set[str] = set()
    for finding in findings or []:
        action = _action(finding)
        if action is None or action["id"] in seen:
            continue
        seen.add(action["id"])
        actions.append(action)

    # Only history_summarized (or nothing): keep a routine review action.
    if not actions:
        actions.append({
            "id": "review-observations",
            "title": "Review the recorded observations",
            "rationale": (
                "The assessment summarizes available data without applying "
                "clinical thresholds."
            ),
            "evidence_links": [
                f"finding:{f.get('code', 'unknown')}" for f in findings or []
            ],
            "urgency": URGENCY_ROUTINE,
        })
    return actions


__all__ = ["generate_guidance"]
