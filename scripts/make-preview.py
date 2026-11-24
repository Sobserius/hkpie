#!/usr/bin/env python3
"""Generate the square hkpie preview image. ✿

Purely programmatic: no external artwork, just the wallpaper palette.
Usage: python3 make-preview.py [output/path/preview.jpg]
"""
from __future__ import annotations

import math
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont

from palette import load, rgb

COLORS = load()
CREAM = rgb("cream", COLORS)
BUTTER = rgb("butter", COLORS)
BLUSH = rgb("blush", COLORS)
PAPER = rgb("paper", COLORS)
TAN = rgb("tan", COLORS)
INK = rgb("ink", COLORS)

SIZE = 700
CENTER = SIZE // 2


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ]
    for path in candidates:
        if pathlib.Path(path).is_file():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def square_chip(draw: ImageDraw.ImageDraw, cx: int, cy: int, radius: int,
                fill: tuple[int, int, int], label: str, font) -> None:
    box = (cx - radius, cy - radius, cx + radius, cy + radius)
    shadow = (box[0] + 9, box[1] + 9, box[2] + 9, box[3] + 9)
    draw.rectangle(shadow, fill=INK)
    draw.rectangle(box, fill=fill, outline=INK, width=5)
    if label:
        draw.text((cx, cy), label, font=font, fill=INK, anchor="mm")


def main() -> None:
    default_out = (
        pathlib.Path.home() / ".local/share/kawaii-rice/preview.jpg"
    )
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else default_out

    image = Image.new("RGB", (SIZE, SIZE), CREAM)
    draw = ImageDraw.Draw(image)

    # Neubrutalist dot grid
    for x in range(24, SIZE, 30):
        for y in range(24, SIZE, 30):
            draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=TAN)

    label_font = load_font(22)
    center_font = load_font(30)
    footer_font = load_font(18)

    # Eight slices
    for index in range(8):
        angle = math.radians(index * 45 - 90)
        cx = round(CENTER + 220 * math.cos(angle))
        cy = round(CENTER + 220 * math.sin(angle))
        square_chip(draw, cx, cy, 40, BUTTER if index % 2 == 0 else PAPER,
                    str(index + 1), label_font)

    # Center item
    square_chip(draw, CENTER, CENTER, 86, PAPER, "HK", center_font)

    # Caption chip
    draw.rectangle((250, 630, 450, 668), fill=PAPER, outline=INK, width=5)
    draw.text((CENTER, 649), "hkpie-brutal", font=footer_font, fill=INK,
              anchor="mm")

    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out, quality=92)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
