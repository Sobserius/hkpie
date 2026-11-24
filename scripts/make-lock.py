#!/usr/bin/env python3
"""Build the hkpie lock screen on a flat cream filler, with a live-at-lock clock. ✿"""
from __future__ import annotations

import os
import pathlib
import re
import subprocess
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

from palette import load, rgba

HOME = pathlib.Path.home()
OUT = HOME / ".local/share/backgrounds/kawaii-rice/hkpie-lock.png"

COLORS = load()
INK = rgba("ink", COLORS)
DEEP = rgba("deep", COLORS)
PAPER = rgba("paper", COLORS)
BUTTER = rgba("butter", COLORS)
BLUSH = rgba("blush", COLORS)
CREAM = rgba("cream", COLORS)

DAYS = ("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")
MONTHS = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN",
          "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")


def resolve_font(pattern: str, fallback: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    path = fallback
    try:
        found = subprocess.check_output(
            ["fc-match", "-f", "%{file}", pattern],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=2,
        ).strip()
        if found and pathlib.Path(found).is_file():
            path = found
    except (OSError, subprocess.SubprocessError):
        pass
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def sans(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    return resolve_font(
        "Fira Sans:style=Bold",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
        size,
    )


def mono(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    return resolve_font(
        "JetBrains Mono:style=Bold",
        "/usr/share/fonts/dejavu/DejaVuSansMono-Bold.ttf",
        size,
    )


def screen_size() -> tuple[int, int]:
    env_w = os.environ.get("RICE_LOCK_WIDTH", "")
    env_h = os.environ.get("RICE_LOCK_HEIGHT", "")
    if env_w.isdigit() and env_h.isdigit():
        return int(env_w), int(env_h)
    try:
        out = subprocess.check_output(
            ["xrandr", "--current"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=2,
        )
        match = re.search(r"\sconnected\s+(?:primary\s+)?(\d+)x(\d+)", out)
        if match:
            return int(match.group(1)), int(match.group(2))
    except (OSError, subprocess.SubprocessError):
        pass
    return 1920, 1080


def chip(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    fill: tuple[int, int, int, int],
    label: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    width: int = 6,
) -> None:
    draw.rectangle((box[0] + 14, box[1] + 14, box[2] + 14, box[3] + 14), fill=DEEP)
    draw.rectangle(box, fill=fill, outline=INK, width=width)
    draw.text(
        ((box[0] + box[2]) // 2, (box[1] + box[3]) // 2),
        label,
        font=font,
        fill=DEEP,
        anchor="mm",
    )


def main() -> None:
    width, height = screen_size()
    # Lock screens use a flat filler instead of the desktop wallpaper; the
    # cream is sampled from the wallpaper palette and keeps the ring/slab crisp.
    image = Image.new("RGBA", (width, height), CREAM)
    draw = ImageDraw.Draw(image)

    cx, cy = width // 2, height // 2
    # Lift the card so the pmenu-style ring sits below it instead of on top of
    # the clock; rice-lock keeps its centre at h/2 + 330.
    card_cy = cy - 70
    card_w = min(760, width - 80)
    card_h = min(460, height - 80)
    card = (cx - card_w // 2, card_cy - card_h // 2,
            cx + card_w // 2, card_cy + card_h // 2)

    # Neubrutalist lock card: square, 18px hard shadow, heavy ink outline.
    draw.rectangle(
        (card[0] + 18, card[1] + 18, card[2] + 18, card[3] + 18), fill=DEEP
    )
    draw.rectangle(card, fill=PAPER, outline=INK, width=10)

    now = datetime.now()
    time_text = now.strftime("%H:%M")
    date_text = f"{DAYS[now.weekday()]} {now.day:02d} {MONTHS[now.month - 1]}"

    draw.text((cx, card[1] + 196), time_text, font=mono(132), fill=DEEP, anchor="mm")
    draw.rectangle((cx - 180, card[1] + 276, cx + 180, card[1] + 288), fill=BLUSH)
    draw.text((cx, card[1] + 326), date_text, font=sans(38), fill=INK, anchor="mm")

    chip(draw, (cx - 270, card[3] - 112, cx + 270, card[3] - 42),
         CREAM, "TYPE PASSWORD / ENTER", sans(28), width=5)
    draw.text((card[2] - 26, card[1] + 26), "ALT+SHIFT : EN/RU",
              font=sans(20), fill=PAPER, anchor="ra")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
