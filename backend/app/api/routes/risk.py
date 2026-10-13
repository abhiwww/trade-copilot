from fastapi import APIRouter
from pydantic import BaseModel

from app.services.risk_engine import RiskEngine

router = APIRouter()
engine = RiskEngine()


class RiskRequest(BaseModel):
    document: float = 0.0
    regulatory: float = 0.0
    sanctions: float = 0.0
    financial: float = 0.0
    shipment: float = 0.0
    integrity: float = 0.0
    party: float = 0.0
    data_quality: float = 0.0


@router.post("/risk/calculate")
def calculate_risk(request: RiskRequest):
    return engine.calculate(request.model_dump())
