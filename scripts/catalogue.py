"""Write docs/COVERAGE.md: per jurisdiction, what Fontes reaches and what it does not.

    uv run python scripts/catalogue.py      # then runs scripts/coverage_map.py (the map)

Reach comes from each adapter's sources, tools and notes; gaps from Jurisdiction.gaps.
UN member states without an adapter come from scripts/no_adapter.py.
Also writes docs/i18n/<lang>/COVERAGE.md for every language with a strings.json: only the
summary (counts and scorecard) with headings and labels translated, data as it is, and a link
to the full English file.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from world_legal_mcp import registry
from world_legal_mcp.base import CASELAW, LEGISLATION, Jurisdiction

sys.path.insert(0, str(Path(__file__).resolve().parent))
import i18n_docs  # noqa: E402
from no_adapter import NO_ADAPTER  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "COVERAGE.md"
MAPS = ROOT / "research" / "maps"   # <code>.json: the country's courts and legislation types, each marked reached or not
L = i18n_docs.labels()   # set per language by write()


def _map(code):
    f = MAPS / f"{code}.json"
    return json.loads(f.read_text()) if f.exists() else None


def _count(rows) -> str:
    if not rows:
        return "–"
    yes = sum(r["reached"] == "yes" for r in rows)
    part = sum(r["reached"] == "partly" for r in rows)
    return f"{yes}+{part}½/{len(rows)}" if part else f"{yes}/{len(rows)}"


ELSE = ("available", "blocked", "offline", "unknown")


def _esc(c) -> str:
    return str(c).replace("|", "\\|").replace("\n", " ")


def _elsewhere(r) -> str:
    e = r.get("elsewhere")
    if not e:
        return "" if r["reached"] == "yes" else L["cov_not_researched"]
    src = e.get("source") or ""
    if e.get("url"):
        src = f"[{src or e['url']}]({e['url']})"
    bits = [L[f"cov_else_{e['status']}"] if e.get("status") in ELSE else e.get("status") or "", src,
            e.get("note") or "", L["cov_evidence"].format(evidence=e["evidence"]) if e.get("evidence") else ""]
    return " — ".join(b for b in bits if b)


def _table(rows, first, second):
    out = [f"| {first} | {second} | {L['cov_col_in_fontes']} | {L['cov_col_via']} | {L['cov_col_elsewhere']} |",
           "|---|---|---|---|---|"]
    for r in rows:
        kind = r.get("tier") or r.get("level") or ""
        why = "; ".join(b for b in (r.get("via"), r.get("note")) if b)
        name = r["name"] + (f" ({r['en']})" if r.get("en") and r["en"] != r["name"] else "")
        mark = L[f"cov_mark_{r['reached']}"] if r["reached"] in ("yes", "partly", "no") else r["reached"]
        cells = [name, kind, mark, why, _elsewhere(r)]
        out.append("| " + " | ".join(_esc(c) for c in cells) + " |")
    return out


def _state_rows(m):
    return [r for st in (m or {}).get("states", []) for r in st["courts"]]


def _rows(m):
    return [r for k in ("courts", "legislation") for r in (m or {}).get(k, [])] + _state_rows(m)


def _gap_counts(m) -> str:
    rows = [r for r in _rows(m) if r["reached"] != "yes"]
    if not rows:
        return "–"
    st = [(r.get("elsewhere") or {}).get("status", "unknown") for r in rows]
    icon = {"available": "🟢", "blocked": "🔒", "offline": "⚫", "unknown": "❓"}
    return " ".join(f"{icon[k]}{st.count(k)}" for k in ELSE if st.count(k))


OVERRIDES = json.loads((ROOT / "research" / "scorecard_overrides.json").read_text())
SCORE = {"complete": "✅", "gap": "◐", "none": "❌", None: "–"}


def _area(code, area, rows):
    if code in OVERRIDES[area]:
        return OVERRIDES[area][code]
    if not rows:
        return None, ""
    got = {r["reached"] for r in rows}
    st = "complete" if got == {"yes"} else ("gap" if got & {"yes", "partly"} else "none")
    why = "; ".join(f"{r.get('en') or r['name']}: {r.get('note')}" for r in rows if r["reached"] != "yes" and r.get("note"))
    return st, why


def _score(code, m):
    """Coverage measure: the top general court's precedents, and the constitution plus primary acts."""
    courts = (m or {}).get("courts", [])
    top = [r for r in courts if r.get("tier") == "apex" and r.get("branch") in ("civil-criminal", "civil", "criminal")]
    top = top or [r for r in courts if r.get("tier") == "apex"][:1]
    top = [r for r in top if r.get("final")] or top     # a current final court outranks a former one
    acts = [r for r in (m or {}).get("legislation", []) if r.get("level") in ("constitution", "primary")]
    return _area(code, "caselaw", top), _area(code, "legislation", acts)


def _terms(s) -> str:
    bits = [s.licence,
            {True: L["cov_term_commercial"], False: L["cov_term_no_commercial"]}.get(s.commercial_use, ""),
            L["cov_term_no_ai"] if s.ai_use is False else "",
            "" if s.auth == "none" else L["cov_term_auth"].format(auth=s.auth),
            "" if s.official else L["cov_term_unofficial"],
            L["cov_term_permission"] if s.needs_permission else ""]
    return "; ".join(b for b in bits if b)


def _half(j, methods) -> str:
    # the methods the adapter has, also when it is off here for want of a key (France, US states)
    have = [m for m in methods if Jurisdiction.supports(j, m)]
    return L["cov_yes"] if len(have) == len(methods) else (L["cov_partly"] if have else L["cov_no"])


def render(lang: str = "en") -> str:
    global L
    L = i18n_docs.labels(lang)
    js = sorted(registry._all.values(), key=lambda j: j.name.lower())
    counts = [L["cov_counts"].format(adapters=len(js), missing=len(NO_ADAPTER)), ""]
    if lang == "en":
        out = [f"# {L['cov_title']}", "", L["cov_intro"], "", L["cov_reliability"], "", L["cov_last_column"], ""]
    else:  # a translation is only the summary: counts and scorecard, then a link to the English file
        out = [f"> {L['doc_notice']}", "", f"# {L['cov_title']}", ""]
    out += counts
    sc = {j.code: _score(j.code, _map(j.code)) for j in js}
    covered = [c for c, (a, b) in sc.items() if "complete" in (a[0], b[0])]
    out += [f"## {L['cov_scorecard']}", "", L["cov_scorecard_intro"], "",
            L["cov_covered"].format(n=len(covered), total=len(js)), "",
            "| " + " | ".join(L[f"cov_col_{c}"] for c in ("code", "jurisdiction", "top_court", "constitution",
                                                         "covered", "missing")) + " |",
            "|---|---|---|---|---|---|"]
    for j in sorted(js, key=lambda j: ("complete" not in (sc[j.code][0][0], sc[j.code][1][0]), j.name.lower())):
        (a, aw), (b, bw) = sc[j.code]
        miss = " / ".join(w for w in (aw, bw) if w)
        out.append(f"| `{j.code}` | {j.name} | {SCORE[a]} | {SCORE[b]} | "
                   f"{L['cov_yes'] if j.code in covered else L['cov_no']} | {_esc(miss)[:300]} |")
    if lang != "en":
        return "\n".join(out + ["", L["cov_full_english"].format(url="../../COVERAGE.md")]) + "\n"
    out += ["", f"## {L['cov_detail']}", "",
            "| " + " | ".join(L[f"cov_col_{c}"] for c in ("code", "jurisdiction", "caselaw", "legislation", "courts",
                                                         "state_courts", "leg_types", "rest")) + " |",
            "|---|---|---|---|---|---|---|---|"]
    out += [f"| `{j.code}` | {j.name} | {_half(j, CASELAW)} | {_half(j, LEGISLATION)} | "
            f"{_count((_map(j.code) or {}).get('courts'))} | {_count(_state_rows(_map(j.code)))} | "
            f"{_count((_map(j.code) or {}).get('legislation'))} | {_gap_counts(_map(j.code))} |" for j in js]
    for j in js:
        out += ["", f"## {j.name} (`{j.code}`)", ""]
        m = _map(j.code)
        if m:
            src = ", ".join(m.get("structure_sources") or []) or L["cov_unverified"]
            out += [L["cov_court_system"], ""] + _table(m.get("courts", []), L["cov_col_court"], L["cov_col_level"])
            for st in m.get("states", []):
                out += ["", L["cov_state_courts"].format(name=st["name"], count=_count(st["courts"])), ""]
                out += _table(st["courts"], L["cov_col_court"], L["cov_col_level"])
            out += ["", L["cov_legislation"], ""] + _table(m.get("legislation", []), L["cov_col_instrument"],
                                                             L["cov_col_level"])
            out += ["", L["cov_drafted"].format(date=m.get("checked", "?"), refs=src), ""]
        out += [L["cov_sources"], ""]
        for s in j.sources:
            t = _terms(s)
            out.append(f"- {s.name} — {s.url} ({', '.join(s.covers) or 'n/a'})" + (f" — {t}" if t else ""))
            if s.warning:
                out.append(f"  - ⚠ {s.warning}")
        out.append(L["cov_tools"].format(tools=", ".join(j.supported()) or L["cov_none"]))
        if j.notes:
            out.append(L["cov_notes"].format(notes=j.notes))
        out += ["", L["cov_not_reached"], ""]
        out += [f"- {g}" for g in j.gaps] or [L["cov_not_catalogued"]]
    out += ["", f"## {L['cov_no_adapter']}", "",
            f"| {L['cov_col_code']} | {L['cov_col_country']} | {L['cov_col_why_not']} |", "|---|---|---|"]
    out += [f"| `{c}` | {n} | {why} |" for c, (n, why) in sorted(NO_ADAPTER.items(), key=lambda x: x[1][0])]
    return "\n".join(out) + "\n"


def main() -> None:
    registry.discover()
    OUT.write_text(render())
    print(f"wrote {OUT} ({len(registry._all)} adapters, {len(NO_ADAPTER)} without)")
    for lang in i18n_docs.translations():
        path = i18n_docs.I18N / lang / "COVERAGE.md"
        path.write_text(render(lang), encoding="utf-8")
        print(f"wrote {path}")
    import coverage_map  # same scorecard, drawn as a map; imported here because it imports this module
    coverage_map.main()


if __name__ == "__main__":
    main()
