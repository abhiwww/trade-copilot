from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, Optional
from app.services.llm_service import llm_service

class IntegrityEngine:
    """
    Fraud and Integrity Engine for detecting anomalies in trade transactions.
    Focuses on route illogicality, entity behavior, and structural anomalies.
    """

    def __init__(self):
        # In a production system, this would be connected to a database of
        # historical trade patterns and a global risk database.
        self.historical_baseline = {
            "high_risk_ports": ["Port X", "Port Y"], # Simulated watch-list
            "standard_routes": ["India->USA", "China->Germany", "Brazil->UK"]
        }

    async def detect_anomalies(self, facts: Dict[str, Any], documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyzes the transaction for fraudulent patterns or integrity anomalies.
        """
        # 1. Route Anomaly Detection
        route = facts.get("case_country_pair", "Unknown->Unknown")
        origin_port = facts.get("origin_port", "Unknown")
        dest_port = facts.get("destination_port", "Unknown")

        # 2. Entity Anomaly Detection (extracted from docs)
        entities = []
        for doc in documents:
            for field in doc.get("fields", []):
                if "entity" in field.get("name", "").lower() or "company" in field.get("name", "").lower():
                    entities.append(field.get("normalized_value"))

        # 3. LLM-Powered Fraud Analysis
        # We send the route, entities, and a summary of the documents to the LLM.
        system_prompt = (
            "You are a Forensic Trade Auditor and Anti-Fraud Specialist. "
            "Your goal is to detect 'Red Flags' and anomalies in trade transactions. "
            "Look for: \n"
            "1. Route Illogicality: Does the shipment path make sense for the product?\n"
            "2. Entity Red Flags: Do the company names or ports look suspicious or unusual?\n"
            "3. Structural Anomalies: Are the document values inconsistent with industry standards?\n"
            "Return ONLY a JSON object with a 'findings' list. "
            "Each finding must include: 'severity' (low, medium, high), 'title', 'description' (explaining the red flag), and 'confidence' (0-1)."
        )

        user_prompt = (
            f"Transaction Data:\n"
            f"- Route: {route}\n"
            f"- Origin Port: {origin_port}\n"
            f"- Destination Port: {dest_port}\n"
            f"- Involved Entities: {', '.join(entities) if entities else 'None extracted'}\n"
            f"- Document Summary: {len(documents)} documents analyzed."
        )

        try:
            result = await llm_service.call_llm(system_prompt, user_prompt)
            findings = result.get("findings", [])

            # Add structural metadata to findings
            processed_findings = []
            for f in findings:
                processed_findings.append({
                    "type": "integrity_anomaly",
                    "severity": f.get("severity", "medium"),
                    "title": f"Fraud Alert: {f.get('title', 'Anomaly detected')}",
                    "description": f.get("description", "A suspicious pattern was detected in the trade flow."),
                    "confidence": f.get("confidence", 0.8),
                    "details": {"engine": "IntegrityEngine_v1"}
                })

            return processed_findings

        except Exception as e:
            print(f"Integrity Engine LLM Error: {e}")
            return []

integrity_engine = IntegrityEngine()
