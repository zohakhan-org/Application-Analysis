from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class FindingSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(slots=True)
class AnalysisFinding:
    category: str
    title: str
    description: str
    severity: FindingSeverity
    impact: int
    effort: int
    confidence: int
    evidence: str

    def priority_score(self) -> float:
        """Simple weighted score in range ~0-10+."""
        severity_weight = {
            FindingSeverity.LOW: 1,
            FindingSeverity.MEDIUM: 2,
            FindingSeverity.HIGH: 3,
            FindingSeverity.CRITICAL: 4,
        }[self.severity]
        return round(((self.impact * 0.5) + (self.confidence * 0.3) + (severity_weight * 2)) / max(self.effort, 1), 2)


@dataclass(slots=True)
class AnalysisReport:
    subject: str
    report_type: str
    findings: list[AnalysisFinding] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_finding(self, finding: AnalysisFinding) -> None:
        self.findings.append(finding)

    def prioritized_findings(self) -> list[AnalysisFinding]:
        return sorted(self.findings, key=lambda f: f.priority_score(), reverse=True)

    def summary(self) -> dict[str, Any]:
        counts = {severity.value: 0 for severity in FindingSeverity}
        for finding in self.findings:
            counts[finding.severity.value] += 1
        return {
            "subject": self.subject,
            "report_type": self.report_type,
            "total_findings": len(self.findings),
            "severity_counts": counts,
        }
