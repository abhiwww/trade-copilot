from fastapi import APIRouter
from pydantic import BaseModel

from app.services.report_generator import ReportGenerator

router = APIRouter()
engine = ReportGenerator()


class ReportRequest(BaseModel):
    case_id: str
    title: str
    findings: list[dict] = []
    risk: dict = {"overall_score": 0, "risk_level": "LOW"}


@router.post("/reports/generate")
def generate_report(request: ReportRequest):
    return engine.generate_report(
        case_id=request.case_id,
        title=request.title,
        findings=request.findings,
        risk=request.risk,
    )
