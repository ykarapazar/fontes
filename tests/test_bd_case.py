from world_legal_mcp.jurisdictions import bd


def test_case_from_file_restores_lost_number():
    assert bd._case_from_file("Civil Appeal /2017", "1500568_CA_No_470_471_of_2017_Final.pdf") == "Civil Appeal No. 470, 471 of 2017"
    assert bd._case_from_file("Criminal Petition /2022", "2011581_Crl.P._No.214_of_2022-final.pdf") == "Criminal Petition No. 214 of 2022"


def test_case_no_uppercase_and_decision_date():
    head = "PRESENT :\nMr. Justice A\nCIVIL APPEAL NO.293 OF 2019.\n"
    assert bd._CASE_NO.search(head)[1] == "CIVIL APPEAL NO.293 OF 2019"
    m = bd._JDATE.search("(judgment and order dated 13.03.2017)\nDate of Judgment. : The 11 th May, 202 3.")
    assert (m[1], m[2], m[3]) == ("11", "May", "202 3")


def test_lead_case_not_impugned_or_with_line():
    import re
    head = ("PRESENT:\nMr. Justice A\nCIVIL APPEAL NOS.23-24 AND 55-56 OF 2020\nWITH\n"
            "CIVIL PETITION FOR LEAVE TO APPEAL NOS.3204 OF 2018\n")
    assert bd._CASE_NO.search(head)[1] == "CIVIL APPEAL NOS.23-24 AND 55-56 OF 2020"
    head = ("Present:\nMr. Justice A\nCRIMINAL PETITION FOR LEAVE TO APPEAL\nNOS.1059-1061 OF 2024\n"
            "(From the orders dated 30.05.2024 passed by the High Court Division in Criminal\n"
            "Revision Nos.3178,3180 & 3179 of 2024 respectively)\n")
    lead = re.split(r"^\s*\(\s*From\b", head, maxsplit=1, flags=re.M | re.I)[0]
    assert " ".join(bd._CASE_NO.search(lead)[1].split()) == "CRIMINAL PETITION FOR LEAVE TO APPEAL NOS.1059-1061 OF 2024"
    assert bd._JDATE_NUM.search("Date of judgment : 19-10-2022")[3] == "2022"


def test_bijoy_garble_detected():
    assert len(bd._BIJOY.findall("13| Rvwgb msµvšÍ weavb|- †Kvb e¨w³‡K " * 10)) > 20
    assert not bd._BIJOY.findall("Plain English judgment text, section 13 of the Ain.")


def test_bijoy_converted_to_unicode():
    src = "(L) Zvnvi weiæ‡× AvbxZ Awf‡hv‡M wZwb †`vlx mve¨¯’ nIqvi\ng‡g© Av`vjZ mš‘ó nb|\nEnglish line stays."
    out, clean = bd._bijoy_text(src)
    assert clean
    assert out.split("\n")[0] == "(খ) তাহার বিরুদ্ধে আনীত অভিযোগে তিনি দোষী সাব্যস্থ হওয়ার"
    assert out.split("\n")[1] == "মর্মে আদালত সন্তুষ্ট হন।"
    assert out.endswith("English line stays.")


def _row(file, desc):
    return (f"<tr class='font_e_12'><td>1</td><td><a href='/resources/documents/{file}'>Criminal Petition 1/2022</a>"
            f" Uploaded on : 01-JAN-22</td><td>A -Versus- B</td><td>{desc}</td></tr>")


def test_caselaw_search_is_case_insensitive_and_word_fallback(monkeypatch):
    import asyncio
    sent = []

    class R:
        status_code = 200

        def __init__(self, t):
            self.text = t

    async def post(url, data=None, **kw):     # the site matches case-sensitively and literally
        t = data["short_desc"]
        sent.append(t)
        rows = [(f, d) for f, d in (("a.pdf", "Money Laundering bail"),
                                    ("b.pdf", "bail under section 498 of the Code of Criminal Procedure"),
                                    ("c.pdf", "bail granted")) if t in d]
        return R("<table>" + "".join(_row(f, d) for f, d in rows) + "</table>")

    monkeypatch.setattr(bd._http, "post", post)
    bd._search_cache.clear()
    adapter = bd.Bangladesh()
    res = asyncio.run(adapter.search_caselaw("money laundering", filters={"division": "appellate"}))
    assert [h.id for h in res.items] == ["a.pdf"]
    res = asyncio.run(adapter.search_caselaw("bail section 498 Code of Criminal Procedure", filters={"division": "appellate"}))
    assert [h.id for h in res.items] == ["b.pdf"]


def test_title_search_bengali_spacing(monkeypatch):
    import asyncio

    class R:
        status_code = 200
        content = b""
        text = ("<div id='searchtext'><div class='result'><h3><a href='/act-1088.html'>"
                "মানিলন্ডারিং প্রতিরোধ আইন, ২০১২</a></h3><p>x</p></div></div> 1 to 1 of 1")

    async def get(url, params=None, **kw):
        return R() if params["q"] == "লন্ডারিং" else type("E", (R,), {"text": "1 to 0 of 0"})()

    monkeypatch.setattr(bd._http, "get", get)
    bd._search_cache.clear()
    res = asyncio.run(bd.Bangladesh().search_legislation("মানি লন্ডারিং প্রতিরোধ আইন"))
    assert [h.id for h in res.items] == ["1088"]


def test_toc_provision_ascii_digits_for_bengali_sections():
    import asyncio
    page = ('<html><body><section class="bg-act-section"><h3>মানিলন্ডারিং আইন</h3><h4>(নং ৫)</h4></section>'
            '<div class="search-here"><p class="act-section-name"><a href="/act-1/section-9.html">১৩। জামিন</a></p>'
            '<p class="act-section-name"><a href="/act-1/section-10.html">উপধারা</a></p></div></body></html>')

    async def fake(path, what):
        return page
    old = bd._get_laws
    bd._get_laws = fake
    try:
        bd._act_cache.clear()
        a = asyncio.run(bd._act("77"))
    finally:
        bd._get_laws = old
        bd._act_cache.clear()
    assert [e.provision for e, _ in a["entries"]] == ["13", "13"]
    assert a["entries"][0][0].title.startswith("১৩")
    assert bd._norm("13") == bd._norm("১৩")


def test_english_query_is_searched_in_bengali_and_superseded_flagged(monkeypatch):
    import asyncio
    sent = []

    def page(aid, title):
        return ("<div>1 to 1 of 1</div><div id='searchtext'><div class='result'>"
                f"<h3><a href='/act-{aid}.html'>{title}</a></h3><p>x</p></div></div>").encode("utf-16")

    class R:
        status_code = 200
        def __init__(self, c): self.content = c

    async def fake_get(url, params=None, **kw):
        sent.append(params["q"])
        return R(page(886, "মানিলণ্ডারিং প্রতিরোধ আইন, ২০০২"))

    monkeypatch.setattr(bd._http, "get", fake_get)
    bd._search_cache.clear()
    res = asyncio.run(bd.Bangladesh().search_legislation("Money Laundering Prevention Act"))
    assert sent == ["মানিলন্ডারিং"]
    assert "repealed" in res.items[0].status
    assert "searched as the Bengali" in res.note
