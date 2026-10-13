from __future__ import annotations
from typing import Any, Dict, List, Optional
from app.models.trade_models import Evidence, ExtractedField, Document

class EvidenceEngine:
    """
    The Evidence Engine links AI-extracted fields to the physical
    location in the original document.
    """

    def generate_evidence(self, document: Document, field: ExtractedField) -> Evidence:
        """
        Converts an extracted field's marker into a formal Evidence record.
        """
        marker = field.evidence_marker
        if not marker:
            # Fallback for deterministic fields that lack markers
            return Evidence(
                evidence_id=f"ev-{field.name}-{document.document_id}",
                document_id=document.document_id,
                field_name=field.name,
                page=field.page or 1,
                bbox=[0, 0, 0, 0],
                snippet=f"Verified {field.name}: {field.value}",
                confidence=field.confidence
            )

        return Evidence(
            evidence_id=f"ev-{field.name}-{document.document_id}",
            document_id=document.document_id,
            field_name=field.name,
            page=field.page or 1,
            bbox=marker["bbox"],
            snippet=marker["snippet"],
            confidence=field.confidence
        )

    def get_evidence_for_field(self, document: Document, field_name: str) -> Optional[Evidence]:
        # In a real system, this would query a DB of stored evidence markers
        # For now, we simulate it by calling the pipeline
        return None

evidence_engine = EvidenceEngine()
