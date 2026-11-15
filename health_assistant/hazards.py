"""Link NASA spaceflight hazards to health indicators.

Links describe association only, never diagnosis. Each link carries a
`basis`: "nasa_documented" (supported by the listed sources) or
"team_review_needed" (plausible, not yet verified).
"""

import json
from pathlib import Path
from typing import Any

from .guidance import _metric_from

KB_PATH = Path(__file__).parent / "knowledge_base" / "hazards.json"


def load_knowledge_base() -> dict[str, Any]:
    with KB_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def hazards_for_indicator(name: str) -> list[dict[str, Any]]:
    """Hazards associated with a metric or check-in field."""
    kb = load_knowledge_base()
    links = []
    for hazard in kb["hazards"]:
        for indicator in hazard["indicators"]:
            if indicator["name"] == name:
                links.append({
                    "hazard_id": hazard["id"],
                    "hazard": hazard["name"],
                    "basis": indicator["basis"],
                    "sources": kb["sources"],
                })
    return links


def hazard_links_for_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """For each unusual_change finding, list associated hazards."""
    results = []
    for finding in findings or []:
        if finding.get("code") != "unusual_change":
            continue
        metric = _metric_from(finding)
        if metric is None:
            continue
        results.append({
            "metric": metric,
            "evidence_links": [f"finding:{finding['code']}"],
            "hazards": hazards_for_indicator(metric),
        })
    return results


__all__ = [
    "load_knowledge_base",
    "hazards_for_indicator",
    "hazard_links_for_findings",
]
