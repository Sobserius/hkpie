# 🌸 hkpie rice — Gentoo / i3wm / kawaii neubrutalism ✿

A complete **neubrutalist** desktop rice for **Gentoo + i3wm**, themed with colors
sampled directly from `~/Pictures/hkpiewallpaper.png`.

Neubrutalism here means: **square geometry, heavy ink outlines, hard offset shadows,
flat ungradient fills, oversized type, and raw high contrast** — not soft rounded
“kawaii stickers”. The wallpaper palette keeps it warm while the treatment stays harsh.
Includes dunst, a lock screen, a matching **pmenu** pie menu, letter-block
icons, and a **Bibata Modern Ice** cursor.

> No hours of compiling: every Gentoo package is installed with `emerge -g`
> (binary packages first). pmenu and the lock-screen ring are tiny local C builds;
> Bibata comes from a verified upstream release archive.

---

## 🎨 Palette (from hkpiewallpaper.png)

| Name    | Hex       | Where it comes from in the wallpaper        |
|---------|-----------|---------------------------------------------|
| `cream` | `#EAE7AA` | Dominant pale yellow-green backdrop (~82%)  |
| `butter`| `#F6F098` | Bright buttery yellow highlights             |
| `paper` | `#F7F7F7` | White eye / shine highlights                 |
| `blush` | `#F0A090` | Coral-pink cheek blush (accent)              |
| `tan`   | `#C3AF8D` | Warm tan shading                             |
| `mocha` | `#A79071` | Deeper warm shading                          |
| `ink`   | `#474333` | Dark olive "lineart" outline                 |
| `deep`  | `#2E2B21` | Darkest outline shade (shadows / urgency)    |

The whole rice — i3 borders, picom shadows, dunst notifications, lock screen,
GTK overrides, icons, and the pmenu X resources — uses only these colors.

### Edit the palette live

Press `Mod+Shift+t` (or pick **Rice → Edit theme** in `Mod+d`) to open
`~/.config/hkpie/palette.conf` in nano inside kitty. The file contains only the
eight `name=#HEX` lines above — no exports, no CSS, no comments. A small daemon
started by i3 watches it and re-renders the GTK 3/4 themes, pmenu X resources,
lock image, preview, and merged X resources as soon as you save.

---

## ✨ What's inside

* **i3wm** — 5px ink outline borders with no title bars or tab/stack headers, plain split
  layouts, 12px gaps, named workspaces (pressing `Mod+1` always goes to 1, never
  toggles back), blush-red active border matching the GTK selection, nagbar exit
  prompt. All binds use a modifier; even resize mode uses `Mod+h/j/k/l` and
  `Mod+Escape` (no bare-key binds).
* **picom** — zero rounded corners, rock-hard 12px offset slabs with zero blur, full
  opacity, in the wallpaper's darkest ink; no dimming, with short appear/disappear
  animations on window open/close.
* **dunst + lock screen** — square notification blocks; `Mod+Shift+x` locks with
  a flat cream filler, a square paper card showing the current time/date and a
  hard ink outline, plus a fat butter ring below it with a scaled dark ink line
  and a +12/+12 ink slab shadow like picom. The ring echoes the pmenu pie slices:
  blush typing arcs, dark slab separators, and clear WRONG/CHECK text; the EN/RU
  hint stays on the card.
* **polkit-gnome** — lightweight GUI authentication prompts; autostarts with i3.
* **pmenu menu** — `Mod+d` opens a pie menu modelled on the lock ring: a paper
  centre, butter slices, a blush active arc, deep ink separators and rim, plus the
  hard dark slab shadow. No fullscreen Electron overlay.
* **Custom apps** — `kitty` as the default terminal (`$TERMINAL`, PCManFM/libfm,
  and pmenu terminal apps), `pavucontrol`, PCManFM/Thunar,
  fullscreen/window/region screenshots copied to the clipboard, notification
  history, and `ncmpcpp` installed with clock / outputs / taglib / visualizer USE
  flags.
* **Retrosmart everywhere** — one upstream icon theme for GTK, Nemo/folders, dunst,
  and the pie menu; pmenu gets PNGs rendered from the same Retrosmart SVGs.
* **Bibata Modern Ice cursor** — official v2.0.7 archive, SHA256 verified.
* **Portage/binhost templates** — root-only setup that makes plain `emerge` prefer
  binary packages too.
* **GTK3/GTK4 / fontconfig** — pastel overrides, Fira Sans + JetBrains Mono.
* **Helper scripts** — `rice-wallpaper`, `rice-reload`, `rice-check`, `rice-shot`,
  `rice-lock`, `rice-menu`, `rice-menu-spec.py`, `rice-clipboard.py`, `make-pmenu-icons.sh`.

---

## 📦 Requirements & install

Run the installer from this directory:

```bash
cd ~/hkpie
./install.sh
```

The installer:

1. Installs packages with **`emerge -g --ask`** (prefer binary packages):
   `x11-wm/i3`, `x11-misc/picom`, `x11-misc/dunst`,
   `x11-misc/i3lock`, `media-gfx/feh`, `media-gfx/scrot`,
   `media-fonts/jetbrains-mono`, `media-fonts/fira-sans`, `media-fonts/noto-emoji`,
   `x11-terms/kitty`,
   `media-sound/pavucontrol`, `x11-misc/pcmanfm`, `app-arch/unzip`, `sys-apps/dbus`,
   `x11-apps/xrandr`, `x11-apps/xrdb`, `gnome-base/librsvg`, `dev-python/pygobject`,
   plus pmenu and lock-ring build deps.
2. Generates the lock image with PIL and renders pmenu PNGs from Retrosmart SVGs.
3. Copies the bundled `assets/hkpiewallpaper.png` (or your existing
   `~/Pictures/hkpiewallpaper.png` if present) to
   `~/.local/share/backgrounds/kawaii-rice/hkpiewallpaper.png`.
4. Installs the configs, scripts, Retrosmart globally (GTK/GSettings/Xfconf/dunst/Nemo),
   pmenu X resources and verified Bibata cursor, then builds pmenu and the styled
   locker locally into `~/.local/bin` (no Node toolchain, no system i3lock swap).
5. Backs up any existing config it replaces into
   `~/.config/kawaii-rice-backups/<timestamp>/`.

The styled locker lives at `~/.local/bin/hkpie-i3lock`. If its tiny local build
fails, `rice-lock` falls back to vanilla `i3lock`, which still shows the circular
unlock feedback.

If packages are already installed, skip the emerge step:

```bash
SKIP_EMERGE=1 ./install.sh
```

If you want **strictly binary-only** packages, put this in `make.conf` or prefix the
command: `EMERGE="sudo emerge -G --ask" ./install.sh`.
(`-g` prefers binpkgs and falls back to source; `-G` refuses to fall back.)

### Logging in

If you use a display manager, select **i3** in the session menu and log in.
If you use `startx`, the installer installs `~/.xinitrc` (only when you don't already
have one; otherwise it writes `~/.xinitrc.rice`).

---

## 🐧 Portage / Gentoo binhost side (root required)

The installer normally cannot touch `/etc`. To make *plain* `emerge` prefer binary
packages too, either run:

```bash
PORTAGE_SETUP=1 ./install.sh
```

...or do the root steps yourself:

```bash
cd ~/hkpie
sudo install -d /etc/portage/binrepos.conf
sudo cp portage/gentoo.conf /etc/portage/binrepos.conf/99-hkpie-gentoo.conf

sudo install -d /etc/portage/package.use
sudo cp portage/package.use/99-hkpie-rice /etc/portage/package.use/99-hkpie-rice

# x11-misc/pcmanfm is ~amd64 on Gentoo.
sudo install -d /etc/portage/package.accept_keywords
sudo cp portage/package.accept_keywords/99-hkpie-rice \
       /etc/portage/package.accept_keywords/99-hkpie-rice

sudo cp /etc/portage/make.conf /etc/portage/make.conf.hkpie-rice.bak
cat portage/make.conf.snippet | sudo tee -a /etc/portage/make.conf

# If getuto is available, import the binhost signing keys:
command -v getuto >/dev/null && sudo getuto || true
```

For arm64, edit `portage/gentoo.conf` and replace `amd64/x86-64` with `arm64/arm64`,
and change `~amd64` to `~arm64` in `portage/package.accept_keywords/99-hkpie-rice`.

Then the exact package command this rice wants is:

```bash
sudo emerge -g --ask \
  x11-wm/i3 x11-misc/picom x11-misc/dunst x11-misc/i3lock \
  media-gfx/feh media-gfx/scrot media-fonts/jetbrains-mono media-fonts/fira-sans \
  x11-terms/kitty media-sound/pavucontrol x11-misc/pcmanfm \
  app-arch/unzip sys-apps/dbus x11-apps/xrandr x11-apps/xrdb \
  gnome-base/librsvg dev-python/pygobject media-libs/imlib2 x11-libs/libXft x11-libs/libXinerama \
  x11-libs/libXrender x11-libs/libXext
```

`-g` is deliberate: it prefers `getbinpkg` and only falls back to source when no
binary package is available. `-G` would be stricter, but the installer uses `-g` as
requested.

---

## ⌨️ Keybindings

| Keys | Action |
|------|--------|
| `Mod + Return` | kitty (default terminal) |
| `Mod + Shift + Return` | kitty (explicit shortcut) |
| `Mod + e` | PCManFM with Thunar fallback |
| `Mod + d` | Open the pmenu pie menu with Retrosmart icons |
| `Mod + v` | pavucontrol volume mixer |
| `Mod + n` | Show notification history (dunst) |
| `Mod + Shift + n` | Close the newest notification |
| `Mod + Shift + x` | Lock with live time/date card and a pmenu-style round indicator |
| `Mod + 1…0` | Switch workspace |
| `Mod + Shift + 1…0` | Move focused window to workspace |
| `Mod + h/j/k/l` or arrows | Focus window |
| `Mod + Shift + h/j/k/l` | Move window |
| `Mod + r` | Resize mode; use `Mod+h/j/k/l`, exit with `Mod+Escape` |
| `Mod + f` | Fullscreen toggle |
| `Mod + t` | Floating toggle |
| `Mod + Space` | Focus tiling / floating toggle |
| `Mod + a` | Focus parent container |
| `Mod + Shift + s` | Fullscreen screenshot to `~/Pictures/` + clipboard |
| `Mod + Shift + o` | Cycle wallpaper |
| `Mod + Shift + p` | Reload the whole rice |
| `Mod + Shift + c` | Reload i3 |
| `Mod + Shift + r` | Restart i3 in place |
| `Mod + Shift + q` | Close focused window |
| `Mod + Shift + e` | Exit i3 (with a cute confirmation nagbar) |
| `XF86Audio*` | Volume / media keys |

---

## 🧩 pmenu menu

`Mod + d` runs `~/.local/bin/rice-menu`, which calls `rice-menu-spec.py` to build a
tab-indented menu spec on the fly for [pmenu](https://github.com/phillbush/pmenu).
It is a real X11 pie menu — no fullscreen Electron window, no black overlay, no
compositor hacks.

Slices:

* **Apps** — every visible `.desktop` app is scanned on each open, including
  Flatpak exports, grouped by category; plus Notifications and Music
* **Terminal** — Kitty
* **Files** — Nemo with pcmanfm/Thunar fallback
* **Screenshot** — its own pie slice with the Retrosmart camera/screenshot icon;
  its entries are plain text: Fullscreen, Active window, Region
* **Rice** — reload, compositor reload, lock, suspend

pmenu treats any output starting with `$` as a dynamic-submenu command, so the
action commands are wrapped in `sh -c '...'`; that is why Screenshot works now.

The look comes from X resources at `~/.config/pmenu/Xresources` plus a small
patched build of pmenu (paper centre, butter ring, blush active arc, deep ink
line/separators), loaded automatically by i3. The dark slab around the whole
pie is picom's rock-hard offset shadow, matching the lock ring and app windows.
Icons come from `ICONPATH` pointing at `~/.local/share/icons/retrosmart-pmenu/48x48/apps`,
rendered from the same Retrosmart SVGs that GTK/Nemo/dunst use.

## 🗂 File tree

```
hkpie/
├── README.md
├── palette.env                     # shared color values
├── install.sh                      # backs up, installs with emerge -g
├── assets/
│   └── hkpiewallpaper.png          # shipped wallpaper, no generation needed
├── portage/
│   ├── gentoo.conf                 # official amd64 binhost template
│   ├── make.conf.snippet           # getbinpkg defaults
│   ├── package.use/99-hkpie-rice
│   └── package.accept_keywords/99-hkpie-rice  # pcmanfm ~amd64
├── config/
│   ├── i3/config
│   ├── picom/picom.conf
│   ├── dunst/dunstrc
│   ├── kitty/kitty.conf
│   ├── icons/default-index.theme   # Bibata cursor inheritance
│   ├── pmenu/Xresources
│   ├── gtk-3.0/{settings.ini,gtk.css}
│   ├── gtk-4.0/settings.ini
│   ├── fontconfig/99-kawaii-rice.conf
│   └── xinitrc
├── patches/
│   ├── pmenu-hkpie-lock-ring.patch  # pmenu centre/ring/segments styling
│   └── i3lock-color-hkpie-ring.patch # scaled dark ring line + slab shadow
├── scripts/
│   ├── install-portage.sh          # optional root helper
│   ├── palette.py                  # reads ~/.config/hkpie/palette.conf
│   ├── rice-theme                  # opens the palette in nano (kitty)
│   ├── rice-theme.py               # renders GTK/pmenu/lock from the palette
│   ├── rice-theme-daemon           # watches for palette saves
│   ├── make-lock.py                # generates the lock-screen image
│   ├── make-preview.py             # regenerates the pmenu/GTK preview
│   ├── rice-wallpaper
│   ├── rice-reload
│   ├── rice-check
│   ├── rice-shot
│   ├── rice-clipboard.py        # holds PNGs on the X clipboard
│   ├── rice-lock
│   ├── rice-menu
│   ├── rice-menu-spec.py          # scans .desktop files, builds the pmenu spec
│   ├── make-pmenu-icons.sh        # renders Retrosmart SVGs to pmenu PNGs
└── share/
    └── xfce4/terminal/colorschemes/HkpieBrutal.theme
```

---

## 🧪 Verify

```bash
rice-check        # checks i3 syntax, configs, icons, cursor, wallpaper, apps
```

---

## 🙏 Credits

* Wallpaper and pastel98 assets: Sobserius (`pastel98-xfce-setup`).
* pmenu by phillbush — https://github.com/phillbush/pmenu
* Bibata cursor by ful1e5 — https://github.com/ful1e5/Bibata_Cursor
* i3, dunst, picom and the Gentoo maintainers 💛

Made with 🌸 and no long compiles.
