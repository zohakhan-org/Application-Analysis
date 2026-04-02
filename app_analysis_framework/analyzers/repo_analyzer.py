from __future__ import annotations

from pathlib import Path

from app_analysis_framework.models import AnalysisFinding, AnalysisReport, FindingSeverity


class RepoAnalyzer:
    def analyze(self, repo_path: str) -> AnalysisReport:
        root = Path(repo_path).resolve()
        if not root.exists() or not root.is_dir():
            raise ValueError(f"Invalid repository path: {repo_path}")

        report = AnalysisReport(subject=str(root), report_type="repository")

        python_files = [p for p in root.rglob("*.py") if ".git" not in p.parts and "venv" not in p.parts]
        if not python_files:
            report.add_finding(
                AnalysisFinding(
                    category="repo",
                    title="No Python files found",
                    description="No .py files detected for analysis.",
                    severity=FindingSeverity.LOW,
                    impact=2,
                    effort=1,
                    confidence=10,
                    evidence="Repository scan did not find Python source files.",
                )
            )
            return report

        long_functions = 0
        todo_count = 0
        very_long_lines = 0

        for file_path in python_files:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = text.splitlines()

            todo_count += sum(1 for line in lines if "TODO" in line)
            very_long_lines += sum(1 for line in lines if len(line) > 120)

            current_len = 0
            in_def = False
            base_indent = 0
            for line in lines:
                stripped = line.lstrip()
                indent = len(line) - len(stripped)
                if stripped.startswith("def ") or stripped.startswith("async def "):
                    if in_def and current_len > 80:
                        long_functions += 1
                    in_def = True
                    current_len = 1
                    base_indent = indent
                elif in_def:
                    if stripped and indent <= base_indent and not stripped.startswith("#"):
                        if current_len > 80:
                            long_functions += 1
                        in_def = False
                        current_len = 0
                    else:
                        current_len += 1
            if in_def and current_len > 80:
                long_functions += 1

        if long_functions > 0:
            report.add_finding(
                AnalysisFinding(
                    category="maintainability",
                    title="Long functions detected",
                    description="Large functions can increase cognitive load and change risk.",
                    severity=FindingSeverity.MEDIUM,
                    impact=6,
                    effort=4,
                    confidence=7,
                    evidence=f"Detected {long_functions} functions exceeding ~80 lines.",
                )
            )

        if very_long_lines > 0:
            report.add_finding(
                AnalysisFinding(
                    category="code_quality",
                    title="Style consistency issue",
                    description="Very long lines may reduce readability and review speed.",
                    severity=FindingSeverity.LOW,
                    impact=3,
                    effort=2,
                    confidence=9,
                    evidence=f"Detected {very_long_lines} lines over 120 characters.",
                )
            )

        if todo_count > 5:
            report.add_finding(
                AnalysisFinding(
                    category="delivery",
                    title="High TODO backlog",
                    description="Many TODO markers can indicate deferred technical debt.",
                    severity=FindingSeverity.MEDIUM,
                    impact=5,
                    effort=5,
                    confidence=8,
                    evidence=f"Detected {todo_count} TODO markers across Python files.",
                )
            )

        report.metadata.update(
            {
                "python_file_count": len(python_files),
                "todo_count": todo_count,
                "long_functions": long_functions,
                "very_long_lines": very_long_lines,
            }
        )
        return report
