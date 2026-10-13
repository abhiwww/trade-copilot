from fastapi import APIRouter
from pydantic import BaseModel

from app.services.reconciliation_engine import MultiDocumentReconciliationEngine

router = APIRouter()
engine = MultiDocumentReconciliationEngine()


class ReconciliationDocument(BaseModel):
    document_type: str
    fields: list[dict]


class ReconciliationRequest(BaseModel):
    documents: list[ReconciliationDocument]


@router.post("/reconciliation/analyze")
async def analyze_reconciliation(request: ReconciliationRequest):
    result = await engine.reconcile([document.model_dump() for document in request.documents])
    return result
