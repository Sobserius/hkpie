#!/usr/bin/env python3
"""Render GTK, pmenu and generated assets from ~/.config/hkpie/palette.conf. ✿"""
from __future__ import annotations

import os
import pathlib
import re
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from palette import CONF, DEFAULT, load, write_default  # noqa: E402

HOME = pathlib.Path.home()
GTK_CSS = [
    HOME / ".themes/HkpieBrutal/gtk-3.0/gtk.css",
    HOME / ".themes/HkpieBrutal/gtk-4.0/gtk.css",
    HOME / ".local/share/themes/HkpieBrutal/gtk-3.0/gtk.css",
    HOME / ".local/share/themes/HkpieBrutal/gtk-4.0/gtk.css",
    HOME / ".config/gtk-3.0/gtk.css",
]
PMENU_XRESOURCES = HOME / ".config/pmenu/Xresources"
PMENU_COLORS = {
    "centerColor": "paper",
    "background": "butter",
    "foreground": "deep",
    "activeBackground": "blush",
    "activeForeground": "deep",
    "borderColor": "deep",
    "topShadowColor": "deep",
    "bottomShadowColor": "deep",
}

GTK_DEFINE = re.compile(r"@define-color\s+([a-z]+)\s+#[0-9A-Fa-f]{6}\s*;")
PMENU_LINE = re.compile(r"^(PMenu\.([A-Za-z]+):)(\s*)(#[0-9A-Fa-f]{6})(.*)$", re.MULTILINE)


def update_gtk(path: pathlib.Path, colors: dict[str, str]) -> bool:
    if not path.is_file():
        return False
    text = path.read_text()

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        return f"@define-color {name} {colors.get(name, DEFAULT[name])};"

    updated = GTK_DEFINE.sub(replace, text)
    if updated == text:
        return False
    path.write_text(updated)
    return True


def update_pmenu(colors: dict[str, str]) -> bool:
    if not PMENU_XRESOURCES.is_file():
        return False
    text = PMENU_XRESOURCES.read_text()

    def replace(match: re.Match[str]) -> str:
        key = match.group(2)
        color = PMENU_COLORS.get(key)
        if color is None:
            return match.group(0)
        return f"{match.group(1)}{match.group(3)}{colors[color]}{match.group(5)}"

    updated = PMENU_LINE.sub(replace, text)
    if updated == text:
        return False
    PMENU_XRESOURCES.write_text(updated)
    return True


def refresh_live() -> None:
    if os.environ.get("DISPLAY") and shutil.which("xrdb"):
        subprocess.run(
            ["xrdb", "-merge", str(PMENU_XRESOURCES)],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    if shutil.which("gsettings"):
        subprocess.run(
            ["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", "HkpieBrutal"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def regenerate_assets() -> None:
    for name in ("make-lock.py", "make-preview.py"):
        script = HERE / name
        if script.is_file():
            subprocess.run(
                [sys.executable, str(script)],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )


def main() -> None:
    if not CONF.is_file():
        write_default(CONF)
    colors = load(CONF)

    changed = 0
    for css in GTK_CSS:
        changed += update_gtk(css, colors)
    changed += update_pmenu(colors)
    refresh_live()
    regenerate_assets()
    print(f"hkpie theme synced from {CONF} ({changed} file(s) changed)")


if __name__ == "__main__":
    main()
