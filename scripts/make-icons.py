#!/usr/bin/env python3
"""Generate the HkpieBlocks icon theme + matching Kando icon theme. ✿

Every icon is a square neubrutalist block with a heavy ink outline and a hard
offset shadow, in a pseudo-random wallpaper color, with the app's first letter
stamped on it. Deterministic: the same app always gets the same color.

Outputs:
  share/icons/HkpieBlocks/<size>x<size>/apps/<id>.png
  config/kando/icon-themes/hkpie-blocks/<id>.svg
"""
from __future__ import annotations

import html
import pathlib
import random
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Samples from hkpiewallpaper.png (plus two close pastel relatives).
BUTTER = (246, 240, 152)  # #F6F098
BLUSH = (240, 160, 144)   # #F0A090
CREAM = (234, 231, 170)   # #EAE7AA
PAPER = (247, 247, 247)   # #F7F7F7
TAN = (195, 175, 141)     # #C3AF8D
MOCHA = (167, 144, 113)   # #A79071
SOFT_PINK = (244, 196, 188)
SOFT_YELLOW = (250, 232, 160)
FILLS = [BUTTER, BLUSH, CREAM, PAPER, TAN, SOFT_PINK, SOFT_YELLOW]

INK = (71, 67, 51)        # #474333
DEEP = (46, 43, 33)       # #2E2B21

SIZES = (16, 22, 24, 32, 48, 64, 128)

# icon id -> (human label, letter override). The first letter is used by default.
ICONS: dict[str, tuple[str, str | None]] = {
    "hkpie": ("HK Pie", "H"),
    "firefox": ("Firefox", None),
    "browser": ("Browser", "B"),
    "kitty": ("Kitty", None),
    "terminal": ("Terminal", "T"),
    "xfce4-terminal": ("Terminal", "T"),
    "utilities-terminal": ("Terminal", "T"),
    "thunar": ("Thunar", None),
    "pcmanfm": ("PCManFM", None),
    "files": ("Files", "F"),
    "system-file-manager": ("Files", "F"),
    "pictures": ("Pictures", "P"),
    "downloads": ("Downloads", "D"),
    "music": ("Music", "M"),
    "home": ("Home", "H"),
    "pavucontrol": ("Volume", "V"),
    "audio-volume-high": ("Volume", "V"),
    "volume": ("Volume", "V"),
    "play": ("Play", "P"),
    "next": ("Next", "N"),
    "prev": ("Previous", "P"),
    "mute": ("Mute", "M"),
    "media-playback-start": ("Play", "P"),
    "windows": ("Windows", "W"),
    "maximize": ("Maximize", "M"),
    "tile-left": ("Left", "L"),
    "tile-right": ("Right", "R"),
    "close": ("Close", "C"),
    "rice": ("Rice", "R"),
    "reload": ("Reload", "R"),
    "wallpaper": ("Wallpaper", "W"),
    "scrot": ("Screenshot", "S"),
    "settings": ("Settings", "S"),
    "preferences-desktop": ("Settings", "S"),
    "kando": ("Kando", "K"),
    "dunst": ("Notifications", "N"),
    "sleep": ("Sleep", "S"),
    "lock": ("Lock", "L"),
    "suspend": ("Suspend", "S"),
    "exit": ("Exit", "E"),
    "i3": ("i3", "I"),
    "picom": ("Picom", "P"),
    "about": ("About", "A"),
    "website": ("Website", "W"),
    "source": ("Source", "S"),
    "apps": ("Apps", "A"),
    "dialog-information": ("Info", "I"),
    "dialog-warning": ("Warning", "W"),
    "dialog-error": ("Error", "E"),
}


def letter_for(name: str, override: str | None) -> str:
    return (override or name)[0].upper()


def fill_for(icon_id: str) -> tuple[int, int, int]:
    return random.Random("hkpie-" + icon_id).choice(FILLS)


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ):
        if pathlib.Path(path).is_file():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def text_color(fill: tuple[int, int, int]) -> tuple[int, int, int]:
    luminance = 0.299 * fill[0] + 0.587 * fill[1] + 0.114 * fill[2]
    return INK if luminance > 110 else PAPER


def save_png(icon_id: str, label: str, size: int, out: pathlib.Path) -> None:
    fill = fill_for(icon_id)
    fg = text_color(fill)
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    pad = max(1, round(size * 0.08))
    off = max(2, round(size * 0.09))
    width = max(2, round(size * 0.085))

    block = (pad, pad, size - pad, size - pad)
    shadow = (block[0] + off, block[1] + off, block[2] + off, block[3] + off)
    # Neubrutalism: square blocks, heavy ink outline, hard offset shadow.
    draw.rectangle(shadow, fill=DEEP)
    draw.rectangle(block, fill=fill, outline=INK, width=width)

    font = load_font(max(8, round(size * 0.60)))
    draw.text(
        (size / 2, size / 2 - size * 0.02),
        letter_for(label, ICONS[icon_id][1]),
        font=font,
        fill=fg,
        anchor="mm",
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out)


def save_svg(icon_id: str, label: str, out: pathlib.Path) -> None:
    r, g, b = fill_for(icon_id)
    fg = "#%02x%02x%02x" % text_color(fill_for(icon_id))
    letter = html.escape(letter_for(label, ICONS[icon_id][1]))
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
  <rect x="25" y="25" width="104" height="104" fill="#2E2B21"/>
  <rect x="14" y="14" width="104" height="104" fill="#{r:02x}{g:02x}{b:02x}" stroke="#474333" stroke-width="9"/>
  <text x="66" y="72" text-anchor="middle" dominant-baseline="central"
        font-family="DejaVu Sans, sans-serif" font-size="72" font-weight="900"
        fill="{fg}">{letter}</text>
</svg>
'''
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg, encoding="utf-8")


def main() -> None:
    icon_root = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "share/icons/HkpieBlocks"
    kando_root = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "config/kando/icon-themes/hkpie-blocks"

    # Write each block into every common freedesktop context. This is what makes
    # the theme behave like a real icon pack instead of only showing in Kando.
    contexts = {
        "apps": "Applications",
        "actions": "Actions",
        "places": "Places",
        "status": "Status",
        "categories": "Categories",
        "mimetypes": "MimeTypes",
    }

    for size in SIZES:
        for icon_id, (label, _override) in ICONS.items():
            for context in contexts:
                save_png(icon_id, label, size,
                         icon_root / f"{size}x{size}/{context}/{icon_id}.png")

    dirs = ",".join(f"{s}x{s}/{c}" for s in SIZES for c in contexts)
    index = ["[Icon Theme]", "Name=Hkpie Blocks",
             "Comment=Square neubrutalist blocks with app initials (hkpiewallpaper palette)",
             "Inherits=Adwaita,hicolor", f"Directories={dirs}", ""]
    for size in SIZES:
        for context, freedesktop_context in contexts.items():
            index += [f"[{size}x{size}/{context}]", f"Size={size}",
                      f"Context={freedesktop_context}", "Type=Fixed", ""]
    (icon_root / "index.theme").write_text("\n".join(index), encoding="utf-8")

    for icon_id, (label, _override) in ICONS.items():
        save_svg(icon_id, label, kando_root / f"{icon_id}.svg")

    print(f"wrote {len(ICONS)} icons × {len(SIZES)} sizes to {icon_root}")
    print(f"wrote {len(ICONS)} Kando SVG icons to {kando_root}")


if __name__ == "__main__":
    main()
