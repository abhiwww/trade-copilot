from __future__ import annotations

from typing import Any, Dict, List, Optional
from enum import Enum

class Jurisdiction(Enum):
    GLOBAL = "GLOBAL"
    COUNTRY = "COUNTRY"
    STATE = "STATE"
    CITY = "CITY"
    PORT = "PORT"

class Rule:
    def __init__(self, id: str, jurisdiction: Jurisdiction, level_value: Optional[str], check: Any, finding: Dict[str, Any]):
        self.id = id
        self.jurisdiction = jurisdiction
        self.level_value = level_value # e.g., "USA" for COUNTRY, "Los Angeles" for PORT
        self.check = check # A lambda or function that returns True if a finding is triggered
        self.finding = finding

class RuleEngine:
    """Granular Trade Compliance Engine with Jurisdiction Hierarchies."""

    def __init__(self):
        # Initialize the Rule Database
        self.rules: List[Rule] = [
            # GLOBAL RULES
            Rule(
                "R-001", Jurisdiction.GLOBAL, None,
                lambda f: f.get("lc_expiry_days", 99) <= 14,
                {"type": "lc_expiry_risk", "severity": "medium", "title": "LC expiry risk", "description": "Letter of credit expiry is close to the current transaction timeline."}
            ),

            # COUNTRY RULES
            Rule(
                "R-002", Jurisdiction.COUNTRY, "USA",
                lambda f: not f.get("has_certificate_of_origin", True),
                {"type": "missing_coo", "severity": "high", "title": "Certificate of Origin missing", "description": "USA imports typically require a Certificate of Origin."}
            ),

            # PORT RULES
            Rule(
                "R-003", Jurisdiction.PORT, "Port of Los Angeles",
                lambda f: f.get("product", "").lower() == "electronics" and not f.get("customs_bond", False),
                {"type": "port_bond_required", "severity": "high", "title": "Customs Bond Required", "description": "Electronics entering via Port of LA require a validated customs bond."}
            ),
            Rule(
                "R-004", Jurisdiction.PORT, "Singapore",
                lambda f: f.get("product", "").lower() == "chemicals",
                {"type": "hazardous_material_permit", "severity": "critical", "title": "HazMat Permit Required", "description": "Chemical shipments through Singapore require a special hazardous material permit."}
            ),
        ]

    def evaluate(self, facts: Dict[str, Any]) -> Dict[str, Any]:
        findings: List[Dict[str, Any]] = []

        # Extract route details for jurisdiction matching
        route = facts.get("route", {})
        origin = route.get("origin", {})
        destination = route.get("destination", {})

        # Combine all jurisdiction values for easy lookup
        jurisdiction_values = {
            Jurisdiction.COUNTRY: {origin.get("country"), destination.get("country")},
            Jurisdiction.STATE: {origin.get("state"), destination.get("state")},
            Jurisdiction.CITY: {origin.get("city"), destination.get("city")},
            Jurisdiction.PORT: {origin.get("port"), destination.get("port")},
        }

        for rule in self.rules:
            # 1. Check Jurisdiction Match
            is_match = False
            if rule.jurisdiction == Jurisdiction.GLOBAL:
                is_match = True
            elif rule.jurisdiction in jurisdiction_values:
                if rule.level_value in jurisdiction_values[rule.jurisdiction]:
                    is_match = True

            # 2. If jurisdiction matches, run the logic check
            if is_match and rule.check(facts):
                findings.append({
                    **rule.finding,
                    "rule_id": rule.id,
                    "jurisdiction": rule.jurisdiction.value
                })

        return {
            "status": "ok",
            "findings": findings,
            "count": len(findings)
        }
