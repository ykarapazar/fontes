"""Live smoke tests against the Knesset OData service and the Open Law Book on
Hebrew Wikisource. Needs network."""
from world_legal_mcp import server


async def test_il_search_filters():
    out = await server.search_legislation("il", "כבוד", limit=5,
                                          filters={"basic_law": "true", "status": "in force"})
    assert "חוק-יסוד: כבוד האדם וחירותו" in out and '"2000046"' in out
    bad = await server.search_legislation("il", "חוק", filters={"status": "xx"})
    assert "Bad request" in bad


async def test_il_provision_label_variants():
    for label in ("סעיף 25", "25", "ס' 25", "section 25"):
        out = await server.get_legislation_provision("il", "2000292", label)
        assert "אומד דעתם" in out, label
    letter = await server.get_legislation_provision("il", "2000046", "1א")
    assert "חוק־יסוד זה, מטרתו" in letter


async def test_il_toc_and_ordinance_title():
    # Knesset name "פקודת הנזיקין [נוסח חדש]" -> Wikisource "פקודת הנזיקין"
    toc = await server.get_legislation_toc("il", "2000894", keyword="רשלנות")
    assert "סעיף 35" in toc
    missing = await server.get_legislation_provision("il", "2000292", "סעיף 999")
    assert "Not found" in missing and "סעיף 999" in missing


async def test_il_official_gazette_pdf_links():
    out = await server.get_legislation_text("il", "2000046")
    assert "fs.knesset.gov.il//12/law/12_lsr_211801.PDF" in out


async def test_il_official_gazette_text():
    # 1992 scan with an OCR layer: rebuilt right-to-left, soft hyphen and brackets fixed
    out = await server.get_legislation_text("il", "2000046/original")
    assert "חוק-יסוד: כבוד האדם וחירותו" in out and "אין פוגעים בקנינו של אדם" in out
    assert "2000046/155642" in out                                  # amending law id listed
    # born-digital 2018 PDF: HadasaMFO ',' '.' glyphs mapped to letters are repaired
    page = await server.get_legislation_provision("il", "2073986/original", "page 2")
    assert "ארץ ישראל היא מולדתו ההיסטורית של העם היהודי, שבה קמה מדינת ישראל." in page
    bad = await server.get_legislation_text("il", "2000046/xyz")
    assert "Bad request" in bad


async def test_il_long_name_search_and_ordinance_pdf():
    # >3 words used to trip the Knesset WAF (HTTP 473); only the 3 longest are sent
    out = await server.search_legislation("il", "חוק יסוד כבוד האדם וחירותו", limit=5)
    assert '"2000046"' in out
    # Mandate ordinance: official text from the KNS_DocumentLaw [נוסח חדש] PDF
    page = await server.get_legislation_provision("il", "2000894/original", "עמוד 1")
    assert "פקודת הנזיקין" in page
