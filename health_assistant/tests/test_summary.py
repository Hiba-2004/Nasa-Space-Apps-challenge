from health_assistant.summary import DISCLAIMER, build_summary


def finding(code, status, metric=None):
    return {
        "code": code,
        "title": "t",
        "detail": "d",
        "evidence": [f"metric: {metric}"] if metric else [],
        "data_status": status,
    }


def test_no_history():
    text = build_summary([finding("insufficient_history", "insufficient_data")])
    assert "no pattern can be described" in text


def test_unusual_change_is_named_without_diagnosis():
    text = build_summary([
        finding("history_summarized", "observed"),
        finding("unusual_change", "observed", "sleep_hours"),
    ])
    assert "sleep_hours" in text
    assert "not a diagnosis" in text


def test_insufficient_data_is_reported_as_missing():
    text = build_summary([
        finding("history_summarized", "observed"),
        finding("insufficient_baseline", "insufficient_data", "body_temperature"),
    ])
    assert "Not enough data to compare: body_temperature" in text


def test_never_claims_normal():
    text = build_summary([finding("history_summarized", "observed")])
    assert "does not mean the values are normal" in text


def test_checkin_reported_and_missing():
    text = build_summary(
        [finding("history_summarized", "observed")],
        {"recorded_at": "2026-10-01T18:00:00Z", "mood": 4, "fatigue": None},
    )
    assert "Check-in reported: mood." in text
    assert "Not reported: fatigue, notes." in text


def test_no_checkin():
    assert "No check-in was provided." in build_summary([], None)


def test_disclaimer_present():
    assert "not a diagnosis" in DISCLAIMER
