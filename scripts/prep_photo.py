
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "source-photo.jpg"
OUTPUT = ROOT / "source-prepped.png"


def main():
    if not INPUT.exists():
        print(f"Photo not found: {INPUT}")
        print("Place source-photo.jpg in the project root.")
        return

    print("Preparing your portrait...")

    image = Image.open(INPUT).convert("RGBA")
    image = remove(image)

    rgba = np.array(image)
    alpha = rgba[:, :, 3].astype(np.float32) / 255.0
    rgb = rgba[:, :, :3].astype(np.float32)

    # Place the subject on a pure white background.
    white = np.full_like(rgb, 255)
    composite = (rgb * alpha[:, :, None] +
                 white * (1 - alpha[:, :, None]))

    composite = np.clip(composite, 0, 255).astype(np.uint8)
    gray = cv2.cvtColor(composite, cv2.COLOR_RGB2GRAY)

    # Improve local contrast for clearer ASCII shading.
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )
    enhanced = clahe.apply(gray)

    Image.fromarray(enhanced).save(OUTPUT)
    print(f"Done! Prepared portrait saved to: {OUTPUT}")


if __name__ == "__main__":
    main()