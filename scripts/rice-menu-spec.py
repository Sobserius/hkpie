#!/usr/bin/env python3
"""Build the pmenu spec for the hkpie rice.

The Apps slice is generated on every open from every visible .desktop file,
including Flatpak exports. Icons are resolved from installed icon themes
(Retrosmart first) and rendered to 48x48 PNGs for pmenu.
"""

from __future__ import annotations

import configparser
import glob
import hashlib
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
ICON_DIR = HOME / ".local/share/icons/retrosmart-pmenu/48x48/apps"
RETROSMART = HOME / ".local/share/icons/retrosmart-icon-theme/scalable"

# Category name -> (friendly label, Retrosmart SVG basename).
CATEGORY_MAP = (
    ("AudioVideo", "Multimedia", "applications-multimedia"),
    ("Audio", "Multimedia", "applications-multimedia"),
    ("Video", "Multimedia", "applications-multimedia"),
    ("Development", "Development", "text-x-python"),
    ("Education", "Education", "applications-education"),
    ("Game", "Games", "applications-games"),
    ("Graphics", "Graphics", "applications-graphics"),
    ("Network", "Network", "applications-internet"),
    ("Office", "Office", "applications-office"),
    ("Settings", "Settings", "preferences-system"),
    ("System", "System", "applications-system"),
    ("Utility", "Utilities", "applications-utilities"),
)
FALLBACK_ICON = "applications-all"
FIELD_CODE = re.compile(r"(?<!%)%[fFuUdDnNickvm]")


def desktop_dirs() -> list[str]:
    dirs = [
        str(HOME / ".local/share/applications"),
        str(HOME / ".local/share/flatpak/exports/share/applications"),
        "/var/lib/flatpak/exports/share/applications",
        "/usr/local/share/applications",
        "/usr/share/applications",
    ]
    for root in os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share").split(":"):
        if root:
            dirs.append(os.path.join(root, "applications"))
    seen: set[str] = set()
    return [d for d in dirs if not (d in seen or seen.add(d))]


def icon_roots() -> list[Path]:
    roots = [
        HOME / ".local/share/icons/retrosmart-icon-theme",
        HOME / ".local/share/icons",
        HOME / ".icons",
        Path("/var/lib/flatpak/exports/share/icons"),
        HOME / ".local/share/flatpak/exports/share/icons",
        Path("/usr/local/share/icons"),
        Path("/usr/share/icons"),
        Path("/usr/local/share/pixmaps"),
        Path("/usr/share/pixmaps"),
        Path("/usr/share/app-info/icons"),
    ]
    seen: set[Path] = set()
    unique: list[Path] = []
    for root in roots:
        if root.exists() and root not in seen:
            seen.add(root)
            unique.append(root)
    return unique


def build_icon_index() -> dict[str, list[Path]]:
    index: dict[str, list[Path]] = {}
    for root in icon_roots():
        try:
            paths = root.rglob("*")
        except OSError:
            continue
        for path in paths:
            if path.suffix.lower() not in (".svg", ".png"):
                continue
            key = path.stem.lower()
            index.setdefault(key, []).append(path)
    return index


def slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", value)[:64]


def render_icon(name: str, source: Path | None, index: dict[str, list[Path]]) -> str:
    """Render `name` to a 48px PNG in ICON_DIR and return its basename."""
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    candidates: list[Path] = []
    if source is not None and source.is_file():
        candidates.append(source)
    candidates.extend(index.get(name.lower(), []))
    if not candidates:
        candidates.extend(index.get(FALLBACK_ICON, []))

    for candidate in candidates:
        digest = hashlib.sha1(str(candidate.resolve()).encode("utf-8")).hexdigest()[:8]
        out = ICON_DIR / f"app-{slug(name)}-{digest}.png"
        if out.is_file():
            return out.name
        try:
            if candidate.suffix.lower() == ".svg" and shutil.which("rsvg-convert"):
                subprocess.run(
                    ["rsvg-convert", "-w", "48", "-h", "48", "-o", str(out), str(candidate)],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                from PIL import Image

                image = Image.open(candidate).convert("RGBA")
                image.thumbnail((48, 48), Image.Resampling.LANCZOS)
                canvas = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
                canvas.alpha_composite(image, ((48 - image.width) // 2, (48 - image.height) // 2))
                canvas.save(out)
            return out.name
        except Exception:
            out.unlink(missing_ok=True)
            continue

    fallback = index.get(FALLBACK_ICON, [])
    if fallback and fallback[0] not in candidates:
        return render_icon(FALLBACK_ICON, fallback[0], index)
    return "apps.png"


def clean(text: str) -> str:
    return " ".join(str(text).replace("\t", " ").replace("\n", " ").split())


def desktop_command(exec_line: str, terminal: bool) -> str:
    cmd = FIELD_CODE.sub("", exec_line).replace("%%", "%")
    # Flatpak file-forwarding tokens are meaningless without file arguments.
    cmd = re.sub(r"@@[^@]*@@", "", cmd).replace("@@", "")
    cmd = re.sub(r"\s+--\s*$", "", cmd).strip()
    if terminal:
        return "kitty -- sh -c " + shlex.quote(cmd)
    return clean(cmd)


def parse_desktop(path: Path) -> dict[str, str] | None:
    parser = configparser.RawConfigParser(strict=False, interpolation=None)
    try:
        parser.read(path, encoding="utf-8")
    except (OSError, configparser.Error, UnicodeDecodeError):
        return None
    if not parser.has_section("Desktop Entry"):
        return None
    section = parser["Desktop Entry"]

    if section.get("NoDisplay", "false").lower() == "true":
        return None
    if section.get("Hidden", "false").lower() == "true":
        return None
    if section.get("Type", "Application") != "Application":
        return None

    exec_line = section.get("Exec", "").strip()
    if not exec_line:
        return None

    try_exec = section.get("TryExec", "").strip()
    if try_exec:
        found = shutil.which(try_exec) or (
            os.path.isabs(try_exec) and os.path.exists(try_exec)
        )
        if not found:
            return None

    name = clean(section.get("Name", path.stem))
    if not name:
        return None

    return {
        "name": name,
        "exec": exec_line,
        "icon": section.get("Icon", "").strip(),
        "categories": section.get("Categories", ""),
        "terminal": section.get("Terminal", "false").lower() == "true",
    }


def category_for(entry: dict[str, str]) -> tuple[str, str]:
    categories = {c.strip().lower() for c in entry["categories"].split(";") if c.strip()}
    for key, label, _icon in CATEGORY_MAP:
        if key.lower() in categories:
            return label, _icon
    return "Other", FALLBACK_ICON


def load_apps() -> list[dict[str, str]]:
    apps: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for directory in desktop_dirs():
        for path in sorted(glob.glob(os.path.join(directory, "*.desktop"))):
            entry = parse_desktop(Path(path))
            if entry is None:
                continue
            key = (entry["name"].casefold(), entry["exec"])
            if key in seen:
                continue
            seen.add(key)
            apps.append(entry)
    return sorted(apps, key=lambda item: item["name"].casefold())


def emit_apps(groups: dict[str, list[dict[str, str]]], icons: dict[str, str], index: dict[str, list[Path]]) -> None:
    print("\tIMG:dunst.png\tNotifications\tdunstctl history-pop")
    print("\tIMG:music.png\tMusic\tkitty -e ncmpcpp")

    category_icon = {label: icon for _key, label, icon in CATEGORY_MAP}
    category_icon["Other"] = FALLBACK_ICON

    for label in sorted(groups):
        cat_icon = render_icon(category_icon.get(label, FALLBACK_ICON), None, index)
        print(f"\tIMG:{cat_icon}\t{label}")
        for app in groups[label]:
            icon_key = re.sub(r"\.(svg|png)$", "", app["icon"].split("/")[-1], flags=re.I)
            app_icon = render_icon(icon_key or FALLBACK_ICON, None, index)
            command = desktop_command(app["exec"], app["terminal"])
            print(f"\t\tIMG:{app_icon}\t{app['name']}\t{command}")


def main() -> int:
    index = build_icon_index()
    groups: dict[str, list[dict[str, str]]] = {}
    for app in load_apps():
        label, _icon = category_for(app)
        groups.setdefault(label, []).append(app)

    print("IMG:apps.png\tApps")
    emit_apps(groups, {}, index)
    print("IMG:terminal.png\tTerminal\tkitty")
    print("IMG:files.png\tFiles\tnemo || pcmanfm || thunar")
    # Dedicated pie slice: camera icon on the parent, plain-text child entries.
    print("IMG:scrot.png\tScreenshot")
    print("\tFullscreen\tsh -c '$HOME/.local/bin/rice-shot full'")
    print("\tActive window\tsh -c '$HOME/.local/bin/rice-shot window'")
    print("\tRegion\tsh -c '$HOME/.local/bin/rice-shot region'")
    print("IMG:rice.png\tRice")
    print("\tIMG:wallpaper.png\tWallpaper\tsh -c '$HOME/.local/bin/rice-wallpaper pick'")
    print("\tIMG:reload.png\tReload rice\tsh -c '$HOME/.local/bin/rice-reload'")
    print("\tIMG:rice.png\tEdit theme\tsh -c '$HOME/.local/bin/rice-theme'")
    print("\tIMG:picom.png\tReload compositor\tsh -c 'pkill -x picom; picom --config $HOME/.config/picom/picom.conf &'")
    print("\tIMG:lock.png\tLock\tsh -c '$HOME/.local/bin/rice-lock'")
    print("\tIMG:sleep.png\tSuspend\tsh -c '$HOME/.local/bin/rice-lock && systemctl suspend'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
