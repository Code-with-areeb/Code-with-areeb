"""Create a simple grayscale bust so the ASCII pipeline works without a photo."""

from __future__ import annotations

import math
import os

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "source-prepped.png")
SIZE = 1024


def main() -> None:
    image = Image.new("L", (SIZE, SIZE), 255)
    draw = ImageDraw.Draw(image)
    center_x, center_y = SIZE // 2, SIZE // 2 + 40

    draw.ellipse([center_x - 340, center_y + 80, center_x + 340, center_y + 720], fill=40)
    draw.ellipse([center_x - 190, center_y - 280, center_x + 190, center_y + 80], fill=55)
    draw.ellipse([center_x - 200, center_y - 310, center_x + 200, center_y - 40], fill=18)
    draw.rectangle([center_x - 200, center_y - 140, center_x + 200, center_y - 40], fill=55)
    draw.ellipse([center_x - 90, center_y - 140, center_x - 30, center_y - 95], fill=22)
    draw.ellipse([center_x + 30, center_y - 140, center_x + 90, center_y - 95], fill=22)
    draw.arc([center_x - 50, center_y - 40, center_x + 50, center_y + 20], 20, 160, fill=22, width=8)

    pixels = image.load()
    for y in range(SIZE):
        for x in range(SIZE):
            dx = (x - center_x) / (SIZE * 0.52)
            dy = (y - center_y + 40) / (SIZE * 0.58)
            radius = math.sqrt(dx * dx + dy * dy)
            if radius > 1:
                pixels[x, y] = 255
            elif radius > 0.82:
                blend = (radius - 0.82) / 0.18
                pixels[x, y] = int(pixels[x, y] * (1 - blend) + 255 * blend)

    image.filter(ImageFilter.GaussianBlur(radius=1.2)).save(OUT)
    print("wrote", OUT, "(placeholder; replace with prep_photo.py and a real portrait)")


if __name__ == "__main__":
    main()
