"""Legislation of the countries Fontes has no live adapter for, read through Lexifina's record.

One adapter per entry of _lexifina_data.COUNTRIES (scripts/lexifina_countries.py builds it).
Lexifina (github.com/lexifina/global-law) keeps each country's law as git history and answers
through a free hosted MCP server (lexifina.py). It is Lexifina's record of the publishers' text, not
the official site: every response names Lexifina as the source and says so (Source.warning).
A hit's id is the act's folder in the record ("south-africa/national/acts/act/2013/4"); a TOC
label is a provision's file name without ".md" ("section-001").

Probed 2026-11-27: search_law lists provisions (30 lines at most per call, paged by line), but
its `acts` list ranks every matching act (12 at most) and does not depend on max_results; hits
are built from `acts`, one call per search, and paged here.
"""
from __future__ import annotations

import difflib
from datetime import date
import re

from .. import lexifina
from ..base import BadRequest, Jurisdiction, NotFound, Source
from ..models import LawHit, LawText, Provision, Results, Toc, TocEntry
from ._lexifina_data import COUNTRIES

OWN_ADAPTER = {"in"}   # India: its adapter keeps the Supreme Court and reads the Acts from Lexifina's record
_ACT_CAP = 12       # acts one search lists
_TEXT_PARTS = 10    # read_law calls for one whole text
_PART = 100000


def _folder(path: str) -> str:
    return path.rsplit("/", 1)[0] if path.endswith(".md") else path


def _label(path: str) -> str:
    return path.rsplit("/", 1)[-1].removesuffix(".md")


def _name(path: str) -> str:
    """An act's name when Lexifina gives no title: its type, year and number from the path."""
    return path.split("/acts/", 1)[1] if "/acts/" in path else _label(path)


def _as_of(s: dict, body: str) -> tuple[str, str]:
    """The date a text stands for. read_law without a date says "as in force on <today>", but the
    record only runs to its end date: when it says the wording is unchanged to there, show that
    date (in the header and in the first lines of the body), else the date of the last change."""
    changed = (s.get("last_change") or {}).get("in_force", "")
    latest = s.get("latest") or {}
    end = latest.get("record_end", "")
    if latest.get("state") != "same" or not end:
        checked = re.search(r"last checked[^\n]{0,200}? on (\d{4}-\d{2}-\d{2})", body)
        if changed and checked and (date.fromisoformat(checked[1]) - date.fromisoformat(changed)).days > 30:
            return f"{changed} (latest change in Lexifina's record; record last checked {checked[1]})", body
        return changed, body
    if s.get("date"):
        head, rest = body[:1500], body[1500:]
        body = head.replace(f"as in force on {s['date']}", f"as in force on {end}") + rest
    checked = re.search(r"last checked[^\n]{0,200}? on (\d{4}-\d{2}-\d{2})", body)
    far = checked and (date.fromisoformat(checked[1]) - date.fromisoformat(end)).days > 30
    record = f"the latest state in Lexifina's record{f', last checked {checked[1]}' if far else ''}"
    return f"{end} ({record}; this wording in force since {changed})" if changed else end, body



def _title_has_words(query: str, items: list) -> bool:
    """True if some title holds at least half of the query's significant words (4+ letters)."""
    words = set(re.findall(r"[^\W\d_]{4,}", query.lower()))
    need = (len(words) + 1) // 2
    return not words or any(sum(w in (i.title or "").lower() for w in words) >= need for i in items)



class _Lexifina(Jurisdiction):
    code = ""
    via_lexifina = True            # the whole adapter is Lexifina's (False where only the legislation is)
    lexifina_legislation = True    # its legislation tools read Lexifina's record
    _slug = ""
    _coverage = ""
    gaps = ("Live official source: not built in Fontes yet; Lexifina's record can be days or weeks behind",
            "Case law: not covered")

    def supports(self, method: str) -> bool:
        return lexifina.enabled() and super().supports(method)

    @property
    def notes(self) -> str:
        if not lexifina.enabled():
            return "Off: WLM_LEXIFINA=0 turns off Lexifina."
        return ("Read through Lexifina's record, not live from the official publisher. "
                f"What the record holds: {self._coverage}.")

    async def search_legislation(self, query, *, limit, page, filters):
        if not (query or "").strip():
            raise BadRequest("give search words.")
        res = await lexifina.call("search_law", query=query, jurisdiction=self._slug, kind="laws",
                                  max_results=10)
        s = res.get("structuredContent") or {}
        by_act = {}
        for m in s.get("matches", []):
            by_act.setdefault(_folder(m["path"]), m)
        acts = s.get("acts") or [{"path": p, "title": m.get("act") or m.get("title", "")}
                                 for p, m in by_act.items()]
        items = []
        for a in acts[(page - 1) * limit: page * limit]:
            m = by_act.get(a["path"], {})
            snip = f"{a['matching_provisions']} matching provisions" if a.get("matching_provisions") else ""
            best_change = (m.get("last_change") or {}).get("in_force", "")
            unit = " ".join(x for x in (m.get("unit"), m.get("heading")) if x)
            items.append(LawHit(id=a["path"], title=a.get("title") or _name(a["path"]),
                                snippet="; ".join(x for x in (snip, unit and f"best match: {unit}", best_change and
                                                              f"that provision last changed {best_change}") if x),
                                url=m.get("official_url") or lexifina.REPO))
        if not acts:
            note = lexifina.esc(lexifina.text(res)[:700])
        else:
            note = "Lexifina's record; the record can be days or weeks behind the official text."
            if s.get("matched_by") != "index" or s.get("match") != "phrase":
                note += f" {lexifina.esc(lexifina.tidy(s.get('summary', '')))}"
            if len(acts) >= _ACT_CAP:
                note += (f" Lexifina lists only its {_ACT_CAP} best-matching acts, so there may be more. "
                         "It can rank a country's national laws below state or provincial ones: try a "
                         "narrower query or the law's title.")
        total = None if len(acts) >= _ACT_CAP else len(acts)   # at the cap: Lexifina's cut-off, no total
        if acts and s.get("match") != "most_words" and not _title_has_words(query, items):
            note = ("None of these acts has those words in its title, so they only mention them; the law you "
                    "want may not be in Lexifina's record. " + note)
        if acts and s.get("match") == "most_words":
            # no provision holds the phrase: these are partial word matches, not results
            note = ("NO act or provision matched the phrase. The acts below only hold some of the "
                    "words, so they may be unrelated; the law may not be in Lexifina's record. "
                    + note)
            total = 0
        return Results(items=items, total=total, note=note)

    async def _provisions(self, id: str) -> list[dict]:
        out, offset = [], None
        for _ in range(_TEXT_PARTS):
            s = (await lexifina.call("list_provisions", path=id, offset=offset))["structuredContent"]
            out += s.get("provisions", [])
            offset = s["page"].get("next_offset")
            if offset is None:
                break
        if not out:
            raise NotFound(f"no provisions under {id}; use an id from search_legislation.")
        return out

    async def _title(self, path: str) -> str:
        s = (await lexifina.call("read_law", path=path, max_chars=1))["structuredContent"]
        return s.get("act") or _name(_folder(path))

    async def get_legislation_toc(self, id):
        provs = await self._provisions(id)
        return Toc(id=id, title=await self._title(provs[0]["path"]), url=lexifina.REPO,
                   entries=[TocEntry(title=p["heading"], provision=_label(p["path"])) for p in provs],
                   note="Lexifina's record of the law; provision labels are the record's file names.")

    async def get_legislation_provision(self, id, provision):
        p = re.sub(r"^(section|sec|article|art|s)(\.\s*|\s+)", "", (provision or "").strip(), flags=re.I)
        if not p:
            raise BadRequest("give a provision label from get_legislation_toc, e.g. 'section-001' or '5'.")
        provs = await self._provisions(id)
        hit = next((x for x in provs if _label(x["path"]).lower() == p.lower()), None) or next(
            (x for x in provs if re.match(rf"{re.escape(p)}(\.|\s|$)", x["heading"], re.I)), None)
        note = ""
        if hit is None and re.fullmatch(r"\d[0-9a-z]*", p, re.I):   # "1" for a label like "cl-001"
            num = re.sub(r"^0+(?=\d)", "", p.lower())
            hit = next((x for x in provs if re.sub(r"^[a-z]+-0*(?=\d)", "", _label(x["path"]).lower()) == num), None)
        if hit is None and len(provs) == 1 and _label(provs[0]["path"]) == "text":
            hit = provs[0]
            note = (f"This act is held as one record ('{_label(hit['path'])}'), not split by provision, so "
                    f"'{provision}' cannot be picked out; showing all of it.")
        if hit is None:
            res = await lexifina.call("find_provision", query=p, jurisdiction=id)
            found = res["structuredContent"].get("results", [])
            hit = found[0] if found else None
            if hit and not (re.fullmatch(r"\d[0-9a-z]*", p, re.I) and re.sub(r"^[a-z]+-0*(?=\d)", "", _label(hit["path"]).lower())
                            == re.sub(r"^0+(?=\d)", "", p.lower())):
                note = (f"'{provision}' is not a label of this act; this is Lexifina's closest match "
                        f"('{_label(hit['path'])}').")
        if hit is None:
            close = difflib.get_close_matches(p.lower(), [_label(x["path"]).lower() for x in provs], n=5, cutoff=0.6)
            raise NotFound(f"no provision '{lexifina.esc(provision)}' in {id}; get_legislation_toc lists them."
                           + (f" Closest labels: {', '.join(close)}." if close else ""))
        res = await lexifina.call("read_law", path=hit["path"])
        s = res["structuredContent"]
        as_of, body = _as_of(s, lexifina.text(res))
        return Provision(law_id=id, law_title=s.get("act") or _label(id), provision=_label(hit["path"]),
                         text=body, url=(s.get("cite") or {}).get("official_url") or lexifina.REPO,
                         as_of=as_of, note=note)

    async def get_legislation_text(self, id):
        res = await lexifina.call("read_law", path=id, max_chars=_PART)
        first = res["structuredContent"]
        as_of, body = _as_of(first, lexifina.text(res))
        parts, cur, calls = [body], first, 1
        while (cur.get("text_part") or {}).get("next_offset") is not None and calls < _TEXT_PARTS:
            nxt = cur["text_part"]["next_offset"]
            cur = (await lexifina.call("read_law", path=id, max_chars=_PART, offset=nxt))["structuredContent"]
            parts.append(cur.get("text", ""))
            calls += 1
        end = (cur.get("text_part") or {}).get("next_offset")
        note = ""
        if end is not None:
            note = (f"Only the first {end:,} of {cur['text_part']['chars']:,} characters were read; "
                    "get_legislation_provision reads single provisions.")
        title = first.get("act") or (await self._title(first["provisions"][0]["path"])
                                     if first.get("provisions") else _label(id))
        return LawText(id=id, title=title, text="\n".join(parts),
                       url=(first.get("cite") or {}).get("official_url") or lexifina.REPO,
                       as_of=as_of, note=note)


def source_for(c: dict) -> Source:
    """The Source line for one COUNTRIES entry (also used by adapters that read their legislation here)."""
    pub = "; ".join(c["publishers"])
    return Source(
        name="Lexifina global law record" + (f" (publisher: {pub})" if pub else ""),
        url=lexifina.REPO, covers=("legislation",), official=False,
        licence=("Lexifina's tools and tables CC0; the law text under each publisher's terms "
                 "(see the country's LICENSE in the repository)"),
        warning=lexifina.CREDIT,
        rate_limit="60 calls/min and 10,000/day per address, one at a time (documented 2026-11-27)",
        terms_url="https://github.com/lexifina/global-law/blob/main/LICENSE.md")


for _code, _c in COUNTRIES.items():
    if _code in OWN_ADAPTER:   # has an adapter of its own (case law) that reads its legislation from here
        continue
    _aliases = tuple(dict.fromkeys(a for a in (_c["slug"].lower(), _c["slug"].replace("-", " ").lower())
                                   if a != _code))
    globals()[f"Lexifina_{_code}"] = type(f"Lexifina_{_code}", (_Lexifina,), {
        "code": _code, "name": _c["name"], "aliases": _aliases, "_slug": _c["slug"],
        "_coverage": _c["coverage"], "sources": (source_for(_c),),
    })
