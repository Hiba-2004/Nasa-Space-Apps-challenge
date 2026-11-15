from health_assistant.checkin import (
    DAILY_QUESTIONS,
    missing_fields,
    reported_fields,
    validate_checkin,
)


def test_valid_checkin():
    assert validate_checkin({"recorded_at": "2026-10-01T18:00:00Z", "mood": 4}) == []


def test_null_fatigue_is_allowed():
    checkin = {"recorded_at": "2026-10-01T18:00:00Z", "mood": 4, "fatigue": None}
    assert validate_checkin(checkin) == []


def test_zero_is_not_a_valid_value():
    errors = validate_checkin({"recorded_at": "2026-10-01T18:00:00Z", "mood": 0})
    assert errors


def test_out_of_range_rejected():
    errors = validate_checkin({"recorded_at": "2026-10-01T18:00:00Z", "fatigue": 6})
    assert errors


def test_boolean_rejected():
    errors = validate_checkin({"recorded_at": "2026-10-01T18:00:00Z", "mood": True})
    assert errors


def test_empty_checkin_rejected():
    errors = validate_checkin({"recorded_at": "2026-10-01T18:00:00Z"})
    assert "at least one of mood, fatigue or notes is required" in errors


def test_unknown_field_rejected():
    errors = validate_checkin(
        {"recorded_at": "2026-10-01T18:00:00Z", "mood": 3, "symptoms": ["x"]}
    )
    assert "unknown field: symptoms" in errors


def test_missing_recorded_at_rejected():
    assert "recorded_at is required" in validate_checkin({"mood": 3})


def test_notes_too_long_rejected():
    errors = validate_checkin(
        {"recorded_at": "2026-10-01T18:00:00Z", "notes": "x" * 1001}
    )
    assert errors


def test_missing_values_stay_missing():
    checkin = {"recorded_at": "2026-10-01T18:00:00Z", "mood": 4, "fatigue": None}
    assert reported_fields(checkin) == ["mood"]
    assert missing_fields(checkin) == ["fatigue", "notes"]


def test_questions_match_schema_fields():
    assert {q["field"] for q in DAILY_QUESTIONS} <= {"mood", "fatigue", "notes"}
