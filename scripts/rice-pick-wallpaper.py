#!/usr/bin/env python3
"""Open a GTK file chooser and print the chosen wallpaper path. ✿"""
from __future__ import annotations

import pathlib
import sys

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402


def main() -> None:
    dialog = Gtk.FileChooserDialog(
        title="Choose wallpaper",
        parent=None,
        action=Gtk.FileChooserAction.OPEN,
    )
    dialog.add_buttons(
        Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
        Gtk.STOCK_OPEN, Gtk.ResponseType.OK,
    )
    dialog.set_modal(True)
    pictures = pathlib.Path.home() / "Pictures"
    if pictures.is_dir():
        dialog.set_current_folder(str(pictures))

    images = Gtk.FileFilter()
    images.set_name("Images")
    for pattern in ("*.png", "*.jpg", "*.jpeg", "*.webp", "*.gif", "*.bmp"):
        images.add_pattern(pattern)
    dialog.add_filter(images)

    chosen = ""
    if dialog.run() == Gtk.ResponseType.OK:
        chosen = dialog.get_filename() or ""
    dialog.destroy()
    if chosen:
        print(chosen)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # keep pmenu alive if GTK is unavailable
        print(f"rice-pick-wallpaper: {exc}", file=sys.stderr)
        raise SystemExit(1)
