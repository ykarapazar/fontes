# Sourced by the macOS installer scripts: pick the language and read strings from locales/<lang>.json
# with plutil (built into macOS; runs before uv or Python exist). Same order as fontes_i18n.py:
# FONTES_LANG, then the Mac's preferred languages, then English; pt-BR -> pt, pt-AO -> pt-PT -> pt,
# zh-TW -> zh-Hant.
# Set LOCALES to the locales folder before sourcing.

fontes_pick_lang() {
  local tag c
  for tag in "$@"; do
    tag=${tag%%.*}; tag=${tag//_/-}
    while [ -n "$tag" ]; do
      c=$tag
      case "$tag" in
        zh|zh-CN|zh-SG) c=zh-Hans ;;
        zh-TW|zh-HK|zh-MO) c=zh-Hant ;;
        pt-BR) ;;
        pt-??) c=pt-PT ;;   # Portuguese outside Brazil: European norm
      esac
      for x in "$tag" "$c"; do
        if [ -f "$LOCALES/$x.json" ]; then echo "$x"; return; fi
      done
      [ "${tag%-*}" = "$tag" ] && break
      tag=${tag%-*}
    done
  done
  echo en
}

# s KEY: the string in the chosen language, English if that file lacks it.
s() {
  plutil -extract "$1" raw -o - "$LOCALES/$FONTES_LANG.json" 2>/dev/null \
    || plutil -extract "$1" raw -o - "$LOCALES/en.json"
}

FONTES_LANG=$(fontes_pick_lang ${FONTES_LANG:-} $(defaults read -g AppleLanguages 2>/dev/null | sed '1d;$d' | tr -d ' ",'))
export FONTES_LANG
