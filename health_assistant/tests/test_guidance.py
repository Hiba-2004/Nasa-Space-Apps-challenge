from health_assistant import generate_guidance


def test_guidance_links_to_finding():
    findings = [{"code": "insufficient_history", "data_status": "insufficient_data"}]
    actions = generate_guidance(findings, None, {})
    assert actions[0]["evidence_links"] == ["finding:insufficient_history"]

