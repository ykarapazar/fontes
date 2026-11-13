"""Source health: the offline logic behind scripts/health.py, and the optional runtime notice.

* `robots_allows` evaluates robots.txt the way RFC 9309 says, for our own product token
  "Fontes": a group naming Fontes binds us; otherwise the `*` group does. Groups naming
  only other crawlers (ClaudeBot, GPTBot, ...) do not.
* `bot_wall` spots a challenge / block page (Cloudflare, Akamai, Imperva, ...).
* `classify` turns one source's checks into ok / degraded / down / blocked.
* `diff` and `carry_since` compare two health reports; `markdown` renders docs/HEALTH.md.
* `notices` is what list_jurisdictions shows: off unless WLM_HEALTH names a health JSON
  (a local path or an https URL). Nothing is read until list_jurisdictions is called.
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from urllib.parse import urlsplit

STATUSES = ("ok", "degraded", "down", "blocked", "skipped")
BROKEN = {"down", "blocked"}
SLOW = 30.0                # seconds; a call slower than this makes a source "degraded"
TOKEN = "fontes"           # our robots.txt product token (see _http.UA)


# --------------------------------------------------------------------------- #
# robots.txt
# --------------------------------------------------------------------------- #
def parse_robots(txt: str) -> list[tuple[set[str], list[tuple[bool, str]]]]:
    """robots.txt -> [(agents, [(allow, pattern), ...]), ...]. Consecutive User-agent
    lines share one group; any other line ends the run of agents."""
    groups: list[tuple[set[str], list[tuple[bool, str]]]] = []
    in_agents = False
    for line in txt.splitlines():
        line = line.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        key, val = (x.strip() for x in line.split(":", 1))
        key = key.lower()
        if key == "user-agent":
            if not in_agents:
                groups.append((set(), []))
            groups[-1][0].add(val.lower())
            in_agents = True
            continue
        in_agents = False
        if key in ("allow", "disallow") and groups and val:
            groups[-1][1].append((key == "allow", val))
    return groups


def _matches(pattern: str, path: str) -> bool:
    rx = re.escape(pattern).replace(r"\*", ".*")
    if rx.endswith(r"\$"):
        rx = rx[:-2] + "$"
    return re.match(rx, path) is not None


def robots_allows(txt: str, url: str) -> bool:
    """May Fontes fetch url under this robots.txt? Longest match wins; Allow wins a tie."""
    groups = parse_robots(txt)
    ours = [r for agents, r in groups if any(a.split("/")[0] == TOKEN for a in agents)]
    rules = [x for r in (ours or [r for agents, r in groups if "*" in agents]) for x in r]
    u = urlsplit(url)
    path = (u.path or "/") + (f"?{u.query}" if u.query else "")
    best = (-1, True)
    for allow, pattern in rules:
        if _matches(pattern, path):
            best = max(best, (len(pattern), allow))
    return best[1]


# --------------------------------------------------------------------------- #
# Bot walls
# --------------------------------------------------------------------------- #
_WALLS = (
    ("cloudflare challenge", r"cf-chl|challenge-platform|<title>just a moment"),
    ("captcha", r"captcha"),
    ("imperva/incapsula", r"incapsula|_incapsula_resource|pardon our interruption"),
    ("akamai", r"access denied.{0,400}reference #"),
    ("ddos-guard", r"ddos-guard"),
    ("sucuri", r"sucuri website firewall"),
    ("aws waf", r"awswaf|aws-waf-token"),
)


def bot_wall(status: int, headers: dict, body: str) -> str:
    """Name of the bot wall a response shows, or ''."""
    h = {k.lower(): str(v).lower() for k, v in (headers or {}).items()}
    if h.get("cf-mitigated") == "challenge":
        return "cloudflare challenge"
    if status not in (200, 202, 403, 405, 429, 503):
        return ""
    low = (body or "")[:20000].lower()
    for name, rx in _WALLS:
        if re.search(rx, low, re.S):
            # A normal 200 page may mention "captcha" in a form; only count it on an error
            # status or a tiny page that is nothing but the challenge.
            if status == 200 and len(low) > 15000:
                continue
            return name
    return ""


# --------------------------------------------------------------------------- #
# Status of one source
# --------------------------------------------------------------------------- #
def classify(*, robots_blocked: list[str], reach: dict, calls: list[dict]) -> tuple[str, str]:
    """robots_blocked: URLs robots.txt disallows for us. reach: {status, error, wall, latency}
    for the source's own URL. calls: functional probes, each {method, kind, detail, latency}
    with kind ok | empty | malformed | notfound | error | blocked. -> (status, detail)."""
    if robots_blocked:
        more = f" (+{len(robots_blocked) - 1} more)" if len(robots_blocked) > 1 else ""
        return "blocked", f"robots.txt disallows {robots_blocked[0]}{more}"
    ok = [c for c in calls if c["kind"] == "ok"]
    walled = [c for c in calls if c["kind"] == "blocked"]
    if walled and not ok:
        return "blocked", f"{walled[0]['method']}: {walled[0]['detail']}"
    if reach.get("wall") and not ok:
        return "blocked", f"bot wall on source URL ({reach['wall']}, HTTP {reach.get('status')})"
    reach_bad = reach.get("error") or (reach.get("status") or 0) >= 400
    reach_note = f"source URL: {reach.get('error') or 'HTTP ' + str(reach.get('status'))}"
    if calls:
        failed = [c for c in calls if c["kind"] != "ok"]
        if not ok:
            hard = [c for c in failed if c["kind"] == "error"]
            c = (hard or failed)[0]
            return ("down" if hard else "degraded"), f"{c['method']}: {c['kind']}: {c['detail']}"
        if failed:
            c = failed[0]
            return "degraded", f"partial: {c['method']}: {c['kind']}: {c['detail']}"
        slow = [c for c in calls if c["latency"] > SLOW]
        if slow:
            return "degraded", f"slow: {slow[0]['method']} took {slow[0]['latency']:.0f}s"
        if reach_bad:
            return "degraded", f"probes ok, but {reach_note}"
        return "ok", "probes ok: " + ", ".join(c["method"] for c in calls)
    if reach_bad:
        return "down", reach_note
    if (reach.get("latency") or 0) > SLOW:
        return "degraded", f"slow: source URL took {reach['latency']:.0f}s"
    return "ok", "source URL reachable (no functional probe reaches this source)"


# --------------------------------------------------------------------------- #
# Reports: since-dates, diff, markdown
# --------------------------------------------------------------------------- #
def _key(r: dict) -> tuple[str, str]:
    return r["jurisdiction"], r["source"]


def carry_since(old: dict | None, new: dict) -> dict:
    """Set each result's `since`: kept from the old report while the status is unchanged."""
    prev = {_key(r): r for r in (old or {}).get("results", [])}
    for r in new["results"]:
        o = prev.get(_key(r))
        r["since"] = (o.get("since") or o["checked_at"]) if o and o["status"] == r["status"] else r["checked_at"]
    return new


def diff(old: dict, new: dict) -> dict[str, list[dict]]:
    """What a daily job alerts on: newly broken (down/blocked) and recovered sources."""
    prev = {_key(r): r for r in old.get("results", [])}
    out: dict[str, list[dict]] = {"newly_broken": [], "recovered": [], "changed": []}
    for r in new["results"]:
        was = prev.get(_key(r), {}).get("status", "")
        if was == r["status"]:
            continue
        row = {"jurisdiction": r["jurisdiction"], "source": r["source"], "was": was or "(new)",
               "now": r["status"], "detail": r["detail"]}
        if r["status"] in BROKEN and was not in BROKEN:
            out["newly_broken"].append(row)
        elif was in BROKEN and r["status"] not in BROKEN:
            out["recovered"].append(row)
        else:
            out["changed"].append(row)
    return out


def diff_text(d: dict[str, list[dict]]) -> str:
    lines = []
    for label, rows in (("Newly down/blocked", d["newly_broken"]), ("Recovered", d["recovered"]),
                        ("Other changes", d["changed"])):
        lines.append(f"{label}: {len(rows)}")
        lines += [f"  {r['jurisdiction']} | {r['source']}: {r['was']} -> {r['now']} ({r['detail']})"
                  for r in rows]
    return "\n".join(lines)


def _cell(s: str) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def markdown(report: dict) -> str:
    rs = report["results"]
    counts = ", ".join(f"{s} {sum(r['status'] == s for r in rs)}" for s in STATUSES)
    lines = [
        "# Source health",
        "",
        f"Generated by `scripts/health.py` on {report['checked_at'][:16].replace('T', ' ')} UTC, "
        f"Fontes {report['fontes_version']}. {len(rs)} sources: {counts}.",
        "",
        "Probe: `specific` = the source's own probe; `adapter` = the adapter's samples, which "
        "reached this source; `url` = only the source URL and robots.txt were checked.",
        "",
        "| Code | Source | Status | Since | Latency | Probe | Detail |",
        "|---|---|---|---|---|---|---|",
    ]
    order = {s: i for i, s in enumerate(("blocked", "down", "degraded", "skipped", "ok"))}
    for r in sorted(rs, key=lambda r: (order[r["status"]], r["jurisdiction"], r["source"])):
        lat = f"{r['latency']:.1f}s" if r.get("latency") is not None else ""
        lines.append(f"| {r['jurisdiction']} | {_cell(r['source'][:70])} | {r['status']} | "
                     f"{(r.get('since') or '')[:10]} | {lat} | {r.get('probe', '')} | {_cell(r['detail'][:160])} |")
    lines += [
        "",
        "## Where this runs",
        "",
        "GitHub (`.github/workflows/health.yml`, daily 05:17 UTC) is the canonical run: it commits "
        "`research/health/<date>.json`, this file and `docs/status/index.html` (the status page; "
        "GitHub Pages serves it at `/status/` once the repo is public).",
        "",
        "`scripts/health_daily.sh` runs daily on a maintainer's machine: it probes every source, keeps a "
        "timestamped report in `research/health/` (not committed), writes `status/HEALTH.md`, copies "
        "GitHub's status page from `origin/main` to `status/index.html` (or builds one from the local "
        "reports until GitHub has published), and shows a notification when a source changes status.",
        "",
        "```sh",
        "# install (daily 09:00, log: ~/Library/Logs/fontes-health.log)",
        "cp scripts/launchd/io.github.ykarapazar.fontes-health.plist ~/Library/LaunchAgents/",
        "launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/io.github.ykarapazar.fontes-health.plist",
        "launchctl kickstart gui/$(id -u)/io.github.ykarapazar.fontes-health   # optional: run once now",
        "# uninstall",
        "launchctl bootout gui/$(id -u)/io.github.ykarapazar.fontes-health",
        "rm ~/Library/LaunchAgents/io.github.ykarapazar.fontes-health.plist",
        "```",
    ]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- #
# Runtime: known-broken sources for list_jurisdictions (off unless WLM_HEALTH is set)
# --------------------------------------------------------------------------- #
REFRESH = 6 * 3600
_loaded: tuple[float, dict[tuple[str, str], str]] = (0.0, {})


async def notices() -> dict[tuple[str, str], str]:
    """(code, source name) -> 'down since 2026-11-10: <detail>' for broken sources in the
    health JSON named by WLM_HEALTH (path or https URL). {} when unset or unreadable."""
    global _loaded
    where = os.environ.get("WLM_HEALTH", "").strip()
    if not where:
        return {}
    if _loaded[0] and time.monotonic() - _loaded[0] < REFRESH:
        return _loaded[1]
    out: dict[tuple[str, str], str] = {}
    try:
        if where.startswith(("https://", "http://")):
            from . import _http
            r = await _http.get(where, max_bytes=5 * 2**20)
            r.raise_for_status()
            data = r.json()
        else:
            data = json.loads(Path(where).expanduser().read_text())
        for r in data.get("results", []):
            # Shown to users: outages and bot walls. A robots.txt conflict is the
            # maintainer's problem (the source still answers), so it is not shown.
            if r.get("status") == "down" or (r.get("status") == "blocked"
                                             and not r.get("detail", "").startswith("robots.txt")):
                since = (r.get("since") or r.get("checked_at") or "")[:10]
                out[(r["jurisdiction"], r["source"])] = (
                    f"health check: {r['status']} since {since} "
                    f"(last checked {r.get('checked_at', '')[:10]}): {r.get('detail', '')}")
    except Exception:
        pass  # a missing or bad health file must never break list_jurisdictions
    _loaded = (time.monotonic(), out)
    return out
