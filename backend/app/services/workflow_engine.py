from __future__ import annotations

from typing import Any, Dict, List


class ReviewTask:
    def __init__(self, task_id: str, task_type: str, title: str, description: str, severity: str = "MEDIUM", assignee: str = "analyst") -> None:
        self.task_id = task_id
        self.task_type = task_type
        self.title = title
        self.description = description
        self.severity = severity
        self.assignee = assignee
        self.status = "OPEN"


class WorkflowEngine:
    """Review task and approval workflow for human triage in trade compliance cases."""

    def __init__(self) -> None:
        self.tasks: List[ReviewTask] = []

    def create_task(self, task_type: str, title: str, description: str, severity: str = "MEDIUM", assignee: str = "analyst") -> Dict[str, Any]:
        task = ReviewTask(
            task_id=f"task-{len(self.tasks)+1}",
            task_type=task_type,
            title=title,
            description=description,
            severity=severity,
            assignee=assignee,
        )
        self.tasks.append(task)
        return {
            "task_id": task.task_id,
            "task_type": task.task_type,
            "title": task.title,
            "description": task.description,
            "severity": task.severity,
            "assignee": task.assignee,
            "status": task.status,
        }

    def resolve_findings(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        tasks: List[Dict[str, Any]] = []
        for finding in findings:
            if finding.get("severity", "").lower() in {"high", "critical"}:
                tasks.append(
                    self.create_task(
                        task_type="FINDING_REVIEW",
                        title=f"Review: {finding.get('title', 'Compliance finding')}",
                        description=finding.get("description", "Human review required for this finding."),
                        severity=finding.get("severity", "MEDIUM").upper(),
                    )
                )
        return tasks

    def list_tasks(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "tasks": [
                {
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                    "title": task.title,
                    "description": task.description,
                    "severity": task.severity,
                    "assignee": task.assignee,
                    "status": task.status,
                }
                for task in self.tasks
            ],
        }
