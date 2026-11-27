"""Offline tests for scripts/status_page.py on a fixture history."""
import datetime as dt
import importlib.util
import json
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "status_page", Path(__file__).resolve().parents[1] / "scripts" / "status_page.py")
sp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sp)

NOW = dt.datetime(2026, 11, 10, 12, 0, tzinfo=dt.UTC)


def _rep(when, **statuses):
    return {"checked_at": when, "fontes_version": "t", "results": [
        {"jurisdiction": k, "source": f"{k} src", "status": s, "detail": f"{k} {s}",
         "latency": 1.0, "checked_at": when} for k, s in statuses.items()]}


HISTORY = [
    _rep("2026-10-01T09:00:00+00:00", nl="down", tr="ok"),        # outside 30 days
    _rep("2026-11-01T09:00:00+00:00", nl="ok", tr="ok"),
    _rep("2026-11-05T09:00:00+00:00", nl="ok", tr="down"),
    _rep("2026-11-06T09:00:00+00:00", nl="degraded", tr="blocked"),
    _rep("2026-11-07T09:00:00+00:00", nl="ok", tr="ok"),
    _rep("2026-11-09T09:00:00+00:00", nl="skipped", tr="down"),
    _rep("2026-11-09T15:00:00+00:00", nl="ok", tr="down"),        # second run the same day
]


def test_uptime_counts_runs_and_skips_skipped():
    s = sp.series(HISTORY)
    assert sp.uptime(s[("nl", "nl src")], NOW, 30) == 100.0       # degraded counts as up
    assert sp.uptime(s[("nl", "nl src")], NOW, 60) == 100.0 * 5 / 6
    assert sp.uptime(s[("tr", "tr src")], NOW, 7) == 20.0            # 1 up of 5 since Nov 3
    assert sp.uptime([], NOW, 7) is None


def test_strip_worst_per_day():
    bars = sp.strip(sp.series(HISTORY)[("tr", "tr src")], NOW)
    assert len(bars) == 30 and bars[-1] == "" and bars[-2] == "down"
    assert bars[-5] == "blocked" and bars[-6] == "down" and bars[-8] == ""   # Nov 6, Nov 5, Nov 3
    assert sp.strip(sp.series(HISTORY)[("nl", "nl src")], NOW)[-2] == "ok"   # skipped ignored


def test_incidents_start_end_and_escalation():
    inc = sp.incidents(sp.series(HISTORY))
    tr = [i for i in inc if i["jurisdiction"] == "tr"]
    assert [(i["start"][:10], (i["end"] or "")[:10], i["status"]) for i in tr] == [
        ("2026-11-09", "", "down"), ("2026-11-05", "2026-11-07", "down")]   # keeps the worst
    nl = [(i["start"][:10], i["end"][:10]) for i in inc if i["jurisdiction"] == "nl"]
    assert nl == [("2026-11-06", "2026-11-07"), ("2026-10-01", "2026-11-01")]
    assert inc[0]["start"] >= inc[-1]["start"]                      # newest first


def test_render_and_load(tmp_path):
    for i, r in enumerate(HISTORY):
        (tmp_path / f"{i}.json").write_text(json.dumps(r))
    (tmp_path / "junk.json").write_text("{")
    reports = sp.load(tmp_path)
    assert len(reports) == len(HISTORY)
    page = sp.render(reports, NOW)
    assert "1 source down or blocked" in page and "tr src" in page
    fetched = page.replace(f"<link rel=canonical href='{sp.i18n_docs.SITE}status/'>", "")  # a canonical is not a request
    assert "http://" not in fetched and "https://" not in fetched and " src=" not in fetched  # one file, no requests
    assert "prefers-color-scheme:dark" in page
    assert "All sources operational" in sp.render([_rep("2026-11-10T09:00:00+00:00", nl="ok")], NOW)
