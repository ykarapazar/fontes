#!/bin/bash
# Main program of "Fontes Installer.app": plain dialogs around install.sh (no Terminal).
# All text comes from Resources/locales/<lang>.json via i18n.sh, which also exports FONTES_LANG
# for fontes_setup.py.
R="$(cd "$(dirname "$0")/../Resources" && pwd)"
LOCALES="$R/locales"
. "$R/i18n.sh"
TITLE="Fontes"
INSTALL=$(s app_button_install); KEYS=$(s app_button_keys); REMOVE=$(s app_button_remove)
CANCEL=$(s app_button_cancel); OK=$(s app_button_ok)

dialog() { osascript -e "on run argv" -e "$1" -e "end run" "${@:2}" 2>/dev/null; }

# Three actions plus Cancel: more than display dialog's three buttons, so a list.
choice=$(dialog 'set r to choose from list {item 3 of argv, item 4 of argv, item 5 of argv} with title (item 2 of argv) with prompt (item 1 of argv) default items {item 3 of argv} OK button name (item 6 of argv) cancel button name (item 7 of argv)
if r is false then error number -128
item 1 of r' \
  "$(s app_ask)" "$TITLE" "$INSTALL" "$KEYS" "$REMOVE" "$OK" "$CANCEL") || exit 0
export FONTES_BRIEF=1   # fontes_setup.py leaves out the per-file lines (long paths) for the closing dialog
export FONTES_GUI=1     # fontes_setup.py asks for the optional keys with dialogs (hidden input)
if [ "$choice" = "$INSTALL" ]; then
  dialog 'display notification (item 1 of argv) with title (item 2 of argv)' "$(s app_working)" "$TITLE"
  out=$("$R/install.sh" install 2>&1 </dev/null)
elif [ "$choice" = "$KEYS" ]; then
  out=$("$R/install.sh" keys 2>&1 </dev/null)
else
  out=$("$R/install.sh" uninstall 2>&1 </dev/null)
fi
status=$?
summary=$(printf '%s\n' "$out" | tail -8)
dialog 'display dialog (item 1 of argv) with title (item 2 of argv) buttons {item 3 of argv} default button (item 3 of argv)' "$summary" "$TITLE" "$OK" >/dev/null
exit $status
