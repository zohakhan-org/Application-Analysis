from __future__ import annotations

import json
from dataclasses import asdict

from app_analysis_framework.models import AnalysisReport
from app_analysis_framework.planner import PlannedTask


def render_json(report: AnalysisReport, tasks: list[PlannedTask]) -> str:
    data = {
        "summary": report.summary(),
        "findings": [
            {
                "category": f.category,
                "title": f.title,
                "severity": f.severity.value,
                "priority_score": f.priority_score(),
                "description": f.description,
                "evidence": f.evidence,
            }
            for f in report.prioritized_findings()
        ],
        "implementation_plan": [asdict(task) for task in tasks],
        "metadata": report.metadata,
    }
    return json.dumps(data, indent=2)


def render_markdown(report: AnalysisReport, tasks: list[PlannedTask]) -> str:
    summary = report.summary()
    lines = [
        f"# Analysis Report: {summary['subject']}",
        "",
        f"- Report type: **{summary['report_type']}**",
        f"- Total findings: **{summary['total_findings']}**",
        "",
        "## Findings",
    ]

    for finding in report.prioritized_findings():
        lines.extend(
            [
                f"### {finding.title}",
                f"- Category: `{finding.category}`",
                f"- Severity: `{finding.severity.value}`",
                f"- Priority score: `{finding.priority_score()}`",
                f"- Description: {finding.description}",
                f"- Evidence: {finding.evidence}",
                "",
            ]
        )

    lines.append("## Implementation Plan")
    for idx, task in enumerate(tasks, start=1):
        lines.extend(
            [
                f"{idx}. **{task.title}**",
                f"   - Priority: `{task.priority}`",
                f"   - Owner: {task.owner_role}",
                f"   - ETA: {task.eta_days} days",
                f"   - Done when: {task.acceptance_criteria}",
            ]
        )

    lines.append("")
    return "\n".join(lines)
