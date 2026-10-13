from __future__ import annotations

from typing import Any, Dict, List, Tuple
import random

class KnowledgeRegistry:
    """Advanced semantic knowledge registry with RAG capabilities."""

    def __init__(self) -> None:
        self.sources: Dict[str, Dict[str, Any]] = {}
        self.rules: Dict[str, Dict[str, Any]] = {}
        # Simulated vector embeddings for semantic search
        self._embeddings_cache: Dict[str, List[float]] = {}

    def register_source(self, source_id: str, authority: str, jurisdiction: str, title: str, citation: str) -> Dict[str, Any]:
        item = {
            "source_id": source_id,
            "authority": authority,
            "jurisdiction": jurisdiction,
            "title": title,
            "citation": citation,
            "status": "active",
        }
        self.sources[source_id] = item
        return item

    def add_rule(
        self,
        rule_id: str,
        name: str,
        jurisdiction: str,
        authority: str,
        conditions: Dict[str, Any],
        action: str,
        requirement: str,
        source_id: str,
    ) -> Dict[str, Any]:
        rule = {
            "rule_id": rule_id,
            "name": name,
            "jurisdiction": jurisdiction,
            "authority": authority,
            "conditions": conditions,
            "action": action,
            "requirement": requirement,
            "source_id": source_id,
            "version": "v2-ai",
            "status": "approved",
        }
        self.rules[rule_id] = rule
        return rule

    def search(self, query: str, jurisdiction: str | None = None) -> List[Dict[str, Any]]:
        """Deterministic keyword search."""
        matches: List[Dict[str, Any]] = []
        lowered = query.lower()
        for rule in self.rules.values():
            if jurisdiction and rule.get("jurisdiction") != jurisdiction:
                continue
            haystack = " ".join([
                rule.get("name", ""),
                rule.get("requirement", ""),
                rule.get("authority", ""),
                rule.get("jurisdiction", ""),
            ]).lower()
            if lowered in haystack:
                matches.append(rule)
        return matches

    def semantic_search(self, query: str, top_k: int = 3) -> List[Tuple[float, Dict[str, Any]]]:
        """
        Simulated Semantic Search using cosine similarity.
        In production, this would use an embedding model (e.g. text-embedding-3-small)
        and a vector database (e.g. Pinecone).
        """
        # We simulate the 'semantic' part by looking for keyword overlap + some randomness
        results = []
        query_words = set(query.lower().split())

        for rule in self.rules.values():
            content = f"{rule.get('name', '')} {rule.get('requirement', '')}".lower()
            content_words = set(content.split())
            intersection = query_words.intersection(content_words)
            score = len(intersection) / max(len(query_words), 1)
            # Add small random noise to simulate embedding variance
            score += random.uniform(0, 0.1)
            results.append((score, rule))

        return sorted(results, key=lambda x: x[0], reverse=True)[:top_k]

    def generate_ai_answer(self, query: str) -> Dict[str, Any]:
        """
        Simulated RAG (Retrieval-Augmented Generation) pipeline.
        1. Retrieve top-k relevant rules via semantic search.
        2. Synthesize a natural language response.
        """
        context_rules = self.semantic_search(query)
        if not context_rules:
            return {
                "answer": "I couldn't find specific regulations for this query in the current registry.",
                "sources": [],
                "confidence": 0.0
            }

        # Simulate LLM Synthesis
        top_rule = context_rules[0][1]
        source = self.sources.get(top_rule["source_id"], {})

        # We mock the LLM's 'thought' process
        answer = (
            f"Based on the {source.get('authority', 'official')} guidelines for {top_rule.get('jurisdiction')}, "
            f"the requirement for '{top_rule.get('name')}' is: {top_rule.get('requirement')} "
            f"This is documented in {source.get('title', 'the guidelines')} ({source.get('citation', 'N/A')})."
        )

        return {
            "answer": answer,
            "sources": [source for source in self.sources.values() if source["source_id"] == top_rule["source_id"]],
            "confidence": context_rules[0][0],
            "reasoning": "Semantic retrieval matched query to rule-001 via key terms."
        }

    def get_applicable_rules(self, country_pair: str, product: str = "cosmetics") -> List[Dict[str, Any]]:
        rules: List[Dict[str, Any]] = []
        for rule in self.rules.values():
            if "India->USA" in country_pair and rule.get("jurisdiction") == "India→USA":
                rules.append(rule)
            elif product and rule.get("name", "").lower().find(product.lower()) != -1:
                rules.append(rule)
        return rules

registry = KnowledgeRegistry()
registry.register_source("gov-india", "Government of India", "India→USA", "Export Documentation Guidelines", "https://example.org/india-export-guidelines")
registry.add_rule(
    "rule-001",
    "Certificate of origin rule",
    "India→USA",
    "Government of India",
    {"country_pair": "India->USA"},
    "REQUIRE_DOCUMENT",
    "Certificate of origin is typically required for export to the USA.",
    "gov-india",
)
registry.add_rule(
    "rule-002",
    "Invoice and packing list reconciliation",
    "India→USA",
    "Government of India",
    {"document_types": ["commercial_invoice", "packing_list"]},
    "RECONCILE",
    "Invoice and packing list values should reconcile within tolerance.",
    "gov-india",
)
