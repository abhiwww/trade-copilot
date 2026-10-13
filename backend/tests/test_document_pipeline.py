import pytest
from app.services.document_pipeline import DocumentAnalysisPipeline
from app.services.reconciliation_engine import MultiDocumentReconciliationEngine

@pytest.mark.asyncio
async def test_document_classification_and_extraction():
    pipeline = DocumentAnalysisPipeline()
    document = {
        "document_id": "doc-001",
        "filename": "commercial_invoice.pdf",
        "size_bytes": 1200,
        "text": "Commercial Invoice Number INV-1001 Total Amount USD 5,000.00 Currency USD",
    }

    result = await pipeline.analyze_document(document)

    assert result.document_type == "commercial_invoice"
    assert any(field.name == "invoice_total" for field in result.extracted_fields)


@pytest.mark.asyncio
async def test_multi_document_reconciliation_detects_mismatch():
    engine = MultiDocumentReconciliationEngine()
    documents = [
        {
            "document_type": "commercial_invoice",
            "fields": [
                {"name": "invoice_total", "normalized_value": 5000},
                {"name": "quantity", "normalized_value": 120},
            ],
        },
        {
            "document_type": "packing_list",
            "fields": [
                {"name": "packing_list_total", "normalized_value": 4500},
                {"name": "quantity", "normalized_value": 100},
            ],
        },
    ]

    result = await engine.reconcile(documents)

    assert result["finding_count"] >= 1
    assert any(item["category"] == "financial_reconciliation" for item in result["findings"])
