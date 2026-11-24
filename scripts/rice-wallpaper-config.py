#!/usr/bin/env python3
"""Store the chosen wallpaper in the installed hkpie config. ✿"""
from __future__ import annotations

import argparse
import pathlib


def write(config: pathlib.Path, wallpaper: str) -> None:
    try:
        lines = config.read_text().splitlines()
    except OSError:
        lines = []

    # Replace the installer's default line (and any older explicit choice).
    lines = [line for line in lines if not line.startswith("export RICE_WALLPAPER=")]
    escaped = wallpaper.replace("'", "'\\''")
    lines.append(f"export RICE_WALLPAPER='{escaped}'")

    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Update the hkpie wallpaper config")
    parser.add_argument("wallpaper", help="absolute path to the chosen image")
    parser.add_argument(
        "--config",
        type=pathlib.Path,
        default=pathlib.Path.home() / ".config/kawaii-rice/palette.env",
        help="palette.env to update",
    )
    args = parser.parse_args()
    write(args.config, args.wallpaper)


if __name__ == "__main__":
    main()
