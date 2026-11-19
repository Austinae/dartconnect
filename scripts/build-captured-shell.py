#!/usr/bin/env python3
"""Sanitize captured dashboard HTML for a high-fidelity React shell."""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "reference" / "dashboard" / "dashboard.html"
OUT = ROOT / "src" / "generated"
MOCK = ROOT / "src" / "data" / "performances.json"
SEASON_START = "2026-08-15"  # keep in sync with PLAYER.seasonStart
PLAY_TYPES = ["Social", "DartBot", "Lobbies", "Events", "League Singles", "League Team"]
ONLINE_TYPES = {"Lobbies"}

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


def dca_bar_chart_svg(online: dict[str, float], in_person: dict[str, float]) -> str:
    """Static copy of the Chart.js 'Online vs In-Person' bar chart (canvas is blank without JS)."""
    cats = PLAY_TYPES
    left, right, top, bottom = 40, 772, 10, 340
    peak = max([*online.values(), *in_person.values(), 1])
    tick = 5 if peak <= 40 else 10
    ymax = int(-(-peak // tick) * tick)
    step = (right - left) / len(cats)
    y = lambda v: bottom - (bottom - top) * v / ymax
    text = 'font-family="Open Sans, sans-serif" font-size="11" fill="#666"'
    out = ['<svg viewBox="0 0 782 440" width="100%" height="100%" role="img" '
           'aria-label="Online vs In-Person Performance">']
    for v in range(0, ymax + 1, tick):
        out.append(f'<line x1="{left}" x2="{right}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="#e5e5e5"/>')
        out.append(f'<text x="{left - 8}" y="{y(v) + 4:.1f}" text-anchor="end" {text}>{v}</text>')
    for i in range(len(cats) + 1):
        x = left + i * step
        out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{top}" y2="{bottom + 6}" stroke="#e5e5e5"/>')
    out.append(f'<line x1="{left}" x2="{right}" y1="{bottom}" y2="{bottom}" stroke="#999"/>')
    bw = step * 0.36
    for i, c in enumerate(cats):
        cx = left + (i + 0.5) * step
        out.append(f'<text x="{cx:.1f}" y="{bottom + 20}" text-anchor="middle" {text}>{c}</text>')
        bars = [(online.get(c), cx - step * 0.04 - bw, "#c9dcee", "#3d5a75"),
                (in_person.get(c), cx + step * 0.04, "#f7d68a", "#6b5a2a")]
        for v, bx, fill, ink in bars:
            if v is None:
                continue
            out.append(f'<rect x="{bx:.1f}" y="{y(v):.1f}" width="{bw:.1f}" '
                       f'height="{bottom - y(v):.1f}" fill="{fill}"/>')
            out.append(f'<text x="{bx + bw / 2:.1f}" y="{(y(v) + bottom) / 2 + 4:.1f}" text-anchor="middle" '
                       f'font-family="Open Sans, sans-serif" font-size="12" font-weight="700" '
                       f'fill="{ink}">{v:.2f}</text>')
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


def mock_stats() -> dict:
    """Numbers for the static cards, derived from the widget's mock sessions so both agree."""
    sessions = sorted(json.loads(MOCK.read_text(encoding="utf-8")), key=lambda p: p["date"])

    def totals(rows: list[dict]) -> dict:
        legs = darts = 0
        for i, p in enumerate(rows):
            n = 2 + i % 3  # 2 to 4 legs of 501 per session
            legs += n
            darts += round(n * 501 * 3 / p["threeDartAvg"])
        rivals = sum(1 for p in rows if p["playType"] != "DartBot")
        return {"opponents": round(rivals * 0.6), "matches": len(rows), "legs": legs, "darts": darts}

    last = sessions[-1]["date"]
    season = [p for p in sessions if p["date"] >= SEASON_START]
    avgs = {}
    for pt in PLAY_TYPES:
        vals = [p["threeDartAvg"] for p in season if p["playType"] == pt]
        if vals:
            avgs[pt] = round(sum(vals) / len(vals), 2)
    best = max(p["threeDartAvg"] for p in season)
    sido = totals(season)
    visits = sido["darts"] / 3
    # The activity card counts every game type, not only Singles 501.
    all_games = lambda t: {**t, "legs": round(t["legs"] * 2.5), "darts": round(t["darts"] * 2.5)}
    return {
        "first_year": sessions[0]["date"][:4],
        "last_match": f"{date.fromisoformat(last).day} {date.fromisoformat(last):%b %Y}",
        "this_year": all_games(totals([p for p in sessions if p["date"][:4] == last[:4]])),
        "all_time": all_games(totals(sessions)),
        "online": {k: v for k, v in avgs.items() if k in ONLINE_TYPES},
        "in_person": {k: v for k, v in avgs.items() if k not in ONLINE_TYPES},
        "sido": sido,
        "high_avg": best,
        "low_dart_game": round(501 * 3 / (best * 1.3)),
        "highest_finish": 104,
        "tons": [round(visits * r) for r in (0.38, 0.11, 0.02, 0.004)],  # 60+, 100+, 140+, 180s
    }


def region(body: str, start: str, end: str | None) -> tuple[int, int]:
    a = body.find(start)
    b = body.find(end, a) if end else len(body)
    if a < 0 or b < 0:
        raise SystemExit(f"Region not found: {start!r}")
    return a, b


def sub_in_order(seg: str, pattern: str, values: list[str | None], what: str) -> str:
    """Replace group 'v' of each match with the next value (None keeps the match)."""
    it = iter(values)
    count = 0

    def repl(m: re.Match) -> str:
        nonlocal count
        count += 1
        v = next(it, None)
        if v is None:
            return m.group(0)
        a, b = m.span("v")
        return m.group(0)[: a - m.start()] + v + m.group(0)[b - m.start():]

    out = re.sub(pattern, repl, seg)
    if count != len(values):
        raise SystemExit(f"{what}: expected {len(values)} slots, found {count}")
    return out


COUNT_UP = r'CountUp\(\$refs\.input, [\d.]+, \{[^"]*">(?P<v>[\d,.]+)</span>'


def align_with_mock_data(body: str, st: dict) -> str:
    """Rewrite the captured numbers so every card tells the same story as the trend widget."""
    fmt = lambda t: [f"{t[k]:,}" for k in ("opponents", "matches", "legs", "darts")]

    body = body.replace("Member Since 2026", f"Member Since {st['first_year']}", 1)
    body = body.replace(
        '<span class="font-semibold">Member Since</span> 2026',
        f'<span class="font-semibold">Member Since</span> {st["first_year"]}',
        1,
    )
    body = re.sub(r"(Last DC Match:\s*)\d+ \w+ \d{4}", rf"\g<1>{st['last_match']}", body, count=1)

    # Player Activity: this year then all time, once for desktop and once for mobile.
    a, b = region(body, "Player Activity", "Competition Average")
    rows = fmt(st["this_year"]) + fmt(st["all_time"])
    body = body[:a] + sub_in_order(body[a:b], COUNT_UP, rows * 2, "Player Activity") + body[b:]

    # Play-type tiles: slots run online then in-person, in the order the site draws them.
    slots = []
    for pt, kinds in [("Social", "oi"), ("DartBot", "i"), ("Lobbies", "o"),
                      ("Events", "oi"), ("League Singles", "oi"), ("League Team", "oi")]:
        for k in kinds:
            v = (st["online"] if k == "o" else st["in_person"]).get(pt)
            slots.append(None if v is None else f"{v:.2f}")
    a, b = region(body, 'id="react-trend-chart-root"', "My DartConnect Average (DCA)")
    tile = r'<span>\s*(?P<v><span class="text-blue-300">---</span>|\d+\.\d{2})\s*</span>'
    body = body[:a] + sub_in_order(body[a:b], tile, slots, "Performance tiles") + body[b:]

    # Cards below follow the page filter, which reads Fall Season.
    a, b = region(body, "My DartConnect Average (DCA)", None)
    seg = re.sub(r'(<span class="font-normal text-blue-500">\s*)All Time(\s*</span>)', r"\1Fall Season\2", body[a:b])
    body = body[:a] + seg

    a, b = region(body, "<span>My Achievements</span>", None)
    seg = body[a:b]
    t60, t100, t140, t180 = st["tons"]
    seg = sub_in_order(seg, COUNT_UP, fmt(st["sido"]) + [f"{t60:,}", f"{t100:,}"], "Achievements")
    for label, old, new in [("Low Dart Game", "24", st["low_dart_game"]),
                            ("High Match Average", "51.68", f"{st['high_avg']:.2f}"),
                            ("Highest Finish", "56", st["highest_finish"])]:
        seg, n = re.subn(rf"<span>{re.escape(old)}</span>(?=[\s\S]{{0,400}}?{label})", f"<span>{new}</span>", seg, count=1)
        if n != 1:
            raise SystemExit(f"Achievements: {label} not found")
    for label, val in [("140+", t140), ("180s", t180)]:
        seg, n = re.subn(rf"---(\s*</span>\s*<span class=\"text-blue-400 text-center\">\s*{re.escape(label)})",
                         rf"{val}\1", seg, count=1)
        if n != 1:
            raise SystemExit(f"Achievements: {label} not found")
    return body[:a] + seg


def replace_bar_chart_canvas(body: str, st: dict) -> str:
    svg = dca_bar_chart_svg(st["online"], st["in_person"])
    out, n = re.subn(r'<canvas id="barChart"[^>]*></canvas>', lambda _: svg, body, count=1)
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
    stats = mock_stats()
    body = replace_bar_chart_canvas(body, stats)
    body = hide_activity_pie_card(body)
    body = polish_performance_copy(body)
    body = redact_sensitive_strings(body)
    body = inject_trend_card(body)
    body = align_with_mock_data(body, stats)
    before, after = split_footer(body)

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "shell-before-chart.html").write_text(before, encoding="utf-8")
    (OUT / "shell-after-chart.html").write_text(after, encoding="utf-8")
    print(f"Wrote {OUT}/shell-before-chart.html ({len(before):,} bytes)")
    print(f"Wrote {OUT}/shell-after-chart.html ({len(after):,} bytes)")


if __name__ == "__main__":
    main()