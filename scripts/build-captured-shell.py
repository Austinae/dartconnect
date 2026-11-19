#!/usr/bin/env python3
"""Sanitize captured dashboard HTML for a high-fidelity React shell."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "reference" / "dashboard" / "dashboard.html"
OUT = ROOT / "src" / "generated"

TREND_CARD = """
<div class="rounded-md bg-white shadow p-3.5 relative xl:p-5 flex flex-col">
    <h1 class="text-2xl md:text-3xl font-bold flex mb-2">
        <div class="flex flex-col">
            <div class="flex items-center">
                <span>My 3-Dart Average Trend</span>
            </div>
            <div class="flex flex-col text-xl lg:items-center lg:space-x-3 lg:flex-row">
                <span class="font-normal text-blue-500">Singles 501 SIDO</span>
                <span class="hidden lg:inline-flex rounded-full bg-coolblue-500 w-1.5 h-1.5"></span>
                <span class="font-normal text-blue-500">Per session · rolling average</span>
            </div>
        </div>
    </h1>
    <div id="react-trend-chart-root"></div>
</div>
""".strip()


def strip_livewire_comments(html: str) -> str:
    html = re.sub(r"<!--\[if BLOCK\]><!\[endif\]-->", "", html)
    html = re.sub(r"<!--\[if ENDBLOCK\]><!\[endif\]-->", "", html)
    return html


def sanitize(html: str) -> str:
    html = re.sub(r"<script[\s\S]*?</script>", "", html, flags=re.I)
    html = re.sub(r"<style[\s\S]*?</style>", "", html, flags=re.I)

    # Drop Livewire loading shells (both blocks render without Alpine/Livewire → duplicates).
    html = re.sub(
        r'<div[^>]*\swire:loading(?!\.remove)[^>]*>',
        '<div hidden data-dc-loading-shell="1">',
        html,
        flags=re.I,
    )
    html = re.sub(
        r"<span[^>]*\swire:loading(?!\.remove)[^>]*>[\s\S]*?</span>\s*",
        "",
        html,
        flags=re.I,
    )

    html = re.sub(r'\swire:[^\s=]+="[^"]*"', "", html)
    html = re.sub(r"\swire:[^\s=]+(?=\s|>)", "", html)

    attrs = (
        "data-has-alpine-state",
    )
    for attr in attrs:
        html = re.sub(rf'\s{re.escape(attr)}="[^"]*"', "", html)
        html = re.sub(rf"\s{re.escape(attr)}(?=\s|>)", "", html)

    html = re.sub(r'\sx-data="[^"]*"', "", html)
    html = re.sub(r'\sx-show="[^"]*"', "", html)
    html = re.sub(r'\s@[\w.]+="[^"]*"', "", html)
    html = re.sub(r'\sonclick="[^"]*"', "", html)

    html = re.sub(r'name="_token" value="[^"]*"', 'name="_token" value=""', html)
    html = re.sub(r"mailto:[^\s\"']+", "#", html)
    html = re.sub(r"webcal://[^\s\"']+", "#", html)
    html = re.sub(
        r"https://my\.dartconnect\.com/api/league/schedules/ical/[^\s\"']+",
        "#",
        html,
    )
    html = re.sub(
        r"https://calendar\.google\.com/calendar/r\?cid=[^\s\"']+",
        "#",
        html,
    )
    # Prototype is static — no runtime asset fetches from my.dartconnect.com.
    html = re.sub(
        r"https://my\.dartconnect\.com/(?:images|assets)/[^\s\"']+",
        "/dartconnect-placeholder.svg",
        html,
    )
    html = strip_livewire_comments(html)
    html = re.sub(
        r"<!-- Google Tag Manager \(noscript\) -->[\s\S]*?<!-- End Google Tag Manager \(noscript\) -->",
        "",
        html,
    )
    html = re.sub(r"<noscript>[\s\S]*?</noscript>", "", html, flags=re.I)
    html = re.sub(
        r'<div id="unsupported-browser"[\s\S]*?</div>\s*</div>',
        "",
        html,
        count=1,
    )
    return html


def excise_loading_shells(html: str) -> str:
    """Remove Livewire loading placeholders (entire subtrees)."""
    needle = 'data-dc-loading-shell="1"'
    while needle in html:
        start = html.find("<div hidden data-dc-loading-shell=\"1\">")
        if start < 0:
            start = html.find('<div hidden data-dc-loading-shell="1">')
        if start < 0:
            break
        depth = 0
        i = start
        end = -1
        while i < len(html):
            if html.startswith("<div", i):
                depth += 1
                i = html.find(">", i) + 1
                continue
            if html.startswith("</div>", i):
                depth -= 1
                if depth == 0:
                    end = i + len("</div>")
                    break
                i += len("</div>")
                continue
            i += 1
        if end < 0:
            raise SystemExit("Failed to excise Livewire loading shell")
        html = html[:start] + html[end:]
    return html


def extract_body_inner(html: str) -> str:
    m = re.search(r"<body[^>]*>([\s\S]*)</body>", html, re.I)
    if not m:
        raise SystemExit("No <body> in dashboard capture")
    return m.group(1).strip()


def remove_bottom_line_chart_section(body: str) -> str:
    """Drop the buried 'My Performance Average (DCA)' card at the bottom."""
    pattern = re.compile(
        r"<div>\s*<div class=\"rounded-md bg-white shadow p-3.5 relative xl:p-5 flex overflow-hidden flex-col\">"
        r"[\s\S]*?My Performance Average \(DCA\)[\s\S]*?</div>\s*</div>\s*</div>\s*</div>",
        re.MULTILINE,
    )
    out, n = pattern.subn("", body, count=1)
    if n != 1:
        raise SystemExit("Could not remove bottom line chart section (pattern miss)")
    return out


def polish_performance_copy(body: str) -> str:
    """Pitch-friendly labels: default range reads as season, not one annual dot."""
    body = re.sub(
        r"(<span>My Performance</span>[\s\S]*?)<span class=\"text-2xl font-normal\">All Time</span>",
        r'\1<span class="text-2xl font-normal">Fall Season</span>',
        body,
        count=1,
    )
    body = body.replace(
        '<option value="">All Time</option>',
        '<option value="" selected>Fall Season</option>',
        1,
    )
    return body


def redact_sensitive_strings(body: str) -> str:
    body = re.sub(
        r">\s*[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\s*<",
        ">Contact captain<",
        body,
    )
    return body


def inject_trend_card(body: str) -> str:
    needle = '<div class="grid grid-cols-2 gap-2 md:gap-4 sm:grid-cols-3 lg:grid-cols-6 xl:grid-cols-7">'
    if needle not in body:
        raise SystemExit("Performance stat grid not found for trend card injection")
    # Fix erroneous motionStat placeholder from template
    card = TREND_CARD.replace("<motionStat />", "")
    return body.replace(needle, card + "\n" + needle, 1)


def split_footer(body: str) -> tuple[str, str]:
    marker = '<footer class="mt-12 border-t-4 border-[#ad1f23] bg-[#16273A] text-white">'
    idx = body.find(marker)
    if idx < 0:
        raise SystemExit("Footer marker not found")
    return body[:idx], body[idx:]


def main() -> None:
    raw = SRC.read_text(encoding="utf-8")
    body = extract_body_inner(sanitize(raw))
    body = excise_loading_shells(body)
    body = remove_bottom_line_chart_section(body)
    body = polish_performance_copy(body)
    body = redact_sensitive_strings(body)
    body = inject_trend_card(body)
    before, after = split_footer(body)

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "shell-before-chart.html").write_text(before, encoding="utf-8")
    (OUT / "shell-after-chart.html").write_text(after, encoding="utf-8")
    print(f"Wrote {OUT}/shell-before-chart.html ({len(before):,} bytes)")
    print(f"Wrote {OUT}/shell-after-chart.html ({len(after):,} bytes)")


if __name__ == "__main__":
    main()