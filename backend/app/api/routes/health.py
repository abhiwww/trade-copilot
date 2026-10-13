from fastapi import APIRouter
from app.services.llm_service import llm_service

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok", "service": "trade-copilot-api"}


@router.get("/ready")
async def readiness_check():
    ai = await llm_service.health_check()
    return {
        "status": "ready",
        "service": "trade-copilot-api",
        "ai": {"provider": ai.get("provider"), "available": ai.get("available"), "model": ai.get("model")},
    }
