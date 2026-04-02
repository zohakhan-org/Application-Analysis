from app_analysis_framework.models import AnalysisFinding, AnalysisReport, FindingSeverity
from app_analysis_framework.planner import ImplementationPlanner


def test_planner_prioritizes_higher_score():
    report = AnalysisReport(subject="x", report_type="repo")
    report.add_finding(
        AnalysisFinding(
            category="security",
            title="Critical issue",
            description="desc",
            severity=FindingSeverity.CRITICAL,
            impact=9,
            effort=2,
            confidence=8,
            evidence="e1",
        )
    )
    report.add_finding(
        AnalysisFinding(
            category="code_quality",
            title="Minor style",
            description="desc",
            severity=FindingSeverity.LOW,
            impact=2,
            effort=5,
            confidence=8,
            evidence="e2",
        )
    )

    tasks = ImplementationPlanner().build_plan(report)
    assert tasks[0].priority == "P0"
    assert "Critical issue" in tasks[0].title
