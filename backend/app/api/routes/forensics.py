from fastapi import APIRouter
from pydantic import BaseModel

from app.services.document_forensics import DocumentForensicsEngine

router = APIRouter()
engine = DocumentForensicsEngine()


class ForensicsRequest(BaseModel):
    filename: str
    metadata: dict | None = None
    text: str = ""
    hash: str | None = None


@router.post("/forensics/analyze")
def analyze_document(request: ForensicsRequest):
    return engine.analyze_document(request.model_dump())
