from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

from app.core import repository as repo
from app.models.trade_models import Conversation, User
from app.api.routes.auth import get_current_user
from app.core.permissions import require_permission, CHAT_SEND, CASE_DELETE, CASE_READ
from app.services import chat_service

router = APIRouter(prefix="/conversations", tags=["Conversations"])


class ConversationCreate(BaseModel):
    title: Optional[str] = None
    case_id: Optional[str] = None
    document_ids: List[str] = []


class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    case_id: Optional[str] = None
    add_document_ids: List[str] = []


@router.get("/")
async def list_conversations(user: User = Depends(require_permission(CASE_READ))):
    convos = repo.conversations.get_by_org(user.org_id)
    return [
        {
            "conversation_id": c.conversation_id,
            "title": c.title,
            "case_id": c.case_id,
            "document_ids": c.document_ids,
            "updated_at": str(c.updated_at),
        }
        for c in convos
    ]


@router.post("/")
async def create_conversation(req: ConversationCreate, user: User = Depends(require_permission(CHAT_SEND))):
    if req.case_id:
        case = repo.cases.get_by_id(req.case_id)
        if not case or case.org_id != user.org_id:
            raise HTTPException(status_code=404, detail="Trade case not found or access denied")

    conversation_id = str(uuid.uuid4())[:12]
    convo = Conversation(
        conversation_id=conversation_id,
        org_id=user.org_id,
        user_id=user.user_id,
        title=(req.title or "New Chat").strip()[:60],
        case_id=req.case_id,
        document_ids=req.document_ids,
    )
    repo.conversations.save(conversation_id, convo)
    return {"conversation_id": conversation_id, "title": convo.title}


def _get_owned_conversation(conversation_id: str, user: User) -> Conversation:
    convo = repo.conversations.get_by_id(conversation_id)
    if not convo or convo.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return convo


@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str, user: User = Depends(require_permission(CASE_READ))):
    convo = _get_owned_conversation(conversation_id, user)
    msgs = repo.messages.get_by_conversation(conversation_id)
    return {
        "conversation_id": convo.conversation_id,
        "title": convo.title,
        "case_id": convo.case_id,
        "document_ids": convo.document_ids,
        "messages": [
            {
                "message_id": m.message_id,
                "role": m.role,
                "content": m.content,
                "findings": m.findings,
                "document_ids": m.document_ids,
            }
            for m in msgs
        ],
    }


@router.patch("/{conversation_id}")
async def update_conversation(conversation_id: str, req: ConversationUpdate, user: User = Depends(get_current_user)):
    convo = _get_owned_conversation(conversation_id, user)
    if req.title is not None:
        convo.title = req.title.strip()[:60]
    if req.case_id is not None:
        case = repo.cases.get_by_id(req.case_id)
        if not case or case.org_id != user.org_id:
            raise HTTPException(status_code=404, detail="Trade case not found or access denied")
        convo.case_id = req.case_id
    for doc_id in req.add_document_ids:
        doc = repo.docs.get_by_id(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
        case = repo.cases.get_by_id(doc.case_id)
        if not case or case.org_id != user.org_id:
            raise HTTPException(status_code=403, detail="Access denied for document")
        if doc_id not in (convo.document_ids or []):
            convo.document_ids.append(doc_id)
    chat_service.touch_conversation(convo)
    return {"status": "ok", "title": convo.title, "case_id": convo.case_id, "document_ids": convo.document_ids}


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str, user: User = Depends(get_current_user)):
    _get_owned_conversation(conversation_id, user)
    repo.conversations.delete(conversation_id)
    return {"status": "ok"}
