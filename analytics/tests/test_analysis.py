from analytics import analyze_health


def test_empty_history_is_explicitly_insufficient():
    findings = analyze_health([], None, {"is_synthetic": True})
    assert findings[0]["data_status"] == "insufficient_data"


def test_history_summary_is_descriptive():
    findings = analyze_health([{"metric": "sleep_hours", "value": 7}], None, {})
    assert findings[0]["code"] == "history_summarized"

def test_detects_unusual_value_against_personal_history():
    history = [
        {"metric": "resting_heart_rate", "value": value,
         "measured_at": f"2026-10-{day:02d}T08:00:00Z"}
        for day, value in enumerate([60, 61, 59, 60, 62, 61, 60], start=1)
    ]

    history.append({
        "metric": "resting_heart_rate",
        "value": 75,
        "measured_at": "2026-10-08T08:00:00Z",
    })

    findings = analyze_health(history, None, {"is_synthetic": True})

    assert any(f["code"] == "unusual_change" for f in findings)

def test_insufficient_metric_history_is_reported():
    history = [
        {
            "metric": "sleep_hours",
            "value": 7.0,
            "measured_at": f"2026-10-0{day}T08:00:00Z",
        }
        for day in range(1, 4)
    ]

    findings = analyze_health(history, None, {})

    assert any(
        f["code"] == "insufficient_baseline"
        and f["data_status"] == "insufficient_data"
        for f in findings
    )

def test_zero_mad_is_reported_as_unavailable():
    history = [
        {
            "metric": "resting_heart_rate",
            "value": 60,
            "measured_at": f"2026-10-{day:02d}T08:00:00Z",
        }
        for day in range(1, 8)
    ]

    history.append({
        "metric": "resting_heart_rate",
        "value": 75,
        "measured_at": "2026-10-08T08:00:00Z",
    })

    findings = analyze_health(history, None, {})

    assert any(
        f["code"] == "insufficient_variability"
        and f["data_status"] == "insufficient_data"
        for f in findings
    )