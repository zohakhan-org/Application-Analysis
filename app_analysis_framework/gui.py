from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app_analysis_framework.analyzers.repo_analyzer import RepoAnalyzer
from app_analysis_framework.analyzers.url_analyzer import URLAnalyzer
from app_analysis_framework.llm import LLMClient, LLMConfig, LLMError
from app_analysis_framework.planner import ImplementationPlanner
from app_analysis_framework.report import render_markdown


class AnalysisApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Application Analysis Framework")
        self.geometry("1000x700")

        self.mode_var = tk.StringVar(value="url")
        self.target_var = tk.StringVar(value="https://example.com")
        self.provider_var = tk.StringVar(value="ollama")
        self.model_var = tk.StringVar(value="llama3.1:8b")
        self.base_url_var = tk.StringVar(value="http://localhost:11434")
        self.api_key_var = tk.StringVar(value="")

        self._build_ui()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Mode").grid(row=0, column=0, sticky=tk.W)
        ttk.Combobox(frame, textvariable=self.mode_var, values=["url", "repo"], state="readonly", width=12).grid(
            row=0, column=1, sticky=tk.W
        )

        ttk.Label(frame, text="Target URL/Path").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.target_var, width=80).grid(row=1, column=1, columnspan=3, sticky=tk.EW)

        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=2, column=0, columnspan=4, sticky=tk.EW, pady=8)

        ttk.Label(frame, text="LLM Provider").grid(row=3, column=0, sticky=tk.W)
        ttk.Combobox(
            frame,
            textvariable=self.provider_var,
            values=["ollama", "openai", "openai-compatible", "azure-openai", "groq"],
            state="readonly",
            width=22,
        ).grid(row=3, column=1, sticky=tk.W)

        ttk.Label(frame, text="Model").grid(row=4, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.model_var, width=40).grid(row=4, column=1, sticky=tk.W)

        ttk.Label(frame, text="Base URL").grid(row=5, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.base_url_var, width=40).grid(row=5, column=1, sticky=tk.W)

        ttk.Label(frame, text="API Key").grid(row=6, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.api_key_var, width=40, show="*").grid(row=6, column=1, sticky=tk.W)

        ttk.Button(frame, text="Run Analysis", command=self._run).grid(row=7, column=0, pady=10, sticky=tk.W)

        self.output = tk.Text(frame, wrap=tk.WORD)
        self.output.grid(row=8, column=0, columnspan=4, sticky=tk.NSEW)

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(8, weight=1)

    def _run(self) -> None:
        mode = self.mode_var.get()
        target = self.target_var.get().strip()

        try:
            report = URLAnalyzer().analyze(target) if mode == "url" else RepoAnalyzer().analyze(target)
            tasks = ImplementationPlanner().build_plan(report)
            markdown = render_markdown(report, tasks)

            config = LLMConfig(
                provider=self.provider_var.get(),
                model=self.model_var.get(),
                base_url=self.base_url_var.get(),
                api_key=self.api_key_var.get() or None,
            )
            try:
                llm_text = LLMClient(config).summarize_report(report)
                markdown += f"\n\n## LLM Summary ({config.provider}:{config.model})\n\n{llm_text}\n"
            except LLMError as llm_err:
                markdown += f"\n\n## LLM Summary Error\n\n{llm_err}\n"

        except Exception as exc:  # noqa: BLE001 - user-facing app catches errors for display
            markdown = f"Error: {exc}"

        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, markdown)


def run_gui() -> None:
    app = AnalysisApp()
    app.mainloop()


if __name__ == "__main__":
    run_gui()
