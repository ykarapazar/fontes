#!/bin/bash
# Double-click to install Fontes for your AI apps (Claude, Codex, Cursor, ...).
"$(dirname "$0")/install.sh" install
echo
LOCALES="$(dirname "$0")/locales"; [ -d "$LOCALES" ] || LOCALES="$(dirname "$0")/../locales"
. "$(dirname "$0")/i18n.sh"
read -r -p "$(s sh_press_enter) "
