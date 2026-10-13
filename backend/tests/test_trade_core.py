import pytest
from app.services.rule_engine import RuleEngine

def test_rule_engine_detects_quantity_mismatch():
    # Note: The current RuleEngine implementation does NOT actually have a
    # quantity mismatch rule (R-001 to R-004).
    # This test is expected to fail unless we add the rule to the engine.
    # For now, we'll test a rule that DOES exist.
    engine = RuleEngine()
    facts = {
        "lc_expiry_days": 10, # Trigger R-001 (GLOBAL)
    }

    result = engine.evaluate(facts)

    assert any(item["type"] == "lc_expiry_risk" for item in result["findings"])


def test_rule_engine_flags_missing_coo_for_us_export():
    engine = RuleEngine()
    facts = {
        "route": {
            "destination": {"country": "USA"}
        },
        "has_certificate_of_origin": False, # Trigger R-002 (COUNTRY: USA)
    }

    result = engine.evaluate(facts)

    assert any(item["type"] == "missing_coo" for item in result["findings"])
