#!/bin/bash
# Build the Fontes installer artifacts into installer/dist/ (macOS; nothing is uploaded).
#
#   installer/build.sh
#
# Produces:
#   Fontes-Installer-<ver>.zip      folder with the .command (Mac) and .cmd (Windows) installers
#   Fontes-Installer-<ver>-mac.zip  "Fontes Installer.app" (signed + notarized if configured)
#   Fontes-<ver>.mcpb               Claude Desktop extension (launcher only; auto-updating)
#
# Signing is OFF unless these are set:
#   FONTES_SIGN_IDENTITY   codesign identity, e.g. "Developer ID Application: Name (TEAMID)"
#   FONTES_NOTARY_KEY      path to the App Store Connect API key (.p8)   } all three set =
#   FONTES_NOTARY_KEY_ID   its key id                                    } notarize + staple
#   FONTES_NOTARY_ISSUER   its issuer id                                 }
set -euo pipefail
cd "$(dirname "$0")"
VER=$(sed -n 's/^version = "\(.*\)"/\1/p' ../pyproject.toml | head -1)
OUT="$PWD/dist"; STAGE="$OUT/stage"
rm -rf "$OUT"; mkdir -p "$STAGE"

# 1. Plain installer folder (both OSes).
F="$STAGE/Fontes Installer"; mkdir -p "$F"
cp fontes_setup.py fontes_i18n.py fontes_launcher.py macos/install.sh macos/i18n.sh \
   "macos/Install Fontes.command" "macos/Add or change keys.command" "macos/Uninstall Fontes.command" \
   windows/install.ps1 "windows/Install Fontes.cmd" "windows/Add or change keys.cmd" "windows/Uninstall Fontes.cmd" "$F/"
cp -R locales "$F/"
PRIV="$STAGE/privacy-languages.txt"   # translated privacy notices, for fontes_i18n.privacy_url
(cd ../docs/i18n && for f in */PRIVACY.md; do if [ -e "$f" ]; then echo "${f%/PRIVACY.md}"; fi; done) > "$PRIV"
cp "$PRIV" "$F/"
cp ../docs/INSTALL.md "$F/READ ME.md"
(cd "$STAGE" && ditto -c -k --keepParent "Fontes Installer" "$OUT/Fontes-Installer-$VER.zip")

# 2. Mac app.
APP="$STAGE/Fontes Installer.app"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp macos/app-main.sh "$APP/Contents/MacOS/fontes-installer"
cp fontes_setup.py fontes_i18n.py fontes_launcher.py macos/install.sh macos/i18n.sh "$APP/Contents/Resources/"
cp -R locales "$PRIV" "$APP/Contents/Resources/"
cat > "$APP/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleName</key><string>Fontes Installer</string>
  <key>CFBundleIdentifier</key><string>io.github.ykarapazar.fontes.installer</string>
  <key>CFBundleVersion</key><string>$VER</string>
  <key>CFBundleShortVersionString</key><string>$VER</string>
  <key>CFBundleExecutable</key><string>fontes-installer</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>LSMinimumSystemVersion</key><string>11.0</string>
</dict></plist>
PLIST
if [ -n "${FONTES_SIGN_IDENTITY:-}" ]; then
  codesign --force --options runtime --timestamp --sign "$FONTES_SIGN_IDENTITY" "$APP"
  codesign --verify --strict --verbose=1 "$APP"
fi
ditto -c -k --keepParent "$APP" "$OUT/Fontes-Installer-$VER-mac.zip"
if [ -n "${FONTES_NOTARY_KEY:-}" ] && [ -n "${FONTES_NOTARY_KEY_ID:-}" ] && [ -n "${FONTES_NOTARY_ISSUER:-}" ]; then
  [ -n "${FONTES_SIGN_IDENTITY:-}" ] || { echo "Notarizing needs FONTES_SIGN_IDENTITY too." >&2; exit 1; }
  xcrun notarytool submit "$OUT/Fontes-Installer-$VER-mac.zip" --key "$FONTES_NOTARY_KEY" \
    --key-id "$FONTES_NOTARY_KEY_ID" --issuer "$FONTES_NOTARY_ISSUER" --wait
  xcrun stapler staple "$APP"
  rm "$OUT/Fontes-Installer-$VER-mac.zip"
  ditto -c -k --keepParent "$APP" "$OUT/Fontes-Installer-$VER-mac.zip"
fi

# 3. Claude Desktop extension.
B="$STAGE/mcpb"; mkdir -p "$B/server"
sed "s/\"version\": \"0.0.0\"/\"version\": \"$VER\"/" mcpb/manifest.json > "$B/manifest.json"
# Translated description, keywords and tool descriptions from locales/<lang>.json (mcpb_* keys);
# Claude Desktop picks the file for its own language (MCPB manifest "localization").
python3 mcpb/localize.py "$B/manifest.json" locales "$B/mcpb-resources"
cp mcpb/pyproject.toml "$B/"; cp fontes_launcher.py "$B/server/"; cp ../LICENSE "$B/"
(cd "$B" && zip -qrX "$OUT/Fontes-$VER.mcpb" .)

rm -rf "$STAGE"
ls -l "$OUT"
