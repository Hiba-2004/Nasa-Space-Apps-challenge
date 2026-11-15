"""Plain-text summary for the shared Assessment schema.

Descriptive only: no diagnosis, no clinical threshold. Missing data is
reported as missing, never as normal.
"""

from typing import Any

from .checkin import missing_fields, reported_fields
from .guidance import _metric_from

DISCLAIMER = (
    "Decision support only; not a diagnosis or validated risk prediction."
)


def _metrics(findings: list[dict[str, Any]], codes: set[str]) -> list[str]:
    return sorted({
        metric
        for f in findings
        if f.get("code") in codes
        for metric in [_metric_from(f)]
        if metric
    })


def build_summary(
    findings: list[dict[str, Any]] | None,
    checkin: dict[str, Any] | None = None,
) -> str:
    """Return a short descriptive summary of findings and check-in."""
    findings = findings or []
    codes = {f.get("code") for f in findings}
    parts: list[str] = []

    if "insufficient_history" in codes:
        parts.append(
            "No valid measurements were available, so no pattern can be described."
        )
    else:
        parts.append("Descriptive review of the available observations.")

        changed = _metrics(
            [f for f in findings if f.get("data_status") == "observed"],
            {"unusual_change"},
        )
        lacking = _metrics(
            findings, {"insufficient_baseline", "insufficient_variability"}
        )

        if changed:
            parts.append(
                "Statistically unusual change noted in: "
                f"{', '.join(changed)} (not a diagnosis)."
            )
        if lacking:
            parts.append(
                f"Not enough data to compare: {', '.join(lacking)}."
            )
        if not changed:
            parts.append(
                "No statistically unusual change was flagged; this does not "
                "mean the values are normal."
            )

    reported = reported_fields(checkin)
    if reported:
        parts.append(f"Check-in reported: {', '.join(reported)}.")
        missing = missing_fields(checkin)
        if missing:
            parts.append(f"Not reported: {', '.join(missing)}.")
    else:
        parts.append("No check-in was provided.")

    return " ".join(parts)


__all__ = ["build_summary", "DISCLAIMER"]
