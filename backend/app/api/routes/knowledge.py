from fastapi import APIRouter

from app.services.knowledge_engine import registry

router = APIRouter()


@router.get("/knowledge/rules")
def list_rules():
    return {"rules": list(registry.rules.values())}


@router.get("/knowledge/search")
def search_knowledge(query: str, jurisdiction: str | None = None):
    return {"matches": registry.search(query, jurisdiction)}
