from __future__ import annotations
import asyncio
from typing import Any, Dict, List, Optional, AsyncGenerator
import re

from app.core import repository as repo
from app.services.llm_service import llm_service

MAX_CONTEXT_CHARS = 6000
MAX_DOC_CHARS = 4000
MAX_HISTORY_MESSAGES = 12

# Prompt defense patterns
_INJECTION_PATTERNS = [
    r"ignore (all )?previous instructions",
    r"system prompt",
    r"you are now a",
    r"forget everything",
    r"act as a",
]

def sanitize_prompt(message: str) -> str:
    """Detect and neutralize basic prompt injection attempts."""
    sanitized = message
    for pattern in _INJECTION_PATTERNS:
        if re.search(pattern, sanitized, re.IGNORECASE):
            sanitized = f"[REDACTED INJECTION ATTEMPT]: {sanitized}"
    return sanitized

def detect_intent(message: str, has_documents: bool) -> str:
    msg = message.strip()
    if re.search(r"^\s*(hi+|hello+|hey+|yo|good\s*(morning|afternoon|evening)|howdy|greetings|namaste| Vanakkam)\b[!.\s]*$", msg, re.IGNORECASE):
        return "greeting"
    if re.search(r"\b(what can you do|who are you|your capabilities|what do you do|help me|how do you work|features)\b", msg, re.IGNORECASE):
        return "capability"
    if has_documents:
        return "document"
    if re.search(r"\b(export|import|hs code|hs classification|customs|tariff|duty|compliance|sanctions|incoterm|letter of credit|lc |bill of lading|invoice|packing list|shipment|trade|regulation|customs bond|coo|origin)\b", msg, re.IGNORECASE):
        return "trade"
    return "general"

def _doc_text(doc) -> str:
    try:
        with open(doc.storage_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()[:MAX_DOC_CHARS]
    except Exception:
        return ""

def build_context(user, conversation, message: str, intent: Optional[str] = None) -> Dict[str, Any]:
    if intent is None:
        intent = detect_intent(message, bool(conversation.document_ids))

    docs: List[Dict[str, Any]] = []
    case = None

    if intent in ("document", "trade", "general") and conversation.document_ids:
        for doc_id in conversation.document_ids:
            doc = repo.docs.get_by_id(doc_id)
            if doc:
                docs.append({
                    "document_id": doc.document_id,
                    "filename": doc.filename,
                    "document_type": doc.document_type,
                    "text_excerpt": _doc_text(doc),
                })

    if intent in ("trade", "general") and conversation.case_id:
        case_record = repo.cases.get_by_id(conversation.case_id)
        if case_record:
            case = {
                "case_id": case_record.case_id,
                "name": case_record.name,
                "product": case_record.product,
                "origin": case_record.origin,
                "destination": case_record.destination,
            }

    return {
        "intent": intent,
        "docs": docs,
        "case": case,
    }

_SYSTEM_PROMPT = (
    "You are Trade Copilot, a professional trade intelligence assistant inside a SaaS product. "
    "You help users analyse trade documents, understand compliance, and answer questions about "
    "their shipments. Be accurate, concise, and professional. Use markdown when it improves "
    "readability. When you use information from an attached document, name the document. "
    "Never invent document contents, page numbers, or regulatory requirements. If you do not "
    "know something or the information was not provided, say so honestly and explain what would "
    "be needed."
)

_DOCUMENT_SYSTEM_ADDENDUM = (
    " The user has attached document(s) provided in the CONTEXT below. Ground your answer in "
    "that text. Quote or cite the document when describing what it says. Clearly separate "
    "DOCUMENT FACT (what the text says) from AI INTERPRETATION (your analysis) and UNCERTAINTY "
    "(what the text does not cover)."
)

_CAPABILITY_TEXT = (
    "I'm Trade Copilot — your trade intelligence partner. Here's what I can help with:\n\n"
    "- **Document intelligence** — upload trade documents (invoices, packing lists, letters of "
    "credit, certificates, technical papers) and ask me anything about their contents\n"
    "- **Trade case analysis** — organize shipments into trade cases and analyze them for "
    "compliance, discrepancies, and risk\n"
    "- **Compliance & rules** — explain applicable trade regulations and flag issues like "
    "missing certificates, quantity mismatches, or required permits\n"
    "- **Risk assessment** — predictive risk scoring across sanctions, reconciliation, "
    "documentation, and integrity dimensions\n"
    "- **Fraud signals** — anomaly detection across your documents and trade routes\n\n"
    "Try attaching a document or asking about a shipment — I read the actual content and answer "
    "from it."
)

async def generate_answer_stream(user, conversation, message: str, history: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
    """Produce a streamed answer using the LLM service."""
    sanitized_msg = sanitize_prompt(message)
    intent = detect_intent(sanitized_msg, bool(conversation.document_ids))
    context = build_context(user, conversation, sanitized_msg, intent)

    context_blocks = []
    for d in context["docs"]:
        context_blocks.append(
            f"--- DOCUMENT: {d['filename']} (type: {d['document_type'] or 'unknown'}, id: {d['document_id']}) ---\n"
            f"{d['text_excerpt']}"
        )
    if context["case"]:
        c = context["case"]
        context_blocks.append(
            f"--- TRADE CASE: {c['name']} ({c['case_id']}) ---\n"
            f"Product: {c['product']}\nOrigin: {c['origin']}\nDestination: {c['destination']}"
        )

    system_prompt = _SYSTEM_PROMPT
    if intent == "document":
        system_prompt += _DOCUMENT_SYSTEM_ADDENDUM
    elif intent == "capability":
        system_prompt += (
            " The user is asking what you can do. Describe Trade Copilot's actual capabilities "
            f"truthfully. Supported capabilities summary for reference: {_CAPABILITY_TEXT}"
        )

    history_block = "\n".join(
        f"{m['role'].upper()}: {m['content'][:400]}" for m in history[-MAX_HISTORY_MESSAGES:]
    )

    user_prompt_parts = []
    if context_blocks:
        user_prompt_parts.append("CONTEXT:\n" + "\n\n".join(context_blocks))
    if history_block:
        user_prompt_parts.append("CONVERSATION SO FAR:\n" + history_block)
    user_prompt_parts.append("USER MESSAGE: " + (sanitized_msg if sanitized_msg else "(The user sent only attachment(s). Summarize what the attached document(s) contain and how you can help with them.)"))

    return llm_service.chat_completion_stream(system_prompt, "\n\n".join(user_prompt_parts))

async def generate_answer(user, conversation, message: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
    """Legacy non-streaming version."""
    answer = await llm_service.chat_completion(_SYSTEM_PROMPT, message)
    return {"answer": answer, "context_used": {}}

def persist_message(conversation_id: str, role: str, content: str,
                    findings: Optional[List[Dict[str, Any]]] = None,
                    document_ids: Optional[List[str]] = None) -> str:
    message_id = str(uuid.uuid4())[:12]
    from app.models.trade_models import Message
    repo.messages.save(message_id, Message(
        message_id=message_id,
        conversation_id=conversation_id,
        role=role,
        content=content,
        findings=findings or [],
        document_ids=document_ids or [],
    ))
    return message_id

def touch_conversation(conversation, title_hint: Optional[str] = None):
    conversation.updated_at = datetime.utcnow()
    if title_hint and (not conversation.title or conversation.title == "New Chat"):
        conversation.title = title_hint.strip()[:60]
    repo.conversations.save(conversation.conversation_id, conversation)
