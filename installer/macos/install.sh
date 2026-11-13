#!/bin/bash
# Fontes installer core for macOS: make sure uv is present, then run fontes_setup.py.
# Usage: install.sh install|keys|uninstall
set -euo pipefail
UV_VERSION="0.11.4"   # uv release fetched from astral.sh when uv is missing; bump deliberately

HERE="$(cd "$(dirname "$0")" && pwd)"
SETUP="$HERE/fontes_setup.py"
[ -f "$SETUP" ] || SETUP="$HERE/../fontes_setup.py"
LOCALES="$(dirname "$SETUP")/locales"
I18N="$HERE/i18n.sh"
. "$I18N"

UV="$(command -v uv || true)"
for c in "$HOME/.local/bin/uv" "$HOME/.cargo/bin/uv"; do
  if [ -z "$UV" ] && [ -x "$c" ]; then UV="$c"; fi
done
if [ -z "$UV" ] && [ "${1:-}" = "install" ]; then
  s sh_installing_uv
  curl -LsSf "https://astral.sh/uv/$UV_VERSION/install.sh" | env UV_NO_MODIFY_PATH=1 sh
  UV="$HOME/.local/bin/uv"
fi
if [ -z "$UV" ]; then s sh_no_uv; exit 0; fi
exec "$UV" run --managed-python --python 3.13 --no-project --quiet "$SETUP" "$@"
