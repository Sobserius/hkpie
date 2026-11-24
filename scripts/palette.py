#!/usr/bin/env python3
"""Shared hkpie palette reader.

The editable palette lives at ~/.config/hkpie/palette.conf and contains only
bare key=value lines, e.g. `cream=#EAE7AA`. Every theme generator reads it.
"""
from __future__ import annotations

import argparse
import pathlib
import re

DEFAULT = {
    "cream": "#EAE7AA",
    "butter": "#F6F098",
    "paper": "#F7F7F7",
    "blush": "#F0A090",
    "tan": "#C3AF8D",
    "mocha": "#A79071",
    "ink": "#474333",
    "deep": "#2E2B21",
}

CONF = pathlib.Path.home() / ".config/hkpie/palette.conf"
HEX = re.compile(r"#[0-9A-Fa-f]{6}\Z")


def load(path: pathlib.Path = CONF) -> dict[str, str]:
    colors = dict(DEFAULT)
    try:
        text = path.read_text()
    except OSError:
        return colors
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = (part.strip() for part in line.split("=", 1))
        key = key.lower()
        if key in colors and HEX.match(value):
            colors[key] = value.upper()
    return colors


def rgb(key: str, colors: dict[str, str] | None = None) -> tuple[int, int, int]:
    value = (colors or load())[key].lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def rgba(key: str, colors: dict[str, str] | None = None) -> tuple[int, int, int, int]:
    return rgb(key, colors) + (255,)


def write_default(path: pathlib.Path = CONF) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"{key}={value}" for key, value in DEFAULT.items()) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Read the editable hkpie palette")
    parser.add_argument("--init", action="store_true", help="write the default palette if missing")
    parser.add_argument("--get", metavar="COLOR", help="print one hex value")
    parser.add_argument("--path", type=pathlib.Path, default=CONF, help="palette file path")
    args = parser.parse_args()

    if args.init and not args.path.is_file():
        write_default(args.path)
    if args.get:
        print(load(args.path)[args.get])
    elif not args.init:
        parser.print_help()


if __name__ == "__main__":
    main()
