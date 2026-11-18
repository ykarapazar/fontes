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
from typing import Any

import httpx
from dotenv import find_dotenv, load_dotenv
from mcp.server.fastmcp import Context, FastMCP

from . import bugreport, health, registry, render, stats, update_check
from .base import (AdapterError, BadRequest, Jurisdiction, NotFound, SourceError, blocked_sources,
                   kind_of, permitted_codes)

mcp = FastMCP(
    "fontes",
    instructions=(
        "Live case law and legislation from official government sources. Call "
        "list_jurisdictions first to see codes, supported tools and filters. Every "
        "result carries the source URL or identifier; always read the full text "
        "before relying on a decision or provision."
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


def _resolve(code: str, method: str) -> Jurisdiction | str:
    j = registry.get(code)
    if j is None:
        why = registry._broken.get(registry.canonical(code))
        if why:
            return (f"Jurisdiction {code!r} failed to load on this computer ({why}). "
                    "Please report it with report_bug.")
        codes = ", ".join(x.code for x in registry.available())
        return (f"Unknown or disabled jurisdiction {code!r}. Available here: {codes}. "
                "Use list_jurisdictions() to see them.")
    if not j.supports(method):
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
        rows = [f"- {j.code}: {j.name} ({_kinds(j)})" for j in matches]
        head = (f"{len(matches)} jurisdictions" + (f" match {query!r}" if q else " covered")
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
            lines.append(f"- Source: {s.name} — {s.url}" + (" [unofficial]" if not s.official else "")
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
        return f"No jurisdiction matches {query!r}."
    out.insert(0, _BETA)
    if note := update_check.notice():
        out.insert(0, note)
    return "\n\n".join(out)


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
    limit, page = max(1, int(limit)), max(1, int(page))
    r = await _fetch(j, "search_caselaw", query, limit=limit, page=page, filters=dict(filters or {}))
    return r if isinstance(r, str) else render.caselaw_results(j, query, r, limit=limit, page_no=page)


@mcp.tool()
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
    d = await _fetch(j, "get_decision", id.strip(), cache=True)
    return d if isinstance(d, str) else render.decision(j, d, max_chars=max_chars, offset=offset)


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
    limit, page = max(1, int(limit)), max(1, int(page))
    r = await _fetch(j, "search_legislation", query, limit=limit, page=page, filters=dict(filters or {}))
    return r if isinstance(r, str) else render.legislation_results(j, query, r, limit=limit, page_no=page)


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


@mcp.tool()
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
    t = await _fetch(j, "get_legislation_text", id.strip(), cache=True)
    return t if isinstance(t, str) else render.law_text(j, t, max_chars=max_chars, offset=offset)


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
