from __future__ import annotations

import os
import re
import random
import asyncio
from typing import Any, Dict, List, Optional

from app.models.trade_models import DocumentAnalysisResult, ExtractedField
from app.services.llm_service import llm_service

class DocumentAnalysisPipeline:
    """Advanced AI-powered document classification and field extraction pipeline."""

    ALLOWED_EXTENSIONS = {
        ".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".docx", ".xlsx", ".txt", ".csv",
    }

    TYPE_KEYWORDS = {
        "commercial_invoice": ["commercial invoice", "invoice", "tax invoice"],
        "packing_list": ["packing list", "pack list"],
        "bill_of_lading": ["bill of lading", "b/l", "bl"],
        "letter_of_credit": ["letter of credit", "lc", "credit"],
        "certificate_of_origin": ["certificate of origin", "coo", "origin certificate"],
        "purchase_order": ["purchase order", "po number"],
    }

    def validate_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        filename = str(document.get("filename", "")).strip()
        size_bytes = int(document.get("size_bytes", 0) or 0)
        if not filename:
            raise ValueError("Document filename is required.")
        if any(token in filename for token in ("..", "/", "\\")):
            raise ValueError("Unsafe filename.")
        ext = os.path.splitext(filename)[1].lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported document format: {ext}")
        if size_bytes <= 0:
            raise ValueError("Document size is required.")
        if size_bytes > 50 * 1024 * 1024:
            raise ValueError("Document exceeds maximum supported size.")
        return {"status": "validated", "filename": filename, "extension": ext, "size_bytes": size_bytes}

    async def classify_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        filename = str(document.get("filename", "")).lower()
        text = str(document.get("text", "")).lower()
        combined = f"Filename: {filename}\\nContent: {text[:2000]}"

        system_prompt = (
            "You are a global trade document classifier. Your goal is to identify the document type "
            "from a list of known trade documents. Return only a JSON object."
            f"\n\nAllowed Types: {', '.join(self.TYPE_KEYWORDS.keys())}"
            "\n\nExpected JSON format: { 'document_type': 'type', 'confidence': 0.0-1.0, 'reasoning': '...' }"
        )

        try:
            result = await llm_service.call_llm(system_prompt, combined)
            return {
                "document_type": result.get("document_type", "unknown"),
                "confidence": result.get("confidence", 0.5),
                "evidence": [{"source": "llm_classification", "matched_value": result.get("reasoning", "")}]
            }
        except Exception as e:
            print(f"Classification LLM Error: {e}")
            # Fallback to deterministic keyword match
            best_type = "unknown"
            best_score = 0.0
            for doc_type, keywords in self.TYPE_KEYWORDS.items():
                score = sum(1 for kw in keywords if kw in combined)
                if score > best_score:
                    best_score = score
                    best_type = doc_type
            return {
                "document_type": best_type,
                "confidence": 0.4,
                "evidence": [{"source": "keyword_fallback", "matched_value": "keyword_match"}]
            }

    def _extract_single_field(self, text: str, name: str, regex_pattern: str) -> Optional[ExtractedField]:
        match = re.search(regex_pattern, text, re.IGNORECASE | re.MULTILINE)
        if not match:
            return None
        raw_value = match.group(1).strip()
        normalized = self._normalize_field_value(name, raw_value)
        return ExtractedField(
            name=name,
            value=raw_value,
            normalized_value=normalized,
            confidence=0.8,
            page=1,
            source="regex_extraction",
        )

    def _normalize_field_value(self, field_name: str, value: str) -> Any:
        cleaned = value.replace(",", "").replace("USD", "").replace("INR", "").strip()
        if field_name in {"invoice_total", "amount", "lc_amount", "total_amount", "packing_list_total"}:
            try:
                return float(cleaned)
            except ValueError:
                return cleaned
        return cleaned

    async def ai_extract_fields(self, text: str, document_type: str) -> List[ExtractedField]:
        """
        Actual LLM extraction logic with Evidence Markers.
        """
        system_prompt = (
            f"You are an expert Trade Intelligence Analyst. Extract key fields from this {document_type} document. "
            "You must return a JSON object with a 'fields' list. "
            "Each field must have: 'name', 'value', 'confidence' (0-1), 'page' (int), and 'snippet' (the exact text from the document)."
            "\\n\\nFocus on high-value trade data: Invoice numbers, amounts, quantities, dates, and entity names."
        )

        user_prompt = f"Document Text:\\n{text[:10000]}"

        try:
            result = await llm_service.call_llm(system_prompt, user_prompt)
            extracted_fields = result.get("fields", [])

            fields = []
            for f in extracted_fields:
                val = f.get("value", "")
                name = f.get("name", "unknown")
                fields.append(ExtractedField(
                    name=name,
                    value=val,
                    normalized_value=self._normalize_field_value(name, val),
                    confidence=f.get("confidence", 0.5),
                    page=f.get("page", 1),
                    source="llm_extraction",
                    evidence_marker={
                        "bbox": [random.randint(100, 500), random.randint(100, 500), 100, 20], # Bbox simulation until OCR is integrated
                        "snippet": f.get("snippet", "")
                    }
                ))
            return fields
        except Exception as e:
            print(f"Extraction LLM Error: {e}")
            return []

    async def extract_fields(self, document: Dict[str, Any], document_type: str) -> List[ExtractedField]:
        text = str(document.get("text", ""))

        # Hybrid Approach: Regex + AI
        # Try regex first for speed/precision on standard patterns
        fields_map: Dict[str, ExtractedField] = {}

        # Regex definitions
        patterns = {
            "commercial_invoice": {
                "invoice_number": r"invoice\s*(?:no|number)\s*[:#-]?\s*([A-Za-z0-9-]+)",
                "invoice_total": r"total\s*(?:amount|value)\s*[:=]?\s*USD\s*([0-9,]+\.?[0-9]*)",
                "currency": r"currency\s*[:=]?\s*([A-Z]{3})",
            },
            "packing_list": {
                "packing_list_total": r"total\s*(?:weight|qty|value)\s*[:=]?\s*([0-9,]+\.?[0-9]*)",
                "quantity": r"quantity\s*[:=]?\s*([0-9,]+\.?[0-9]*)",
            },
            "letter_of_credit": {
                "lc_number": r"lc\s*(?:no|number)\s*[:#-]?\s*([A-Za-z0-9-]+)",
                "lc_amount": r"amount\s*[:=]?\s*USD\s*([0-9,]+\.?[0-9]*)",
            },
        }

        if document_type in patterns:
            for field_name, pattern in patterns[document_type].items():
                extracted = self._extract_single_field(text, field_name, pattern)
                if extracted:
                    fields_map[field_name] = extracted

        # Fill gaps with AI extraction
        ai_fields = await self.ai_extract_fields(text, document_type)
        for af in ai_fields:
            if af.name not in fields_map or af.confidence > fields_map[af.name].confidence:
                fields_map[af.name] = af

        if not fields_map:
            return [ExtractedField(name="document_text_present", value="present", normalized_value="present", confidence=0.4, page=1, source="fallback")]

        return list(fields_map.values())

    async def analyze_document(self, document: Dict[str, Any]) -> DocumentAnalysisResult:
        validation = self.validate_document(document)
        classification = await self.classify_document(document)
        fields = await self.extract_fields(document, classification["document_type"])

        return DocumentAnalysisResult(
            document_id=str(document.get("document_id") or document.get("filename", "unknown-doc")),
            document_type=classification["document_type"],
            classification_confidence=classification["confidence"],
            extracted_fields=fields,
            evidence=classification["evidence"],
            validation=validation,
        )

    async def analyze_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        results = [await self.analyze_document(doc) for doc in documents]
        return {
            "status": "ok",
            "documents_analyzed": len(results),
            "results": [
                {
                    "document_id": result.document_id,
                    "document_type": result.document_type,
                    "classification_confidence": result.classification_confidence,
                    "fields": [
                        {
                            "name": field.name,
                            "value": field.value,
                            "normalized_value": field.normalized_value,
                            "confidence": field.confidence,
                            "source": field.source,
                        }
                        for field in result.extracted_fields
                    ],
                    "evidence": result.evidence,
                }
                for result in results
            ],
        }
