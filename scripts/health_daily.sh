#!/bin/bash
# Daily source health run on a maintainer's machine: probe every source, keep the report in research/health/
# (untracked), write status/HEALTH.md, refresh status/index.html (GitHub's published page from
# origin/main when there is one) and show one macOS notification when any source changed status
# since the previous run. Network: the probes plus one `git fetch`. Writes no tracked files.
set -u
cd "$(dirname "$0")/.." || exit 1
UV=$(command -v uv || echo "$HOME/.local/bin/uv")
mkdir -p status
prev=$(ls -t research/health/*.json 2>/dev/null | head -n 1)
new="research/health/$(date -u +%Y-%m-%dT%H%MZ).json"
echo "== $(date -u +%FT%TZ) health run -> $new (previous: ${prev:-none})"
"$UV" run python scripts/health.py --json "$new" --md status/HEALTH.md ${prev:+--prev "$prev"}
[ -s "$new" ] || { echo "health run wrote no report"; exit 1; }
# Status page: GitHub's daily run is canonical. Show the page it published on origin/main;
# until it has published one, build the page from the local reports.
if GIT_SSH_COMMAND="ssh -o BatchMode=yes -o ConnectTimeout=15" git fetch -q origin 2>/dev/null \
   && git show origin/main:docs/status/index.html > status/index.html.tmp 2>/dev/null; then
  mv status/index.html.tmp status/index.html; echo "status page: origin/main (GitHub run)"
else
  rm -f status/index.html.tmp
  "$UV" run python scripts/status_page.py; echo "status page: local reports"
fi
msg=$("$UV" run python - "$prev" "$new" <<'PY'
import json, sys
from world_legal_mcp.health import BROKEN, diff
old = json.load(open(sys.argv[1])) if sys.argv[1] else {"results": []}
new = json.load(open(sys.argv[2]))
d = diff(old, new)
if any(d.values()):
    codes = sorted({r["jurisdiction"] for r in new["results"] if r["status"] in BROKEN})
    print(f"{len(codes)} down: {', '.join(codes) or 'none'} ({sum(map(len, d.values()))} changed)")
PY
)
if [ -n "$msg" ]; then
  echo "notify: $msg"
  osascript -e 'on run argv' -e 'display notification (item 1 of argv) with title "Fontes status"' -e 'end run' "$msg"
fi
