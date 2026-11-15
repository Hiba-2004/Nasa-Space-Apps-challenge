from health_assistant.alerts import build_alert_candidates

ALLOWED = {"title", "detail", "status"}


def finding(code, status, metric=None, extra=None):
    evidence = [f"metric: {metric}"] if metric else []
    evidence += extra or []
    return {
        "code": code,
        "title": "t",
        "detail": "d",
        "evidence": evidence,
        "data_status": status,
    }


def test_unusual_change_creates_alert():
    alerts = build_alert_candidates(
        [finding("unusual_change", "observed", "sleep_hours")]
    )
    assert len(alerts) == 1
    assert "sleep_hours" in alerts[0]["title"]
    assert alerts[0]["status"] == "open"


def test_only_schema_fields():
    alerts = build_alert_candidates(
        [finding("unusual_change", "observed", "sleep_hours")]
    )
    assert set(alerts[0]) == ALLOWED


def test_insufficient_data_gives_no_alert():
    findings = [
        finding("insufficient_history", "insufficient_data"),
        finding("insufficient_baseline", "insufficient_data", "sleep_hours"),
        finding("insufficient_variability", "insufficient_data", "sleep_hours"),
    ]
    assert build_alert_candidates(findings) == []


def test_summary_gives_no_alert():
    assert build_alert_candidates([finding("history_summarized", "observed")]) == []


def test_one_alert_per_metric():
    findings = [
        finding("unusual_change", "observed", "sleep_hours"),
        finding("unusual_change", "observed", "sleep_hours"),
        finding("unusual_change", "observed", "body_temperature"),
    ]
    assert len(build_alert_candidates(findings)) == 2


def test_detail_states_not_a_diagnosis_and_cites_source():
    alerts = build_alert_candidates(
        [finding("unusual_change", "observed", "sleep_hours", ["latest_value: 4"])]
    )
    detail = alerts[0]["detail"]
    assert "not a diagnosis" in detail
    assert "latest_value: 4" in detail
    assert "finding:unusual_change" in detail


def test_empty_input():
    assert build_alert_candidates([]) == []
    assert build_alert_candidates(None) == []
