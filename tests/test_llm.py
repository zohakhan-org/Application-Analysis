from app_analysis_framework.llm import LLMClient, LLMConfig, LLMError
from app_analysis_framework.models import AnalysisFinding, AnalysisReport, FindingSeverity


def _sample_report() -> AnalysisReport:
    report = AnalysisReport(subject="https://example.com", report_type="url")
    report.add_finding(
        AnalysisFinding(
            category="seo",
            title="Missing title",
            description="desc",
            severity=FindingSeverity.HIGH,
            impact=7,
            effort=2,
            confidence=9,
            evidence="No title",
        )
    )
    return report


def test_unsupported_provider_raises():
    client = LLMClient(LLMConfig(provider="unknown"))
    try:
        client.summarize_report(_sample_report())
        assert False, "Expected LLMError"
    except LLMError as exc:
        assert "Unsupported provider" in str(exc)


def test_ollama_happy_path_without_network(monkeypatch):
    client = LLMClient(LLMConfig(provider="ollama", model="llama3.1:8b"))

    def fake_post_json(url: str, payload: dict, headers: dict[str, str]) -> dict:
        assert url.endswith("/api/generate")
        assert payload["model"] == "llama3.1:8b"
        return {"response": "Executive summary"}

    monkeypatch.setattr(client, "_post_json", fake_post_json)
    result = client.summarize_report(_sample_report())
    assert "Executive summary" in result
