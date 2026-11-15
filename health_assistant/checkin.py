"""Daily check-in helpers for ASTRAVITAL.

Validates self-reports against the shared CheckInCreate schema and
defines the daily questions. The 1-5 scale is an input vocabulary,
not a clinical threshold. A missing value stays None, never 0.
"""

from typing import Any

SCALE_MIN = 1
SCALE_MAX = 5
NOTES_MAX_LENGTH = 1000
SCALE_FIELDS = ("mood", "fatigue")

# Fields allowed by the shared schema (additionalProperties: false).
ALLOWED_FIELDS = {"recorded_at", "mood", "fatigue", "notes"}

DAILY_QUESTIONS = [
    {
        "field": "mood",
        "prompt": "How is your mood today?",
        "scale": "1 to 5 (self-reported)",
        "optional": True,
    },
    {
        "field": "fatigue",
        "prompt": "How fatigued do you feel today?",
        "scale": "1 to 5 (self-reported)",
        "optional": True,
    },
    {
        "field": "notes",
        "prompt": "Anything else you want to record (symptoms, context)?",
        "scale": "free text, up to 1000 characters",
        "optional": True,
    },
]


def validate_checkin(checkin: dict[str, Any]) -> list[str]:
    """Return a list of error messages. An empty list means valid."""
    errors: list[str] = []

    if not isinstance(checkin, dict):
        return ["check-in must be an object"]

    for key in checkin:
        if key not in ALLOWED_FIELDS:
            errors.append(f"unknown field: {key}")

    if not checkin.get("recorded_at"):
        errors.append("recorded_at is required")

    for field in SCALE_FIELDS:
        value = checkin.get(field)
        if value is None:
            continue
        # bool is a subclass of int in Python: reject it explicitly.
        if isinstance(value, bool) or not isinstance(value, int):
            errors.append(f"{field} must be an integer from 1 to 5")
        elif not SCALE_MIN <= value <= SCALE_MAX:
            errors.append(f"{field} must be an integer from 1 to 5")

    notes = checkin.get("notes")
    if notes is not None:
        if not isinstance(notes, str):
            errors.append("notes must be text")
        elif len(notes) > NOTES_MAX_LENGTH:
            errors.append("notes must be at most 1000 characters")

    # At least one self-report field must be present.
    if all(checkin.get(f) is None for f in ("mood", "fatigue", "notes")):
        errors.append("at least one of mood, fatigue or notes is required")

    return errors


def reported_fields(checkin: dict[str, Any] | None) -> list[str]:
    """List which self-report fields were actually provided."""
    if not checkin:
        return []
    return [f for f in ("mood", "fatigue", "notes") if checkin.get(f) is not None]


def missing_fields(checkin: dict[str, Any] | None) -> list[str]:
    """List self-report fields that were not reported (null/absent)."""
    provided = set(reported_fields(checkin))
    return [f for f in ("mood", "fatigue", "notes") if f not in provided]


__all__ = [
    "DAILY_QUESTIONS",
    "validate_checkin",
    "reported_fields",
    "missing_fields",
]
