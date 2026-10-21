#!/usr/bin/env python3
"""Render contribution data as an animated GitHub-style heatmap SVG."""

from __future__ import annotations

import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from profile import PROMPT

IN_PATH = os.path.join(HERE, "..", "data", "contributions.json")
OUT_PATH = os.path.join(HERE, "..", "contrib-heatmap.svg")

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
CELL = 12
GAP = 3
STEP = CELL + GAP
PAD = 22
LEFT_LABEL_W = 30
TOP_LABEL_H = 20
TITLEBAR_H = 30

BG = "#0a0e14"
BG2 = "#0d1420"
FRAME = "#30363d"
MUTED = "#7d8590"
TEXT = "#e6edf3"
ACCENT = "#22d3ee"
GREEN = "#39d353"
GOLD = "#f2cc60"

COL_T = 0.018
ROW_T = 0.045
CELL_DUR = 0.42
STATIC = bool(os.environ.get("STATIC"))


def level_for(count: int) -> int:
    if count == 0:
        return 0
    if count <= 5:
        return 1
    if count <= 15:
        return 2
    if count <= 30:
        return 3
    if count <= 50:
        return 4
    return 5


def build_grid(days: list[dict]) -> list[list[tuple[str, int, int] | None]]:
    first = datetime.date.fromisoformat(days[0]["date"])
    leading_padding = (first.weekday() + 1) % 7
    grid: list[list[tuple[str, int, int] | None]] = []
    column: list[tuple[str, int, int] | None] = [None] * leading_padding
    for day in days:
        date = datetime.date.fromisoformat(day["date"])
        weekday = (date.weekday() + 1) % 7
        while len(column) < weekday:
            column.append(None)
        column.append((day["date"], day["count"], level_for(day["count"])))
        if len(column) == 7:
            grid.append(column)
            column = []
    if column:
        column.extend([None] * (7 - len(column)))
        grid.append(column)
    return grid


def render(data: dict) -> str:
    days = data["days"]
    grid = build_grid(days)
    column_count = len(grid)
    art_width = column_count * STEP
    art_height = 7 * STEP

    month_labels: list[tuple[int, str]] = []
    seen_months: set[tuple[int, int]] = set()
    for column_index, column in enumerate(grid):
        for cell in column:
            if cell is None:
                continue
            date = datetime.date.fromisoformat(cell[0])
            key = (date.year, date.month)
            if key not in seen_months and date.day <= 7:
                seen_months.add(key)
                month_labels.append((column_index, date.strftime("%b")))
            break

    canvas_width = PAD + LEFT_LABEL_W + art_width + PAD
    stats_height = 88
    canvas_height = TITLEBAR_H + TOP_LABEL_H + art_height + stats_height + PAD
    css = f"""
@keyframes cell {{
  0% {{ opacity: 0; transform: translateY(-6px); }}
  100% {{ opacity: 1; transform: translateY(0); }}
}}
.c {{ opacity: 0; animation: cell {CELL_DUR:.2f}s cubic-bezier(.2,.8,.2,1) both; }}
""".strip()
    if STATIC:
        css = ".c { opacity: 1; }"

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_width}" height="{canvas_height}" '
        f'viewBox="0 0 {canvas_width} {canvas_height}">\n',
        f"<style>{css}</style>\n",
        '<defs><linearGradient id="hmbg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="{BG2}"/>'
        "</linearGradient></defs>\n",
        f'<rect width="100%" height="100%" rx="12" fill="url(#hmbg)" stroke="{FRAME}" stroke-width="1"/>\n',
        f'<rect width="100%" height="{TITLEBAR_H}" rx="12" fill="#161b22"/>\n'
        f'<rect y="{TITLEBAR_H - 12}" width="100%" height="12" fill="#161b22"/>\n',
    ]
    for index, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{18 + index * 16}" cy="{TITLEBAR_H / 2}" r="5" fill="{color}"/>\n')
    parts.append(
        f'<text x="{canvas_width / 2}" y="20" text-anchor="middle" '
        f'font-family="SF Mono, Menlo, Consolas, monospace" font-size="12" '
        f'fill="{MUTED}">{PROMPT}: ~/contributions --graph</text>\n'
    )

    grid_top = TITLEBAR_H + TOP_LABEL_H
    grid_left = PAD + LEFT_LABEL_W
    for column_index, label in month_labels:
        x = grid_left + column_index * STEP
        parts.append(
            f'<text x="{x}" y="{TITLEBAR_H + 16}" font-family="SF Mono, Menlo, Consolas, monospace" '
            f'font-size="10" fill="{MUTED}">{label}</text>\n'
        )
    for weekday_index, weekday_name in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        y = grid_top + weekday_index * STEP + CELL * 0.78
        parts.append(
            f'<text x="{PAD + 2}" y="{y:.1f}" font-family="SF Mono, Menlo, Consolas, monospace" '
            f'font-size="9" fill="{MUTED}">{weekday_name}</text>\n'
        )

    for column_index, column in enumerate(grid):
        x = grid_left + column_index * STEP
        for row_index, cell in enumerate(column):
            if cell is None:
                continue
            date_text, count, level = cell
            y = grid_top + row_index * STEP
            delay = column_index * COL_T + row_index * ROW_T
            plural = "s" if count != 1 else ""
            delay_attribute = "" if STATIC else f' style="animation-delay:{delay:.3f}s"'
            parts.append(
                f'<rect class="c"{delay_attribute} x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'rx="2" fill="{PALETTE[level]}"><title>{date_text}: {count} contribution{plural}</title></rect>\n'
            )

    legend_y = grid_top + art_height + 6
    legend_x = canvas_width - PAD - (len(PALETTE) * (CELL - 1) + 70)
    parts.append(
        f'<text x="{legend_x - 28}" y="{legend_y + CELL - 2}" font-family="SF Mono, Menlo, Consolas, monospace" '
        f'font-size="10" fill="{MUTED}">Less</text>\n'
    )
    x = legend_x + 8
    for color in PALETTE:
        parts.append(f'<rect x="{x}" y="{legend_y}" width="{CELL - 2}" height="{CELL - 2}" rx="2" fill="{color}"/>\n')
        x += CELL
    parts.append(
        f'<text x="{x + 4}" y="{legend_y + CELL - 2}" font-family="SF Mono, Menlo, Consolas, monospace" '
        f'font-size="10" fill="{MUTED}">More</text>\n'
    )

    separator_y = legend_y + CELL + 14
    parts.append(
        f'<line x1="{PAD}" y1="{separator_y}" x2="{canvas_width - PAD}" y2="{separator_y}" '
        f'stroke="{FRAME}" stroke-width="1"/>\n'
    )
    current_streak = data["current_streak"]["length"]
    longest_streak = data["longest_streak"]["length"]
    total = data["total_contributions"]
    best = data["best_day"]
    date_range = data["range"]
    y = separator_y + 24
    parts.append(
        f'<text x="{PAD}" y="{y}" font-family="SF Mono, Menlo, Consolas, monospace" font-size="13">'
        f'<tspan fill="{GREEN}" font-weight="700">{total:,}</tspan>'
        f'<tspan fill="{TEXT}">  contributions in the last year</tspan></text>\n'
    )
    parts.append(
        f'<text x="{canvas_width - PAD}" y="{y}" text-anchor="end" font-family="SF Mono, Menlo, Consolas, monospace" '
        f'font-size="11" fill="{MUTED}">{date_range["start"]} - {date_range["end"]}</text>\n'
    )
    y += 24
    parts.append(
        f'<text x="{PAD}" y="{y}" font-family="SF Mono, Menlo, Consolas, monospace" font-size="12" fill="{MUTED}">'
        f'current streak <tspan fill="{ACCENT}">{current_streak} days</tspan>'
        f'  |  longest <tspan fill="{GOLD}">{longest_streak} days</tspan></text>\n'
    )
    parts.append(
        f'<text x="{canvas_width - PAD}" y="{y}" text-anchor="end" font-family="SF Mono, Menlo, Consolas, monospace" '
        f'font-size="11" fill="{MUTED}">best day {best["count"]} on {best["date"]}</text>\n'
    )
    if data.get("sample"):
        parts.append(
            f'<text x="{canvas_width / 2}" y="{canvas_height - 10}" text-anchor="middle" '
            f'font-family="SF Mono, Menlo, Consolas, monospace" font-size="9" fill="#6e7681">'
            "sample data - update profile.py and run fetch_contributions.py</text>\n"
        )
    parts.append("</svg>\n")
    return "".join(parts)


def main() -> None:
    if not os.path.isfile(IN_PATH):
        raise SystemExit(f"missing {IN_PATH}; run python scripts/fetch_contributions.py first")
    with open(IN_PATH, encoding="utf-8") as source:
        data = json.load(source)
    svg = render(data)
    with open(OUT_PATH, "w", encoding="utf-8") as output:
        output.write(svg)
    print(f"wrote {OUT_PATH} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
