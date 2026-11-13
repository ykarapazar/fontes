# Fontes relay

Receives the opt-in usage counts (`POST /v1/stats`) and confirmed bug reports (`POST /v1/bug`)
from Fontes clients. One file, `relay.py`, Python standard library only (3.9+), SQLite storage.
What clients send and why: `docs/PRIVACY.md`. The client side is
`src/world_legal_mcp/stats.py` and `bugreport.py`; both use `RELAY_URL`
(`https://relay.kinetra.fit`, override with `FONTES_RELAY`).

**Status:** deployed at `relay.kinetra.fit` (PM2 app `fontes-relay`, port 4020, nginx in front,
Let's Encrypt certificate via certbot). If it is down, clients fail silently
(stats are kept locally; bug reports tell the user to open a GitHub issue).

- Validation: exact field sets (unknown fields are rejected), regex-checked codes and tool
  names, size limits (stats 64 KB, bug 8 KB, error 1000 chars, note 4000 chars).
- Rate limit per IP, in memory: 60 stats posts and 5 bug reports per hour.
- No IP is written anywhere: `relay.py` logs nothing per request, and the nginx block below
  turns its access log off.
- Counts are summed into one row per day/version/OS/jurisdiction/tool; single submissions are
  not stored. Retention: counts 730 days, bug reports 365 days (pruned on each write).

## Local check

```bash
RELAY_DB=/tmp/r.sqlite3 python3 relay/relay.py &      # listens on 127.0.0.1:4020
curl -s localhost:4020/healthz
FONTES_RELAY=http://127.0.0.1:4020 uv run fontes report-bug --note "test"
RELAY_DB=/tmp/r.sqlite3 python3 relay/relay.py bugs
```

## Deploying to `<your-host>` (by hand, once)

`<your-host>` is your server's ssh alias. If other apps run on the same server, don't restart or edit them; run `nginx -t` before every reload.

1. **DNS**: add an `A` record `relay.kinetra.fit → <server-ip>` at the domain's DNS
   provider. Wait until `dig +short relay.kinetra.fit` returns that IP.
2. **Port**: `ssh <your-host> "ss -ltnp | grep 4020"` must print nothing. If 4020 is taken, change
   `RELAY_PORT` in `ecosystem.config.js`, `deploy.sh` and the nginx block.
3. **Relay**: from the repo, `RELAY_SSH_HOST=<your-host> relay/deploy.sh`. It shows `pm2 list`, asks to continue, copies
   `relay.py` + `ecosystem.config.js` to `~/fontes-relay`, starts or reloads only the PM2 app
   `fontes-relay`, runs `pm2 save` and checks `/healthz`.
4. **nginx**: check how the existing sites are laid out (`ls /etc/nginx/sites-enabled
   /etc/nginx/conf.d`), then add a new file, e.g.
   `/etc/nginx/sites-available/relay.kinetra.fit` + symlink into `sites-enabled`:

   ```nginx
   server {
       listen 80;
       listen [::]:80;
       server_name relay.kinetra.fit;
       access_log off;                 # no client IPs on disk
       error_log /var/log/nginx/relay.error.log crit;
       client_max_body_size 64k;

       location ~ ^/(v1/stats|v1/bug|healthz)$ {
           proxy_pass http://127.0.0.1:4020;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;   # used in memory for rate limiting only
           proxy_read_timeout 10s;
       }
       location / { return 404; }
   }
   ```

   `sudo nginx -t && sudo systemctl reload nginx`.
5. **Certificate**: `sudo certbot --nginx -d relay.kinetra.fit` (adds the 443 block and the
   redirect to this file only). `sudo nginx -t` again.
6. **Check from your computer**: `curl -s https://relay.kinetra.fit/healthz` → `{"ok": true}`, then
   `uv run fontes report-bug --note "relay test"` and answer `y`.

## Reading what came in

```bash
ssh <your-host> "python3 ~/fontes-relay/relay.py bugs"          # last 50 bug reports
ssh <your-host> "python3 -c \"import sqlite3; c=sqlite3.connect('fontes-relay/data/relay.sqlite3'); \
  [print(*r) for r in c.execute('SELECT jurisdiction, tool, SUM(n) FROM counts GROUP BY 1,2 ORDER BY 3 DESC LIMIT 40')]\""
```

Turning it off: `ssh <your-host> "pm2 delete fontes-relay && pm2 save"`, remove the nginx file,
`sudo nginx -t && sudo systemctl reload nginx`. Clients keep working; they just stop sending.
