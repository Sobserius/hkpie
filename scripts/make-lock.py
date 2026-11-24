#!/usr/bin/env python3
"""Build the pastel-brutalist lock screen image from hkpiewallpaper.png. ✿"""
from __future__ import annotations

import pathlib
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HOME = pathlib.Path.home()
SOURCE = HOME / ".local/share/backgrounds/kawaii-rice/hkpiewallpaper.png"
FALLBACK = HOME / "Pictures/hkpiewallpaper.png"
OUT = HOME / ".local/share/backgrounds/kawaii-rice/hkpie-lock.png"

INK = (71, 67, 51, 255)
DEEP = (46, 43, 33, 255)
PAPER = (247, 247, 247, 255)
BUTTER = (246, 240, 152, 255)
BLUSH = (240, 160, 144, 255)


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ):
        if pathlib.Path(path).is_file():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def main() -> None:
    src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else (
        SOURCE if SOURCE.is_file() else FALLBACK
    )
    if not src.is_file():
        raise SystemExit(f"lock image: missing wallpaper {src}")

    image = Image.open(src).convert("RGBA")
    if image.size != (1920, 1080):
        image = image.resize((1920, 1080), Image.Resampling.LANCZOS)

    image = image.filter(ImageFilter.GaussianBlur(14))
    shade = Image.new("RGBA", image.size, (46, 43, 33, 88))
    image = Image.alpha_composite(image, shade)
    draw = ImageDraw.Draw(image)

    w, h = image.size
    card = (w // 2 - 260, h // 2 - 120, w // 2 + 260, h // 2 + 120)
    # Neubrutalist lock card: square, hard shadow, heavy outline.
    draw.rectangle((card[0] + 14, card[1] + 14, card[2] + 14, card[3] + 14), fill=DEEP)
    draw.rectangle(card, fill=PAPER, outline=INK, width=8)

    draw.text((w // 2, h // 2 - 32), "LOCKED", font=font(54), fill=DEEP, anchor="mm")
    draw.rectangle((w // 2 - 190, h // 2 + 18, w // 2 + 190, h // 2 + 68),
                   fill=BUTTER, outline=INK, width=5)
    draw.text((w // 2, h // 2 + 43), "PRESS ANY KEY",
              font=font(24), fill=INK, anchor="mm")
    draw.rectangle((w // 2 - 30, h // 2 + 84, w // 2 + 30, h // 2 + 114),
                   fill=BLUSH, outline=INK, width=5)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(OUT, quality=92)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
