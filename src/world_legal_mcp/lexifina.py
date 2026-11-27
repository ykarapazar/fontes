"""Lexifina's global law record, read through Lexifina's free hosted MCP server.

Lexifina (https://github.com/lexifina/global-law) keeps the law of about 200 countries as git
history: every change is a commit dated the day it took effect. Fontes uses it for two things
the official sites can't give live: the law as in force on a past date, and countries Fontes
has no live adapter for. Lexifina is not the official publisher and its record can lag it: every
answer says so and links the official page. The text of each country stays under its publisher's terms,
which Lexifina records per country.

Off with WLM_LEXIFINA=0. Limits (documented 2026-11-27): 60 calls a minute and 10,000 a day
per address, one at a time; every answer within 95 seconds.
"""
from __future__ import annotations

import json
import os
import re

from . import _http
from .base import BadRequest, NotFound, SourceError

URL = "https://global-law.lexifina.com/mcp"
HOST = "global-law.lexifina.com"
REPO = "https://github.com/lexifina/global-law"
_http.set_min_interval(HOST, 1.0)

CREDIT = ("From Lexifina's global law record (github.com/lexifina/global-law), a free record of each "
          "country's law that Lexifina builds from the official publishers. Lexifina is not the official "
          "publisher: its record can be days or weeks behind, and the note below says how far it goes. "
          "Check the official publisher's page it links before relying on it.")


def is_lexifina(source) -> bool:
    """True for the Source line of Lexifina's record (it carries its own warning)."""
    return source.url == REPO


def enabled() -> bool:
    return os.environ.get("WLM_LEXIFINA", "1").strip() != "0"


OFF = ("Lexifina is turned off on this computer (WLM_LEXIFINA=0), so past versions of laws and the "
       "countries Fontes reads through Lexifina are not available. Remove that setting to turn it on.")


def esc(s: str) -> str:
    """Text echoed back from a user's input, with < and > made harmless."""
    return s.replace("<", "&lt;").replace(">", "&gt;")


async def call(tool: str, **args) -> dict:
    """One tool call. Returns the result ({"content": [...], "structuredContent": {...}}).
    A refusal, a limit or a failure raises, so it never reads as "no results"."""
    body = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
            "params": {"name": tool, "arguments": {k: v for k, v in args.items() if v is not None}}}
    try:
        r = await _http.post(URL, json=body, timeout=100.0,
                             headers={"Accept": "application/json, text/event-stream"})
    except Exception as e:  # network error or the 100 s timeout
        raise SourceError(f"Lexifina could not be reached ({type(e).__name__}); try again shortly", "network") from e
    if r.status_code in (429, 503):
        wait = r.headers.get("Retry-After", "")
        raise SourceError("Lexifina is busy or this computer has used its calls for now"
                          + (f"; try again in {wait} seconds" if wait else ""), r.status_code)
    if r.status_code != 200:
        raise SourceError("Lexifina's server answered with an error", r.status_code)
    try:
        data = r.json()
    except json.JSONDecodeError as e:
        raise SourceError("Lexifina's answer could not be read", r.status_code) from e
    if "error" in data:
        raise SourceError(f"Lexifina refused the call: {esc(tidy(data['error'].get('message', '')))}", r.status_code)
    res = data.get("result") or {}
    if res.get("isError"):
        msg = esc(text(res))
        raise (NotFound if "not inside a corpus" in msg or "no such" in msg.lower() else BadRequest)(msg)
    return res


# Lexifina's tool names in its own text, as the Fontes tool that does the same
_TOOLS = {"list_provisions": "get_legislation_toc", "read_law": "get_law_on_date", "find_provision": "get_law_on_date",
          "provision_history": "get_law_history", "compare_dates": "get_law_history (with date_a/date_b)",
          "search_law": "search_legislation"}


# Lines about Lexifina's own tooling, not about the law, its dates or its coverage (kept if unsure: a line that
# also speaks of the record's end or last check stays)
_INTERNAL = re.compile(r"bypass_placeholder|provisional upload|pending-change|commit kind\(s\) not recognised", re.I)
_KEEP = re.compile(r"record runs to|last checked|not yet in force", re.I)


# git jargon: "(commit 363bccfe66)", a bare "commit 363bccfe66", and "; the corpus has a newer commit than the one pinned here"
_HASH = re.compile(r"\s*\(\s*commits?\s+[0-9a-f]{7,40}\s*\)|[ \t]*\bcommits?\s+[0-9a-f]{7,40}\b", re.I)
_PINNED = re.compile(r"(?:\s*[;,]\s*|\s+)?(?:\band\s+)?the corpus has a newer commit than (?:the one |the commit )?(?:that is )?pinned(?: here)?", re.I)


def tidy(s: str) -> str:
    """Lexifina's text with its tool names renamed to Fontes', its internal-tooling lines and git jargon
    (commit hashes, "newer commit than the one pinned") dropped (the one place its text comes in)."""
    s = "\n".join(l for l in s.split("\n") if not (_INTERNAL.search(l) and not _KEEP.search(l)))
    s = _PINNED.sub("", _HASH.sub("", s))
    return re.sub(r"\b(" + "|".join(_TOOLS) + r")\b", lambda m: _TOOLS[m[1]], s)


def text(res: dict) -> str:
    return tidy("\n".join(c.get("text", "") for c in res.get("content", []) if c.get("type") == "text").strip())


def credited(body: str) -> str:
    return f"{CREDIT}\n\n{body}"
