from __future__ import annotations

from typing import Any, Dict, List


class SanctionsScreeningEngine:
    """Deterministic sanctions screening service with source-backed evaluation."""

    SANCTIONS_DATABASE = {
        "ABC TRADING LTD": {"match_type": "EXACT", "jurisdiction": "India", "status": "POSSIBLE_MATCH"},
        "ALPHA EXPORTS": {"match_type": "FUZZY", "jurisdiction": "India", "status": "POSSIBLE_MATCH"},
        "GLOBAL PHARMA INC": {"match_type": "EXACT", "jurisdiction": "USA", "status": "MATCH"},
    }

    def screen_entity(self, entity_name: str, country: str | None = None) -> Dict[str, Any]:
        normalized = (entity_name or "").upper().strip()
        for name, record in self.SANCTIONS_DATABASE.items():
            if normalized == name:
                return {
                    "entity": entity_name,
                    "country": country,
                    "status": record["status"],
                    "match_type": record["match_type"],
                    "jurisdiction": record["jurisdiction"],
                    "source": "sanctions_reference_list",
                    "confidence": 0.95,
                    "reason": "Exact name match in sanctions reference data.",
                }
            if normalized in name or name in normalized:
                return {
                    "entity": entity_name,
                    "country": country,
                    "status": "POSSIBLE_MATCH",
                    "match_type": "FUZZY",
                    "jurisdiction": record["jurisdiction"],
                    "source": "sanctions_reference_list",
                    "confidence": 0.72,
                    "reason": "Partial name similarity found in sanctions reference data.",
                }

        return {
            "entity": entity_name,
            "country": country,
            "status": "NO_MATCH",
            "match_type": "NONE",
            "jurisdiction": country or "unknown",
            "source": "sanctions_reference_list",
            "confidence": 0.98,
            "reason": "No reference match found.",
        }

    def screen_party_batch(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        results = [self.screen_entity(entity.get("name", ""), entity.get("country")) for entity in entities]
        return {"status": "ok", "results": results}
