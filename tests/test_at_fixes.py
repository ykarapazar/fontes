import asyncio

from world_legal_mcp.jurisdictions import at


def _law(title):
    return {"Metadaten": {"Bundesrecht": {"Kurztitel": title, "Titel": title, "BrKons": {
        "Gesetzesnummer": "20012184", "Kundmachungsorgan": "BGBl. I Nr. 6/2023"}},
        "Allgemein": {"DokumentUrl": "u"}}}


def test_title_search_retries_with_word_start(monkeypatch):
    seen = []

    async def fake(path, params, limit, page):
        seen.append(params["Titel"])
        if params["Titel"] == "Hinweisgeber*":
            return [_law("HinweisgeberInnenschutzgesetz")], 1
        return [], 0

    monkeypatch.setattr(at, "_paged", fake)
    res = asyncio.run(at.Austria().search_legislation(
        "Hinweisgeberschutzgesetz", limit=20, page=1, filters={}))
    assert seen[0] == "Hinweisgeberschutzgesetz" and seen[-1] == "Hinweisgeber*"
    assert res.items[0].title == "HinweisgeberInnenschutzgesetz" and "Hinweisgeber*" in res.note


def test_rechtssatz_note_and_first_year(monkeypatch):
    doc = {"Metadaten": {"Technisch": {"ID": "JJR_1", "Applikation": "Justiz", "Organ": "OGH"},
                         "Allgemein": {"DokumentUrl": "u"},
                         "Judikatur": {"Dokumenttyp": "Rechtssatz", "Entscheidungsdatum": "2026-07-01",
                                       "EuropeanCaseLawIdentifier": "ECLI:AT:OGH0002:2006:RS0120530",
                                       "Justiz": {"Gericht": "OGH",
                                                  "Rechtssatznummern": {"item": "RS0120530"}}}}}

    async def fake(path, params, limit, page):
        return [doc], 1

    monkeypatch.setattr(at, "_paged", fake)
    res = asyncio.run(at.Austria().search_caselaw(
        "x", limit=10, page=1, filters={"doc_type": "rechtssatz"}))
    assert "First decided 2006" in res.items[0].snippet and "latest" not in res.note.lower() \
        and "most recent decision" in res.note


def test_rechtssatz_date_labelled_and_date_from_filters(monkeypatch):
    def mk(year):
        return {"Metadaten": {"Technisch": {"ID": f"JJR_{year}", "Applikation": "Justiz", "Organ": "OGH"},
                              "Allgemein": {"DokumentUrl": "u"},
                              "Judikatur": {"Dokumenttyp": "Rechtssatz", "Entscheidungsdatum": "2026-05-06",
                                            "Schlagworte": "maximal",
                                            "EuropeanCaseLawIdentifier": f"ECLI:AT:OGH0002:{year}:RS1",
                                            "Justiz": {"Gericht": "OGH",
                                                       "Rechtssatznummern": {"item": "RS1"}}}}}

    async def fake(path, params, limit, page):
        return [mk(1986), mk(2026)], 2

    monkeypatch.setattr(at, "_paged", fake)
    res = asyncio.run(at.Austria().search_caselaw(
        "x", limit=10, page=1, filters={"doc_type": "rechtssatz", "date_from": "2026-01-01"}))
    assert [h.id for h in res.items] == ["JJR_2026"]
    h = res.items[0]
    assert h.date == "" and "Index date 2026-05-06" in h.snippet and "maximal" not in h.snippet


def test_page_past_end_is_empty_not_error(monkeypatch):
    async def fake(path, params):
        if params["Seitennummer"] > 1:
            raise at.SourceError("RIS API returned HTTP 500", 500)
        return {"Hits": {"#text": "6"}}

    monkeypatch.setattr(at, "_get_json", fake)
    assert asyncio.run(at._search("Judikatur", {}, "Ten", 2)) == ([], 6)


def test_compound_article_paragraph_label(monkeypatch):
    seen = {}

    async def fake_search(path, params, size, page_no):
        seen.update(params)
        d = {"Metadaten": {"Technisch": {"ID": "NOR1"}, "Allgemein": {"DokumentUrl": "u"},
                           "Bundesrecht": {"Kurztitel": "DSG", "BrKons": {
                               "ArtikelParagraphAnlage": "Art. 1 § 1"}}}}
        other = {"Metadaten": {**d["Metadaten"], "Bundesrecht": {"Kurztitel": "DSG", "BrKons": {
            "ArtikelParagraphAnlage": "Art. 2 § 1"}}}}
        return [other, d], 2

    async def fake_content(folder, doc_id):
        return b"<html><body><div class='contentBlock'><h1>Text</h1><p>x</p></div></body></html>"

    monkeypatch.setattr(at, "_search", fake_search)
    monkeypatch.setattr(at, "_content", fake_content)
    res = asyncio.run(at.Austria().get_legislation_provision("10001597", "Art. 1 § 1"))
    assert seen["Abschnitt.Typ"] == "Paragraph" and seen["Abschnitt.Von"] == "1"
    assert res.provision == "Art. 1 § 1" and res.url == "u"


def test_rechtssatz_all_dropped_does_not_report_source_total(monkeypatch):
    doc = {"Metadaten": {"Technisch": {"ID": "JJR_1", "Applikation": "Justiz", "Organ": "OGH"},
                         "Allgemein": {"DokumentUrl": "u"},
                         "Judikatur": {"Dokumenttyp": "Rechtssatz", "Entscheidungsdatum": "2026-05-06",
                                       "EuropeanCaseLawIdentifier": "ECLI:AT:OGH0002:1986:RS1",
                                       "Justiz": {"Gericht": "OGH", "Rechtssatznummern": {"item": "RS1"}}}}}

    async def fake(path, params, limit, page):
        return [doc], 6

    monkeypatch.setattr(at, "_paged", fake)
    a = at.Austria()
    f = {"doc_type": "rechtssatz", "date_from": "2026-01-01"}
    r1 = asyncio.run(a.search_caselaw("x", limit=10, page=1, filters=f))
    assert r1.items == [] and r1.total == 0
    r2 = asyncio.run(a.search_caselaw("x", limit=3, page=1, filters=f))
    assert r2.total is None


def test_rechtssatz_past_end_and_text_hint(monkeypatch):
    rs = {"Metadaten": {"Technisch": {"ID": "JJR_1", "Applikation": "Justiz", "Organ": "OGH"},
                        "Allgemein": {"DokumentUrl": "u"},
                        "Judikatur": {"Dokumenttyp": "Rechtssatz", "Entscheidungsdatum": "2026-07-01",
                                      "EuropeanCaseLawIdentifier": "ECLI:AT:OGH0002:2006:RS0120530",
                                      "Justiz": {"Gericht": "OGH",
                                                 "Rechtssatznummern": {"item": "RS0120530"}}}}}
    state = {}

    async def fake(path, params, limit, page):
        return state["r"]

    monkeypatch.setattr(at, "_paged", fake)
    f = {"doc_type": "rechtssatz", "date_from": "2026-01-01"}
    state["r"] = ([rs], 1)
    res = asyncio.run(at.Austria().search_caselaw("x", limit=10, page=1, filters=f))
    assert res.items == [] and "doc_type" in res.note and "'text'" in res.note
    state["r"] = ([], 6)
    res = asyncio.run(at.Austria().search_caselaw("x", limit=10, page=2, filters=f))
    assert res.total == 6 and "past the last page" in res.note
