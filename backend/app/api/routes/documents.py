from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import shutil
import os
import hashlib
import uuid
from pathlib import Path
from app.core import repository as repo
from app.models.trade_models import Document, User, Evidence
from app.services.document_pipeline import DocumentAnalysisPipeline
from app.services.evidence_engine import evidence_engine
from app.api.routes.auth import get_current_user
from app.core.permissions import require_permission, DOCUMENT_UPLOAD, CASE_READ
from app.core.upload_safety import verify_file_signature, compute_sha256
from app.worker.tasks import process_document_task
from app.core.celery_app import celery_app

router = APIRouter(prefix="/documents", tags=["Documents"])
pipeline = DocumentAnalysisPipeline()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload")
async def upload_document(
    case_id: str = Form(...),
    file: UploadFile = File(...),
    user: User = Depends(require_permission(DOCUMENT_UPLOAD))
):
    # 1. Read content for validation (required for magic-bytes and hashing)
    content = await file.read()

    # 2. Validate Case Existence and Quota
    case = repo.cases.get_by_id(case_id)
    if not case or case.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Trade case not found or access denied")

    # Quota Enforcement
    org = repo.orgs.get_by_id(user.org_id)
    if org:
        limits = {"Basic": 10, "Pro": 100, "Enterprise": 10000}
        limit = limits.get(org.plan, 10)
        if org.total_uploads >= limit:
            raise HTTPException(status_code=403, detail=f"Upload quota exceeded for {org.plan} plan. Please upgrade your plan.")

    # 3. Security: Content Sniffing (Magic Bytes)
    if not verify_file_signature(content, file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File content does not match extension {os.path.splitext(file.filename)[1]}. Upload rejected for safety."
        )

    # 4. Deduplication: SHA-256 Content Hashing
    file_hash = compute_sha256(content)

    # Check if this org has already uploaded this exact file
    existing_doc = repo.docs.get_by_hash(file_hash, user.org_id)
    if existing_doc:
        # Link the existing document to this case instead of duplicating storage
        document = Document(
            document_id=str(uuid.uuid4())[:12],
            case_id=case_id,
            filename=file.filename,
            file_type=os.path.splitext(file.filename)[1],
            size_bytes=len(content),
            storage_path=existing_doc.storage_path, # Point to the same file
            status="Processed" if existing_doc.status == "Processed" else "Processing",
            hash=file_hash
        )
        repo.docs.save(document.document_id, document)

        if document.status == "Processing":
            process_document_task.delay(document.document_id)

        return {
            "status": "ok",
            "document_id": document.document_id,
            "filename": document.filename,
            "status": document.status,
            "deduplicated": True
        }

    # 5. Save to Object Storage (Simulated via local folder)
    doc_id = str(uuid.uuid4())[:12]
    ext = os.path.splitext(file.filename)[1]
    storage_filename = f"{doc_id}{ext}"
    storage_path = UPLOAD_DIR / storage_filename

    with open(storage_path, "wb") as buffer:
        buffer.write(content)

    # 6. Create Document Record
    document = Document(
        document_id=doc_id,
        case_id=case_id,
        filename=file.filename,
        file_type=ext,
        size_bytes=len(content),
        storage_path=str(storage_path),
        status="Processing",
        hash=file_hash
    )
    repo.docs.save(doc_id, document)

    # 7. Trigger Durable Background Processing
    process_document_task.delay(doc_id)

    return {
        "status": "ok",
        "document_id": doc_id,
        "filename": file.filename,
        "status": "Processing",
        "deduplicated": False
    }

@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str, user: User = Depends(require_permission(CASE_READ))):
    """
    Poll for the status of a document processing task.
    """
    result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status, # PENDING, STARTED, SUCCESS, FAILURE
        "result": result.result if result.ready() else None
    }

@router.get("/{document_id}/file")
async def get_document_file(document_id: str, user: User = Depends(require_permission(CASE_READ))):
    doc = repo.docs.get_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check access
    case = repo.cases.get_by_id(doc.case_id)
    if not case or case.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Document not found")

    return FileResponse(doc.storage_path)

@router.get("/{document_id}")
async def get_document(document_id: str, user: User = Depends(require_permission(CASE_READ))):

    doc = repo.docs.get_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check if doc belongs to user's org via the case
    case = repo.cases.get_by_id(doc.case_id)
    if not case or case.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "document_id": doc.document_id,
        "filename": doc.filename,
        "status": doc.status,
        "document_type": doc.document_type,
        "size_bytes": doc.size_bytes
    }

@router.post("/analyze")
async def analyze_document(document_id: str, user: User = Depends(require_permission(CASE_READ))):
    doc = repo.docs.get_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Ensure doc is processed
    if doc.status != "Processed":
        raise HTTPException(status_code=400, detail="Document is still being processed")

    # Read content for analysis
    try:
        with open(doc.storage_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    except Exception:
        text = ""

    result = await pipeline.analyze_document({
        "document_id": doc.document_id,
        "filename": doc.filename,
        "document_type": doc.document_type,
        "text": text,
        "size_bytes": doc.size_bytes
    })

    return {
        "status": "ok",
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
        "validation": result.validation,
    }

@router.get("/{document_id}/evidence/{field_name}")
async def get_field_evidence(document_id: str, field_name: str, user: User = Depends(require_permission(CASE_READ))):
    doc = repo.docs.get_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check access
    case = repo.cases.get_by_id(doc.case_id)
    if not case or case.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Document not found")

    # Use the pipeline to remember to re-extract or find the field's evidence
    try:
        with open(doc.storage_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    except Exception:
        text = ""

    analysis = await pipeline.analyze_document({
        "document_id": doc.document_id,
        "filename": doc.filename,
        "text": text,
        "size_bytes": doc.size_bytes
    })

    field = next((f for f in analysis.extracted_fields if f.name == field_name), None)
    if not field:
        raise HTTPException(status_code=404, detail="Evidence not found for this field")

    evidence = evidence_engine.generate_evidence(doc, field)
    return {
        "evidence_id": evidence.evidence_id,
        "document_id": evidence.document_id,
        "field_name": evidence.field_name,
        "page": evidence.page,
        "bbox": evidence.bbox,
        "snippet": evidence.snippet,
        "confidence": evidence.confidence
    }
