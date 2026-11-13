from analytics import analyze_health


def test_empty_history_is_explicitly_insufficient():
    findings = analyze_health([], None, {"is_synthetic": True})
    assert findings[0]["data_status"] == "insufficient_data"


def test_history_summary_is_descriptive():
    findings = analyze_health([{"metric": "sleep_hours", "value": 7}], None, {})
    assert findings[0]["code"] == "history_summarized"

