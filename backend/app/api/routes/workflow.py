from fastapi import APIRouter
from pydantic import BaseModel

from app.services.workflow_engine import WorkflowEngine

router = APIRouter()
engine = WorkflowEngine()


class WorkflowRequest(BaseModel):
    findings: list[dict] = []


@router.post("/workflow/tasks")
def create_review_tasks(request: WorkflowRequest):
    return {"status": "ok", "tasks": engine.resolve_findings(request.findings)}


@router.get("/workflow/tasks")
def list_tasks():
    return engine.list_tasks()
