#!/usr/bin/env python3
"""Render every themable rice config from ~/.config/hkpie/palette.conf. ✿"""
from __future__ import annotations

import os
import pathlib
import re
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from palette import CONF, DEFAULT, ensure, load  # noqa: E402

HOME = pathlib.Path.home()
GTK_CSS = [
    HOME / ".themes/HkpieBrutal/gtk-3.0/gtk.css",
    HOME / ".themes/HkpieBrutal/gtk-4.0/gtk.css",
    HOME / ".local/share/themes/HkpieBrutal/gtk-3.0/gtk.css",
    HOME / ".local/share/themes/HkpieBrutal/gtk-4.0/gtk.css",
    HOME / ".config/gtk-3.0/gtk.css",
]
PMENU_XRESOURCES = HOME / ".config/pmenu/Xresources"
I3_CONFIG = HOME / ".config/i3/config"
KITTY_CONF = HOME / ".config/kitty/kitty.conf"
DUNSTRC = HOME / ".config/dunst/dunstrc"
PICOM_CONF = HOME / ".config/picom/picom.conf"
I3STATUS_CONF = HOME / ".config/i3/i3status.conf"

PMENU_COLORS = {
    "centerColor": "surface",
    "background": "highlight",
    "foreground": "shadow",
    "activeBackground": "accent",
    "activeForeground": "shadow",
    "borderColor": "shadow",
    "topShadowColor": "shadow",
    "bottomShadowColor": "shadow",
}
KITTY_COLORS = {
    "background": "background",
    "foreground": "foreground",
    "cursor": "foreground",
    "cursor_text_color": "surface",
    "selection_background": "accent",
    "selection_foreground": "shadow",
    "url_color": "muted-dark",
    "color0": "outline",
    "color1": "accent",
    "color2": "muted-dark",
    "color3": "muted",
    "color4": "foreground",
    "color5": "muted",
    "color6": "highlight",
    "color7": "surface",
    "color8": "muted-dark",
    "color9": "accent",
    "color10": "highlight",
    "color11": "muted",
    "color12": "background",
    "color13": "surface",
    "color14": "highlight",
    "color15": "shadow",
}
DUNST_COLORS = {
    ("global", "frame_color"): "outline",
    ("urgency_low", "background"): "highlight",
    ("urgency_low", "foreground"): "outline",
    ("urgency_low", "frame_color"): "outline",
    ("urgency_normal", "background"): "surface",
    ("urgency_normal", "foreground"): "outline",
    ("urgency_normal", "frame_color"): "outline",
    ("urgency_critical", "background"): "accent",
    ("urgency_critical", "foreground"): "shadow",
    ("urgency_critical", "frame_color"): "shadow",
}
PICOM_COLORS = {"shadow-color": "shadow"}
I3STATUS_COLORS = {
    "color_good": "outline",
    "color_bad": "shadow",
    "color_degraded": "accent",
    "color_separator": "muted",
}

GTK_DEFINE = re.compile(r"@define-color\s+([a-z-]+)\s+#[0-9A-Fa-f]{6}\s*;")
PMENU_LINE = re.compile(r"^(PMenu\.([A-Za-z]+):)(\s*)(#[0-9A-Fa-f]{6})(.*)$", re.MULTILINE)
I3_VAR = re.compile(r'^(set \$)([a-z-]+)([ \t]+)"#[0-9A-Fa-f]{6}"[ \t]*$', re.MULTILINE)
KITTY_LINE = re.compile(r"^([a-z_][a-z0-9_]*)([ \t]+)#?[0-9A-Fa-f]{6}[ \t]*$", re.MULTILINE)
DUNST_SECTION = re.compile(r"^\[([^\]]+)\]\s*$")
DUNST_LINE = re.compile(r'^([a-z_]+)(\s*=\s*)"#[0-9A-Fa-f]{6}"\s*$')
PICOM_LINE = re.compile(
    r'^(?P<key>[a-z-]+)(?P<mid>[ \t]*=[ \t]*)"#[0-9A-Fa-f]{6}"'
    r'(?P<end>[ \t]*;?[ \t]*)$', re.MULTILINE
)
I3STATUS_LINE = re.compile(
    r'^(?P<prefix>[ \t]*)(?P<key>[a-z_]+)(?P<mid>[ \t]*=[ \t]*)"#[0-9A-Fa-f]{6}"'
    r'(?P<end>[ \t]*)$', re.MULTILINE
)


def rewrite(path: pathlib.Path, transform) -> bool:
    if not path.is_file():
        return False
    text = path.read_text()
    updated = transform(text)
    if updated == text:
        return False
    path.write_text(updated)
    return True


def update_gtk(colors: dict[str, str]) -> int:
    def transform(text: str) -> str:
        def replace(match: re.Match[str]) -> str:
            role = match.group(1)
            return f"@define-color {role} {colors.get(role, DEFAULT[role])};"
        return GTK_DEFINE.sub(replace, text)

    return sum(rewrite(path, transform) for path in GTK_CSS)


def update_pmenu(colors: dict[str, str]) -> bool:
    def transform(text: str) -> str:
        def replace(match: re.Match[str]) -> str:
            role = PMENU_COLORS.get(match.group(2))
            if role is None:
                return match.group(0)
            return f"{match.group(1)}{match.group(3)}{colors[role]}{match.group(5)}"
        return PMENU_LINE.sub(replace, text)

    return rewrite(PMENU_XRESOURCES, transform)


def update_i3(colors: dict[str, str]) -> bool:
    def transform(text: str) -> str:
        def replace(match: re.Match[str]) -> str:
            role = match.group(2)
            if role not in colors:
                return match.group(0)
            return f'{match.group(1)}{role}{match.group(3)}"{colors[role]}"'
        return I3_VAR.sub(replace, text)

    return rewrite(I3_CONFIG, transform)


def update_kitty(colors: dict[str, str]) -> bool:
    def transform(text: str) -> str:
        def replace(match: re.Match[str]) -> str:
            role = KITTY_COLORS.get(match.group(1))
            if role is None:
                return match.group(0)
            return f"{match.group(1)}{match.group(2)}{colors[role]}"
        return KITTY_LINE.sub(replace, text)

    return rewrite(KITTY_CONF, transform)


def update_dunst(colors: dict[str, str]) -> bool:
    def transform(text: str) -> str:
        section = ""
        lines = []
        for line in text.splitlines(keepends=True):
            body = line.rstrip("\r\n")
            ending = line[len(body):]
            section_match = DUNST_SECTION.match(body)
            if section_match:
                section = section_match.group(1).lower()
            value_match = DUNST_LINE.match(body)
            if value_match:
                role = DUNST_COLORS.get((section, value_match.group(1)))
                if role in colors:
                    body = f'{value_match.group(1)}{value_match.group(2)}"{colors[role]}"'
            lines.append(body + ending)
        return "".join(lines)

    return rewrite(DUNSTRC, transform)


def update_simple(path: pathlib.Path, mapping: dict[str, str], pattern: re.Pattern[str], colors: dict[str, str]) -> bool:
    def transform(text: str) -> str:
        def replace(match: re.Match[str]) -> str:
            prefix = match.groupdict().get("prefix") or ""
            key = match.group("key")
            middle = match.group("mid")
            role = mapping.get(key)
            if role is None:
                return match.group(0)
            return f'{prefix}{key}{middle}"{colors[role]}"{match.groupdict().get("end") or ""}'
        return pattern.sub(replace, text)

    return rewrite(path, transform)


def run(args: list[str]) -> None:
    subprocess.run(args, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def running(name: str) -> bool:
    return shutil.which("pgrep") is not None and subprocess.run(
        ["pgrep", "-x", name], check=False,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0


def spawn(name: str, args: list[str]) -> None:
    if shutil.which(name):
        subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)


def refresh_live(i3_changed: bool, dunst_changed: bool, picom_changed: bool) -> None:
    if os.environ.get("DISPLAY") and shutil.which("xrdb"):
        run(["xrdb", "-merge", str(PMENU_XRESOURCES)])
    if shutil.which("gsettings"):
        run(["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", "HkpieBrutal"])

    # Kitty and dunst reload their config automatically; i3 needs a reload to
    # apply new client.* colors. exec_always does not re-run on reload here.
    if i3_changed and shutil.which("i3-msg"):
        run(["i3-msg", "reload"])
    if dunst_changed and running("dunst"):
        run(["pkill", "-x", "dunst"])
        spawn("dunst", ["dunst"])
    if picom_changed and running("picom"):
        run(["pkill", "-x", "picom"])
        run(["sleep", "0.4"])
        spawn("picom", ["picom", "--config", str(PICOM_CONF)])


def regenerate_assets() -> None:
    for name in ("make-lock.py", "make-preview.py"):
        script = HERE / name
        if script.is_file():
            run([sys.executable, str(script)])


def main() -> None:
    ensure(CONF)
    colors = load(CONF)

    changed = update_gtk(colors)
    pmenu_changed = update_pmenu(colors)
    i3_changed = update_i3(colors)
    kitty_changed = update_kitty(colors)
    dunst_changed = update_dunst(colors)
    picom_changed = update_simple(PICOM_CONF, PICOM_COLORS, PICOM_LINE, colors)
    i3status_changed = update_simple(I3STATUS_CONF, I3STATUS_COLORS, I3STATUS_LINE, colors)

    changed += sum((pmenu_changed, i3_changed, kitty_changed, dunst_changed,
                    picom_changed, i3status_changed))
    refresh_live(i3_changed, dunst_changed, picom_changed)
    regenerate_assets()
    print(f"hkpie theme synced from {CONF} ({changed} file(s) changed)")


if __name__ == "__main__":
    main()
