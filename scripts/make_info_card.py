"""Render the animated neofetch-style profile information SVG."""

from __future__ import annotations

import html
import os
import sys
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from profile import DISPLAY_NAME, HIGHLIGHTS, LOCATION, NOW, PREV, PROMPT, ROLE, STACK

OUT = os.path.join(HERE, "..", "info-card.svg")
STATIC = bool(os.environ.get("STATIC"))

W, H = 980, 620
PAD = 30
TITLEBAR_H = 30
BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
TEXT = "#e6edf3"
KEY = "#79c0ff"
ACCENT = "#22d3ee"
GREEN = "#3fb950"
GOLD = "#d29922"
PINK = "#f778ba"


def row_style(index: int) -> str:
    if STATIC:
        return 'opacity="1"'
    delay = 0.18 + index * 0.12
    return f'style="opacity:0;animation:lineIn .45s ease {delay:.2f}s forwards"'


def wrap(value: str, width: int = 42) -> list[str]:
    return textwrap.wrap(value, width=width) or [""]


def render() -> str:
    css = """
@keyframes lineIn {
  from { opacity: 0; transform: translateX(-10px); }
  to { opacity: 1; transform: translateX(0); }
}
""".strip()
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n',
        f"<style>{css}</style>\n",
        '<defs><linearGradient id="cardbg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="{BG2}"/>'
        "</linearGradient></defs>\n",
        f'<rect width="100%" height="100%" rx="12" fill="url(#cardbg)" stroke="{FRAME}" stroke-width="1"/>\n',
        f'<rect width="100%" height="{TITLEBAR_H}" rx="12" fill="#161b22"/>\n'
        f'<rect y="{TITLEBAR_H - 12}" width="100%" height="12" fill="#161b22"/>\n',
    ]
    for index, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{18 + index * 16}" cy="{TITLEBAR_H / 2}" r="5" fill="{color}"/>\n')
    parts.append(
        f'<text x="{W / 2}" y="20" text-anchor="middle" '
        f'font-family="SF Mono, Menlo, Consolas, monospace" font-size="12" '
        f'fill="{MUTED}">{html.escape(PROMPT)}: ~$ neofetch</text>\n'
    )

    x = PAD
    y = TITLEBAR_H + 54
    line_height = 32
    index = 0

    def text_line(content: str, fill: str, size: int = 16, extra: str = "") -> None:
        nonlocal index, y
        parts.append(
            f'<text x="{x}" y="{y}" {row_style(index)} '
            f'font-family="SF Mono, Menlo, Consolas, monospace" font-size="{size}" '
            f'fill="{fill}"{extra}>{content}</text>\n'
        )
        index += 1
        y += line_height

    text_line(html.escape(DISPLAY_NAME), ACCENT, 28)
    text_line(html.escape(f"{ROLE}  /  {LOCATION}"), KEY, 19)
    parts.append(
        f'<line x1="{PAD}" y1="{y + 2}" x2="{W - PAD}" y2="{y + 2}" '
        f'stroke="{FRAME}" stroke-width="1"/>\n'
    )
    y += 24

    fields = [
        ("FOCUS", NOW, GOLD),
        ("PREVIOUS", PREV, KEY),
        ("STACK", STACK, PINK),
    ]
    key_width = 12
    for key, value, color in fields:
        for chunk_index, chunk in enumerate(wrap(value, 48)):
            label = f"{key:<{key_width}}" if chunk_index == 0 else " " * key_width
            parts.append(
                f'<text x="{x}" y="{y}" {row_style(index)} xml:space="preserve" '
                f'font-family="SF Mono, Menlo, Consolas, monospace" font-size="14" fill="{MUTED}">'
                f'{html.escape(label)}'
                f'<tspan fill="{color if chunk_index == 0 else TEXT}" font-size="21">{html.escape(chunk)}</tspan>'
                "</text>\n"
            )
            index += 1
            y += line_height

    y += 8
    text_line("WHAT I ENJOY BUILDING", KEY, 17)
    for item in HIGHLIGHTS:
        for chunk_index, chunk in enumerate(wrap(item, 52)):
            prefix = "  > " if chunk_index == 0 else "    "
            parts.append(
                f'<text x="{x}" y="{y}" {row_style(index)} xml:space="preserve" '
                f'font-family="SF Mono, Menlo, Consolas, monospace" font-size="19" fill="{TEXT}">'
                f'<tspan fill="{ACCENT}">{html.escape(prefix)}</tspan>{html.escape(chunk)}</text>\n'
            )
            index += 1
            y += line_height

    y += 8
    parts.append(
        f'<text x="{x}" y="{y}" {row_style(index)} '
        f'font-family="SF Mono, Menlo, Consolas, monospace" font-size="15" fill="{MUTED}">'
        f'{html.escape(PROMPT)}:~$  <tspan fill="{GREEN}">ready to build</tspan></text>\n'
    )
    parts.append("</svg>\n")
    return "".join(parts)


def main() -> None:
    svg = render()
    with open(OUT, "w", encoding="utf-8") as output:
        output.write(svg)
    print("wrote", OUT, len(svg), "bytes")


if __name__ == "__main__":
    main()
