"""Non-clinical alert candidates for ASTRAVITAL.

The shared Alert schema has only title, detail and status (the backend
adds id, astronaut_id, created_at). Evidence is therefore written into
`detail`. Alerts ask for a review by the crew medical officer. They
apply no clinical threshold and make no diagnosis.
"""

from typing import Any

from .guidance import _metric_from

STATUS_OPEN = "open"
ALERT_CODES = {"unusual_change"}


def build_alert_candidates(findings: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Return alert candidates (title, detail, status), one per metric."""
    alerts: list[dict[str, str]] = []
    seen: set[str] = set()

    for finding in findings or []:
        code = finding.get("code")
        # Never alert on missing or insufficient data.
        if code not in ALERT_CODES or finding.get("data_status") != "observed":
            continue

        metric = _metric_from(finding) or "a measurement"
        if metric in seen:
            continue
        seen.add(metric)

        evidence = "; ".join(
            line for line in finding.get("evidence") or [] if isinstance(line, str)
        )
        detail = (
            f"A statistical change was observed in {metric}. "
            "This is not a diagnosis. Repeat the measurement and review it "
            "with the crew medical officer if it persists."
        )
        if evidence:
            detail += f" Evidence: {evidence}."
        detail += f" Source: finding:{code}."

        alerts.append({
            "title": f"Review recommended: change in {metric}",
            "detail": detail,
            "status": STATUS_OPEN,
        })
    return alerts


__all__ = ["build_alert_candidates"]
