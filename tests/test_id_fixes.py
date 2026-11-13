import asyncio

from world_legal_mcp import _http
from world_legal_mcp.jurisdictions import id as idj

ROWS = [
    {"jns": "UU", "nama_jenis": "Undang-Undang", "no_peraturan": "27", "tahun": "2022",
     "tentang": "PELINDUNGAN DATA PRIBADI", "status_hukum": "berlaku", "tgl_di": "2022-10-17"},
    {"jns": "UU", "nama_jenis": "Undang-Undang", "no_peraturan": "1", "tahun": "1946",
     "tentang": "HUKUM PIDANA", "status_hukum": "sebagian", "tgl_di": "1946-01-01"},
]


def _run(monkeypatch, q, **kw):
    async def post(path, body, what):
        t = body["tentang"].lower().split()
        rows = [r for r in ROWS if any(w in _http.clean(idj._title(r)).lower() for w in t)]
        return {"data": rows[body["start"]:body["start"] + body["length"]], "jml": len(rows)}
    monkeypatch.setattr(idj, "_post", post)
    return asyncio.run(idj.Indonesia().search_legislation(q, filters={"type": "UU"}, **kw))


def test_all_words_required(monkeypatch):
    r = _run(monkeypatch, "Kitab Hukum Perdata")
    assert r.items == [] and r.total == 0 and "1847" in r.note


def test_multiword_and(monkeypatch):
    r = _run(monkeypatch, "perlindungan data pribadi")
    assert [h.id for h in r.items] == ["UU 27/2022"]


def test_spelling_variant(monkeypatch):
    r = _run(monkeypatch, "perlindungan")
    assert [h.id for h in r.items] == ["UU 27/2022"] and "pelindungan" in r.note


def test_provision_status_note(monkeypatch):
    async def law(self, id):
        return ({"id": "UU 13/2003", "title": "t", "url": "u", "row": {"status_hukum": "sebagian"}},
                [], ([], {"59": "**Pasal 59**\n\nx"}, ""))
    monkeypatch.setattr(idj.Indonesia, "_law", law)
    p = asyncio.run(idj.Indonesia().get_legislation_provision("UU 13/2003", "59"))
    assert "As enacted in 2003" in p.text and "sebagian" in p.text


def test_mend_split_words():
    paras = ["untuk pekerjaan tertentu, didasarkan atas memenuhi.",
             "dibuat untu k pekerjaan yang didas arkan dan m emenuhi syarat; memenuhi; untuk; untuk."]
    out = idj._mend(paras)[1]
    assert "untuk pekerjaan" in out and "didasarkan dan" in out and "memenuhi syarat" in out
    assert idj._mend(["yang dan a b"]) == ["yang dan a b"]


def test_provision_names_amending_law(monkeypatch):
    row = {"status_hukum": "sebagian", "idperaturan": "P1", "diubah_sebagian": "P2"}
    meta = {"id": "UU 13/2003", "title": "T", "url": "u", "row": row}
    law = (meta, [], ([], {"59": "**Pasal 59**\n\nx"}, ""))

    async def rel(self, r):
        return {"Partly amended by": "UU 6/2023 (CIPTA KERJA)"}
    async def _law(self, id):
        return law
    monkeypatch.setattr(idj.Indonesia, "_law", _law)
    monkeypatch.setattr(idj.Indonesia, "_relations", rel)
    p = asyncio.run(idj.Indonesia().get_legislation_provision("UU 13/2003", "59"))
    assert "Partly amended by: UU 6/2023" in p.text


def test_provision_ocr_caveat(monkeypatch):
    async def law(self, id):
        return ({"id": "UU 27/2022", "title": "t", "url": "u", "row": {"status_hukum": "berlaku"}},
                [], ([], {"1": "**Pasal 1**\n\nx"}, ""))
    monkeypatch.setattr(idj.Indonesia, "_law", law)
    p = asyncio.run(idj.Indonesia().get_legislation_provision("UU 27/2022", "1"))
    assert "OCR" in p.text
