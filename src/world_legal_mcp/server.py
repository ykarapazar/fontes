"""world-legal-mcp: one small, fixed tool set; the jurisdiction is a parameter.

The same server runs filtered to some jurisdictions with `--only nl,gb`; the
`nl-legal-mcp` / `uk-legal-mcp` console scripts are that, pre-filtered.
"""
from __future__ import annotations

import argparse
import difflib
import re
import sys
import time
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit
from typing import Any

import httpx
from dotenv import find_dotenv, load_dotenv
from mcp.server.fastmcp import Context, FastMCP

from . import bugreport, health, lexifina, registry, render, stats, update_check
from .base import (AdapterError, BadRequest, Jurisdiction, NotFound, SourceError, blocked_sources,
                   kind_of, permitted_codes)

mcp = FastMCP(
    "fontes",
    instructions=(
        "Live case law and legislation from official government sources. Call "
        "list_jurisdictions first to see codes, supported tools and filters. Every "
        "result carries the source URL or identifier; always read the full text "
        "before relying on a decision or provision. get_law_on_date, get_law_history and "
        "some countries use Lexifina's record of the law (not the official publisher, and it may lag it); "
        "check the official publisher's page it links."
    ),
)
# Report our own version in serverInfo, not the mcp library's.
mcp._mcp_server.version = update_check.installed_version() or "dev"


# --------------------------------------------------------------------------- #
# Dispatch helpers
# --------------------------------------------------------------------------- #
_KIND = {"search_caselaw": "caselaw", "get_decision": "caselaw"}


def _sources_line(j: Jurisdiction, method: str = "") -> str:
    """The official sources, narrowed to the kind (case law / legislation) of `method`
    when some source covers it, so a legislation failure does not point at a court."""
    kind = _KIND.get(method, "legislation" if method else "")
    srcs = [s for s in j.sources if kind in s.covers] or list(j.sources)
    return "; ".join(f"{s.name} ({s.url})" for s in srcs)


def _supported_line(j: Jurisdiction) -> str:
    """Supported tools; those whose only sources are gated are marked, not offered as usable."""
    return ", ".join(m + (" (off by default: needs WLM_PERMITTED)" if blocked_sources(j, m) else "")
                     for m in j.supported()) or "none"


def _unsupported(j: Jurisdiction, method: str) -> str:
    """Refusal naming only sources of the requested kind, plus the adapter's notes and gaps."""
    kind = kind_of(method)
    srcs = [s for s in j.sources if kind in s.covers]
    what = "case law" if kind == "caselaw" else "legislation"
    if srcs:
        where = f"Check the official source directly: {'; '.join(f'{s.name} ({s.url})' for s in srcs)}."
    else:
        where = f"This is a scope limit, not a failure: this server has no {what} source for {j.name}."
        if j.notes:   # the pointer to where the {what} lives leads, not trails
            where += f" {j.notes}"
    out = [f"{method} is not supported for {j.name} ({j.code}) by this server. {where}"]
    if j.notes and srcs:
        out.append(f"Notes: {j.notes}")
    if j.gaps:
        out.append("Not covered: " + "; ".join(j.gaps) + ".")
    out.append(f"Supported for {j.code}: {_supported_line(j)}.")
    return "\n".join(out)


def _did_you_mean(q: str) -> str:
    """Up to 3 close jurisdictions (codes, aliases, names) as ' Did you mean: ...?', or ''."""
    names: dict[str, str] = {}
    for j in registry.available():
        for n in (j.code, j.name, *j.aliases):
            names.setdefault(n.lower(), j.code)
    found: list[str] = []
    for n in difflib.get_close_matches((q or "").strip().lower(), list(names), n=10, cutoff=0.75):
        if names[n] not in found:
            found.append(names[n])
    by_code = {j.code: j.name for j in registry.available()}
    return (" Did you mean: " + ", ".join(f"{c} ({by_code[c]})" for c in found[:3]) + "?") if found else ""


def _resolve(code: str, method: str) -> Jurisdiction | str:
    j = registry.get(code)
    if j is None:
        why = registry._broken.get(registry.canonical(code))
        if why:
            return (f"Jurisdiction {code!r} failed to load on this computer ({why}). "
                    "Please report it with report_bug.")
        return (f"Unknown or disabled jurisdiction {code!r}.{_did_you_mean(code)} "
                "Use list_jurisdictions() to see all codes.")
    if not j.supports(method):
        if getattr(j, "lexifina_legislation", False) and kind_of(method) == "legislation" and not lexifina.enabled():
            return lexifina.OFF
        return _unsupported(j, method)
    stats.record(j.code, method)   # no-op unless FONTES_STATS=1; code + tool name only
    return j


def _check_filters(j: Jurisdiction, filters: dict[str, Any] | None, kind: str) -> str | None:
    declared = j.caselaw_filters if kind == "caselaw" else j.legislation_filters
    unknown = sorted(set(filters or {}) - declared.keys())
    if not unknown:
        return _check_dates(j, filters or {}, declared)
    no_date = ""
    if (set(unknown) & {k for r in _RANGES for k in r}
            and not any(k in declared for r in _RANGES for k in r)):
        no_date = f"This source has no date filter for {kind}. "
    if not declared:
        return (f"Unknown {kind} filter(s) for {j.code}: {', '.join(unknown)}. {no_date}{j.name} has no "
                f"{kind} filters at all: its source cannot filter by date, court or type. Search by "
                "words only and sort or filter the results yourself.")
    valid = "\n".join(f"- `{k}`: {v}" for k, v in declared.items())
    close = {u: difflib.get_close_matches(u, declared, n=1) for u in unknown}
    hint = "".join(f" `{u}` -> did you mean `{m[0]}`?" for u, m in close.items() if m)
    return (f"Unknown {kind} filter(s) for {j.code}: {', '.join(unknown)}. {no_date}{hint}\n"
            f"Valid {kind} filters for {j.name} (use these names exactly; a range such as 'since 2022' "
            f"needs the matching year/date filter below, if any):\n{valid}")


_RANGES = (("date_from", "date_to"), ("from", "to"), ("date_start", "date_end"), ("year_from", "year_to"))
_ISO = re.compile(r"(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?")


def _check_dates(j: Jurisdiction, filters: dict[str, Any], declared: dict[str, str]) -> str | None:
    """Reject impossible Gregorian dates and from > to ranges before they reach the source."""
    def bad(msg: str) -> str:
        return f"Bad request ({j.code}): {msg}"
    for lo, hi in _RANGES:
        vals = {}
        for k in (lo, hi):
            v = str(filters.get(k) or "").strip()
            m = _ISO.fullmatch(v)
            if not m:
                continue
            if not re.search(r"Bikram|Sambat|Hijri|Jalali|Shamsi", declared.get(k, "")):
                y, mo, d = m.groups()
                try:
                    date(int(y), int(mo or 1), int(d or 1))
                except ValueError:
                    return bad(f"`{k}` {v!r} is not a real date (use YYYY-MM-DD).")
            vals[k] = v
        if len(vals) == 2:
            n = min(len(vals[lo]), len(vals[hi]))
            if vals[lo][:n] > vals[hi][:n]:
                return bad(f"`{lo}` {vals[lo]!r} is later than `{hi}` {vals[hi]!r}.")
    return None


# Fetched decisions / law texts / TOCs, kept briefly so paging with `offset`
# does not refetch (and so repeat calls spare the source's rate limit).
CACHE_TTL = 15 * 60
CACHE_MAX = 64
_cache: dict[tuple, tuple[float, Any]] = {}


async def _fetch(j: Jurisdiction, method: str, *args, cache: bool = False, **kw):
    """Call the adapter. Returns its record, or an error string for the user."""
    blocked = blocked_sources(j, method)
    if blocked:
        names = "; ".join(f"{s.name} ({s.url})" for s in blocked)
        return (f"Off by default ({j.code}): the terms or robots.txt of {names} forbid automated "
                f"use without the operator's permission. {blocked[0].warning} The lawful route is to ask "
                f"the operator for permission (terms: {blocked[0].terms_url or blocked[0].url}). Only if "
                f"you hold it, add {j.code} to WLM_PERMITTED; that unlocks just what the adapter reads "
                f"(see list_jurisdictions for what {j.code} covers and does not cover), not more.")
    key = (j.code, method, *args)
    if cache and key in _cache and time.monotonic() - _cache[key][0] < CACHE_TTL:
        return _cache[key][1]
    secrets = (*args, *(kw.get("filters") or {}).values())   # cut out of any bug report
    try:
        result = await getattr(j, method)(*args, **kw)
    except NotFound as e:
        return f"Not found ({j.code}): {e}"
    except BadRequest as e:
        return f"Bad request ({j.code}): {e}"
    except SourceError as e:
        msg = re.sub(r"^Error \([^)]*\): ", "", str(e))   # adapters repeat the prefix we add
        # A size-limit refusal is ours, not an HTTP answer from the source.
        status = f" (HTTP {e.status})" if e.status and "too large" not in msg else ""
        return _failed(j, method, secrets, f"Error ({j.code}): {msg.rstrip('.')}{status}. Official source: {_sources_line(j, method)}")
    except AdapterError as e:
        return _failed(j, method, secrets, f"Error ({j.code}): {e}")
    except httpx.HTTPError as e:
        return _failed(j, method, secrets, f"Error ({j.code}): could not reach the source "
                       f"({type(e).__name__}: {e or 'no detail'}). Try again shortly. "
                       f"Official source: {_sources_line(j, method)}")
    except Exception as e:
        bugreport.remember(j.code, method, f"{type(e).__name__}: {e}", secrets)
        raise
    if cache and not isinstance(result, str):
        if len(_cache) >= CACHE_MAX:
            _cache.pop(min(_cache, key=lambda k: _cache[k][0]))
        _cache[key] = (time.monotonic(), result)
    return result


def _failed(j: Jurisdiction, method: str, secrets: tuple, msg: str) -> str:
    """Keep the failure for a possible bug report (inputs cut out), and return it."""
    bugreport.remember(j.code, method, msg, secrets)
    return msg


# --------------------------------------------------------------------------- #
# Tools
# --------------------------------------------------------------------------- #
_FULL_MAX = 6   # more matches than this: compact index, so the reply fits a client's token limit


def _kinds(j: Jurisdiction) -> str:
    cov = j.coverage()
    return ", ".join(k for k, v in cov.items() if v) or "partial"


_BETA = ("Fontes is in beta: sources can be down, slow or change format. When a search fails or "
         "looks thin, say so to the user and point them to the original source link rather than guessing.")


@mcp.tool()
async def list_jurisdictions(query: str | None = None) -> str:
    """List the jurisdictions this server covers. Call this first.

    For each jurisdiction it shows: the code to pass as `jurisdiction` to the
    other tools (aliases accepted, e.g. "uk" -> "gb"), name, languages, the
    official sources (with licence notes), which tools are supported, the
    extra `filters` each search tool accepts, and the identifier formats.

    Args:
        query: optional text to narrow the list (matches code, alias or name,
            e.g. "nl", "united", "netherlands"). An exact code, alias or name
            gives that jurisdiction in full; many matches give a compact index.
    """
    stats.record("*", "list_jurisdictions")
    q = (query or "").strip().lower()
    known_down = await health.notices()   # {} unless WLM_HEALTH names a health report
    matches = [j for j in registry.available()
               if not q or q in " ".join([j.code, j.name, *j.aliases]).lower()]
    exact = [j for j in matches if q in (j.code, j.name.lower(), *(a.lower() for a in j.aliases))]
    matches = exact or matches
    if len(matches) > _FULL_MAX:
        rows = [f"- {j.code}: {j.name} ({_kinds(j)})"
                + ((" [from Lexifina's record, not the official publisher]" if lexifina.enabled()
                    else " [Lexifina's record: turned off, WLM_LEXIFINA=0]")
                   if getattr(j, "via_lexifina", False) else "")
                for j in matches]
        n_lex = sum(bool(getattr(j, "via_lexifina", False)) for j in matches)
        head = (f"{len(matches) - n_lex} live jurisdictions"
                + (f" and {n_lex} from Lexifina's record (not the official publisher)" if n_lex else "")
                + (f" match {query!r}" if q else " covered")
                + f". Call list_jurisdictions(query=<code>) for one's sources, filters and identifier "
                "formats.\n")
        head = _BETA + "\n\n" + head
        if note := update_check.notice():
            head = note + "\n\n" + head
        return head + "\n" + "\n".join(rows)
    out = []
    for j in matches:
        lines = [f"## {j.code} — {j.name}"
                 + (f"  (aliases: {', '.join(j.aliases)})" if j.aliases else "")]
        if j.languages:
            lines.append(f"- Languages: {', '.join(j.languages)}")
        for s in j.sources:
            terms = [x for x in (
                s.licence,
                {True: "commercial use allowed", False: "no commercial use"}.get(s.commercial_use, ""),
                "AI use opted out" if s.ai_use is False else "",
                "" if s.auth == "none" else f"needs {s.auth}",
            ) if x]
            lines.append(f"- Source: {s.name} — {s.url}" + ((" [not the official publisher]" if lexifina.is_lexifina(s) else " [unofficial]") if not s.official else "")
                         + (f" ({'; '.join(terms)})" if terms else ""))
            if s.warning:
                lines.append(f"  - ⚠ {s.warning}")
            if (j.code, s.name) in known_down:
                lines.append(f"  - ⚠ {known_down[(j.code, s.name)]}")
            if s.needs_permission and j.code not in permitted_codes():
                lines.append(f"  - Off by default: set WLM_PERMITTED={j.code} only if you hold that permission.")
        cov = j.coverage()
        gated = {k: bool(blocked_sources(j, m)) for k, m in
                 (("caselaw", "search_caselaw"), ("legislation", "search_legislation"))}
        lines.append("- Covers: " + (", ".join(k + (" (OFF by default: terms forbid automated use)"
                                                    if gated[k] else "")
                                      for k, v in cov.items() if v) or "partial"))
        lines.append(f"- Tools: {', '.join(j.supported())}")
        for label, filt in (("search_caselaw", j.caselaw_filters),
                            ("search_legislation", j.legislation_filters)):
            if filt and j.supports(label):
                lines.append(f"- `{label}` filters:")
                lines += [f"  - `{k}`: {v}" for k, v in filt.items()]
        if j.notes:
            lines.append(f"- Notes: {j.notes}")
        if j.gaps:
            lines.append("- Not covered (tell the user to check these elsewhere):")
            lines += [f"  - {g}" for g in j.gaps]
        out.append("\n".join(lines))
    if not out:
        return f"No jurisdiction matches {query!r}.{_did_you_mean(query)}"
    out.insert(0, _BETA)
    if note := update_check.notice():
        out.insert(0, note)
    return "\n\n".join(out)


MAX_LIMIT, MAX_QUERY, MAX_CHARS = 100, 500, 100000


def _bounds(limit: int, page: int) -> tuple[int, int, str]:
    """limit and page inside their range, and one line saying so when either was changed."""
    lim, pg = max(1, min(int(limit), MAX_LIMIT)), max(1, int(page))
    said = [f"{n} {'capped at' if v > MAX_LIMIT else 'raised to'} {c}"
            for n, v, c in (("limit", int(limit), lim), ("page", int(page), pg)) if v != c]
    return lim, pg, ("Fontes: " + "; ".join(said) + ".\n\n") if said else ""


def _chars(max_chars: int) -> tuple[int, str]:
    n = max(1000, min(int(max_chars), MAX_CHARS))
    return n, (f"Fontes: max_chars {'capped at' if int(max_chars) > n else 'raised to'} {n}.\n\n"
               if n != int(max_chars) else "")


def _long_query(query: str) -> str | None:
    if len(query or "") > MAX_QUERY:
        return f"Bad request: `query` is {len(query)} characters; at most {MAX_QUERY} are accepted. Use the key words."
    return None


@mcp.tool()
async def search_caselaw(
    jurisdiction: str,
    query: str = "",
    limit: int = 10,
    page: int = 1,
    filters: dict[str, Any] | None = None,
) -> str:
    """Search court decisions (case law / precedent) in one jurisdiction.

    Most sources search the full text; some search only titles, parties or metadata, and a few
    ignore the words (the result header and Note say so; see list_jurisdictions Notes). A
    count of 0 may then mean "not searchable this way", not "no such decision".

    Args:
        jurisdiction: code from list_jurisdictions, e.g. "nl", "gb" (alias "uk").
        query: search words in the language of the source (Dutch for nl, English for gb).
            May be empty ("") for sources that can list by filters alone (date, court, number).
            Date, court, type, year and similar narrowing belong INSIDE `filters`; any other
            top-level argument is rejected.
        limit: results per page (default 10).
        page: 1-based page number.
        filters: optional jurisdiction-specific filters as a dict, e.g.
            {"sort": "uitspraak", "period": "dit_jaar"} for nl or
            {"court": "uksc,ewca/civ", "order": "-date"} for gb. The valid
            names differ per jurisdiction; see list_jurisdictions.

    Returns a markdown list; each hit has the identifier to pass to get_decision.
    Snippets are not enough to cite: fetch the full decision.
    """
    j = _resolve(jurisdiction, "search_caselaw")
    if isinstance(j, str):
        return j
    if err := _check_filters(j, filters, "caselaw"):
        return err
    if err := _long_query(query):
        return err
    limit, page, said = _bounds(limit, page)
    r = await _fetch(j, "search_caselaw", query, limit=limit, page=page, filters=dict(filters or {}))
    return said + (r if isinstance(r, str) else render.caselaw_results(j, query, r, limit=limit, page_no=page))


# Claude Code saves text results over 50,000 chars to a file unless the tool raises its limit
# (code.claude.com/docs/en/mcp). A default 60,000-char page plus its header must stay inline.
_LONG_TEXT = {"anthropic/maxResultSizeChars": 100000}


@mcp.tool(meta=_LONG_TEXT)
async def get_decision(jurisdiction: str, id: str, max_chars: int = 60000, offset: int = 0) -> str:
    """Fetch one court decision as markdown (metadata, summary, full text, source URL).

    Args:
        jurisdiction: code from list_jurisdictions, e.g. "nl", "gb".
        id: the identifier the source uses, as returned by search_caselaw. nl:
            ECLI ("ECLI:NL:HR:2024:123"). gb: neutral citation ("[2024] UKSC 1",
            "[2026] EWHC 2093 (Ch)") or Find Case Law slug ("uksc/2024/1").
        max_chars: page size (default 60000). Long decisions end with a note
            giving the next offset.
        offset: character offset to continue from (from that note).
    """
    j = _resolve(jurisdiction, "get_decision")
    if isinstance(j, str):
        return j
    max_chars, said = _chars(max_chars)
    d = await _fetch(j, "get_decision", id.strip(), cache=True)
    return said + (d if isinstance(d, str) else render.decision(j, d, max_chars=max_chars, offset=offset))


@mcp.tool()
async def search_legislation(
    jurisdiction: str,
    query: str = "",
    limit: int = 20,
    page: int = 1,
    filters: dict[str, Any] | None = None,
) -> str:
    """Find laws, acts and statutory instruments in one jurisdiction.

    Args:
        jurisdiction: code from list_jurisdictions, e.g. "nl", "gb".
        query: (may be empty "" when filters alone select) words from the title (or full text where the source allows), in
            the source's language, e.g. "huurprijzen woonruimte" (nl),
            "Companies Act 2006" (gb). nl also accepts a BWB-id directly.
        limit: results per page (default 20).
        page: 1-based page number.
        filters: optional jurisdiction-specific filters as a dict, e.g.
            {"current_only": false} for nl or {"search_in": "text",
            "doc_type": "ukpga"} for gb. See list_jurisdictions.

    Date, type and similar narrowing belong INSIDE `filters`; any other top-level argument
    is rejected.

    Returns a markdown list; each hit has the id to pass to the
    get_legislation_* tools.
    """
    j = _resolve(jurisdiction, "search_legislation")
    if isinstance(j, str):
        return j
    if err := _check_filters(j, filters, "legislation"):
        return err
    if err := _long_query(query):
        return err
    limit, page, said = _bounds(limit, page)
    r = await _fetch(j, "search_legislation", query, limit=limit, page=page, filters=dict(filters or {}))
    if not isinstance(r, str) and not r.items and not getattr(j, "lexifina_legislation", False) and lexifina.enabled():
        r.note = (r.note + " " if r.note else "") + ("get_law_on_date may find it in Lexifina's "
                                                     "record of the law.")
    return said + (r if isinstance(r, str) else render.legislation_results(j, query, r, limit=limit, page_no=page))


@mcp.tool()
async def get_legislation_toc(jurisdiction: str, id: str, keyword: str | None = None) -> str:
    """Table of contents of a law (parts, chapters, articles/sections) with provision labels.

    Args:
        jurisdiction: code from list_jurisdictions, e.g. "nl", "gb".
        id: law id from search_legislation. nl: BWB-id ("BWBR0005289").
            gb: type/year/number ("ukpga/2006/46").
        keyword: optional; only list provisions whose number/title starts a word with
            (else contains) this text, case-insensitive. It does NOT search the body text.
            Strongly recommended for big codes.

    Use the provision labels it shows with get_legislation_provision.
    """
    j = _resolve(jurisdiction, "get_legislation_toc")
    if isinstance(j, str):
        return j
    t = await _fetch(j, "get_legislation_toc", id.strip(), cache=True)
    return t if isinstance(t, str) else render.toc(j, t, keyword=keyword)


@mcp.tool()
async def get_legislation_provision(jurisdiction: str, id: str, provision: str) -> str:
    """Text of one article / section / regulation / schedule paragraph.

    Usually the current consolidated text; some jurisdictions publish only the as-enacted
    text, and the result then says so at the top (check "Text as of" and any warning).

    Args:
        jurisdiction: code from list_jurisdictions, e.g. "nl", "gb".
        id: law id from search_legislation (nl "BWBR0005289", gb "ukpga/2006/46").
        provision: nl: article number ("2", "6:2", "Artikel 7a"). gb: "172",
            "s.172", "section/172", "reg 3", "sch 1 para 2",
            "schedule/1/paragraph/2".
    """
    j = _resolve(jurisdiction, "get_legislation_provision")
    if isinstance(j, str):
        return j
    asked = provision.strip()
    plain = re.sub(r"(?<![\d.,])0+(?=\d)", "", asked)   # "art. 009" -> "art. 9"
    p = await _fetch(j, "get_legislation_provision", id.strip(), plain)
    if plain != asked and isinstance(p, str) and p.startswith("Not found"):
        p = await _fetch(j, "get_legislation_provision", id.strip(), asked)
    return p if isinstance(p, str) else render.provision(j, p)


@mcp.tool(meta=_LONG_TEXT)
async def get_legislation_text(jurisdiction: str, id: str, max_chars: int = 60000, offset: int = 0) -> str:
    """Full consolidated (current) text of a law as markdown, pageable.

    Args:
        jurisdiction: code from list_jurisdictions, e.g. "nl", "gb".
        id: law id from search_legislation.
        max_chars: page size (default 60000). Big codes run to megabytes;
            prefer get_legislation_toc + get_legislation_provision.
        offset: character offset to continue from (from the truncation note).
    """
    j = _resolve(jurisdiction, "get_legislation_text")
    if isinstance(j, str):
        return j
    max_chars, said = _chars(max_chars)
    t = await _fetch(j, "get_legislation_text", id.strip(), cache=True)
    return said + (t if isinstance(t, str) else render.law_text(j, t, max_chars=max_chars, offset=offset))


_RECORD_START = ("The record begins when Lexifina started following that country's law, so an earliest "
                 "date, or \"not yet in force\" before that start, may only mean the record does not reach "
                 "back that far; check the official source.")


def _first_date(body: str) -> str:
    """The date Lexifina's record of a provision starts, from its 'before the record' answers; else ''."""
    m = re.search(r"(?:first appears on|first version of it is the[^.]*? in force on) (\d{4}-\d{2}-\d{2})", body)
    return m.group(1) if m else ""


def _tag_record_start(body: str) -> str:
    """After Lexifina's "was not yet in force on X. It first appears on Y (...)." add what it means."""
    return re.sub(r"(not yet in force on \d{4}-\d{2}-\d{2}\. It first appears on (\d{4}-\d{2}-\d{2})[^\n]*?\.)(?=\s|$)",
                  r"\1 (Fontes: this only means Lexifina's record starts on \2.)", body)


def _before_record(body: str, date: str) -> str:
    if "does not say what it said on" not in body and "not yet in force" not in body:
        return ""
    first = _first_date(body)
    return (f"Fontes: no text for {date}: Lexifina's record for this provision starts "
            + (f"on {first}" if first else "later") + ", so it cannot show what the law said earlier. "
            "Any \"not yet in force\" below only means the record starts later.\n\n")


# Lexifina record path -> the live adapter's (code, law id, provision). Only shapes that map cleanly.
_LIVE_PATHS = (
    ("nl", re.compile(r"^netherlands/.*-(BWBR\d+)/art-(\d+[a-z]*)\.md$"), lambda m: (m[1], m[2])),
    ("gb", re.compile(r"^united-kingdom/uk/legislation/([a-z]+/\d{4}/\d+)/((?:section|regulation|rule|article|schedule)/.+)\.md$"),
     lambda m: (m[1], m[2])),
    ("us", re.compile(r"^united-states/federal/usc/title-(\d+[a-z]?)/([^/]+)\.md$"), lambda m: (f"{m[1]} USC", m[2])),
)


_NOTE = re.compile(r"(?m)^(?:#+ Annotations|- \*\*[A-Z]\d+\*\*|_\d+ more annotations|Key: |\((?=[^)\n]*(?:Pub\. L\.|Stat\.|R\.S\.)))")


def _trim(t: str) -> str:
    """The wording of a provision: without front matter, leading headings, and trailing notes
    (annotations, statute history) that start with a recognisable marker."""
    t = re.sub(r"\A---\n.*?\n---\n", "", t.lstrip(), flags=re.S)
    if m := _NOTE.search(t):
        t = t[:m.start()]
    lines = t.split("\n")
    while lines and re.fullmatch(r"\s*(?:#.*|\*\*[^*]+\*\*)?\s*", lines[0]):
        lines.pop(0)
    t = "\n".join(lines)
    return re.sub(r"\A\s*\**(?:(?:section|sec|article|art|s|§)\.?\s*)?\d+[a-z]*\.?\**\s+", "", t, count=1, flags=re.I)


_LIST_NO = re.compile(r"(?m)^[\s>*#_-]*(?:\(\w{1,4}\)|\w{1,4}[°.)]+)\s+")


def _words(t: str) -> list[tuple[str, int, int]]:
    """Lower-case words of a text as (word, start, end) positions in `t`, without list numbering ("a.", "(2)", "3)").
    Markdown, spacing and punctuation never make a word."""
    skip = [m.span() for m in _LIST_NO.finditer(t)]
    return [(m[0].lower(), m.start(), m.end()) for m in re.finditer(r"\w+", t)
            if not any(a <= m.start() < b for a, b in skip)]


def _passage(t: str, w: list, i1: int, i2: int, cap: int = 200) -> str:
    """The text as written (case, punctuation) from 4 words before word i1 to 4 words after word i2, whitespace collapsed."""
    lo, hi = max(0, i1 - 4), min(len(w), i2 + 4)
    if lo >= hi:
        return ""
    a, b = w[lo][1], w[hi - 1][2]
    while a and not t[a - 1].isspace():   # keep the punctuation stuck to the first and last word: "(ii)", "“term"
        a -= 1
    while b < len(t) and not t[b].isspace():
        b += 1
    p = " ".join(t[a:b].split())
    return p if len(p) <= cap else p[:cap].rstrip() + "…"


def _differences(lex: str, live: str) -> str:
    """The passages where two texts differ ('' only when they are equal, or nearly: ratio of at least 0.98 and no
    differing run longer than 3 words). The comparison is on lower-case words, so markdown, spacing, punctuation and
    list numbers do not count; each passage is shown as written in each source, with a few words around it."""
    ta, tb = _trim(lex), _trim(live)
    wa, wb = _words(ta), _words(tb)
    a, b = [x[0] for x in wa], [x[0] for x in wb]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    diffs = [o for o in sm.get_opcodes() if o[0] != "equal"]
    if not diffs or (sm.ratio() >= 0.98 and all(max(i2 - i1, j2 - j1) <= 3 for _, i1, i2, j1, j2 in diffs)):
        return ""
    out = [f"- Lexifina: \"{_passage(ta, wa, i1, i2)}\" / official: \"{_passage(tb, wb, j1, j2)}\""
           for _, i1, i2, j1, j2 in diffs[:3]]
    return "\n".join(out + ([f"- ({len(diffs) - 3} more differing passages)"] if len(diffs) > 3 else []))


# what the adapter's date means, per live adapter
_LIVE_DATE = {"nl": "current official version, in force since {}", "gb": "current official version, in force since {}",
              "us": "current official text, U.S. Code current through {}"}


def _applies_notes(text: str, url: str) -> str:
    """A line when the official page carries notes on how a provision applies or changed (UK annotations C/F/I/M)."""
    notes = re.findall(r"(?m)^- \*\*([A-Z]\d+)\*\* (.+)$", text)
    if not notes:
        return ""
    notes.sort(key=lambda n: n[0][0] != "C")   # modifications and exclusions first
    quoted = "; ".join(f"'{k} {v[:90]}{'…' if len(v) > 90 else ''}'" for k, v in notes[:2])
    return (f"Fontes: the official page also lists notes on how this provision applies or has changed (e.g. {quoted}), "
            f"which Lexifina's record does not hold; check them on the official page: {url}\n\n")


async def _live_check(path: str, date: str, body: str) -> str:
    """Lines for the top of a get_law_on_date answer: today's official text when it differs from Lexifina's record,
    else one line saying it agrees or was not compared. '' when the answer is a past date or no live adapter exists."""
    end = re.search(r"the record runs to (\d{4}-\d{2}-\d{2})", body)
    if date != "today" and not (end and date > end.group(1)):
        return ""
    target = next(((c, f(m)) for c, r, f in _LIVE_PATHS if (m := r.match(path))), None)
    j = registry.get(target[0] if target else path.split("/", 1)[0])
    if j is None or getattr(j, "lexifina_legislation", False):
        return ""
    live_ok = j.supports("get_legislation_provision") and not blocked_sources(j, "get_legislation_provision")
    skipped = ("Fontes: this text was not compared with the live official source; for today's official text "
               f"use get_legislation_provision with jurisdiction {j.code}.\n\n" if live_ok else
               f"Fontes: there is no active live official source for {j.name} in Fontes, so this text was not "
               "compared with one; check the official page it links.\n\n")
    if not target or "For the next part, call again" in body or "\n\n" not in body:
        return skipped
    try:
        p = await _fetch(j, "get_legislation_provision", *target[1])
    except Exception:
        return skipped
    lex = body.split("\n\n", 1)[1]
    if isinstance(p, str) or len(lex) + len(p.text) > 60000:
        return skipped
    diff = _differences(lex, p.text)
    when = _LIVE_DATE.get(j.code, "text as of {}").format(p.as_of or "today")
    notes = _applies_notes(p.text, p.url)
    if not diff:
        return f"Fontes: the wording of the live official text ({p.url}; {when}) agrees with Lexifina's record.\n\n" + notes
    name = urlsplit(p.url).hostname or j.name
    end = re.search(r"the record runs to (\d{4}-\d{2}-\d{2})", body)
    later = (f"The official text is dated {p.as_of}, after Lexifina's record ends ({end[1]}), which may explain "
             "the difference.\n" if end and re.fullmatch(r"\d{4}-\d{2}-\d{2}", p.as_of or "") and p.as_of > end[1] else "")
    return (f"Official source ({name}, {when}): {p.url}\n\n{p.text}\n\n"
            "Fontes: Lexifina's record, shown below, differs from that official text. The differing "
            f"passages (as written in each source):\n{diff}\n{later}Please check the official page yourself: {p.url}\n\n" + notes)


def _at_record_end(body: str, date: str) -> str:
    """For a date after the end of Lexifina's record, its heading and "Cite as" line say "as in force on <date>":
    make them say the record's date instead."""
    m = re.search(r"the record runs to (\d{4}-\d{2}-\d{2})", body)
    asked = time.strftime("%Y-%m-%d") if date == "today" else date
    if not m or asked <= m.group(1):
        return body
    return body[:1500].replace(f"as in force on {asked}", f"as in force on {m.group(1)}, the end of Lexifina's record") + body[1500:]


async def _lexifina(tool: str, *, start_note: bool = False, live: bool = False, **args) -> str:
    """A Lexifina call as text for the user, with the credit; failures as one clear line."""
    try:
        try:
            res = await lexifina.call(tool, **args)
        except BadRequest as e:
            if "not a provision file" not in str(e) or args.get("path", ".md").endswith(".md"):
                raise
            args = {**args, "path": args["path"] + ".md"}
            res = await lexifina.call(tool, **args)
        body = _tag_record_start(lexifina.text(res))
        if tool == "read_law" and args.get("date"):
            body = _at_record_end(body, args["date"])
        lead = _before_record(body, args["date"]) if tool == "read_law" and args.get("date") else ""
        if live:
            lead = await _live_check(args["path"], args["date"], body) + lead
        return lead + lexifina.CREDIT + ("\n\n" + _RECORD_START if start_note else "") + "\n\n" + body
    except (NotFound, BadRequest, SourceError) as e:
        return _lexifina_error(e)


def _lexifina_error(e: Exception) -> str:
    if isinstance(e, (NotFound, BadRequest)):
        e = type(e)(lexifina.tidy(str(e)))
        hint = (" If you do not have the exact path, find it with search_legislation first."
                if "not a provision file" in str(e) else "")
        return _lexifina_error_line(e) + hint
    return _lexifina_error_line(e)


def _lexifina_error_line(e: Exception) -> str:
    if isinstance(e, NotFound):
        return f"Not found (Lexifina): {e}"
    if isinstance(e, BadRequest):
        return f"Bad request (Lexifina): {e}"
    status = f" (HTTP {e.status})" if e.status else ""
    return f"Error (Lexifina): {e}{status}. Nothing was searched; this is not a 'no results' answer."


def _no_match(jurisdiction: str | None, rows: bool = False) -> str:
    return ("Fontes: that citation did not match one provision" + (", so the list below is candidates, not results"
            if rows else "") + ". Find the act with search_legislation (or the country's own tools) and pass its path as "
            "`provision`" + (", or pick one of the paths below if one fits" if rows else "")
            + ("" if jurisdiction else "; also pass `jurisdiction`") + ".\n\n")


async def _lexifina_path(provision: str, jurisdiction: str | None) -> str | tuple[str]:
    """A provision path from a path or a citation. A tuple holds the answer to show instead
    (no match, several matches, or an error)."""
    p = provision.strip()
    if "/" in p and " " not in p:
        return p
    try:
        res = await lexifina.call("find_provision", query=p, jurisdiction=jurisdiction, max_results=10)
    except (NotFound, BadRequest, SourceError) as e:
        return ((_no_match(jurisdiction) if "No act called" in str(e) else "") + _lexifina_error(e),)
    rows = (res.get("structuredContent") or {}).get("results") or []
    if not any(r.get("whole_act") for r in rows) and (
            len(rows) == 1 or (rows and (res.get("structuredContent") or {}).get("read_as"))):
        return rows[0]["path"]
    body = lexifina.esc(lexifina.text(res))
    return (_no_match(jurisdiction, bool(rows)) + lexifina.credited(body)
            + ("\n\nPass one of these paths as `provision`." if rows else ""),)


def _date_arg(name: str, v: str | None) -> str | None:
    if v is None or v == "today":
        return None
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
        try:
            date.fromisoformat(v)
            return None
        except ValueError:
            return (f"Bad request: `{name}` {v!r} is out of range (years start at 0001)." if v.startswith("0000")
                    else f"Bad request: `{name}` {v!r} is not a valid calendar date.")
    return f"Bad request: `{name}` must be YYYY-MM-DD or \"today\", got {v!r}."


@mcp.tool(meta=_LONG_TEXT)
async def get_law_on_date(provision: str, date: str = "today", jurisdiction: str | None = None,
                          max_chars: int = 60000, offset: int = 0) -> str:
    """A provision's text as in force on a date (also a past one), with the law that last changed it.

    From Lexifina's global law record: a record of about 200 countries' law that keeps every
    change. Lexifina is not the official publisher and may lag it; the answer links the official page and
    says how far the record goes. For today's text from the official source, use
    get_legislation_provision where the jurisdiction has it.

    Args:
        provision: a citation or name, e.g. "Art. 1 GG", "Equality Act 2010 s. 4" (with
            jurisdiction "gb"), "Article L3141-3 du code du travail", or a path from an earlier
            answer, e.g. "germany/bund/acts/grundgesetz/artikel/001.md".
        date: in-force date, YYYY-MM-DD, or "today" (default).
        jurisdiction: optional country to narrow a citation, e.g. "germany", "de", "France".
        max_chars: page size (default 60000, at most 100000).
        offset: character offset to continue from (from the note at the end of a long text).
    """
    stats.record("lexifina", "get_law_on_date")
    if not lexifina.enabled():
        return lexifina.OFF
    if err := _date_arg("date", date):
        return err
    path = await _lexifina_path(provision, jurisdiction)
    if isinstance(path, tuple):
        return path[0]
    max_chars, said = _chars(max_chars)
    out = await _lexifina("read_law", start_note=True, live=not offset, path=path, date=date,
                          max_chars=max_chars, offset=max(0, int(offset)))
    if date != "today" and date > time.strftime("%Y-%m-%d"):
        out = (f"Fontes: {date} is in the future, so this is the record's current text plus any changes "
               "already scheduled; a later law could still change it.\n\n" + out)
    return said + out


async def _record_starts_later(path: str, earliest: str = "", latest: str = "") -> str:
    """A line when the record of a provision starts after the compared dates (or, with no dates, holds one entry:
    the record's start, not necessarily a change), so "no difference" or "1 change" can mislead."""
    try:
        changes = (await lexifina.call("provision_history", path=path)).get("structuredContent", {}).get("changes") or []
    except (NotFound, BadRequest, SourceError):
        return ""
    first = changes[0].get("in_force", "") if changes else ""
    if not first:
        return ""
    if not earliest:
        return (f"Fontes: the only entry, {first}, is where Lexifina's record for this provision begins, "
                "not necessarily a change.\n\n" if len(changes) == 1 else "")
    if earliest >= first:
        return ""
    if latest < first:
        return (f"Fontes: Lexifina's record for this provision starts on {first}, later than both dates, so "
                "\"no difference\" may only mean the record does not reach back that far.\n\n")
    return (f"Fontes: Lexifina's record for this provision starts on {first}, so it cannot show the text on "
            f"{earliest}; the entry on {first} is when the record begins, not necessarily a change.\n\n")


@mcp.tool(meta=_LONG_TEXT)
async def get_law_history(provision: str, jurisdiction: str | None = None,
                          date_a: str | None = None, date_b: str | None = None) -> str:
    """How a provision changed: every law that changed it, or the word-by-word change between two dates.

    From Lexifina's global law record (not the official publisher, and it may lag it; see get_law_on_date).

    Args:
        provision: a citation or name ("Art. 1 GG", "11 U.S.C. 1182") or a path from an
            earlier answer.
        jurisdiction: optional country to narrow a citation, e.g. "germany", "us".
        date_a, date_b: give both (YYYY-MM-DD or "today") for the changes between those
            dates, word by word. Without them: the list of every law that changed it.
    """
    stats.record("lexifina", "get_law_history")
    if not lexifina.enabled():
        return lexifina.OFF
    if (date_a is None) != (date_b is None):
        return "Bad request: give both date_a and date_b, or neither."
    if err := _date_arg("date_a", date_a) or _date_arg("date_b", date_b):
        return err
    today = time.strftime("%Y-%m-%d")
    if date_a and (today if date_a == "today" else date_a) > (today if date_b == "today" else date_b):
        return "Bad request: date_a must be on or before date_b."
    path = await _lexifina_path(provision, jurisdiction)
    if isinstance(path, tuple):
        return path[0]
    if date_a:
        out = await _lexifina("compare_dates", start_note=True, path=path, date_a=date_a, date_b=date_b)
        if "change(s) took effect" in out or "No difference" in out:
            a, b = sorted(today if d == "today" else d for d in (date_a, date_b))
            out = await _record_starts_later(path, a, b) + out
        return out
    out = await _lexifina("provision_history", start_note=True, path=path)
    return (await _record_starts_later(path) if "1 change(s)" in out else "") + out


@mcp.tool()
async def report_bug(ctx: Context, note: str = "") -> str:
    """Prepare a bug report about Fontes for its developers. Only when the user asks to report a problem.

    The report holds the Fontes version, the OS, and the last failed call's jurisdiction, tool
    and error message (search text and ids removed). The user sees it in a dialog from their
    app and decides whether to send it; nothing is sent otherwise.

    Args:
        note: what went wrong, in the user's words. Do not copy document text, search terms
            or client details into it unless the user explicitly asks you to.
    """
    return await bugreport.confirm_and_send(bugreport.build(note), getattr(ctx, "elicit", None))


# Unknown top-level arguments (e.g. `year_from`, `category`) used to be dropped silently, so the
# search ran unfiltered. Reject them; the tool descriptions say to put filters inside `filters`.
def _explain_extras(model: Any) -> None:
    """Make the rejection say where the stray argument belongs, not just 'Extra inputs'."""
    plain = model.model_validate.__func__

    def validate(cls, obj, *a, **kw):
        extra = sorted(set(obj) - set(cls.model_fields)) if isinstance(obj, dict) else []
        if extra:
            raise ValueError(
                f"Unknown argument(s): {', '.join(extra)}. Tool arguments are only "
                f"{', '.join(cls.model_fields)}. Search options such as category, court, "
                "date_from, date_to, year or type go inside `filters`, e.g. "
                '{"filters": {"date_from": "2022"}}; list_jurisdictions shows which ones each '
                "jurisdiction accepts.")
        return plain(cls, obj, *a, **kw)

    model.model_validate = classmethod(validate)


for _t in mcp._tool_manager.list_tools():
    _t.fn_metadata.arg_model.model_config["extra"] = "forbid"
    _t.fn_metadata.arg_model.model_rebuild(force=True)
    _explain_extras(_t.fn_metadata.arg_model)


# --------------------------------------------------------------------------- #
# Entry points
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None, only: str | None = None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["report-bug"]:
        sys.exit(bugreport.cli(argv[1:]))
    p = argparse.ArgumentParser(
        prog="fontes",
        description="MCP server (stdio) for live case law and legislation from official sources.",
    )
    p.add_argument("--only", metavar="CODES", default=only,
                   help="comma-separated jurisdiction codes to expose, e.g. 'nl' or 'nl,gb'")
    args = p.parse_args(argv)
    # API keys (WLM_<CODE>_<NAME>_KEY) from a .env file: the working directory's,
    # else the checkout's. Variables already set in the environment win.
    load_dotenv(find_dotenv(usecwd=True)) or load_dotenv(Path(__file__).resolve().parents[2] / ".env")
    if args.only:
        registry.enable_only(args.only.split(","))
    mcp.run()


def main_nl() -> None:
    main(only="nl")


def main_uk() -> None:
    main(only="gb")


if __name__ == "__main__":
    main()
