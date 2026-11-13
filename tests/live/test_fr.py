"""France (PISTE: Judilibre + Légifrance) checks the conformance suite does not cover.
Skipped unless WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET are set (env or .env)."""
import os

import pytest

from world_legal_mcp import server
from world_legal_mcp.jurisdictions import fr

pytestmark = pytest.mark.skipif(
    not (os.environ.get(fr.ENV_ID) and os.environ.get(fr.ENV_SECRET)),
    reason="needs a PISTE app: set WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET")


async def test_fr_cassation_decision_by_id_and_url():
    a = await server.get_decision("fr", "5fca7d162a251e6bf9c78514")
    b = await server.get_decision("fr", "https://www.courdecassation.fr/decision/5fca7d162a251e6bf9c78514")
    assert a == b and "17-18.194" in a and "Cour de cassation" in a
    assert "decision id" in (await server.get_decision("fr", "17-18.194")).lower()


async def test_fr_appeal_court_filter_and_dates():
    out = await server.search_caselaw("fr", "licenciement", limit=5,
                                      filters={"jurisdiction": "ca", "date_start": "2023-01-01"})
    assert "Cour d'appel" in out


async def test_fr_code_civil_article_variants():
    a = await server.get_legislation_provision("fr", "LEGITEXT000006070721", "Article 1240")
    b = await server.get_legislation_provision("fr", "LEGITEXT000006070721", "art. 1240")
    assert a == b and "Tout fait quelconque de l'homme" in a


async def test_fr_search_codes_and_loda():
    codes = await server.search_legislation("fr", "code civil")
    assert "LEGITEXT000006070721" in codes
    loda = await server.search_legislation("fr", "informatique et libertés", filters={"fond": "loda"})
    assert "JORFTEXT000000886460" in loda


async def test_fr_administrative_courts():
    j = fr.France()
    ce = await j.search_caselaw("responsabilité", limit=3, page=1, filters={"jurisdiction": "ce"})
    assert ce.total > 10000 and all(h.court.startswith("Conseil d") for h in ce.items)
    caa = await j.search_caselaw("responsabilité", limit=3, page=1, filters={"jurisdiction": "caa", "sort": "date"})
    assert caa.total > 30000 and all(h.id.startswith("CETATEXT") and h.case_number for h in caa.items)
    tc = await j.search_caselaw("compétence", limit=3, page=1, filters={"jurisdiction": "tc"})
    assert all("conflits" in h.court.lower() for h in tc.items)
    d = await j.get_decision("CETATEXT000053464527")
    assert d.court == "Conseil d'État" and d.case_number == "498240" and d.date == "2026-02-11"
    assert d.metadata["ECLI"].startswith("ECLI:FR:CECHR:2026") and "responsabilité" in d.summary


async def test_fr_conseil_constitutionnel():
    j = fr.France()
    r = await j.search_caselaw("liberté", limit=3, page=1, filters={
        "jurisdiction": "constit", "date_start": "2020-01-01", "date_end": "2020-12-31"})
    assert 0 < r.total < 500 and all(h.date.startswith("2020") for h in r.items)
    a = await server.get_decision("fr", "CONSTEXT000043596386")
    b = await server.get_decision("fr", "https://www.legifrance.gouv.fr/cons/id/CONSTEXT000043596386")
    assert a == b and "2021-817" in a and "sécurité globale" in a


async def test_fr_journal_officiel():
    j = fr.France()
    r = await j.search_legislation("portant nomination", limit=3, page=1, filters={"fond": "jorf"})
    assert r.total > 100000 and all(h.id.startswith("JORFTEXT") for h in r.items)
    t = await j.get_legislation_text(r.items[0].id)        # JORF-only text: no consolidated version
    assert t.metadata.get("Version") == "as published in the Journal officiel" and t.as_of
    p = await j.get_legislation_provision("JORFTEXT000028933611", "Article 1")
    assert "Code monétaire et financier" in p.text
