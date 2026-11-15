from health_assistant.hazards import (
    hazard_links_for_findings,
    hazards_for_indicator,
    load_knowledge_base,
)

ALLOWED_BASIS = {"nasa_documented", "team_review_needed"}


def test_five_hazards_with_sources():
    kb = load_knowledge_base()
    assert len(kb["hazards"]) == 5
    assert kb["sources"]


def test_basis_values_are_valid():
    for hazard in load_knowledge_base()["hazards"]:
        for indicator in hazard["indicators"]:
            assert indicator["basis"] in ALLOWED_BASIS


def test_sleep_linked_to_isolation_and_documented():
    links = hazards_for_indicator("sleep_hours")
    assert links[0]["hazard_id"] == "isolation_confinement"
    assert links[0]["basis"] == "nasa_documented"


def test_unlinked_indicator_returns_empty():
    assert hazards_for_indicator("unknown_metric") == []


def test_radiation_has_no_invented_indicator():
    kb = load_knowledge_base()
    radiation = next(h for h in kb["hazards"] if h["id"] == "space_radiation")
    assert radiation["indicators"] == []


def test_findings_links_only_for_unusual_change():
    findings = [
        {"code": "history_summarized", "evidence": [], "data_status": "observed"},
        {
            "code": "unusual_change",
            "evidence": ["metric: sleep_hours"],
            "data_status": "observed",
        },
    ]
    result = hazard_links_for_findings(findings)
    assert len(result) == 1
    assert result[0]["metric"] == "sleep_hours"
    assert result[0]["evidence_links"] == ["finding:unusual_change"]
