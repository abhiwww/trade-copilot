from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
from app.core import repository as repo
from app.models.trade_models import TradeCase
from app.api.routes.auth import get_current_user, User
from app.core.permissions import require_permission, CASE_READ, CASE_WRITE, CASE_DELETE

router = APIRouter(prefix="/cases", tags=["Trade Cases"])

class CaseCreateRequest(BaseModel):
    name: str
    origin_country: str
    origin_state: Optional[str] = None
    origin_city: Optional[str] = None
    origin_port: Optional[str] = None
    dest_country: str
    dest_state: Optional[str] = None
    dest_city: Optional[str] = None
    dest_port: Optional[str] = None
    product: str
    hs_code: Optional[str] = None

@router.get("/", response_model=List[dict])
async def list_cases(user: User = Depends(require_permission(CASE_READ))):
    # Get all cases for the user's organization
    cases = repo.cases.get_by_org(user.org_id)
    return [case.__dict__ for case in cases]

@router.post("/", response_model=dict)
async def create_case(req: CaseCreateRequest, user: User = Depends(require_permission(CASE_WRITE))):
    case_id = f"TC-{datetime.now().year}-{str(uuid.uuid4())[:6].upper()}"

    new_case = TradeCase(
        case_id=case_id,
        org_id=user.org_id,
        name=req.name,
        status="Draft",
        origin={
            "country": req.origin_country,
            "state": req.origin_state,
            "city": req.origin_city,
            "port": req.origin_port
        },
        destination={
            "country": req.dest_country,
            "state": req.dest_state,
            "city": req.dest_city,
            "port": req.dest_port
        },
        product=req.product,
        hs_code=req.hs_code
    )

    repo.cases.save(case_id, new_case)
    return {"message": "Trade case created successfully", "case_id": case_id}

@router.get("/{case_id}", response_model=dict)
async def get_case(case_id: str, user: User = Depends(require_permission(CASE_READ))):
    case = repo.cases.get_by_id(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Trade case not found")
    if case.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="Trade case not found")
    return case.__dict__
