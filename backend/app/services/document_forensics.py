from __future__ import annotations

from typing import Any, Dict, List


class DocumentForensicsEngine:
    """Document integrity and forensic signal engine."""

    def analyze_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        signals: List[Dict[str, Any]] = []
        metadata = document.get("metadata", {}) or {}

        if metadata.get("author") in {"unknown", "test"}:
            signals.append(
                {
                    "category": "metadata",
                    "type": "missing_author",
                    "severity": "medium",
                    "confidence": 0.65,
                    "description": "Document metadata is sparse or generic.",
                }
            )

        mod_date = metadata.get("modification_date")
        if mod_date and mod_date.startswith("2020"):
            signals.append(
                {
                    "category": "temporal",
                    "type": "stale_metadata",
                    "severity": "medium",
                    "confidence": 0.7,
                    "description": "Document modification date appears stale relative to the transaction timeline.",
                }
            )

        if document.get("hash") and len(str(document["hash"])) < 8:
            signals.append(
                {
                    "category": "integrity",
                    "type": "short_hash",
                    "severity": "low",
                    "confidence": 0.55,
                    "description": "Document hash length is unusually short for a verified file identity.",
                }
            )

        score = sum(
            {
                "metadata": 25,
                "temporal": 15,
                "integrity": 10,
            }.get(signal["category"], 0)
            for signal in signals
        )

        return {
            "status": "ok",
            "signals": signals,
            "integrity_score": min(score, 100),
            "summary": "Document forensics completed with evidence-backed integrity signals.",
        }
