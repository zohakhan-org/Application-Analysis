# App Analysis Framework (Python)

A Python implementation of an AI-powered framework that:
- analyzes a live application URL for UX/SEO/accessibility signals,
- analyzes a code repository for maintainability/code-quality signals,
- creates a prioritized implementation plan,
- optionally asks an LLM to generate an executive summary and 30/60/90-day roadmap.

## LLM support
- **Primary (default): Ollama** for open-source local models.
- Also supports **OpenAI-compatible endpoints** (`openai`, `azure-openai`, `groq`, or custom OpenAI-compatible gateways).
- Provider/model/base URL/API key are configurable via CLI and GUI.

## CLI usage

```bash
python -m app_analysis_framework.cli analyze-url https://example.com --format markdown
python -m app_analysis_framework.cli analyze-repo . --format json

# Ollama summary (default local endpoint)
python -m app_analysis_framework.cli analyze-url https://example.com --with-llm

# OpenAI-compatible summary
python -m app_analysis_framework.cli analyze-repo . --with-llm \
  --llm-provider openai \
  --llm-base-url https://api.openai.com \
  --llm-model gpt-4o-mini \
  --llm-api-key "$OPENAI_API_KEY"
```

## GUI usage

```bash
python -m app_analysis_framework.gui
# or installed entry point:
app-analysis-gui
```

The GUI allows choosing:
- analysis mode (`url` or `repo`),
- LLM provider,
- model,
- base URL,
- API key.

## Notes
This is an MVP implementation using deterministic analyzers + optional LLM summarization.
