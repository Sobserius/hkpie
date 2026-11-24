#!/bin/sh
# Derive pmenu PNG icons from the installed Retrosmart icon theme.
# pmenu loads images with imlib2, so SVG symlinks alone are not enough.
set -eu

SRC="${1:-${HOME}/.local/share/icons/retrosmart-icon-theme/scalable}"
DST="${2:-${HOME}/.local/share/icons/retrosmart-pmenu/48x48/apps}"

if ! command -v rsvg-convert >/dev/null 2>&1; then
    echo "rsvg-convert is required to build pmenu icons" >&2
    exit 1
fi

mkdir -p "$DST"

# pmenu filename : Retrosmart SVG basename
while IFS=: read -r out src; do
    if [ ! -f "$SRC/$src.svg" ]; then
        echo "missing Retrosmart icon: $SRC/$src.svg" >&2
        exit 1
    fi
    rsvg-convert -w 48 -h 48 -o "$DST/$out.png" "$SRC/$src.svg"
done <<'EOF'
apps:applications-all
firefox:firefox
kitty:retrosmart-kitty
nemo:system-file-manager
pavucontrol:gnome-volume-control
scrot:screenshot
dunst:dialog-information
music:music
terminal:utilities-terminal
files:folder
rice:preferences-system
reload:view-refresh
wallpaper:preferences-desktop-wallpaper
picom:display-brightness
lock:system-lock-screen
sleep:system-suspend
EOF

echo "Retrosmart pmenu icons installed to $DST"
