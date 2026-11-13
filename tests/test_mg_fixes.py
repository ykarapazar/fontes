import asyncio
import json

from world_legal_mcp.jurisdictions import mg


class _R:
    def __init__(self, posts, total):
        self.status_code = 200
        self.headers = {"content-type": "application/json", "X-WP-Total": str(total)}
        self._p = posts
        self.text = ""

    def json(self):
        return self._p


def _post(i, title):
    return {"id": i, "title": {"rendered": title}, "categories": [8], "excerpt": {"rendered": ""}, "link": ""}


def test_caselaw_dedup_relevance(monkeypatch):
    calls = []
    t = "Décision n°01-HCC/D2 du 2 avril 2008 relative à une requête"

    async def get(url, params=None, **kw):
        calls.append(params)
        return _R([_post(566, t), _post(442, t + ".")], 2)
    monkeypatch.setattr(mg._http, "get", get)
    r = asyncio.run(mg.Madagascar().search_caselaw("Air Madagascar"))
    assert [h.id for h in r.items] == ["566"] and r.total == 1
    assert calls[-1]["orderby"] == "relevance"


def test_jo_placeholders():
    assert mg._jo({"num_jo": "VOIR_J.O", "date_jo": "00-00-0000", "page_jo": "2600"}) == ""
    assert mg._jo({"num_jo": "4354", "date_jo": "14-09-2026", "page_jo": "0"}) == "J.O. n°4354 du 14-09-2026"
    assert mg._jo({"num_jo": "4354", "date_jo": "30-07-2026", "page_jo": "2570"}) == \
        "J.O. n°4354 du 30-07-2026, p. 2570"


def test_notes(monkeypatch):
    async def s(*a, **k):
        return [], 0
    monkeypatch.setattr(mg, "_cnl_search", s)
    n = lambda q: asyncio.run(mg.Madagascar().search_legislation(q)).note
    assert "Co2010" in n("Constitution")
    assert "Code pénal" in n("Code pénal malgache")
    assert "L66-003" in n("Code civil")
    assert "Co2010" not in n("Code du travail")


def test_caselaw_multiword_is_exact_phrase(monkeypatch):
    calls = []

    async def get(url, params=None, **kw):
        calls.append(params)
        return _R([], 0)
    monkeypatch.setattr(mg._http, "get", get)
    r = asyncio.run(mg.Madagascar().search_caselaw("contrat de travail"))
    assert calls[-1]["search"] == '"contrat de travail"' and "exact phrase" in r.note
    asyncio.run(mg.Madagascar().search_caselaw("BIANCO"))
    assert calls[-1]["search"] == "BIANCO"


def test_legislation_limit_not_capped_at_10(monkeypatch):
    calls = []

    async def s(form, ep, q, offset, limit):
        calls.append((offset, limit))
        return [{"int_name": f"L{i}"} for i in range(offset, min(offset + limit, 40))], 40
    monkeypatch.setattr(mg, "_cnl_search", s)
    r = asyncio.run(mg.Madagascar().search_legislation("procédure civile", limit=25, page=2))
    assert calls == [(25, 25)] and [h.id for h in r.items] == [f"L{i}" for i in range(25, 40)] and r.total == 40


def test_legislation_page_past_end_is_empty(monkeypatch):
    posts = []

    class _H:
        def __init__(self, text):
            self.status_code, self.text, self.headers = 200, text, {"content-type": "text/html"}

    async def post(url, data):
        posts.append(url)
        return _H("12 résultats")
    monkeypatch.setattr(mg._http, "post", post)
    rows, total = asyncio.run(mg._cnl_search("page_find_direct_mots", "page_data_result_direct_mots", "x", 25, 25))
    assert rows == [] and total == 12 and len(posts) == 1     # no data request past the end
