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
    # wire:loading.class / .remove sit on the real content, so leave those alone.
    html = re.sub(
        r'<div[^>]*\swire:loading(?!\.remove|\.class)[^>]*>',
        '<div hidden data-dc-loading-shell="1">',
        html,
        flags=re.I,
    )
    html = re.sub(
        r"<span[^>]*\swire:loading(?!\.remove|\.class)[^>]*>[\s\S]*?</span>\s*",
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


def dca_bar_chart_svg() -> str:
    """Static copy of the Chart.js 'Online vs In-Person' bar chart (canvas is blank without JS)."""
    cats = ["Social", "DartBot", "Lobbies", "Events", "League Singles", "League Team"]
    in_person = {"League Team": 38.14}
    left, right, top, bottom, ymax = 40, 772, 10, 340, 40
    step = (right - left) / len(cats)
    y = lambda v: bottom - (bottom - top) * v / ymax
    text = 'font-family="Open Sans, sans-serif" font-size="11" fill="#666"'
    out = ['<svg viewBox="0 0 782 440" width="100%" height="100%" role="img" '
           'aria-label="Online vs In-Person Performance">']
    for v in range(0, ymax + 1, 5):
        out.append(f'<line x1="{left}" x2="{right}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="#e5e5e5"/>')
        out.append(f'<text x="{left - 8}" y="{y(v) + 4:.1f}" text-anchor="end" {text}>{v}</text>')
    for i in range(len(cats) + 1):
        x = left + i * step
        out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{top}" y2="{bottom + 6}" stroke="#e5e5e5"/>')
    out.append(f'<line x1="{left}" x2="{right}" y1="{bottom}" y2="{bottom}" stroke="#999"/>')
    for i, c in enumerate(cats):
        cx = left + (i + 0.5) * step
        out.append(f'<text x="{cx:.1f}" y="{bottom + 20}" text-anchor="middle" {text}>{c}</text>')
        if c in in_person:
            v = in_person[c]
            bw = step * 0.36
            bx = cx + step * 0.04
            out.append(f'<rect x="{bx:.1f}" y="{y(v):.1f}" width="{bw:.1f}" '
                       f'height="{bottom - y(v):.1f}" fill="#f7d68a"/>')
            out.append(f'<text x="{bx + bw / 2:.1f}" y="{(y(v) + bottom) / 2 + 4:.1f}" text-anchor="middle" '
                       f'font-family="Open Sans, sans-serif" font-size="12" font-weight="700" '
                       f'fill="#6b5a2a">{v:.2f}</text>')
    mid = (left + right) / 2
    out.append(f'<text x="{mid}" y="{bottom + 44}" text-anchor="middle" font-family="Open Sans, sans-serif" '
               f'font-size="12" font-weight="700" fill="#666">Online vs In-Person Performance</text>')
    ly = bottom + 64
    out.append(f'<rect x="{mid - 110}" y="{ly}" width="40" height="12" fill="#c9dcee"/>')
    out.append(f'<text x="{mid - 64}" y="{ly + 10}" {text}>Online DCA</text>')
    out.append(f'<rect x="{mid + 12}" y="{ly}" width="40" height="12" fill="#f7d68a"/>')
    out.append(f'<text x="{mid + 58}" y="{ly + 10}" {text}>In-Person DCA</text>')
    out.append("</svg>")
    return "".join(out)


def replace_bar_chart_canvas(body: str) -> str:
    out, n = re.subn(r'<canvas id="barChart"[^>]*></canvas>', dca_bar_chart_svg(), body, count=1)
    if n != 1:
        raise SystemExit("barChart canvas not found")
    return out


def hide_activity_pie_card(body: str) -> str:
    """The flip card's front (My Activity) is only a blank Chart.js canvas; show the Achievements side."""
    out, n = re.subn(
        r'(<div class="flex overflow-hidden flex-col p-4 bg-white rounded-md shadow lg:p-6 front")',
        r'\1 style="display:none"',
        body,
        count=1,
    )
    if n != 1:
        raise SystemExit("My Activity front card not found")
    return out


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
    body = replace_bar_chart_canvas(body)
    body = hide_activity_pie_card(body)
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