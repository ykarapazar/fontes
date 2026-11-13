from world_legal_mcp.jurisdictions import ad
from world_legal_mcp.models import LawHit


def _h(lid, title):
    return ad._law_hit(lid, title, "llei", "in force")


def test_older_same_title_flagged_and_recent_flagged(monkeypatch):
    monkeypatch.setattr(ad._http, "today", lambda: "2026-11-12")
    new = _h("L2026018", "Llei 18/2026, del 15 de juliol, qualificada del Codi penal")
    old = _h("L2005009", "Llei 9/2005, del 21 de febrer, qualificada del Codi penal (Text refós sense caràcter oficial)")
    other = _h("L2021022", "Llei 22/2021, del 17 de setembre, de text consolidat del Codi de procediment civil")
    ad._flag_status([new, old, other])
    assert "newer law" in old.status
    assert "entry into force" in new.status
    assert other.status == "in force"


def test_repeal_confirmed_from_newer_law_text(monkeypatch):
    import asyncio
    from lxml import html
    monkeypatch.setattr(ad._http, "today", lambda: "2026-11-12")
    new = _h("L2026018", "Llei 18/2026, del 15 de juliol, qualificada del Codi penal")
    old = _h("L2005009", "Llei 9/2005, del 21 de febrer, qualificada del Codi penal")
    src = ad.AndorraSource() if hasattr(ad, "AndorraSource") else None
    if src is None:
        src = next(v for v in vars(ad).values()
                   if isinstance(v, type) and v.__module__ == ad.__name__ and hasattr(v, "_confirm_repeals"))()

    async def fake_law(self, raw):
        return raw, "t", html.fromstring("<div>Queda derogada la Llei 9/2005, del 21 de febrer.</div>")
    monkeypatch.setattr(type(src), "_law", fake_law)
    asyncio.run(src._confirm_repeals([new, old], ad._flag_status([new, old])))
    assert old.status.startswith("repealed")
    assert "Llei 18/2026" in old.status
    assert new.status != "in force"


def test_phrase_run_ranks_company_law_above_company_tax():
    from world_legal_mcp.jurisdictions.ad import _phrase_run
    qw = ["llei", "de", "societats"]
    law = "Llei 20/2007, del 18 d’octubre, de societats anònimes i de responsabilitat limitada"
    tax = "Llei 95/2010, del 29 de desembre, de l’impost sobre societats"
    assert _phrase_run(qw, law) > _phrase_run(qw, tax)
