"""Static status page from the health history: one self-contained HTML file, no external requests.

    uv run python scripts/status_page.py [--history research/health] [--out status/index.html]

Reads every health report (scripts/health.py --json) in --history. Per source: current
status, last checked, 7- and 30-day uptime, a 30-day bar strip (worst status per day) and
the last error; plus an incidents list (status changes, with start and end).
Uptime counts runs: ok/degraded = up, down/blocked = down; skipped runs are left out.

One page for every language: strings from docs/i18n/*/strings.json are embedded and an inline
script picks the reader's language (?lang=<code>, then their last choice, then the browser's
languages), with a switcher. Without JavaScript the page is English.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "installer"))
import fontes_i18n  # noqa: E402
import i18n_docs  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
UP = {"ok", "degraded"}
RANK = {"ok": 0, "skipped": 0, "degraded": 1, "blocked": 2, "down": 3}
# status -> key in docs/i18n/<lang>/strings.json
LABEL = {"ok": "status_ok", "degraded": "status_degraded", "down": "status_down", "blocked": "status_blocked",
         "skipped": "status_skipped", "": "status_no_data"}


def load(folder: Path) -> list[dict]:
    """All reports, oldest first."""
    reports = []
    for p in folder.glob("*.json"):
        try:
            r = json.loads(p.read_text())
        except (OSError, ValueError):
            continue
        if "results" in r and "checked_at" in r:
            reports.append(r)
    return sorted(reports, key=lambda r: r["checked_at"])


def _ts(s: str) -> dt.datetime:
    t = dt.datetime.fromisoformat(s)
    return t if t.tzinfo else t.replace(tzinfo=dt.UTC)


def series(reports: list[dict]) -> dict[tuple[str, str], list[dict]]:
    """(code, source) -> that source's results, oldest first."""
    out: dict[tuple[str, str], list[dict]] = {}
    for rep in reports:
        for r in rep["results"]:
            out.setdefault((r["jurisdiction"], r["source"]), []).append(
                dict(r, checked_at=r.get("checked_at") or rep["checked_at"]))
    return out


def uptime(runs: list[dict], now: dt.datetime, days: int) -> float | None:
    """Share of non-skipped runs in the last `days` days that were up; None without data."""
    since = now - dt.timedelta(days=days)
    rs = [r for r in runs if r["status"] != "skipped" and _ts(r["checked_at"]) >= since]
    return None if not rs else 100.0 * sum(r["status"] in UP for r in rs) / len(rs)


def strip(runs: list[dict], now: dt.datetime, days: int = 30) -> list[str]:
    """Worst status per UTC day, oldest first; '' for a day without a run."""
    worst: dict[dt.date, str] = {}
    for r in runs:
        d = _ts(r["checked_at"]).date()
        if r["status"] != "skipped" and RANK[r["status"]] >= RANK.get(worst.get(d, "ok"), 0):
            worst[d] = r["status"]
    today = now.date()
    return [worst.get(today - dt.timedelta(days=i), "") for i in range(days - 1, -1, -1)]


def incidents(runs_by_source: dict[tuple[str, str], list[dict]]) -> list[dict]:
    """Each stretch of runs where a source was not ok: start = first such run, end = the
    first ok run after it (None while open). Newest first."""
    out = []
    for (code, source), runs in runs_by_source.items():
        cur = None
        for r in runs:
            if r["status"] == "skipped":
                continue
            if r["status"] != "ok":
                if cur is None:
                    cur = {"jurisdiction": code, "source": source, "status": r["status"],
                           "start": r["checked_at"], "end": None, "detail": r.get("detail", "")}
                    out.append(cur)
                elif RANK[r["status"]] > RANK[cur["status"]]:
                    cur["status"], cur["detail"] = r["status"], r.get("detail", "")
            elif cur is not None:
                cur["end"], cur = r["checked_at"], None
    return sorted(out, key=lambda i: i["start"], reverse=True)


# --------------------------------------------------------------------------- #
# HTML
# --------------------------------------------------------------------------- #
CSS = """
:root{--bg:#fff;--fg:#1a1a1a;--mute:#6b6b6b;--line:#e5e5e5;--card:#fafafa;
--ok:#2e9e5b;--degraded:#d9a21b;--down:#d64545;--blocked:#8a4fd1;--skipped:#9e9e9e;--none:#e2e2e2}
@media (prefers-color-scheme:dark){:root{--bg:#141414;--fg:#ececec;--mute:#9a9a9a;--line:#2c2c2c;
--card:#1c1c1c;--none:#333}}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,-apple-system,sans-serif}
main{max-width:1000px;margin:0 auto;padding:24px 16px}
h1{font-size:22px;margin:0 0 4px}h2{font-size:17px;margin:28px 0 8px}
.mute{color:var(--mute)}.banner{padding:14px 16px;border-radius:8px;color:#fff;font-weight:600;margin:16px 0}
details{border:1px solid var(--line);border-radius:8px;margin:6px 0;background:var(--card)}
summary{padding:8px 12px;cursor:pointer;display:flex;gap:10px;align-items:center}
.row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:4px 12px;padding:8px 12px;border-top:1px solid var(--line)}
.dot{display:inline-block;width:10px;height:10px;border-radius:50%;flex:none}
.bars{display:flex;gap:2px;margin-top:4px}.bars i{flex:1;max-width:10px;height:18px;border-radius:2px}
.err{color:var(--mute);font-size:12px;word-break:break-word}
table{border-collapse:collapse;width:100%;font-size:13px}td,th{text-align:left;padding:6px;border-bottom:1px solid var(--line);vertical-align:top}
.ok{background:var(--ok)}.degraded{background:var(--degraded)}.down{background:var(--down)}
.blocked{background:var(--blocked)}.skipped{background:var(--skipped)}.none{background:var(--none)}
"""


def _e(s) -> str:
    return html.escape(str(s or ""))


def _pct(x: float | None) -> str:
    return "–" if x is None else f"{x:.1f}%"


def _strings() -> dict[str, dict[str, str]]:
    """lang -> the page's strings (status_*, doc_notice, doc_languages) for English and every
    translation; a key a translation lacks is left out (the page falls back to English)."""
    keep = lambda k: k.startswith("status_") or k in ("doc_notice", "doc_languages")  # noqa: E731
    en = i18n_docs.labels("en")
    out = {"en": {k: v for k, v in en.items() if keep(k)}}
    for lang in i18n_docs.translations():
        t = i18n_docs._table(lang)
        out[lang] = {k: v for k, v in t.items() if keep(k) and k in en and isinstance(v, str)}
    return out


def _arg(s: dict[str, str], v) -> str:
    """A format argument: plain, or {'p': key, 'n': n} for a plural phrase."""
    return i18n_docs.plural(s, v["p"], v["n"]) if isinstance(v, dict) else str(v)


# Language choice in the browser: ?lang=, then the saved choice, then navigator.languages, each
# with the installer's fallback chain (installer/fontes_i18n.py: chain), then English.
JS = """
(function(){
var S=%(strings)s,R=%(rtl)s,N=%(names)s,Z=%(script)s,G=%(legacy)s;
function chain(t){t=String(t||'').split('.')[0].split('@')[0].replace(/_/g,'-').trim();if(!t)return[];
var p=t.split('-'),o=[];p[0]=p[0].toLowerCase();p[0]=G[p[0]]||p[0];
for(var n=p.length;n>0;n--){o.push(p.slice(0,n).join('-'));
if(n==2&&p[0]=='pt'&&p[1].length==2&&!/^(br|pt)$/i.test(p[1]))o.push('pt-PT');
if(n<=2&&!p.slice(1,n).some(function(x){return x.length==4})){var sc=Z[p.slice(0,n).join('-').toLowerCase()];if(sc)o.push(p[0]+'-'+sc)}}
return o}
function pick(prefs){var h={};for(var c in S)h[c.toLowerCase()]=c;
for(var i=0;i<prefs.length;i++){var ch=chain(prefs[i]);for(var j=0;j<ch.length;j++)if(h[ch[j].toLowerCase()])return h[ch[j].toLowerCase()]}return 'en'}
var L;function g(k){return(S[L]&&S[L][k])||S.en[k]||''}
function v(x){return x&&typeof x=='object'?f(g(x.p+(x.n==1?'_one':'_other')),{n:x.n}):x}
function f(s,a){return s.replace(/\\{(\\w+)\\}/g,function(m,k){return k in a?v(a[k]):m})}
function apply(lang){L=lang;var d=document.documentElement;d.lang=lang;d.dir=R.indexOf(lang)>=0?'rtl':'ltr';
document.title=g('status_title');
var es=document.querySelectorAll('[data-i],[data-p]');for(var i=0;i<es.length;i++){var e=es[i],a=JSON.parse(e.dataset.a||'{}'),
t=e.dataset.p?v({p:e.dataset.p,n:a.n}):f(g(e.dataset.i),a);
if(e.dataset.l)t=t.toLowerCase();e.textContent=t}
es=document.querySelectorAll('.bars i.none');for(i=0;i<es.length;i++)es[i].title=g('status_no_run');
document.getElementById('notice').hidden=lang=='en';document.getElementById('langs').value=lang}
var prefs=[];try{prefs.push(new URLSearchParams(location.search).get('lang')||'')}catch(e){}
try{prefs.push(localStorage.getItem('fontes-lang')||'')}catch(e){}
prefs=prefs.concat(navigator.languages||[navigator.language||'']);
var sel=document.getElementById('langs');var cs=Object.keys(S).sort();
if(cs.length>1){for(var i=0;i<cs.length;i++){var o=document.createElement('option');o.value=cs[i];o.lang=cs[i];o.textContent=N[cs[i]]||cs[i];sel.appendChild(o)}
document.getElementById('switch').hidden=false}
sel.onchange=function(){try{localStorage.setItem('fontes-lang',sel.value)}catch(e){}
try{var u=new URL(location.href);u.searchParams.set('lang',sel.value);history.replaceState(null,'',u)}catch(e){}apply(sel.value)};
apply(pick(prefs))})();
"""


def render(reports: list[dict], now: dt.datetime | None = None) -> str:
    """One page for every language: English is rendered here; elements carry their string key
    (data-i) and arguments (data-a), and the inline script re-renders them in the reader's
    language from the embedded docs/i18n/*/strings.json. Without JavaScript it stays English."""
    now = now or dt.datetime.now(dt.UTC)
    strings = _strings()
    s = strings["en"]
    L = {k: s[v] for k, v in LABEL.items()}

    def T(key: str, tag: str = "span", attrs: str = "", lower: bool = False, **args) -> str:
        text = s[key].format(**{k: _arg(s, v) for k, v in args.items()})
        a = f" data-a='{_e(json.dumps(args, ensure_ascii=False, separators=(',', ':')))}'" if args else ""
        return (f"<{tag}{attrs} data-i={key}{a}{' data-l=1' if lower else ''}>"
                f"{_e(text.lower() if lower else text)}</{tag}>")

    def _plural(key: str, n: int) -> str:
        return f"<span data-p={key} data-a='{{\"n\":{n}}}'>{_e(i18n_docs.plural(s, key, n))}</span>"

    script_tables = json.dumps(strings, ensure_ascii=False, separators=(",", ":"))
    js = JS % {
        "strings": script_tables.replace("</", "<\\/"),
        "rtl": json.dumps([c for c in strings if i18n_docs.rtl(c)]),
        "names": json.dumps({c: ("English" if c == "en" else i18n_docs.autonym(c)) for c in strings},
                            ensure_ascii=False).replace("</", "<\\/"),
        "script": json.dumps(fontes_i18n._SCRIPT), "legacy": json.dumps(fontes_i18n._LEGACY),
    }
    head = (f"<!doctype html><html lang=en><meta charset=utf-8>"
            f"<meta name=viewport content='width=device-width,initial-scale=1'>"
            + i18n_docs.favicon_html("").replace("assets/brand/", "../assets/brand/").replace("\n", "")
            + f"<title>{_e(s['status_title'])}</title><style>{CSS}</style><main>"
            + T("status_title", "h1")
            + f"<div id=switch class=mute hidden><label>{T('doc_languages')}: <select id=langs></select></label></div>"
            + T("doc_notice", "p", " id=notice class=mute hidden"))
    tail = f"</main><script>{js}</script></html>"
    if not reports:
        return head + T("status_no_reports", "p") + tail
    latest = reports[-1]
    by_src = series(reports)
    current = {(r["jurisdiction"], r["source"]): r for r in latest["results"]}
    n = {st: sum(r["status"] == st for r in current.values()) for st in RANK}
    broken = n["down"] + n["blocked"]
    src = lambda k: {"p": "status_source", "n": k}  # noqa: E731
    if broken:
        banner, cls = T("status_banner_broken", sources=src(broken), degraded=n["degraded"]), "down"
    elif n["degraded"]:
        banner, cls = T("status_banner_degraded", sources=src(n["degraded"])), "degraded"
    else:
        banner, cls = T("status_banner_ok"), "ok"
    parts = [head,
             f"<div class=mute>{T('status_last_check', time=latest['checked_at'][:16].replace('T', ' '))} · "
             f"Fontes {_e(latest.get('fontes_version'))} · {_plural('status_source', len(current))} · "
             f"{T('status_runs', n=len(reports))} · "
             + " · ".join(f"{T(LABEL[x], lower=True)} {n[x]}" for x in ("ok", "degraded", "down", "blocked", "skipped"))
             + "</div>",
             f"<div class='banner {cls}'>{banner}</div>"]
    codes = sorted({c for c, _ in current})
    worst = {c: max((current[k]["status"] for k in current if k[0] == c), key=lambda x: RANK[x]) for c in codes}
    for c in sorted(codes, key=lambda c: (-RANK[worst[c]], c)):
        keys = sorted(k for k in current if k[0] == c)
        parts.append(f"<details{' open' if RANK[worst[c]] >= 2 else ''}><summary>"
                     f"<span class='dot {worst[c]}'></span><b>{_e(c)}</b>"
                     f"<span class=mute>{_plural('status_source', len(keys))} · {T(LABEL[worst[c]])}</span></summary>")
        for k in keys:
            r, runs = current[k], by_src[k]
            last_err = next((x for x in reversed(runs) if x["status"] not in ("ok", "skipped")), None)
            bars = "".join(f"<i class='{x}' title='{_e(x)}'></i>" if x else
                           f"<i class=none title='{_e(s['status_no_run'])}'></i>"
                           for x in strip(runs, now))
            parts.append(
                f"<div class=row><div><span class='dot {r['status']}'></span> {_e(k[1])}"
                f"<div class=bars>{bars}</div>"
                + (T("status_last_error", "div", " class=err", date=last_err["checked_at"][:10],
                     detail=last_err.get("detail") or "") if last_err else "")
                + f"</div><div class=mute style='text-align:right;white-space:nowrap'>{T(LABEL[r['status']])}<br>"
                f"{T('status_uptime', week=_pct(uptime(runs, now, 7)), month=_pct(uptime(runs, now, 30)))}<br>"
                f"{T('status_checked', time=r['checked_at'][:16].replace('T', ' '))}</div></div>")
        parts.append("</details>")
    inc = incidents(by_src)
    parts.append(T("status_incidents", "h2", n=len(inc)))
    if inc:
        parts.append("<table><tr>" + "".join(T("status_col_" + c, "th")
                                             for c in ("source", "status", "start", "end", "detail")) + "</tr>")
        for i in inc[:200]:
            end = _e(i["end"][:16].replace("T", " ")) if i["end"] else T("status_ongoing")
            parts.append(f"<tr><td><b>{_e(i['jurisdiction'])}</b> {_e(i['source'])}</td>"
                         f"<td><span class='dot {i['status']}'></span> {T(LABEL[i['status']])}</td>"
                         f"<td>{_e(i['start'][:16].replace('T', ' '))}</td>"
                         f"<td>{end}</td><td class=err>{_e(i['detail'][:200])}</td></tr>")
        parts.append("</table>")
    else:
        parts.append(T("status_no_incidents", "p", " class=mute"))
    parts.append(T("status_footnote", "p", " class=mute") + tail)
    return "\n".join(p for p in parts if p)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="status_page", description=__doc__.split("\n\n")[0])
    p.add_argument("--history", default=str(ROOT / "research" / "health"))
    p.add_argument("--out", default=str(ROOT / "status" / "index.html"))
    a = p.parse_args(argv)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(load(Path(a.history))), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
