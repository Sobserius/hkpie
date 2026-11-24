#!/usr/bin/env python3
"""Shared hkpie palette reader.

The editable palette lives at ~/.config/hkpie/palette.conf and contains only
role=value lines, e.g. `accent=#F0A090`. Old color-name keys are migrated on
read so existing installs keep their custom values.
"""
from __future__ import annotations

import argparse
import pathlib
import re

DEFAULT = {
    "background": "#EAE7AA",
    "surface": "#F7F7F7",
    "highlight": "#F6F098",
    "accent": "#F0A090",
    "foreground": "#474333",
    "outline": "#474333",
    "shadow": "#2E2B21",
    "muted": "#C3AF8D",
    "muted-dark": "#A79071",
}

# Existing installs used toy color names; map them to roles without losing values.
LEGACY = {
    "cream": "background",
    "paper": "surface",
    "butter": "highlight",
    "blush": "accent",
    "ink": "outline",
    "deep": "shadow",
    "tan": "muted",
    "mocha": "muted-dark",
}

CONF = pathlib.Path.home() / ".config/hkpie/palette.conf"
HEX = re.compile(r"#[0-9A-Fa-f]{6}\Z")


def parse(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = (part.strip() for part in line.split("=", 1))
        key = key.lower()
        role = LEGACY.get(key, key)
        if role in DEFAULT and HEX.match(value):
            values[role] = value.upper()
    return values


def load(path: pathlib.Path = CONF) -> dict[str, str]:
    colors = dict(DEFAULT)
    try:
        colors.update(parse(path.read_text()))
    except OSError:
        pass
    return colors


def rgb(role: str, colors: dict[str, str] | None = None) -> tuple[int, int, int]:
    value = (colors or load())[LEGACY.get(role, role)].lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def rgba(role: str, colors: dict[str, str] | None = None) -> tuple[int, int, int, int]:
    return rgb(role, colors) + (255,)


def default_text() -> str:
    return "\n".join(f"{role}={value}" for role, value in DEFAULT.items()) + "\n"


def ensure(path: pathlib.Path = CONF) -> bool:
    """Create the palette or rewrite legacy keys as roles. Returns True if changed."""
    if not path.is_file():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(default_text())
        return True
    try:
        original = path.read_text()
    except OSError:
        return False
    values = {role: parse(original).get(role, DEFAULT[role]) for role in DEFAULT}
    updated = "\n".join(f"{role}={values[role]}" for role in DEFAULT) + "\n"
    if updated == original:
        return False
    path.write_text(updated)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Read the editable hkpie palette")
    parser.add_argument("--init", action="store_true", help="create or migrate the palette")
    parser.add_argument("--get", metavar="ROLE", help="print one hex value")
    parser.add_argument("--path", type=pathlib.Path, default=CONF, help="palette file path")
    args = parser.parse_args()

    if args.init:
        ensure(args.path)
    if args.get:
        role = LEGACY.get(args.get.lower(), args.get.lower())
        print(load(args.path)[role])
    elif not args.init:
        parser.print_help()


if __name__ == "__main__":
    main()
