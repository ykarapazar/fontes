"""Turns model records into the one markdown format every jurisdiction shares."""
from __future__ import annotations

import re
import unicodedata

from . import lexifina
from .base import Jurisdiction, permitted_codes
from .models import Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc


def _facts(pairs: list[tuple[str, str]]) -> list[str]:
    return [f"- {k}: {v}" for k, v in pairs if v]


def _warnings(j: Jurisdiction, kind: str) -> list[str]:
    """Per source of this kind: an unofficial-source notice, then any terms warning.
    Gated sources (needs_permission) are skipped unless permitted: adapters don't use them."""
    out = []
    allowed = j.code in permitted_codes()
    for s in j.sources:
        if kind not in s.covers or (s.needs_permission and not allowed):
            continue
        if not s.official and not lexifina.is_lexifina(s):   # Lexifina: its own warning says it
            out.append(f"> ⚠ Unofficial source: {s.name} ({s.url}) is not an official publication. "
                       "When you use this text, tell the user where it comes from, that it is "
                       "unofficial, and that they should check it against the official text "
                       "before relying on it.")
        if s.warning:
            out.append(f"> ⚠ {s.name}: {s.warning}")
    return out


def _header(j: Jurisdiction, kind: str, noun: str, query: str, r: Results, limit: int, page_no: int) -> str:
    """The first line. Never reads as a definitive count when the source gave none, as a
    keyword match when the keyword was ignored, or as a firm zero when the adapter explains it."""
    if r.query_ignored:
        what = f"{r.total:,} {noun} listed (search words not applied)" if r.total is not None \
            else f"{noun} listed (search words not applied, count not reported)"
    elif r.total is None:
        what = f"count not reported by the source, {noun} listed for {query!r}"
    elif r.incomplete:
        what = (f"{r.total:,} {noun} found so far for {query!r}; INCOMPLETE, only part of the "
                "source was searched (see the Note below)")
    elif r.total == 0 and r.note:
        what = f"no {noun} listed for {query!r}; this is not a finding that none exist (see the Note below)"
    else:
        what = f"{r.total:,} {noun} found for {query!r}"
    return f"# {j.name} ({j.code}) {kind}: {what} (page {page_no}, {limit} per page)"


def page(body: str, offset: int, max_chars: int) -> str:
    """body[offset:offset+max_chars] with a continuation note (pages are at least 1000 chars)."""
    total = len(body)
    offset, max_chars = int(offset), int(max_chars)
    if offset < 0:
        return f"Bad request: offset must be 0 or more (got {offset})."
    if offset and offset >= total:
        return (f"Bad request: offset {offset} is past the end of this text ({total} chars). "
                f"Use an offset below {total}.")
    size = max(1000, max_chars)
    end = min(total, offset + size)
    chunk = body[offset:end]
    if offset:
        chunk = f"… [continuing from char {offset}]\n\n" + chunk
    if end < total:
        floor = " (pages are at least 1000 chars)" if max_chars < 1000 else ""
        chunk += (f"\n\n… [truncated: chars {offset}–{end} of {total}{floor}. "
                  f"Call again with offset={end} for the next part.]")
    return chunk


def _page_size(r: Results, limit: int, page_no: int) -> int:
    """On page 1, a short page with more results left means the source capped `limit`."""
    n = len(r.items)
    if page_no == 1 and 0 < n < limit and r.total is not None and r.total > n:
        return n
    return limit


def caselaw_results(j: Jurisdiction, query: str, r: Results, *, limit: int, page_no: int) -> str:
    limit = _page_size(r, limit, page_no)
    out = [_header(j, "case law", "decisions", query, r, limit, page_no)]
    out += _warnings(j, "caselaw")
    if r.note:
        out.append(f"Note: {r.note}")
    if not r.items:
        out.append("\nNo decisions on this page.")
    start = (page_no - 1) * limit
    for n, h in enumerate(r.items, start + 1):
        h: DecisionHit
        out.append(f"\n### {n}. {h.title}")
        out += _facts([("Court", h.court), ("Date", h.date), ("Case number", h.case_number),
                       ("Source", h.url)])
        if h.has_text:
            out.append(f'- Open: get_decision("{j.code}", "{h.id}") (what it returns depends on the source; may be a summary)')
        else:
            out.append("- Text: not available from this source")
        if h.snippet:
            out.append(f"> {h.snippet}")
    return "\n".join(out)


def decision(j: Jurisdiction, d: Decision, *, max_chars: int, offset: int) -> str:
    head = [f"# {d.title}"] + _warnings(j, "caselaw")
    if d.note:
        head.append(f"> ⚠ {d.note}")
    head += _facts([("Jurisdiction", f"{j.name} ({j.code})"), ("Court", d.court), ("Date", d.date),
                    ("Case number", d.case_number), ("Identifier", d.id)])
    head += _facts(list(d.metadata.items()))
    head.append(f"- Source: {d.url}")
    if d.summary:
        head.append(f"\n## Summary\n\n{d.summary}")
    body = "\n".join(head) + "\n\n## Text\n\n" + d.text
    return page(body, offset, max_chars)


def legislation_results(j: Jurisdiction, query: str, r: Results, *, limit: int, page_no: int) -> str:
    limit = _page_size(r, limit, page_no)
    out = [_header(j, "legislation", "results", query, r, limit, page_no)]
    out += _warnings(j, "legislation")
    if r.note:
        out.append(f"Note: {r.note}")
    if not r.items:
        out.append("\nNo results on this page.")
    start = (page_no - 1) * limit
    for n, h in enumerate(r.items, start + 1):
        h: LawHit
        out.append(f"\n### {n}. {h.title}")
        out += _facts([("Type", h.type), ("Number", h.number), ("Date", h.date),
                       ("Status", h.status), ("Source", h.url)])
        if h.has_toc and j.supports("get_legislation_toc"):
            out.append(f'- Contents: get_legislation_toc("{j.code}", "{h.id}")')
        elif j.supports("get_legislation_text"):
            out.append(f'- Text: get_legislation_text("{j.code}", "{h.id}")')
        if h.snippet:
            out.append(f"> {h.snippet}")
    return "\n".join(out)


def toc(j: Jurisdiction, t: Toc, *, keyword: str | None, max_chars: int = 40000) -> str:
    entries = t.entries
    if keyword:
        # An entry matches on its own title/label, or when a heading above it matches.
        # Tiers, first one with a hit wins: the keyword at the start of a word ("art" finds
        # "Article 5", not "Part II"); anywhere in the text; ignoring spaces and dots
        # ("L.124" finds "L. 124-1").
        # Accents are ignored both ways ("preavis" finds "préavis").
        fold = lambda x: "".join(c for c in unicodedata.normalize("NFD", x.lower())
                                 if not unicodedata.combining(c))
        compact = lambda x: re.sub(r"[\s.]+", "", fold(x))
        k = fold(keyword)
        word = re.compile(r"(?<!\w)" + re.escape(k))
        tiers = (lambda x: bool(word.search(fold(x))),
                 lambda x: k in fold(x),
                 lambda x: bool(compact(keyword)) and compact(keyword) in compact(x))
        for test in tiers:
            kept, hit_levels = [], []
            for e in entries:
                while hit_levels and hit_levels[-1] >= e.level:
                    hit_levels.pop()
                if hit_levels or test(e.title) or test(e.provision):
                    kept.append(e)
                    if not hit_levels:
                        hit_levels.append(e.level)
            if kept:
                break
        entries = kept
    out = [f"# Contents: {t.title}", *_warnings(j, "legislation"),
           f"- Identifier: {t.id}", f"- Source: {t.url}"]
    if t.note:
        out.append(f"Note: {t.note}")
    if keyword:
        out.append(f"- Filtered by {keyword!r}: {len(entries)} of {len(t.entries)} entries")
    out.append(f'- Read one: get_legislation_provision("{j.code}", "{t.id}", "<provision>")\n')
    for e in entries:
        label = f" → provision \"{e.provision}\"" if e.provision else ""
        out.append(f"{'  ' * e.level}- {e.title}{label}")
    if not entries:
        out.append("(no matching entries)")
        if keyword:
            out.append("Note: the keyword is matched against section numbers and titles only, not the "
                       "body text, so 0 matches does not mean the law is silent on it. Try another "
                       "word or omit `keyword` to browse; if the entries look wrong or there is no "
                       "article split, this id may be a different instrument (check search_legislation) "
                       "or only get_legislation_text will show the wording.")
            out.append(f"Entries available without the keyword (first 30 of {len(t.entries)}):")
            for e in t.entries[:30]:
                label = f" → provision \"{e.provision}\"" if e.provision else ""
                out.append(f"{'  ' * e.level}- {e.title}{label}")
    text = "\n".join(out)
    if len(text) > max_chars:
        text = text[:max_chars] + "\n… [contents truncated: pass `keyword` to narrow the list]"
    return text


def provision(j: Jurisdiction, p: Provision) -> str:
    head = [f"# {p.law_title}: {p.provision}"] + _warnings(j, "legislation")
    if p.note:
        head.append(f"> ⚠ {p.note}")
    head += _facts([("Jurisdiction", f"{j.name} ({j.code})"), ("Law", p.law_id),
                    ("Text as of", p.as_of), ("Source", p.url)])
    return "\n".join(head) + "\n\n" + p.text


def law_text(j: Jurisdiction, t: LawText, *, max_chars: int, offset: int) -> str:
    head = [f"# {t.title}"] + _warnings(j, "legislation")
    if t.note:
        head.append(f"> ⚠ {t.note}")
    head += _facts([("Jurisdiction", f"{j.name} ({j.code})"), ("Identifier", t.id),
                    ("Text as of", t.as_of)])
    head += _facts(list(t.metadata.items()))
    head.append(f"- Source: {t.url}")
    return page("\n".join(head) + "\n\n" + t.text, offset, max_chars)
