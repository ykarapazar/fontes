"""Health check of every Source of every adapter: reachability, robots.txt, one functional probe.

    uv run python scripts/health.py [--only tr,nl] [--json out.json] [--md docs/HEALTH.md] [--prev old.json]
                                    [--prev2 older.json]   # exit 1 only if down/blocked two runs in a row
    uv run python scripts/health.py --diff old.json new.json     # exit 1 if a source newly broke

Per source: (a) GET the source URL (status, latency, bot wall); (b) robots.txt for `*` /
Fontes must allow the source URL and every URL the probe fetched; (c) a functional probe
through the adapter's own methods: the source's `probe` (base.Source), else PROBES below,
else the adapter's `samples`. A fallback probe counts for a source only if it is the only
source of that kind, or the probe's requests reached the source's host.
Sources that need permission (unless WLM_PERMITTED) or a key this machine lacks are skipped
and never called. All requests go through _http (project User-Agent, per-host throttle).
"""
from __future__ import annotations

import argparse
import asyncio
import contextvars
import datetime
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit

import httpx
from dotenv import load_dotenv

from world_legal_mcp import _http, registry
from world_legal_mcp.base import BadRequest, NotFound, SourceError, blocked_sources, permitted_codes
from world_legal_mcp.health import (bot_wall, carry_since, classify, diff, diff_text, markdown,
                                    robots_allows, still_broken)

ROOT = Path(__file__).resolve().parents[1]
CALL_TIMEOUT = 90.0       # one adapter call, throttle waits included
REACH_TIMEOUT = 30.0
PARALLEL = 24             # adapters checked at once (hosts are still throttled one by one)

# Probes for sources that share a kind with siblings, taken from tests/live, keyed by
# (code, start of Source.name). Prefer Source.probe in the adapter; this is for adapters
# being edited elsewhere. Without decision_id/law_id the first search hit is fetched.
PROBES: dict[tuple[str, str], dict] = {
    ("tr", "Anayasa Mahkemesi"): {"caselaw_query": '"ifade özgürlüğü"', "filters": {"court": "aym_bb"}},
    ("tr", "Uyuşmazlık"): {"caselaw_query": "kamulaştırmasız el atma", "filters": {"court": "uyusmazlik"}},
    ("tr", "Sayıştay"): {"caselaw_query": "ihale", "filters": {"court": "sayistay_daire"}},
    ("tr", "Rekabet"): {"caselaw_query": "Google", "filters": {"court": "rekabet"}},
    ("tr", "Gelir İdaresi"): {"caselaw_query": "kira geliri", "filters": {"court": "gib_ozelge"}},
}

# --------------------------------------------------------------------------- #
# Record which URLs each probe call fetches (for the robots check and host attribution)
# --------------------------------------------------------------------------- #
_urls: contextvars.ContextVar[list | None] = contextvars.ContextVar("urls", default=None)
_request = _http.request


async def _recording_request(method, url, **kw):
    if (seen := _urls.get()) is not None:
        seen.append(str(url))
    return await _request(method, url, **kw)


_http.request = _recording_request


def _owner(j, s):
    """url -> does it belong to source s? Same host, or same domain when no sibling
    source of the adapter shares that domain (*.govmu.org are three different sources)."""
    host = (urlsplit(s.url).hostname or "").lower().removeprefix("www.")
    shared = any(_site(urlsplit(x.url).hostname) == _site(host) for x in j.sources if x is not s)

    def owns(url: str) -> bool:
        h = (urlsplit(url).hostname or "").lower().removeprefix("www.")
        return h == host or (not shared and _site(h) == _site(host))
    return owns


def _site(host: str) -> str:
    """Registrable-ish domain: last two labels, three under gov.xx / co.uk style suffixes."""
    parts = (host or "").lower().removeprefix("www.").split(".")
    n = 3 if len(parts) >= 3 and len(parts[-2]) <= 3 and len(parts[-1]) == 2 else 2
    return ".".join(parts[-n:])


# --------------------------------------------------------------------------- #
# robots.txt and reachability
# --------------------------------------------------------------------------- #
_robots: dict[str, asyncio.Task] = {}


async def _fetch_robots(base: str) -> tuple[str | None, str]:
    """(robots text or None when it does not bind us, note). One retry on a network error
    or 5xx, so a flaky robots.txt does not flip a source between blocked and ok."""
    for attempt in (1, 2):
        try:
            r = await asyncio.wait_for(_http.get(base + "/robots.txt", max_bytes=2**20), REACH_TIMEOUT)
        except (httpx.HTTPError, SourceError, TimeoutError) as e:
            if attempt == 2:
                return None, f"robots.txt unreadable ({type(e).__name__})"
            continue
        if r.status_code < 500:
            break
        if attempt == 2:
            return None, f"robots.txt HTTP {r.status_code}"
    if r.status_code >= 400 or "html" in r.headers.get("content-type", ""):
        return None, ""      # RFC 9309: unavailable (4xx) = no restrictions
    return r.text, ""


async def robots_check(urls: list[str]) -> tuple[list[str], list[str]]:
    """(URLs robots.txt disallows for us, notes)."""
    blocked, notes = [], []
    for url in dict.fromkeys(urls):
        u = urlsplit(url)
        base = f"{u.scheme}://{u.netloc}"
        if base not in _robots:
            _robots[base] = asyncio.ensure_future(_fetch_robots(base))
        txt, note = await _robots[base]
        if note and note not in notes:
            notes.append(note)
        if txt is not None and not robots_allows(txt, url):
            blocked.append(url)
    return blocked, notes


async def reach(url: str) -> dict:
    t0 = time.monotonic()
    try:
        r = await asyncio.wait_for(_http.get(url, max_bytes=4 * 2**20), REACH_TIMEOUT)
    except SourceError as e:
        if e.status == 413:  # bigger than we read: it answered
            return {"status": 200, "latency": time.monotonic() - t0, "error": "", "wall": ""}
        return {"status": e.status, "latency": time.monotonic() - t0, "error": str(e)[:150], "wall": ""}
    except TimeoutError:
        return {"status": None, "latency": REACH_TIMEOUT, "error": "timeout", "wall": ""}
    except httpx.HTTPError as e:
        return {"status": None, "latency": time.monotonic() - t0,
                "error": f"{type(e).__name__}: {str(e)[:120]}", "wall": ""}
    body = r.text if "text" in r.headers.get("content-type", "") or "html" in r.headers.get("content-type", "") else ""
    return {"status": r.status_code, "latency": time.monotonic() - t0, "error": "",
            "wall": bot_wall(r.status_code, dict(r.headers), body)}


# --------------------------------------------------------------------------- #
# Functional probes
# --------------------------------------------------------------------------- #
_WALL_WORDS = re.compile(r"captcha|bot wall|bot check|block page|challenge|cloudflare|access denied", re.I)
_calls: dict[tuple, asyncio.Task] = {}


def _check(method: str, res) -> tuple[str, str, str]:
    """(kind, detail, first id) for a returned record."""
    if method.startswith("search_"):
        items = getattr(res, "items", None) or []
        if not items:
            return "empty", "no hits", ""
        bad = [h for h in items if not (getattr(h, "id", "") or "").strip() or not (h.title or "").strip()]
        if bad:
            return "malformed", "hit without id/title", ""
        return "ok", f"{len(items)} hits", items[0].id
    if method == "get_legislation_toc":
        return ("ok", f"{len(res.entries)} entries", "") if res.entries else ("empty", "empty TOC", "")
    need = {"get_decision": 200, "get_legislation_provision": 20, "get_legislation_text": 1000}[method]
    text = getattr(res, "text", "") or ""
    if len(text) < need:
        return "empty", f"text only {len(text)} chars", ""
    if not (getattr(res, "url", "") or "").startswith("http"):
        return "malformed", "no url", ""
    return "ok", f"{len(text)} chars", ""


async def _call(j, method: str, args: tuple, filters: dict) -> dict:
    seen: list[str] = []
    _urls.set(seen)
    kw = {"limit": 3, "page": 1, "filters": dict(filters)} if method.startswith("search_") else {}
    t0 = time.monotonic()
    out = {"method": method, "kind": "ok", "detail": "", "first_id": "", "urls": seen}
    try:
        res = await asyncio.wait_for(getattr(j, method)(*args, **kw), CALL_TIMEOUT)
        out["kind"], out["detail"], out["first_id"] = _check(method, res)
    except (NotFound, BadRequest) as e:
        out["kind"], out["detail"] = "notfound", f"{type(e).__name__}: {str(e)[:150]}"
    except SourceError as e:
        msg = f"{str(e)[:150]}" + (f" (HTTP {e.status})" if e.status else "")
        out["kind"], out["detail"] = ("blocked" if _WALL_WORDS.search(msg) else "error"), msg
    except TimeoutError:
        out["kind"], out["detail"] = "error", f"timeout after {CALL_TIMEOUT:.0f}s"
    except httpx.HTTPError as e:
        out["kind"], out["detail"] = "error", f"{type(e).__name__}: {str(e)[:120] or 'no detail'}"
    except Exception as e:  # adapter bug or changed page layout
        out["kind"], out["detail"] = "error", f"{type(e).__name__}: {str(e)[:120]}"
    out["latency"] = time.monotonic() - t0
    return out


async def call(j, method: str, args: tuple, filters: dict | None = None) -> dict:
    """Each distinct call runs once per health run, shared by the sources that use it."""
    key = (j.code, method, args, json.dumps(filters or {}, sort_keys=True))
    if key not in _calls:
        _calls[key] = asyncio.ensure_future(_call(j, method, args, filters or {}))
    return await _calls[key]


def _kind(method: str) -> str:
    return "caselaw" if method in ("search_caselaw", "get_decision") else "legislation"


def _plan(j, kind: str, spec: dict) -> list[tuple[str, tuple]]:
    """[(method, args)] for one kind; ('get_decision', ()) means: the first search hit."""
    out = []
    if kind == "caselaw":
        if j.supports("search_caselaw") and spec.get("caselaw_query"):
            out.append(("search_caselaw", (spec["caselaw_query"],)))
        if j.supports("get_decision") and (spec.get("decision_id") or out):
            out.append(("get_decision", (spec["decision_id"],) if spec.get("decision_id") else ()))
        return out
    if j.supports("search_legislation") and spec.get("legislation_query"):
        out.append(("search_legislation", (spec["legislation_query"],)))
    law = spec.get("law_id")
    for m in ("get_legislation_provision", "get_legislation_text", "get_legislation_toc"):
        if j.supports(m) and (law or out) and (m != "get_legislation_provision" or spec.get("provision")):
            out.append((m, ((law, spec["provision"]) if m == "get_legislation_provision" else (law,)) if law else ()))
            break
    return out


async def probe(j, kinds: tuple[str, ...], spec: dict, filters: dict) -> tuple[list[dict], list[str]]:
    calls, notes = [], []
    for kind in kinds:
        first = ""
        for method, args in _plan(j, kind, spec):
            if blocked_sources(j, method):
                notes.append(f"{method} not called: a source behind it needs permission")
                continue
            if not args:
                if not first:
                    continue
                args = (first,)
            c = await call(j, method, args, filters if method.startswith("search_") else None)
            first = first or c["first_id"]
            calls.append(c)
    return calls, notes


# --------------------------------------------------------------------------- #
# One source
# --------------------------------------------------------------------------- #
def skip_reason(j, s) -> str:
    if s.needs_permission and j.code not in permitted_codes():
        return "skipped (permission): needs WLM_PERMITTED"
    if "paid" in s.auth.lower():
        return "skipped (key): paid access"
    keys = re.findall(r"WLM_[A-Z0-9_]+_KEY", s.auth)
    if keys and "fall" not in s.auth.lower() and not all(os.environ.get(k) for k in keys):
        return f"skipped (key): {', '.join(keys)} not set"
    return ""


async def check_source(j, s, now: str) -> dict:
    row = {"jurisdiction": j.code, "source": s.name, "url": s.url, "status": "skipped", "detail": "",
           "latency": None, "http_status": None, "probe": "", "checked_at": now,
           "fontes_version": _http._VER}
    if reason := skip_reason(j, s):
        row["detail"] = reason
        return row
    kinds = tuple(k for k in ("caselaw", "legislation") if k in s.covers)
    spec = s.probe or next((p for (c, pre), p in PROBES.items() if c == j.code and s.name.startswith(pre)), {})
    specific = bool(spec)
    calls, notes = await probe(j, kinds, spec or j.samples, spec.get("filters", {}))
    alone = {k: sum(k in x.covers for x in j.sources) == 1 for k in kinds}
    owns = _owner(j, s)
    if not specific:  # adapter samples: keep only calls that reached this source
        calls = [c for c in calls if alone[_kind(c["method"])] or any(owns(u) for u in c["urls"])]
    row["probe"] = "specific" if specific else "adapter" if calls else "url"
    # The source URL is only a landing page: robots.txt there decides whether we GET it,
    # not the status. The status counts the URLs the probe used for this source.
    landing_off, rnotes = await robots_check([s.url])
    r = await reach(s.url) if not landing_off else {"status": None, "latency": None, "error": "", "wall": ""}
    used = [u for c in calls for u in c["urls"] if specific or alone[_kind(c["method"])] or owns(u)]
    blocked, rnotes2 = await robots_check(used)
    status, detail = classify(robots_blocked=blocked, reach=r, calls=calls)
    if landing_off:
        notes.append("source URL disallowed by robots.txt, not fetched")
    extra = list(dict.fromkeys(n for n in notes + rnotes + rnotes2 if n))
    row.update(status=status, detail="; ".join([detail, *extra]), http_status=r.get("status"),
               latency=round(max([r.get("latency") or 0] + [c["latency"] for c in calls]), 2),
               calls=[{k: c[k] for k in ("method", "kind", "detail")} | {"latency": round(c["latency"], 2)}
                      for c in calls])
    return row


async def run(adapters) -> dict:
    now = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")
    gate = asyncio.Semaphore(PARALLEL)
    done = 0

    async def one(j):
        nonlocal done
        async with gate:
            rows = await asyncio.gather(*(check_source(j, s, now) for s in j.sources))
        done += 1
        print(f"[{done}/{len(adapters)}] {j.code}: " + ", ".join(r["status"] for r in rows),
              file=sys.stderr, flush=True)
        return rows

    results = [r for rows in await asyncio.gather(*(one(j) for j in adapters)) for r in rows]
    return {"checked_at": now, "fontes_version": _http._VER, "results": results}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="health", description=__doc__.split("\n\n")[0])
    p.add_argument("--only", metavar="CODES", help="comma-separated jurisdiction codes")
    p.add_argument("--json", metavar="PATH", help="write the report here")
    p.add_argument("--md", metavar="PATH", help="write the markdown table here (e.g. docs/HEALTH.md)")
    p.add_argument("--prev", metavar="PATH", help="previous report: carry `since` dates and print a diff")
    p.add_argument("--prev2", metavar="PATH",
                   help="report before --prev: then exit 1 only for sources down/blocked in both of the last two runs")
    p.add_argument("--diff", nargs=2, metavar=("OLD", "NEW"), help="only compare two reports")
    a = p.parse_args(argv)
    if a.diff:
        d = diff(*(json.loads(Path(x).read_text()) for x in a.diff))
        print(diff_text(d))
        return 1 if d["newly_broken"] else 0
    load_dotenv(ROOT / ".env")   # same keys as the server; values are never printed
    registry.discover()
    adapters = [j for j in registry.available() if not getattr(j, "via_lexifina", False)]
    if a.only:
        want = {registry.canonical(c) for c in a.only.split(",") if c.strip()}
        adapters = [j for j in adapters if j.code in want]
    t0 = time.monotonic()
    report = asyncio.run(run(adapters))
    old = json.loads(Path(a.prev).read_text()) if a.prev else None
    carry_since(old, report)
    report["duration_s"] = round(time.monotonic() - t0)
    if a.json:
        Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        Path(a.json).write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n")
    if a.md:
        Path(a.md).write_text(markdown(report))
    counts = {s: sum(r["status"] == s for r in report["results"]) for s in
              ("ok", "degraded", "down", "blocked", "skipped")}
    print(f"{len(report['results'])} sources in {report['duration_s']}s: {counts}")
    for r in report["results"]:
        if r["status"] in ("down", "blocked", "degraded"):
            print(f"  {r['status']:8} {r['jurisdiction']:5} {r['source'][:60]}: {r['detail'][:160]}")
    if old:
        d = diff(old, report)
        print(diff_text(d))
        if not a.prev2:
            return 1 if d["newly_broken"] else 0
        alert = still_broken(json.loads(Path(a.prev2).read_text()), old, report)
        print(f"Down/blocked two runs in a row (alert): {len(alert)}")
        for r in alert:
            print(f"  {r['jurisdiction']} | {r['source']}: {r['was']} -> {r['now']} ({r['detail']})")
        return 1 if alert else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
