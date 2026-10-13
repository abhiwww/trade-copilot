from app.services.workflow_engine import WorkflowEngine


def test_workflow_creates_review_tasks_for_high_severity_findings():
    engine = WorkflowEngine()
    findings = [
        {"title": "Quantity mismatch", "severity": "high", "description": "Invoice differs from packing list."},
        {"title": "Warning", "severity": "low", "description": "Minor issue."},
    ]

    tasks = engine.resolve_findings(findings)

    assert len(tasks) == 1
    assert tasks[0]["task_type"] == "FINDING_REVIEW"
    assert tasks[0]["severity"] == "HIGH"
