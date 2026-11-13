"""The adapter contract every jurisdiction implements. Full spec: docs/ADAPTER_SPEC.md.

A jurisdiction adapter is a `Jurisdiction` subclass in
`world_legal_mcp/jurisdictions/<code>.py`. It sets the metadata class
attributes and implements any subset of the async methods in METHODS,
returning the records in models.py. A method it does not define is "not
supported": the unified tool says so and points to the official sources.

Signatures (implement only the ones the source supports):

    async def search_caselaw(self, query, *, limit, page, filters) -> Results[DecisionHit]
    async def get_decision(self, id) -> Decision
    async def search_legislation(self, query, *, limit, page, filters) -> Results[LawHit]
    async def get_legislation_toc(self, id) -> Toc
    async def get_legislation_provision(self, id, provision) -> Provision
    async def get_legislation_text(self, id) -> LawText

`page` is 1-based; translate to the source's paging inside the adapter.
`filters` is already checked against caselaw_filters / legislation_filters;
validate the values yourself and raise BadRequest on a bad one.
Return full texts: the server pages, caches and keyword-filters TOCs.
Raise NotFound / BadRequest / SourceError instead of returning error text.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

METHODS = (
    "search_caselaw",
    "get_decision",
    "search_legislation",
    "get_legislation_toc",
    "get_legislation_provision",
    "get_legislation_text",
)
CASELAW = ("search_caselaw", "get_decision")
LEGISLATION = ("search_legislation", "get_legislation_provision")


class AdapterError(Exception):
    """Base for errors an adapter raises; the server turns them into one clear line."""


class NotFound(AdapterError):
    """The id / provision does not exist at the source."""


class BadRequest(AdapterError):
    """The caller sent something unusable (bad id format, bad filter value)."""


class SourceError(AdapterError):
    """The source failed or refused (HTTP error, block page, unexpected payload)."""

    def __init__(self, message: str, status: int | str = ""):
        super().__init__(message)
        self.status = status


@dataclass(frozen=True)
class Source:
    name: str
    url: str
    covers: tuple[str, ...] = ()          # "caselaw", "legislation"
    licence: str = ""                     # e.g. "Open Government Licence v3.0"
    commercial_use: bool | None = None    # None = unknown / not stated
    ai_use: bool | None = None            # False when robots/terms opt out of AI use
    auth: str = "none"                    # "none" | "free key" | "paid"
    rate_limit: str = ""                  # what we know + how + when, e.g. "~10 req/30 s per IP, 429 + Retry-After (measured 2026-11)"
    terms_url: str = ""
    warning: str = ""                     # shown on every response from this source, e.g. terms that need permission
    needs_permission: bool = False        # terms/robots forbid automated use: off unless permitted (see blocked_sources)
    official: bool = True                 # False: private/NGO site or unofficial consolidation; every response says so
    # Known-good inputs that exercise THIS source, for scripts/health.py: the keys of
    # Jurisdiction.samples, plus "filters" (dict passed to the search, e.g. {"court": "aym_bb"}).
    # Empty: the health check falls back to the adapter's samples.
    probe: dict = field(default_factory=dict, compare=False)


class Jurisdiction:
    code: str = ""                       # ISO 3166-1 alpha-2 lower-case, or e.g. "us-ca", "eu", "echr"
    name: str = ""
    languages: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()
    sources: tuple[Source, ...] = ()
    caselaw_filters: dict[str, str] = {}      # filter name -> description
    legislation_filters: dict[str, str] = {}
    min_interval: dict[str, float] = {}       # host -> min seconds between requests
    notes: str = ""                           # one or two lines shown in list_jurisdictions
    # What this jurisdiction does NOT reach, one "<what>: <why>" line each, e.g.
    # "Court of Cassation: terms allow personal use only". Shown in list_jurisdictions.
    gaps: tuple[str, ...] = ()
    # Known-good inputs for tests/live/test_conformance.py.
    # Keys: caselaw_query, decision_id, legislation_query, law_id, provision.
    samples: dict[str, str] = {}

    def supports(self, method: str) -> bool:
        return callable(getattr(self, method, None))

    def supported(self) -> list[str]:
        return [m for m in METHODS if self.supports(m)]

    def coverage(self) -> dict[str, bool]:
        """What the world map shows: case law and/or legislation available."""
        return {"caselaw": all(self.supports(m) for m in CASELAW),
                "legislation": all(self.supports(m) for m in LEGISLATION)}


def permitted_codes() -> set[str]:
    """Codes whose restricted sources the operator holds permission for: WLM_PERMITTED=in,de."""
    return {c.strip().lower() for c in os.environ.get("WLM_PERMITTED", "").split(",") if c.strip()}


def kind_of(method: str) -> str:
    return "legislation" if method.startswith("get_legislation") or method == "search_legislation" else "caselaw"


def blocked_sources(j: Jurisdiction, method: str) -> list[Source]:
    """Sources behind `method` whose terms forbid automated use and that the operator
    has not marked as permitted. The server refuses the call only when every source for
    that kind is gated; an adapter that mixes gated and open sources of one kind must
    skip the gated ones itself unless `j.code in permitted_codes()`."""
    if j.code in permitted_codes():
        return []
    kind = kind_of(method)
    srcs = [s for s in j.sources if kind in s.covers]
    gated = [s for s in srcs if s.needs_permission]
    return gated if gated and len(gated) == len(srcs) else []
