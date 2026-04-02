from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from app_analysis_framework.models import AnalysisFinding, AnalysisReport, FindingSeverity


@dataclass(slots=True)
class ParsedHtmlSignals:
    title: str | None = None
    has_meta_description: bool = False
    h1_count: int = 0
    image_count: int = 0
    images_missing_alt: int = 0
    internal_links: int = 0
    external_links: int = 0


class _SignalExtractor(HTMLParser):
    def __init__(self, domain: str) -> None:
        super().__init__()
        self.signals = ParsedHtmlSignals()
        self._in_title = False
        self._title_buf: list[str] = []
        self._domain = domain

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag == "title":
            self._in_title = True
        if tag == "meta" and attrs_dict.get("name", "").lower() == "description":
            self.signals.has_meta_description = bool(attrs_dict.get("content"))
        if tag == "h1":
            self.signals.h1_count += 1
        if tag == "img":
            self.signals.image_count += 1
            if not attrs_dict.get("alt"):
                self.signals.images_missing_alt += 1
        if tag == "a":
            href = attrs_dict.get("href") or ""
            if href.startswith("http"):
                if self._domain in href:
                    self.signals.internal_links += 1
                else:
                    self.signals.external_links += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
            self.signals.title = "".join(self._title_buf).strip() or None

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title_buf.append(data)


class URLAnalyzer:
    def analyze(self, url: str, timeout_seconds: int = 20) -> AnalysisReport:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid URL: {url}")

        request = Request(url, headers={"User-Agent": "AppAnalysisFramework/0.1"})
        with urlopen(request, timeout=timeout_seconds) as response:
            html = response.read().decode("utf-8", errors="ignore")

        parser = _SignalExtractor(domain=parsed.netloc)
        parser.feed(html)

        report = AnalysisReport(subject=url, report_type="url", metadata={"domain": parsed.netloc})
        signals = parser.signals

        if not signals.title:
            report.add_finding(
                AnalysisFinding(
                    category="seo",
                    title="Missing page title",
                    description="Page appears to have no <title>, reducing discoverability and clarity.",
                    severity=FindingSeverity.HIGH,
                    impact=7,
                    effort=2,
                    confidence=9,
                    evidence="No <title> tag content detected.",
                )
            )

        if not signals.has_meta_description:
            report.add_finding(
                AnalysisFinding(
                    category="seo",
                    title="Missing meta description",
                    description="Meta description is missing or empty.",
                    severity=FindingSeverity.MEDIUM,
                    impact=5,
                    effort=2,
                    confidence=8,
                    evidence="No <meta name='description' content='...'> found.",
                )
            )

        if signals.h1_count != 1:
            sev = FindingSeverity.MEDIUM if signals.h1_count == 0 else FindingSeverity.LOW
            report.add_finding(
                AnalysisFinding(
                    category="accessibility",
                    title="Heading structure issue",
                    description=f"Expected exactly one H1, found {signals.h1_count}.",
                    severity=sev,
                    impact=4,
                    effort=2,
                    confidence=8,
                    evidence=f"Detected H1 count: {signals.h1_count}",
                )
            )

        if signals.images_missing_alt > 0:
            report.add_finding(
                AnalysisFinding(
                    category="accessibility",
                    title="Images missing alt text",
                    description="Some images are missing alt text, impacting accessibility.",
                    severity=FindingSeverity.MEDIUM,
                    impact=6,
                    effort=3,
                    confidence=8,
                    evidence=f"{signals.images_missing_alt}/{signals.image_count} images missing alt.",
                )
            )

        if signals.external_links > (signals.internal_links * 3 + 5):
            report.add_finding(
                AnalysisFinding(
                    category="ux",
                    title="Potential outbound-link heavy page",
                    description="Page contains many external links compared with internal links.",
                    severity=FindingSeverity.LOW,
                    impact=3,
                    effort=2,
                    confidence=6,
                    evidence=f"Internal: {signals.internal_links}, External: {signals.external_links}",
                )
            )

        report.metadata["signals"] = signals.__dict__
        return report
