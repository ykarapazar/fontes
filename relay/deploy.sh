#!/bin/bash
# Deploy the Fontes relay to $RELAY_SSH_HOST. Run by hand, from anywhere; read relay/README.md first.
# This script only copies files into ~/fontes-relay and starts/reloads the one PM2 app
# "fontes-relay". It does not touch nginx, DNS, certificates or any other PM2 app.
set -euo pipefail
HOST="${RELAY_SSH_HOST:?set RELAY_SSH_HOST to the ssh alias of your server}"
DIR="fontes-relay"
HERE="$(cd "$(dirname "$0")" && pwd)"

python3 -m py_compile "$HERE/relay.py"
echo "== PM2 apps on $HOST before deploying (check they are all online) =="
ssh "$HOST" "pm2 list"
read -r -p "Continue? [y/N] " ok
[ "$ok" = "y" ] || { echo "Stopped."; exit 1; }

ssh "$HOST" "mkdir -p ~/$DIR/data && chmod 700 ~/$DIR ~/$DIR/data && python3 --version"
scp "$HERE/relay.py" "$HERE/ecosystem.config.js" "$HOST:~/$DIR/"
ssh "$HOST" "cd ~/$DIR && if pm2 describe fontes-relay >/dev/null 2>&1; then pm2 reload ecosystem.config.js; else pm2 start ecosystem.config.js; fi && pm2 save"
sleep 2
ssh "$HOST" "curl -fsS http://127.0.0.1:4020/healthz && echo && pm2 list"
echo "Relay is running on $HOST:127.0.0.1:4020. nginx/DNS/cert: see relay/README.md (one-time, by hand)."
