"""Live smoke tests against the Journal Officiel (joradp.dz). Needs network."""
from world_legal_mcp import server


async def test_dz_search_by_number():
    out = await server.search_legislation("dz", "08-09", limit=5, filters={"nature": "Loi"})
    assert "Loi n° 08-09 du 25 Février 2008 — JO n° 21/2008 p. 3" in out


async def test_dz_short_id_and_provision():
    out = await server.get_legislation_provision("algerie", "loi 08-09", "Art. 13")
    assert "Nul ne peut ester en justice" in out


async def test_dz_two_column_text_is_cut_at_signature():
    # 2026 issues are set in two columns; the law ends before the next decree on page 5.
    out = await server.get_legislation_text(
        "dz", "Loi n° 26-13 du 12 Octobre 2026 — JO n° 72/2026 p. 4")
    assert "Art. 8. — La présente loi sera publiée" in out
    assert "Abdelmadjid TEBBOUNE." in out and "Décret présidentiel n° 26-326" not in out


async def test_dz_scanned_issue_is_reported():
    out = await server.get_legislation_text("dz", "Loi n° 84-11 du 09 Juin 1984 — JO n° 24/1984 p. 612")
    assert "scanned page images" in out and "/Jo8499/1984/024/Fp612.pdf" in out


async def test_dz_constitution_with_2026_revision():
    out = await server.search_legislation("dz", "constitution", limit=3)
    assert 'get_legislation_toc("dz", "Constitution")' in out
    out = await server.get_legislation_provision("dz", "Constitution", "art. 226")
    assert "En cas de création de nouvelles wilayas" in out
    out = await server.get_legislation_provision("dz", "constitution", "87")   # partly restated
    assert "le reste sans changement" in out and "restates this article only in part" in out


async def test_dz_final_article_line_kept_and_empty_search():
    # "… sera publiée au Journal officiel de la République …" used to be dropped as a page header.
    out = await server.get_legislation_text("dz", "Loi n° 26-04")
    assert "sera publiée au Journal officiel de la République algérienne" in out
    out = await server.search_legislation("dz", "", limit=3, filters={
        "nature": "Décret législatif", "date_from": "2002-01-01"})
    assert "No results on this page" in out


# ---- Cour constitutionnelle (needs the OS trust store: the site's TLS chain is incomplete) ----

async def test_dz_caselaw_search_and_kind_filter():
    out = await server.search_caselaw("dz", "procédure civile", limit=10, filters={"kind": "decision"})
    assert "Décision n° 01/D.C.C/EI/25 du 7 janvier 2025" in out
    out = await server.search_caselaw("dz", "procédure pénale", limit=10,
                                      filters={"kind": "avis", "date_to": "2012-12-31"})
    assert "Avis n° 01/A.CC/12 du 8 janvier 2012" in out and "Décision n°" not in out


async def test_dz_decision_bare_number_and_old_council():
    out = await server.get_decision("dz", "01/D.C.C/EI/25")
    assert "articles 10, 558, 559 et 567" in out
    out = await server.get_decision("algerie", "Décision n° 1-D-L-CC 89 du 20 août 1989")
    assert "Conseil Constitutionnel" in out and "code électoral" in out
