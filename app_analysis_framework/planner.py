from __future__ import annotations

from dataclasses import dataclass

from app_analysis_framework.models import AnalysisFinding, AnalysisReport


@dataclass(slots=True)
class PlannedTask:
    title: str
    priority: str
    owner_role: str
    eta_days: int
    acceptance_criteria: str


class ImplementationPlanner:
    def build_plan(self, report: AnalysisReport, max_tasks: int = 10) -> list[PlannedTask]:
        planned: list[PlannedTask] = []
        for finding in report.prioritized_findings()[:max_tasks]:
            planned.append(self._task_from_finding(finding))
        return planned

    def _task_from_finding(self, finding: AnalysisFinding) -> PlannedTask:
        score = finding.priority_score()
        if score >= 5:
            priority = "P0"
            eta = 3
        elif score >= 3:
            priority = "P1"
            eta = 7
        else:
            priority = "P2"
            eta = 14

        owner_map = {
            "accessibility": "Frontend Engineer",
            "seo": "Frontend Engineer",
            "ux": "Product + Frontend",
            "security": "Security Engineer",
            "maintainability": "Backend Engineer",
            "code_quality": "Backend Engineer",
            "delivery": "Engineering Manager",
            "repo": "Tech Lead",
        }
        owner_role = owner_map.get(finding.category, "Engineering Team")

        return PlannedTask(
            title=f"[{finding.category}] {finding.title}",
            priority=priority,
            owner_role=owner_role,
            eta_days=eta,
            acceptance_criteria=(
                f"Resolved finding with measurable evidence. Validation: {finding.evidence} updated and tests/checks pass."
            ),
        )
