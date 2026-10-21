"""Convert a prepared portrait into the original lightweight animated ASCII SVG."""

from __future__ import annotations

import html
import os
import sys

import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "source-prepped.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "avi-ascii.svg")
COLS = int(os.environ.get("COLS", "100"))
RAMP = " .`:-=+*cs#%@"
CHAR_WIDTH = 7.2
CHAR_HEIGHT = 13.0
STATIC = bool(os.environ.get("STATIC"))


def image_to_ascii(image_path: str, width: int = COLS) -> list[str]:
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Could not open {image_path}")

    image_height, image_width = image.shape
    rows = max(1, int(width * (image_height / image_width) * 0.53))
    resized = cv2.resize(image, (width, rows), interpolation=cv2.INTER_AREA)

    lines = []
    for row in resized:
        characters = []
        for pixel in row:
            index = int((1 - pixel / 255) * (len(RAMP) - 1))
            characters.append(RAMP[index])
        lines.append("".join(characters))
    return lines


def generate_svg(lines: list[str], output_path: str = OUT) -> None:
    columns = max((len(line) for line in lines), default=1)
    width = int(columns * CHAR_WIDTH) + 20
    height = int(len(lines) * CHAR_HEIGHT) + 20

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}">\n',
        "<style>\n"
        ".ascii-text { font-family: 'Courier New', Courier, monospace; "
        "font-size: 11px; font-weight: bold; fill: #8b949e; white-space: pre; }\n"
        "</style>\n",
        '<rect width="100%" height="100%" fill="#0d1117" rx="6"/>\n',
        '<g transform="translate(10, 15)">\n',
    ]
    for index, line in enumerate(lines):
        y = index * CHAR_HEIGHT
        safe_line = html.escape(line, quote=False)
        if STATIC:
            parts.append(
                f'<text x="0" y="{y:.1f}" class="ascii-text" xml:space="preserve">'
                f"{safe_line}</text>\n"
            )
        else:
            delay = index * 0.04
            parts.append(
                f'<text x="0" y="{y:.1f}" class="ascii-text" xml:space="preserve">'
                f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" '
                f'dur="0.01s" fill="freeze"/>{safe_line}</text>\n'
            )
    parts.extend(["</g>\n", "</svg>\n"])

    with open(output_path, "w", encoding="utf-8") as output:
        output.write("".join(parts))
    print(f"ASCII SVG saved to {output_path} ({width} x {height})")


def main() -> None:
    generate_svg(image_to_ascii(SRC), OUT)


if __name__ == "__main__":
    main()
