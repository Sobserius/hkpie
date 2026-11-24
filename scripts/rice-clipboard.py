#!/usr/bin/env python3
"""Hold a PNG on the X clipboard until another app takes ownership.

Run in the background; it exits by itself when the clipboard is replaced or
after ten minutes, so repeated screenshots do not leave stale processes.
"""

from __future__ import annotations

import sys

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
gi.require_version("GLib", "2.0")
# Import Gtk before Gdk: Gtk 3 pulls in Gdk 3, otherwise gi defaults to Gdk 4.
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib  # noqa: E402

HOLD_MS = 10 * 60 * 1000


def main() -> int:
    if len(sys.argv) != 2:
        return 2

    Gtk.init([])
    pixbuf = GdkPixbuf.Pixbuf.new_from_file(sys.argv[1])
    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    state: dict[str, object] = {"owner": None}

    def owner_changed(_clipboard: Gtk.Clipboard, event: object) -> None:
        owner = getattr(event, "owner", None)
        if state["owner"] is None:
            state["owner"] = owner
        elif owner is None or owner != state["owner"]:
            Gtk.main_quit()

    clipboard.connect("owner-change", owner_changed)
    clipboard.set_image(pixbuf)
    clipboard.store()
    GLib.timeout_add(HOLD_MS, Gtk.main_quit)
    Gtk.main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
