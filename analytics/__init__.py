
"""Transparent, personalized health analysis for ASTRAVITAL."""

from math import isfinite
from statistics import median
from typing import Any

MIN_BASELINE_SAMPLES = 7
ANOMALY_THRESHOLD = 3.0
MAD_TO_STD = 1.4826


def analyze_health(
    history: list[dict[str, Any]],
    baseline: dict[str, Any] | None,
    context: dict[str, Any],
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

    metrics: dict[str, list[dict[str, Any]]] = {}

    for item in history:
        metric = item.get("metric")
        value = item.get("value")

        if (
            not metric
            or not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not isfinite(value)
        ):
            continue

        metrics.setdefault(str(metric), []).append(item)

    if not metrics:
        return [{
            "code": "insufficient_history",
            "title": "Valid measurements are unavailable",
            "detail": (
                "No valid numerical measurements were available for analysis."
            ),
            "evidence": [],
            "data_status": "insufficient_data",
        }]

    valid_measurement_count = sum(
        len(records) for records in metrics.values()
    )

    findings = [{
        "code": "history_summarized",
        "title": "Measurement history available",
        "detail": (
            f"Reviewed {valid_measurement_count} valid measurement(s) "
            f"across {len(metrics)} metric(s)."
        ),
        "evidence": [f"metrics: {', '.join(sorted(metrics))}"],
        "data_status": "observed",
    }]

    for metric, records in metrics.items():
        records.sort(key=lambda item: str(item.get("measured_at", "")))

        if len(records) <= MIN_BASELINE_SAMPLES:
            findings.append({
                "code": "insufficient_baseline",
                "title": f"More history needed for {metric}",
                "detail": (
                    f"Only {len(records)} observation(s) are available. "
                    f"At least {MIN_BASELINE_SAMPLES + 1} are needed "
                    "for this prototype's comparison."
                ),
                "evidence": [
                    f"metric: {metric}",
                    f"available_observations: {len(records)}",
                    f"required_observations: {MIN_BASELINE_SAMPLES + 1}",
                ],
                "data_status": "insufficient_data",
            })
            continue

        previous_values = [
            float(item["value"])
            for item in records[:-1]
        ]
        latest = float(records[-1]["value"])

        personal_median = median(previous_values)
        mad = median(
            abs(value - personal_median)
            for value in previous_values
        )

        # A zero MAD does not provide a reliable scale for this score.
        if mad == 0:
            findings.append({
                "code": "insufficient_variability",
                "title": f"Statistical comparison unavailable for {metric}",
                "detail": (
                    "Previous measurements have no variability, "
                    "so a reliable robust deviation score cannot be calculated."
                ),
                "evidence": [
                    f"metric: {metric}",
                    f"personal_median: {personal_median:g}",
                    "mad: 0",
                ],
                "data_status": "insufficient_data",
            })
            continue

        robust_scale = MAD_TO_STD * mad
        robust_z = (latest - personal_median) / robust_scale

        if abs(robust_z) >= ANOMALY_THRESHOLD:
            findings.append({
                "code": "unusual_change",
                "title": f"Unusual change in {metric}",
                "detail": (
                    f"The latest value ({latest:g}) differs notably "
                    f"from the personal historical median "
                    f"({personal_median:g}). This is a statistical "
                    "deviation, not a medical diagnosis."
                ),
                "evidence": [
                    f"metric: {metric}",
                    f"latest_value: {latest:g}",
                    f"personal_median: {personal_median:g}",
                    f"robust_z_score: {robust_z:.2f}",
                    f"previous_observations: {len(previous_values)}",
                ],
                "data_status": "observed",
            })

    return findings


__all__ = ["analyze_health"]
