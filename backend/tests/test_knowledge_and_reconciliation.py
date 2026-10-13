import pytest
from app.services.knowledge_engine import registry
from app.services.reconciliation_engine import MultiDocumentReconciliationEngine

def test_knowledge_registry_has_rules():
    assert registry.rules
    assert any(rule["rule_id"] == "rule-001" for rule in registry.rules.values())


@pytest.mark.asyncio
async def test_reconciliation_with_missing_coo_context():
    engine = MultiDocumentReconciliationEngine()
    documents = [
        {"document_type": "commercial_invoice", "fields": [{"name": "invoice_total", "normalized_value": 1000}]},
        {"document_type": "packing_list", "fields": [{"name": "packing_list_total", "normalized_value": 1000}]},
    ]
    result = await engine.reconcile(documents)
    assert result["status"] == "ok"
