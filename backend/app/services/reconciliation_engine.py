from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List
from app.models.trade_models import ReconciliationFinding
from app.services.llm_service import llm_service

class MultiDocumentReconciliationEngine:
    """Advanced AI-powered reconciliation engine with semantic reasoning capabilities."""

    async def reconcile(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Performs semantic reconciliation across multiple trade documents using an LLM.
        """
        if not documents:
            return {"status": "ok", "finding_count": 0, "findings": []}

        # 1. Build a comprehensive data map for the LLM
        doc_data = {}
        for doc in documents:
            doc_type = doc.get("document_type")
            if doc_type:
                # Extract just the field name: value pairs for the prompt
                fields = {f.get("name"): f.get("normalized_value") for f in doc.get("fields", [])}
                doc_data[doc_type] = fields

        if len(doc_data) < 2:
            # Need at least two documents to reconcile
            return {
                "status": "insufficient_data",
                "finding_count": 0,
                "findings": [],
                "message": "At least two documents are required for cross-document reconciliation."
            }

        # 2. Construct the Semantic Reconciliation Prompt
        system_prompt = (
            "You are a Senior Trade Compliance Auditor. Your task is to reconcile data across multiple trade documents "
            "(e.g., Commercial Invoice, Packing List, Letter of Credit). "
            "Look for discrepancies in quantities, totals, entity names, and dates. "
            "Return ONLY a JSON object with a 'findings' list. "
            "Each finding must include: 'category', 'severity' (low, medium, high), 'title', "
            "'description' (including an AI-driven explanation of WHY the difference exists), "
            "'difference' (numeric if applicable, otherwise null), 'evidence' (list of doc types), and 'confidence' (0-1)."
        )

        user_prompt = f"Reconcile the following extracted document data:\n\n{json.dumps(doc_data, indent=2)}"

        try:
            result = await llm_service.call_llm(system_prompt, user_prompt)
            findings_data = result.get("findings", [])

            findings = [
                ReconciliationFinding(
                    category=f.get("category", "general"),
                    severity=f.get("severity", "medium"),
                    title=f.get("title", "Data Mismatch"),
                    description=f.get("description", "A discrepancy was detected."),
                    difference=f.get("difference"),
                    evidence=f.get("evidence", []),
                    confidence=f.get("confidence", 0.8)
                )
                for f in findings_data
            ]

            return {
                "status": "ok",
                "finding_count": len(findings),
                "findings": [
                    {
                        "category": f.category,
                        "severity": f.severity,
                        "title": f.title,
                        "description": f.description,
                        "difference": f.difference,
                        "evidence": f.evidence,
                        "confidence": f.confidence,
                    }
                    for f in findings
                ],
            }

        except Exception as e:
            print(f"Reconciliation LLM Error: {e}")
            return {"status": "error", "finding_count": 0, "findings": [], "error": str(e)}
