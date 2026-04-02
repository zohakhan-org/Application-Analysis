from __future__ import annotations

import json
import os
from dataclasses import dataclass
from urllib.error import URLError
from urllib.request import Request, urlopen

from app_analysis_framework.models import AnalysisReport


@dataclass(slots=True)
class LLMConfig:
    provider: str = "ollama"
    model: str = "llama3.1:8b"
    base_url: str = "http://localhost:11434"
    api_key: str | None = None
    temperature: float = 0.2


class LLMError(RuntimeError):
    pass


class LLMClient:
    """Small multi-provider LLM gateway.

    Primary support is Ollama. Other providers can be integrated via OpenAI-compatible
    APIs by changing provider/base_url/model in config.
    """

    def __init__(self, config: LLMConfig) -> None:
        self.config = config

    def summarize_report(self, report: AnalysisReport, top_n: int = 5) -> str:
        findings = report.prioritized_findings()[:top_n]
        prompt_lines = [
            f"Subject: {report.subject}",
            f"Report Type: {report.report_type}",
            "Top findings:",
        ]
        for idx, finding in enumerate(findings, start=1):
            prompt_lines.append(
                f"{idx}. [{finding.category}] {finding.title} (severity={finding.severity.value}, score={finding.priority_score()})"
            )
            prompt_lines.append(f"   Evidence: {finding.evidence}")

        prompt_lines.append(
            "Provide: (1) executive summary, (2) quick wins for 2 weeks, (3) 30/60/90 day plan in bullets."
        )
        prompt = "\n".join(prompt_lines)

        if self.config.provider == "ollama":
            return self._call_ollama(prompt)
        if self.config.provider in {"openai", "openai-compatible", "azure-openai", "groq"}:
            return self._call_openai_compatible(prompt)

        raise LLMError(
            f"Unsupported provider '{self.config.provider}'. Supported: ollama, openai-compatible providers"
        )

    def _call_ollama(self, prompt: str) -> str:
        url = f"{self.config.base_url.rstrip('/')}/api/generate"
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": self.config.temperature},
        }
        response = self._post_json(url, payload, {})
        return str(response.get("response", "")).strip() or "No response from Ollama model."

    def _call_openai_compatible(self, prompt: str) -> str:
        url = f"{self.config.base_url.rstrip('/')}/v1/chat/completions"
        api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise LLMError("Missing API key. Provide api_key in config or set OPENAI_API_KEY.")

        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": "You are a senior application architecture reviewer."},
                {"role": "user", "content": prompt},
            ],
            "temperature": self.config.temperature,
        }
        headers = {"Authorization": f"Bearer {api_key}"}
        response = self._post_json(url, payload, headers)
        try:
            return response["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError(f"Unexpected OpenAI-compatible response format: {response!r}") from exc

    def _post_json(self, url: str, payload: dict, headers: dict[str, str]) -> dict:
        body = json.dumps(payload).encode("utf-8")
        request_headers = {"Content-Type": "application/json", **headers}
        req = Request(url, data=body, headers=request_headers, method="POST")
        try:
            with urlopen(req, timeout=60) as res:
                return json.loads(res.read().decode("utf-8", errors="ignore"))
        except URLError as exc:
            raise LLMError(f"Could not reach provider endpoint {url}: {exc}") from exc
