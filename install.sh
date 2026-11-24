#!/usr/bin/env bash
# hkpie rice installer — Gentoo / i3 / kawaii neubrutalism 🌸
# Every Gentoo package is installed with -g (prefer binary packages, no long compiles).
set -euo pipefail

RICE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=palette.env
source "${RICE_DIR}/palette.env"

# The wallpaper ships in the repo so a fresh clone never depends on ~/Pictures.
RICE_WALLPAPER_BUNDLED="${RICE_DIR}/assets/${RICE_WALLPAPER_NAME}"

BACKUP_ROOT="${HOME}/.config/kawaii-rice-backups"
BACKUP_DIR="${BACKUP_ROOT}/$(date +%Y%m%d-%H%M%S)"
EMERGE_CMD="${EMERGE:-sudo emerge -g --ask}"
PMENU_COMMIT="${PMENU_COMMIT:-98052480c168e20463cfe4927e10c279b91de1ab}"
I3LOCK_COLOR_COMMIT="${I3LOCK_COLOR_COMMIT:-e6c0caf9b7aa22cc7864493132a1a2e258da1761}"
RETROSMART_COMMIT="${RETROSMART_COMMIT:-b74839a072eb21256d0cb19119a623d987711414}"
PORTAGE_SETUP="${PORTAGE_SETUP:-0}"

BIBATA_VERSION="2.0.7"
BIBATA_SHA="a68cae60c4dc706350e194ebc91c5fe48bc7bc9d59e119555834a2a7ee5078ef"

info()  { printf ' \033[1;33m✿\033[0m %s\n' "$*"; }
ok()    { printf ' \033[1;32m✔\033[0m %s\n' "$*"; }
warn()  { printf ' \033[1;35m!\033[0m %s\n' "$*" >&2; }
die()   { printf ' \033[1;31m✖\033[0m %s\n' "$*" >&2; exit 1; }

backup() {
    local target="$1"
    [[ -e "$target" || -L "$target" ]] || return 0
    local rel="${target#${HOME}/}"
    mkdir -p "${BACKUP_DIR}/$(dirname "${rel}")"
    cp -a "$target" "${BACKUP_DIR}/${rel}"
    info "backed up ${target}"
}

install_file() {
    local src="$1" dst="$2"
    [[ -f "$src" ]] || die "missing source file: ${src}"
    backup "$dst"
    mkdir -p "$(dirname "$dst")"
    cp -f "$src" "$dst"
    ok "installed ${dst}"
}

install_dir() {
    local src="$1" dst="$2"
    [[ -d "$src" ]] || die "missing source directory: ${src}"
    backup "$dst"
    rm -rf "$dst"
    mkdir -p "$(dirname "$dst")"
    cp -a "$src" "$dst"
    ok "installed ${dst}"
}

# ---------------------------------------------------------------------------
info "Installing Gentoo packages with: ${EMERGE_CMD}"
# ---------------------------------------------------------------------------
PACKAGES=(
    x11-wm/i3
    x11-misc/picom
    x11-misc/dunst
    x11-misc/i3lock
    media-gfx/feh
    media-gfx/scrot
    media-fonts/jetbrains-mono
    media-fonts/fira-sans
    media-fonts/noto-emoji
    media-libs/freetype
    media-libs/fontconfig
    x11-terms/kitty
    media-sound/pavucontrol
    x11-misc/pcmanfm
    app-arch/unzip
    app-editors/nano
    sys-apps/dbus
    gnome-extra/polkit-gnome
    x11-apps/xrandr
    x11-apps/xrdb
    x11-apps/xclock
    x11-apps/setxkbmap
    dev-build/autoconf
    dev-build/automake
    dev-build/libtool
    virtual/pkgconfig
    dev-libs/libev
    x11-libs/xcb-util-image
    x11-libs/xcb-util-xrm
    x11-libs/libxkbcommon
    dev-python/pygobject
    dev-python/pillow
    gnome-base/librsvg
    media-libs/imlib2
    x11-libs/libXft
    x11-libs/libXinerama
    x11-libs/libXrender
    x11-libs/libXext
    media-sound/ncmpcpp
)

if [[ "${SKIP_EMERGE:-0}" == "1" ]]; then
    warn "SKIP_EMERGE=1 — skipping package installation"
else
    # ncmpcpp clock / outputs / taglib / visualiser USE flags.
    if [[ "${EUID}" -eq 0 ]]; then
        mkdir -p /etc/portage/package.use
        printf '%s\n' 'media-sound/ncmpcpp clock outputs taglib visualizer' > /etc/portage/package.use/ncmpcpp
    else
        sudo mkdir -p /etc/portage/package.use
        echo "media-sound/ncmpcpp clock outputs taglib visualizer" | sudo tee /etc/portage/package.use/ncmpcpp >/dev/null
    fi
    ok "ncmpcpp USE flags written"
    # word-splitting is intentional here: EMERGE may carry flags (e.g. -G --ask)
    # shellcheck disable=SC2086
    ${EMERGE_CMD} "${PACKAGES[@]}"
    ok "packages installed from binary packages where available"
fi

# ---------------------------------------------------------------------------
info "Optional: configuring Portage binhost (root required)"
# ---------------------------------------------------------------------------
if [[ "${PORTAGE_SETUP}" == "1" ]]; then
    if [[ "${EUID}" -eq 0 ]]; then
        "${RICE_DIR}/scripts/install-portage.sh"
    else
        sudo "${RICE_DIR}/scripts/install-portage.sh"
    fi
else
    warn "PORTAGE_SETUP=0 — see README for the root-only binhost steps"
fi

# ---------------------------------------------------------------------------
info "Installing wallpaper"
# ---------------------------------------------------------------------------
WALLPAPER_SRC="${RICE_WALLPAPER_SRC}"
if [[ ! -f "${WALLPAPER_SRC}" && -f "${RICE_WALLPAPER_BUNDLED}" ]]; then
    WALLPAPER_SRC="${RICE_WALLPAPER_BUNDLED}"
    info "using bundled wallpaper from ${WALLPAPER_SRC}"
fi
[[ -f "${WALLPAPER_SRC}" ]] || die "no wallpaper found at ${RICE_WALLPAPER_SRC} or ${RICE_WALLPAPER_BUNDLED}"
install_file "${WALLPAPER_SRC}" "${RICE_WALLPAPER_DST}"

# ---------------------------------------------------------------------------
info "Generating palette assets (lock screen + preview)"
# ---------------------------------------------------------------------------
LOCK_ASSET="${HOME}/.local/share/backgrounds/kawaii-rice/hkpie-lock.png"
if python3 -c 'import PIL' >/dev/null 2>&1; then
    python3 "${RICE_DIR}/scripts/make-lock.py"
    python3 "${RICE_DIR}/scripts/make-preview.py"
    [[ -f "${LOCK_ASSET}" ]] || die "lock image generation failed: ${LOCK_ASSET} missing"
else
    warn "python3 PIL not available — install dev-python/pillow or the lock card will be missing"
fi

# ---------------------------------------------------------------------------
info "Installing i3 / picom / dunst / kitty / GTK configs"
# ---------------------------------------------------------------------------
install_file "${RICE_DIR}/palette.env"              "${HOME}/.config/kawaii-rice/palette.env"
install_file "${RICE_DIR}/config/i3/config"         "${HOME}/.config/i3/config"
install_file "${RICE_DIR}/config/picom/picom.conf"  "${HOME}/.config/picom/picom.conf"
install_file "${RICE_DIR}/config/dunst/dunstrc"     "${HOME}/.config/dunst/dunstrc"
install_file "${RICE_DIR}/config/kitty/kitty.conf"  "${HOME}/.config/kitty/kitty.conf"
install_file "${RICE_DIR}/config/gtk-3.0/settings.ini" "${HOME}/.config/gtk-3.0/settings.ini"
install_file "${RICE_DIR}/config/gtk-3.0/gtk.css"      "${HOME}/.config/gtk-3.0/gtk.css"
install_file "${RICE_DIR}/config/gtk-4.0/settings.ini" "${HOME}/.config/gtk-4.0/settings.ini"
install_file "${RICE_DIR}/config/fontconfig/99-kawaii-rice.conf" \
             "${HOME}/.config/fontconfig/conf.d/99-kawaii-rice.conf"
install_file "${RICE_DIR}/config/pmenu/Xresources" \
             "${HOME}/.config/pmenu/Xresources"
rm -f "${HOME}/.config/autostart/kando.desktop"
install_file "${RICE_DIR}/share/xfce4/terminal/colorschemes/HkpieBrutal.theme" \
             "${HOME}/.local/share/xfce4/terminal/colorschemes/HkpieBrutal.theme"

# GTK settings above point at these names; without installing the theme files
# GTK silently falls back to Adwaita.
if [[ -d "${RICE_DIR}/share/themes/HkpieBrutal" ]]; then
    install_dir "${RICE_DIR}/share/themes/HkpieBrutal" "${HOME}/.themes/HkpieBrutal"
    install_dir "${RICE_DIR}/share/themes/HkpieBrutal" "${HOME}/.local/share/themes/HkpieBrutal"
fi

if [[ -e "${HOME}/.xinitrc" || -L "${HOME}/.xinitrc" ]]; then
    install_file "${RICE_DIR}/config/xinitrc" "${HOME}/.xinitrc.rice"
    warn "existing ~/.xinitrc kept — use ~/.xinitrc.rice if you want the i3 one"
else
    install_file "${RICE_DIR}/config/xinitrc" "${HOME}/.xinitrc"
fi
chmod +x "${HOME}/.xinitrc" "${HOME}/.xinitrc.rice" 2>/dev/null || true

# Make kitty the default terminal for apps that read $TERMINAL. The xinitrc
# copy below covers startx sessions; environment.d covers PAM/logind sessions.
mkdir -p "${HOME}/.config/environment.d"
printf '%s\n' 'TERMINAL=kitty' > "${HOME}/.config/environment.d/90-hkpie-terminal.conf"
for xinit in "${HOME}/.xinitrc" "${HOME}/.xinitrc.rice"; do
    [[ -f "$xinit" ]] || continue
    if grep -q '^export TERMINAL=' "$xinit"; then
        sed -i 's|^export TERMINAL=.*|export TERMINAL=kitty|' "$xinit"
    elif grep -q '^exec i3' "$xinit"; then
        sed -i '/^exec i3/i export TERMINAL=kitty' "$xinit"
    else
        printf '\nexport TERMINAL=kitty\n' >> "$xinit"
    fi
done
ok "kitty set as the default terminal"

# PCManFM/libfm ignores $TERMINAL: it reads its own config. Unknown entries fall
# back to `-e`, which kitty supports, so a plain `terminal=kitty` is enough.
LIBFM_CONF="${HOME}/.config/libfm/libfm.conf"
mkdir -p "$(dirname "$LIBFM_CONF")"
if [[ ! -f "$LIBFM_CONF" ]]; then
    printf '[config]\nterminal=kitty\n' > "$LIBFM_CONF"
else
    grep -q '^\[config\]' "$LIBFM_CONF" || printf '\n[config]\n' >> "$LIBFM_CONF"
    if grep -q '^terminal=' "$LIBFM_CONF"; then
        sed -i 's|^terminal=.*|terminal=kitty|' "$LIBFM_CONF"
    else
        sed -i '/^\[config\]/a terminal=kitty' "$LIBFM_CONF"
    fi
fi
ok "PCManFM set to open terminals in kitty"

# ---------------------------------------------------------------------------
info "Installing helper scripts"
# ---------------------------------------------------------------------------
mkdir -p "${HOME}/.local/bin"
for script in palette.py rice-theme.py rice-theme rice-theme-daemon rice-wallpaper rice-pick-wallpaper.py rice-wallpaper-config.py rice-reload rice-check rice-shot rice-lock rice-menu rice-menu-spec.py rice-clipboard.py make-lock.py make-preview.py make-pmenu-icons.sh; do
    install_file "${RICE_DIR}/scripts/${script}" "${HOME}/.local/bin/${script}"
    chmod +x "${HOME}/.local/bin/${script}"
done

# Keep a wallpaper chosen through Rice → Wallpaper after config reinstalls.
if [[ -f "${HOME}/.config/hkpie/wallpaper" ]]; then
    selected_wallpaper="$(<"${HOME}/.config/hkpie/wallpaper")"
    if [[ -n "${selected_wallpaper}" && -f "${selected_wallpaper}" ]]; then
        python3 "${HOME}/.local/bin/rice-wallpaper-config.py" \
            --config "${HOME}/.config/kawaii-rice/palette.env" \
            "${selected_wallpaper}"
        ok "kept custom wallpaper in palette.env"
    fi
fi

# ---------------------------------------------------------------------------
info "Wiring the editable palette to GTK, pmenu, kitty, i3 and lock assets"
# ---------------------------------------------------------------------------
python3 "${HOME}/.local/bin/palette.py" --init
python3 "${HOME}/.local/bin/rice-theme.py"
ok "theme generated from ~/.config/hkpie/palette.conf"

# ---------------------------------------------------------------------------
info "Removing Polybar (no status bar in this rice)"
# ---------------------------------------------------------------------------
pkill -x polybar 2>/dev/null || true
rm -f "${HOME}/.local/bin/polybar-launch" "${HOME}/.config/polybar/config.ini"
rmdir "${HOME}/.config/polybar" 2>/dev/null || true

# ---------------------------------------------------------------------------
info "Installing Retrosmart icons everywhere (GTK, dunst, Nemo, pmenu)"
# ---------------------------------------------------------------------------
# One icon theme for folders, apps, notifications and the pie menu. Nemo is a
# GTK app, so it follows the GTK/GSettings/Xfconf settings below automatically.
install_retrosmart() {
    local src="${HOME}/.local/src/retrosmart-icon-theme"
    local dest="${HOME}/.local/share/icons/retrosmart-icon-theme"

    mkdir -p "$(dirname "${src}")"
    if [[ ! -d "${src}/.git" ]]; then
        info "cloning Retrosmart icon theme"
        git clone --quiet https://github.com/mdomlop/retrosmart-icon-theme.git "${src}"
    fi

    info "building Retrosmart at ${RETROSMART_COMMIT}"
    git -C "${src}" checkout --quiet "${RETROSMART_COMMIT}"
    make -C "${src}" clean >/dev/null 2>&1 || true
    make -C "${src}" PREFIX="${HOME}/.local" >/dev/null
    make -C "${src}" PREFIX="${HOME}/.local" install >/dev/null

    mkdir -p "${HOME}/.icons"
    ln -sfn "${dest}" "${HOME}/.icons/retrosmart-icon-theme"
    ln -sfn "${dest}" "${HOME}/.icons/Retrosmart"

    sh "${RICE_DIR}/scripts/make-pmenu-icons.sh" \
        "${dest}/scalable" "${HOME}/.local/share/icons/retrosmart-pmenu/48x48/apps"

    # GTK 3/4 settings.ini are installed above; these cover apps that ask
    # GSettings/Xfconf instead (GNOME and Xfce settings dialogs, Nemo, etc.).
    if command -v gsettings >/dev/null 2>&1; then
        gsettings set org.gnome.desktop.interface icon-theme retrosmart-icon-theme >/dev/null 2>&1 || true
    fi
    if command -v xfconf-query >/dev/null 2>&1; then
        xfconf-query -c xsettings -p /Net/IconThemeName -s retrosmart-icon-theme >/dev/null 2>&1 || true
    fi
    ok "Retrosmart installed globally (GTK / dunst / Nemo / pmenu)"
}

install_retrosmart

# ---------------------------------------------------------------------------
info "Installing Bibata Modern Ice cursor"
# ---------------------------------------------------------------------------
install_bibata_cursor() {
    local url="https://github.com/ful1e5/Bibata_Cursor/releases/download/v${BIBATA_VERSION}/Bibata-Modern-Ice.tar.xz"
    local cache_dir="${HOME}/.cache/rice-assets"
    local archive="${cache_dir}/Bibata-Modern-Ice.tar.xz"
    local target="${HOME}/.icons/Bibata-Modern-Ice"

    mkdir -p "${cache_dir}"
    if [[ ! -f "${archive}" ]]; then
        info "downloading Bibata Modern Ice ${BIBATA_VERSION}"
        if command -v curl >/dev/null 2>&1; then
            curl -fL --retry 3 -o "${archive}" "${url}"
        elif command -v wget >/dev/null 2>&1; then
            wget -O "${archive}" "${url}"
        else
            warn "neither curl nor wget found — skipping cursor install"
            return 0
        fi
    fi

    info "verifying Bibata sha256"
    printf '%s  %s\n' "${BIBATA_SHA}" "${archive}" | sha256sum -c - || {
        warn "Bibata checksum mismatch — removing ${archive}"
        rm -f "${archive}"
        return 0
    }

    rm -rf "${target}"
    mkdir -p "${target}"
    tar -xJf "${archive}" -C "${target}" --strip-components=1
    install_file "${RICE_DIR}/config/icons/default-index.theme" "${HOME}/.icons/default/index.theme"
    ok "Bibata Modern Ice installed to ${target}"
}

install_bibata_cursor

# ---------------------------------------------------------------------------
info "Installing pmenu (replaces Kando)"
# ---------------------------------------------------------------------------
# pmenu is tiny (two C files), so a local build is faster and more reliable
# than Kando's fullscreen Electron overlay. Gentoo deps are installed with -g
# above; this only builds the binary into ~/.local/bin.
install_pmenu() {
    local src="${HOME}/.local/src/pmenu"
    local bin="${HOME}/.local/bin/pmenu"
    local marker="${src}/.hkpie-lock-ring"
    local patch="${RICE_DIR}/patches/pmenu-hkpie-lock-ring.patch"

    [[ -f "${patch}" ]] || die "missing pmenu patch: ${patch}"

    if [[ -x "${bin}" ]] && [[ -f "${marker}" ]] && \
       [[ "$(git -C "${src}" rev-parse HEAD 2>/dev/null || true)" == "${PMENU_COMMIT}" ]]; then
        ok "pmenu already installed with the hkpie lock-ring patch"
        return 0
    fi

    if ! command -v git >/dev/null 2>&1 || ! command -v make >/dev/null 2>&1; then
        warn "git and make are required to build pmenu"
        return 0
    fi

    mkdir -p "$(dirname "${src}")"
    if [[ ! -d "${src}/.git" ]]; then
        info "cloning pmenu"
        git clone --quiet https://github.com/phillbush/pmenu.git "${src}"
    fi

    info "building pmenu at ${PMENU_COMMIT} with the hkpie lock-ring patch"
    git -C "${src}" reset --hard "${PMENU_COMMIT}" >/dev/null
    git -C "${src}" apply "${patch}"
    touch "${marker}"
    make -C "${src}" clean >/dev/null 2>&1 || true
    make -C "${src}" PREFIX="${HOME}/.local" >/dev/null
    make -C "${src}" PREFIX="${HOME}/.local" install >/dev/null
    ok "pmenu installed to ${bin}"
}

install_pmenu

# ---------------------------------------------------------------------------
info "Installing the hkpie pie-style lock indicator"
# ---------------------------------------------------------------------------
# Gentoo's i3lock 2.16 cannot style its round indicator. This tiny local C build
# stays in ~/.local/bin, so the system i3lock package is untouched and remains
# the fallback. Pinned so the lock look never drifts between installs.
install_i3lock_color() {
    local src="${HOME}/.local/src/i3lock-color"
    local bin="${HOME}/.local/bin/hkpie-i3lock"
    local marker="${src}/.hkpie-ring-style"
    local patch="${RICE_DIR}/patches/i3lock-color-hkpie-ring.patch"

    [[ -f "${patch}" ]] || die "missing i3lock-color patch: ${patch}"

    if [[ -x "${bin}" ]] && [[ -f "${marker}" ]] && \
       [[ "$(git -C "${src}" rev-parse HEAD 2>/dev/null || true)" == "${I3LOCK_COLOR_COMMIT}" ]]; then
        ok "hkpie-i3lock already installed with the hkpie ring-style patch"
        return 0
    fi

    for cmd in git make autoreconf pkg-config; do
        if ! command -v "${cmd}" >/dev/null 2>&1; then
            warn "${cmd} is required to build hkpie-i3lock; using system i3lock"
            return 0
        fi
    done

    mkdir -p "$(dirname "${src}")"
    if [[ ! -d "${src}/.git" ]]; then
        info "cloning i3lock-color"
        git clone --quiet https://github.com/Raymo111/i3lock-color.git "${src}"
    fi

    info "building hkpie-i3lock at ${I3LOCK_COLOR_COMMIT} with the hkpie ring-style patch"
    git -C "${src}" reset --hard "${I3LOCK_COLOR_COMMIT}" >/dev/null
    git -C "${src}" apply "${patch}"
    touch "${marker}"
    if ! (cd "${src}" && sh ./build.sh >/dev/null 2>&1); then
        warn "hkpie-i3lock build failed; using system i3lock"
        return 0
    fi
    install -m 0755 "${src}/build/i3lock" "${bin}"
    ok "hkpie-i3lock installed to ${bin}"
}

install_i3lock_color
pkill -x kando 2>/dev/null || true

# ---------------------------------------------------------------------------
info "Finishing up"
# ---------------------------------------------------------------------------
fc-cache -f >/dev/null 2>&1 || true
if command -v i3-msg >/dev/null 2>&1 && pgrep -x i3 >/dev/null 2>&1; then
    "${HOME}/.local/bin/rice-reload" >/dev/null 2>&1 || true
    ok "live session reloaded"
fi

cat <<EOF

  🌸 hkpie rice is installed! 🌸

  Log out and select i3, or press Mod+Shift+c to reload.
  • Mod+d opens the pmenu pie menu with Retrosmart icons (no Kando overlay).
  • Mod+Return and Mod+Shift+Return both open kitty, the default terminal.
  • Mod+Shift+t opens the editable palette in nano; edits restyle GTK, kitty, i3, dunst, picom, pmenu and the live lock screen.
  • Mod+Shift+x locks with a live time/date card and a pie-style round indicator.
  • Palette roles: background #EAE7AA · highlight #F6F098 · accent #F0A090
  • Backups: ${BACKUP_DIR}

  Have fun ♡
EOF
