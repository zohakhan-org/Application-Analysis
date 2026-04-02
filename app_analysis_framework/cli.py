from __future__ import annotations

import argparse
from pathlib import Path

from app_analysis_framework.analyzers.repo_analyzer import RepoAnalyzer
from app_analysis_framework.analyzers.url_analyzer import URLAnalyzer
from app_analysis_framework.llm import LLMClient, LLMConfig, LLMError
from app_analysis_framework.planner import ImplementationPlanner
from app_analysis_framework.report import render_json, render_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI Application Analysis Framework")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common_flags(cmd: argparse.ArgumentParser) -> None:
        cmd.add_argument("--format", choices=["json", "markdown"], default="markdown")
        cmd.add_argument("--output", help="Output file path")
        cmd.add_argument("--with-llm", action="store_true", help="Generate LLM summary alongside deterministic report")
        cmd.add_argument("--llm-provider", default="ollama", help="ollama (default) or openai-compatible providers")
        cmd.add_argument("--llm-model", default="llama3.1:8b", help="Model identifier")
        cmd.add_argument("--llm-base-url", default="http://localhost:11434", help="Provider base URL")
        cmd.add_argument("--llm-api-key", default=None, help="API key for non-local providers")

    url_p = sub.add_parser("analyze-url", help="Analyze a website URL")
    url_p.add_argument("url", help="Target URL")
    add_common_flags(url_p)

    repo_p = sub.add_parser("analyze-repo", help="Analyze a repository path")
    repo_p.add_argument("path", nargs="?", default=".", help="Repository path")
    add_common_flags(repo_p)

    return parser


def main() -> int:
    args = build_parser().parse_args()

    if args.command == "analyze-url":
        report = URLAnalyzer().analyze(args.url)
    else:
        report = RepoAnalyzer().analyze(args.path)

    tasks = ImplementationPlanner().build_plan(report)
    rendered = render_json(report, tasks) if args.format == "json" else render_markdown(report, tasks)

    if args.with_llm:
        config = LLMConfig(
            provider=args.llm_provider,
            model=args.llm_model,
            base_url=args.llm_base_url,
            api_key=args.llm_api_key,
        )
        try:
            llm_summary = LLMClient(config).summarize_report(report)
            rendered += f"\n\n## LLM Summary ({config.provider}:{config.model})\n\n{llm_summary}\n"
        except LLMError as exc:
            rendered += f"\n\n## LLM Summary Error\n\n{exc}\n"

    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
