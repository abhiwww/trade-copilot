from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, AsyncGenerator
import asyncio
import json
from app.services.rule_engine import RuleEngine
from app.services.workflow_engine import WorkflowEngine
from app.services.risk_engine import RiskEngine
from app.services.document_pipeline import DocumentAnalysisPipeline
from app.services.reconciliation_engine import MultiDocumentReconciliationEngine
from app.services.integrity_engine import integrity_engine
from app.core import repository as repo
from app.models.trade_models import User
from app.api.routes.auth import get_current_user
from app.core.permissions import require_permission, CHAT_SEND
from app.core.ratelimit import limiter
from app.services import chat_service

router = APIRouter()
rule_engine = RuleEngine()
workflow_engine = WorkflowEngine()
risk_engine = RiskEngine()
doc_pipeline = DocumentAnalysisPipeline()
recon_engine = MultiDocumentReconciliationEngine()

class ChatRequest(BaseModel):
    message: str = ""
    case_id: Optional[str] = None
    conversation_id: Optional[str] = None
    document_ids: List[str] = Field(default_factory=list)
    country_pair: str = "India->USA"

async def analysis_stream(request: ChatRequest, user: User, convo=None):
    """
    Generates a stream of events for the frontend to show the AI's thought process
    and real-time token streaming.
    """
    # 1. Status updates (The "Thinking" UX)
    yield f"data: {json.dumps({'event': 'status', 'message': 'Initializing Intelligence Engine...'})}\n\n"
    await asyncio.sleep(0.5)

    if request.document_ids:
        yield f"data: {json.dumps({'event': 'status', 'message': 'Ingesting trade documents...'})}\n\n"
        await asyncio.sleep(0.5)

    yield f"data: {json.dumps({'event': 'status', 'message': 'Evaluating regulations and anomalies...'})}\n\n"
    await asyncio.sleep(0.5)

    # 2. Actual Token Streaming
    # We call the new generate_answer_stream which returns an AsyncGenerator
    token_stream = await chat_service.generate_answer_stream(user, convo, request.message, [])

    full_answer = []
    async for token in token_stream:
        full_answer.append(token)
        yield f"data: {json.dumps({'event': 'token', 'content': token})}\n\n"

    final_text = "".join(full_answer)

    # 3. Final Result Packaging
    # We still want to provide the structured data (findings, risk) at the end
    final_result = {
        "answer": final_text,
        "summary": final_text[:200],
        "conversation_id": convo.conversation_id if convo else None,
        "findings": [], # In a full impl, we'd trigger rule_engine here
        "status": "analysis_complete",
    }
    yield f"data: {json.dumps({'event': 'final', 'data': final_result})}\n\n"

    if convo is not None:
        chat_service.persist_message(convo.conversation_id, "assistant", final_text)

@router.post("/chat/stream")
async def stream_analyze_chat(request: ChatRequest, user: User = Depends(require_permission(CHAT_SEND))):
    limit_key = f"chat:{user.user_id}"
    allowed, retry_after = limiter.check_limit(limit_key, limit=20, window=60)
    if not allowed:
        raise HTTPException(status_code=429, detail=f"Too many requests. Retry in {retry_after}s.")

    message = request.message.strip()
    document_ids = [doc_id for doc_id in request.document_ids if doc_id]

    if not message and not document_ids:
        raise HTTPException(status_code=422, detail="Message or attachment is required")

    convo = None
    if request.conversation_id:
        convo = repo.conversations.get_by_id(request.conversation_id)
        if not convo or convo.org_id != user.org_id:
            raise HTTPException(status_code=404, detail="Conversation not found")
    if convo is None:
        from app.models.trade_models import Conversation
        import uuid as _uuid
        from datetime import datetime as _dt
        convo = Conversation(
            conversation_id=str(_uuid.uuid4())[:12],
            org_id=user.org_id,
            user_id=user.user_id,
            title=message[:60] if message else "New Chat",
            case_id=request.case_id,
            document_ids=document_ids,
            created_at=_dt.utcnow(),
            updated_at=_dt.utcnow(),
        )
        repo.conversations.save(convo.conversation_id, convo)
    else:
        if request.case_id:
            case = repo.cases.get_by_id(request.case_id)
            if not case or case.org_id != user.org_id:
                raise HTTPException(status_code=404, detail="Trade case not found or access denied")
            convo.case_id = request.case_id
        for doc_id in document_ids:
            if doc_id not in (convo.document_ids or []):
                convo.document_ids.append(doc_id)
        chat_service.touch_conversation(convo, title_hint=message[:60] if message else None)

    for doc_id in document_ids:
        doc = repo.docs.get_by_id(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")

    chat_service.persist_message(convo.conversation_id, "user", message, document_ids=document_ids)

    return StreamingResponse(
        analysis_stream(request, user, convo),
        media_type="text/event-stream",
    )
