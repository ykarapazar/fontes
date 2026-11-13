#!/bin/bash
# Double-click to add, change or remove the optional API keys (France, United States).
"$(dirname "$0")/install.sh" keys
echo
LOCALES="$(dirname "$0")/locales"; [ -d "$LOCALES" ] || LOCALES="$(dirname "$0")/../locales"
. "$(dirname "$0")/i18n.sh"
read -r -p "$(s sh_press_enter) "
