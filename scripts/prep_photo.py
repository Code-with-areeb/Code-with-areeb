"""Prepare a portrait for clean ASCII conversion."""

from __future__ import annotations

import os
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove

HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-photo.jpg")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")


def main() -> None:
    if not os.path.isfile(INP):
        raise SystemExit(
            f"missing photo: {INP}\n"
            "drop a portrait in the repo root as source-photo.jpg (or pass a path) and re-run."
        )

    cutout = remove(Image.open(INP).convert("RGBA"))
    array = np.array(cutout)
    rgb = array[:, :, :3]
    alpha = array[:, :, 3]
    grayscale = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    equalized = clahe.apply(grayscale)
    mask = cv2.GaussianBlur(alpha.astype(np.float32) / 255.0, (0, 0), 1.0)
    prepared = equalized.astype(np.float32) * mask + 255.0 * (1.0 - mask)

    ys, xs = np.where(alpha > 20)
    if xs.size == 0:
        Image.fromarray(prepared.astype(np.uint8), mode="L").save(OUT)
        print("wrote", OUT, "(no subject mask; check the source photo)")
        return

    padding = 40
    side = int(max(xs.max() - xs.min(), ys.max() - ys.min()) + padding * 2)
    center_x = int(xs.min() + xs.max()) // 2
    center_y = int(ys.min() + ys.max()) // 2
    canvas = np.full((side, side), 255, np.uint8)
    x0, y0 = center_x - side // 2, center_y - side // 2
    source_x0, source_y0 = max(x0, 0), max(y0, 0)
    source_x1, source_y1 = min(x0 + side, prepared.shape[1]), min(y0 + side, prepared.shape[0])
    canvas[source_y0 - y0 : source_y1 - y0, source_x0 - x0 : source_x1 - x0] = prepared[
        source_y0:source_y1, source_x0:source_x1
    ].astype(np.uint8)

    Image.fromarray(canvas, mode="L").save(OUT)
    print("wrote", OUT, canvas.shape)


if __name__ == "__main__":
    main()
