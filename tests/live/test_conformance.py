"""The contract every adapter must pass, run live against the real source.

    uv run pytest tests/live/test_conformance.py -k tr

Each adapter declares `samples` (known-good inputs). Tests skip what an
adapter does not support or has no sample for. Legacy markdown adapters
(nl, gb until ported) are skipped.
"""
import re

import pytest

from world_legal_mcp import _http, registry
from world_legal_mcp.base import blocked_sources
from world_legal_mcp.models import (Decision, DecisionHit, LawHit, LawText, Provision, Results,
                                    Toc)

registry.discover()
ADAPTERS = [j for j in registry.available() if not getattr(j, "legacy_markdown", False)]
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
HTML_TAG = re.compile(r"<(p|div|span|br|font|b|table)\b", re.I)


def _need(j, method, *keys):
    if not j.supports(method):
        pytest.skip(f"{j.code} does not support {method}")
    if blocked_sources(j, method):
        pytest.skip(f"{j.code} {method}: source needs permission (WLM_PERMITTED)")
    missing = [k for k in keys if not j.samples.get(k)]
    if missing:
        pytest.fail(f"{j.code} supports {method} but samples lacks {missing}")
    return [j.samples[k] for k in keys]


def _check_common(obj, *, where):
    assert obj.id.strip(), f"{where}: empty id"
    assert obj.title.strip(), f"{where}: empty title"
    url = getattr(obj, "url", "")
    assert url.startswith("https://") or url.startswith("http://"), f"{where}: url {url!r}"
    date = getattr(obj, "date", "")
    assert date == "" or ISO_DATE.match(date), f"{where}: date {date!r} is not YYYY-MM-DD"
    assert not HTML_TAG.search(obj.title), f"{where}: HTML in title"


def _check_text(text, where, minimum=200):
    assert len(text) >= minimum, f"{where}: text only {len(text)} chars"
    assert not HTML_TAG.search(text), f"{where}: raw HTML tags left in text"


@pytest.fixture(params=ADAPTERS, ids=lambda j: j.code)
def j(request):
    return request.param


def test_metadata(j):
    assert j.code == j.code.lower() and j.name and j.languages
    assert j.sources, "declare at least one Source"
    for s in j.sources:
        assert s.covers, f"{s.name}: set covers"
        assert s.licence, f"{s.name}: set licence (say 'unknown' if unknown)"
        assert s.rate_limit, f"{s.name}: set rate_limit (say 'unknown; using N s spacing' if unknown)"
    cov = j.coverage()
    for kind in ("caselaw", "legislation"):
        if cov[kind]:
            assert any(kind in s.covers for s in j.sources), f"no Source covers {kind}"


async def test_search_caselaw(j):
    (q,) = _need(j, "search_caselaw", "caselaw_query")
    r = await j.search_caselaw(q, limit=3, page=1, filters={})
    assert isinstance(r, Results) and r.items, "no hits for the sample query"
    assert len(r.items) <= 3, "ignored limit"
    for h in r.items:
        assert isinstance(h, DecisionHit)
        _check_common(h, where=f"hit {h.id}")
    p2 = await j.search_caselaw(q, limit=3, page=2, filters={})
    assert [h.id for h in p2.items] != [h.id for h in r.items], "page 2 equals page 1"


async def test_get_decision(j):
    (did,) = _need(j, "get_decision", "decision_id")
    d = await j.get_decision(did)
    assert isinstance(d, Decision)
    _check_common(d, where="decision")
    _check_text(d.text, "decision")


async def test_search_legislation(j):
    (q,) = _need(j, "search_legislation", "legislation_query")
    r = await j.search_legislation(q, limit=3, page=1, filters={})
    assert isinstance(r, Results) and r.items, "no hits for the sample query"
    assert len(r.items) <= 3
    for h in r.items:
        assert isinstance(h, LawHit)
        _check_common(h, where=f"law hit {h.id}")


async def test_toc_and_provision(j):
    (law, prov) = _need(j, "get_legislation_provision", "law_id", "provision")
    if j.supports("get_legislation_toc"):
        t = await j.get_legislation_toc(law)
        assert isinstance(t, Toc) and t.entries
        labels = [e.provision for e in t.entries if e.provision]
        assert labels, "TOC has no provision labels"
        assert prov in labels, f"sample provision {prov!r} not among TOC labels"
    p = await j.get_legislation_provision(law, prov)
    assert isinstance(p, Provision) and p.law_title and p.url.startswith("http")
    _check_text(p.text, "provision", minimum=20)


async def test_get_legislation_text(j):
    (law,) = _need(j, "get_legislation_text", "law_id")
    t = await j.get_legislation_text(law)
    assert isinstance(t, LawText)
    _check_common(t, where="law text")
    _check_text(t.text, "law text", minimum=1000)


def test_zz_print_rate_limits():
    """Not a check: prints what each host did, to fill Source.rate_limit."""
    print("\n" + (_http.rate_limit_report() or "no requests"))
