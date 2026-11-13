"""Offline tests for the health logic: robots.txt evaluation, bot walls, status, diff, notices."""
import json

from world_legal_mcp import health, registry, server
from world_legal_mcp.base import Source

ROBOTS = """
User-agent: GPTBot
User-agent: ClaudeBot
Disallow: /

User-agent: *
Crawl-delay: 5
Disallow: /search
Allow: /search/public$
Disallow: /*.pdf$
"""


def test_robots_star_rules_bind_named_ai_bots_do_not():
    assert health.robots_allows(ROBOTS, "https://x.example/laws/1")
    assert not health.robots_allows(ROBOTS, "https://x.example/search?q=a")
    assert health.robots_allows(ROBOTS, "https://x.example/search/public")      # longer Allow wins
    assert not health.robots_allows(ROBOTS, "https://x.example/a/b.pdf")
    assert health.robots_allows(ROBOTS, "https://x.example/a/b.pdf?x=1")       # $ anchors the end


def test_robots_fontes_group_replaces_star():
    txt = "User-agent: *\nDisallow: /\n\nUser-agent: Fontes\nDisallow: /private\n"
    assert health.robots_allows(txt, "https://x.example/laws")
    assert not health.robots_allows(txt, "https://x.example/private/1")
    assert not health.robots_allows("User-agent: *\nDisallow: /\n", "https://x.example/")
    assert health.robots_allows("User-agent: *\nDisallow:\n", "https://x.example/")
    assert health.robots_allows("", "https://x.example/anything")


def test_bot_wall():
    assert health.bot_wall(403, {"cf-mitigated": "challenge"}, "") == "cloudflare challenge"
    assert health.bot_wall(403, {}, "<html><title>Just a moment...</title>") == "cloudflare challenge"
    assert health.bot_wall(200, {}, "<p>Request unsuccessful. Incapsula incident ID</p>") == "imperva/incapsula"
    assert health.bot_wall(404, {}, "captcha") == ""
    assert health.bot_wall(200, {}, "<form>captcha</form>" + "x" * 20000) == ""   # a big real page


def _c(kind, method="search_caselaw", latency=1.0, detail="d"):
    return {"method": method, "kind": kind, "detail": detail, "latency": latency}


OK_REACH = {"status": 200, "latency": 0.5, "error": "", "wall": ""}


def test_classify():
    cl = health.classify
    assert cl(robots_blocked=[], reach=OK_REACH, calls=[_c("ok"), _c("ok", "get_decision")])[0] == "ok"
    assert cl(robots_blocked=["https://x/s"], reach=OK_REACH, calls=[_c("ok")])[0] == "blocked"
    assert cl(robots_blocked=[], reach=OK_REACH, calls=[_c("error")])[0] == "down"
    assert cl(robots_blocked=[], reach=OK_REACH, calls=[_c("empty")])[0] == "degraded"
    assert cl(robots_blocked=[], reach=OK_REACH, calls=[_c("ok"), _c("error", "get_decision")]) [0] == "degraded"
    assert cl(robots_blocked=[], reach=OK_REACH, calls=[_c("ok", latency=45)])[1].startswith("slow")
    assert cl(robots_blocked=[], reach=OK_REACH, calls=[_c("blocked")])[0] == "blocked"
    walled = dict(OK_REACH, status=403, wall="captcha")
    assert cl(robots_blocked=[], reach=walled, calls=[])[0] == "blocked"
    assert cl(robots_blocked=[], reach=walled, calls=[_c("ok")])[0] == "degraded"    # API still works
    assert cl(robots_blocked=[], reach={"status": None, "error": "timeout"}, calls=[])[0] == "down"
    assert cl(robots_blocked=[], reach=OK_REACH, calls=[])[0] == "ok"


def _report(when, *rows):
    return {"checked_at": when, "fontes_version": "t", "results": [
        {"jurisdiction": c, "source": s, "status": st, "detail": d, "checked_at": when}
        for c, s, st, d in rows]}


def test_diff_and_since():
    old = health.carry_since(None, _report("2026-11-01T00:00:00", ("nl", "A", "ok", ""),
                                           ("tr", "B", "down", "x"), ("at", "C", "down", "y")))
    new = health.carry_since(old, _report("2026-11-02T00:00:00", ("nl", "A", "down", "timeout"),
                                          ("tr", "B", "ok", ""), ("at", "C", "down", "y")))
    d = health.diff(old, new)
    assert [r["jurisdiction"] for r in d["newly_broken"]] == ["nl"]
    assert [r["jurisdiction"] for r in d["recovered"]] == ["tr"]
    since = {r["jurisdiction"]: r["since"] for r in new["results"]}
    assert since == {"nl": "2026-11-02T00:00:00", "tr": "2026-11-02T00:00:00", "at": "2026-11-01T00:00:00"}
    assert "nl | A: ok -> down" in health.diff_text(d)
    assert "| at | C | down | 2026-11-01 |" in health.markdown(new)


async def test_list_jurisdictions_shows_known_down(tmp_path, monkeypatch):
    registry.discover()
    j = registry.get("gb")
    rep = _report("2026-11-09T06:00:00", ("gb", j.sources[0].name, "down", "timeout"),
                  ("gb", j.sources[-1].name, "blocked", "robots.txt disallows https://x/"))
    p = tmp_path / "h.json"
    p.write_text(json.dumps(health.carry_since(None, rep)))
    monkeypatch.setenv("WLM_HEALTH", str(p))
    monkeypatch.setattr(health, "_loaded", (0.0, {}))
    out = await server.list_jurisdictions("gb")
    assert "health check: down since 2026-11-09" in out
    assert "health check: blocked" not in out                 # robots conflicts are maintainer-only
    monkeypatch.delenv("WLM_HEALTH")
    monkeypatch.setattr(health, "_loaded", (0.0, {}))
    assert "health check" not in await server.list_jurisdictions("gb")


def test_source_probe_field_is_optional_and_hashable():
    s = Source("X", "https://x.example", covers=("caselaw",), probe={"caselaw_query": "a"})
    assert s.probe["caselaw_query"] == "a" and Source("Y", "https://y").probe == {}
    hash(s)
