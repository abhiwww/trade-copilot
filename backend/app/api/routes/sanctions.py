from fastapi import APIRouter
from pydantic import BaseModel

from app.services.sanctions_engine import SanctionsScreeningEngine

router = APIRouter()
engine = SanctionsScreeningEngine()


class SanctionsRequest(BaseModel):
    name: str
    country: str | None = None


@router.post("/sanctions/screen")
def screen_entity(request: SanctionsRequest):
    return engine.screen_entity(request.name, request.country)


@router.post("/sanctions/screen-batch")
def screen_batch(request: list[SanctionsRequest]):
    return engine.screen_party_batch([item.model_dump() for item in request])
