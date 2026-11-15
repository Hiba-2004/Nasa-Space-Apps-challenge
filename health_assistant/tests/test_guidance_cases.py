from health_assistant import generate_guidance

ALLOWED = {"id", "title", "rationale", "evidence_links", "urgency"}


def finding(code, status, metric=None):
    return {
        "code": code,
        "title": "t",
        "detail": "d",
        "evidence": [f"metric: {metric}"] if metric else [],
        "data_status": status,
    }


def test_schema_fields_only():
    actions = generate_guidance(
        [finding("unusual_change", "observed", "sleep_hours")], None, {}
    )
    assert set(actions[0]) <= ALLOWED


def test_insufficient_data_asks_for_collection():
    actions = generate_guidance(
        [finding("insufficient_baseline", "insufficient_data", "resting_heart_rate")],
        None, {},
    )
    assert actions[0]["id"].startswith("collect-")
    assert actions[0]["evidence_links"] == ["finding:insufficient_baseline"]


def test_unusual_change_is_follow_up():
    actions = generate_guidance(
        [finding("unusual_change", "observed", "sleep_hours")], None, {}
    )
    assert actions[0]["urgency"] == "follow_up"
    assert "sleep_hours" in actions[0]["title"]


def test_ids_unique_per_metric():
    actions = generate_guidance([
        finding("insufficient_baseline", "insufficient_data", "sleep_hours"),
        finding("insufficient_baseline", "insufficient_data", "body_temperature"),
    ], None, {})
    ids = [a["id"] for a in actions]
    assert len(ids) == len(set(ids)) == 2


def test_summary_only_gives_routine_review():
    actions = generate_guidance(
        [finding("history_summarized", "observed")], None, {}
    )
    assert actions[0]["urgency"] == "routine"
    assert actions[0]["evidence_links"] == ["finding:history_summarized"]


def test_unknown_code_does_not_crash():
    actions = generate_guidance([finding("something_new", "observed")], None, {})
    assert actions[0]["evidence_links"] == ["finding:something_new"]
