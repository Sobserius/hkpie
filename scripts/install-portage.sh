#!/usr/bin/env bash
# hkpie rice — configure Portage to prefer binary packages. Requires root. 🌸
set -euo pipefail

RICE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ "${EUID}" -ne 0 ]]; then
    exec sudo "$0" "$@"
fi

info() { printf ' \033[1;33m✿\033[0m %s\n' "$*"; }
ok()   { printf ' \033[1;32m✔\033[0m %s\n' "$*"; }

MARKER="# hkpie-rice: prefer binary packages so emerges don't compile for hours."

info "Installing binhost config"
mkdir -p /etc/portage/binrepos.conf
cp -f "${RICE_DIR}/portage/gentoo.conf" /etc/portage/binrepos.conf/99-hkpie-gentoo.conf
ok "/etc/portage/binrepos.conf/99-hkpie-gentoo.conf"

info "Installing USE flags"
mkdir -p /etc/portage/package.use
cp -f "${RICE_DIR}/portage/package.use/99-hkpie-rice" /etc/portage/package.use/99-hkpie-rice
ok "/etc/portage/package.use/99-hkpie-rice"

info "Installing package.accept_keywords"
mkdir -p /etc/portage/package.accept_keywords
cp -f "${RICE_DIR}/portage/package.accept_keywords/99-hkpie-rice" \
      /etc/portage/package.accept_keywords/99-hkpie-rice
ok "/etc/portage/package.accept_keywords/99-hkpie-rice"

touch /etc/portage/make.conf
if ! grep -qF "hkpie-rice: prefer binary packages" /etc/portage/make.conf; then
    cp -a /etc/portage/make.conf /etc/portage/make.conf.hkpie-rice.bak 2>/dev/null || true
    {
        printf '\n%s\n' "$MARKER"
        cat "${RICE_DIR}/portage/make.conf.snippet"
    } >> /etc/portage/make.conf
    ok "appended binary-package defaults to /etc/portage/make.conf (backup: .hkpie-rice.bak)"
else
    ok "make.conf already configured"
fi

if command -v getuto >/dev/null 2>&1 && [[ ! -d /etc/portage/gnupg ]]; then
    info "setting up binary package signature keys (getuto)"
    getuto || true
fi

cat <<'EOF'

  🌸 Portage is ready. From now on plain 'emerge' prefers binpkgs.
  You can still force it per command:  emerge -g --ask <package>

EOF
