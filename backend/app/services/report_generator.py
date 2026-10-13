from __future__ import annotations

from typing import Any, Dict, List
from pathlib import Path


class ReportGenerator:
    """Generates human-readable structured reports as evidence artifacts."""

    def generate_report(
        self,
        case_id: str,
        title: str,
        findings: List[Dict[str, Any]],
        risk: Dict[str, Any],
    ) -> Dict[str, Any]:
        report_dir = Path(__file__).resolve().parent.parent.parent / "reports"
        report_dir.mkdir(exist_ok=True)

        lines: List[str] = [
            f"# {title}",
            "",
            f"- Case ID: {case_id}",
            f"- Overall Risk: {risk.get('risk_level', 'UNKNOWN')} ({risk.get('overall_score', 0)})",
            "",
            "## Findings",
        ]

        for idx, finding in enumerate(findings, start=1):
            lines.append(f"{idx}. {finding.get('title', 'Finding')} [{finding.get('severity', 'UNKNOWN')}]")
            if "description" in finding:
                lines.append(f"   - {finding['description']}")

        output_path = report_dir / f"{case_id.lower().replace(' ', '-')}.md"
        output_path.write_text("\n".join(lines), encoding="utf-8")

        return {
            "status": "generated",
            "path": str(output_path),
            "title": title,
            "risk": risk,
            "finding_count": len(findings),
        }
