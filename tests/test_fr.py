"""Offline tests for the France adapter: PISTE token flow, Judilibre / Légifrance parsing,
and the no-key behaviour. Fixtures are hand-written from the OpenAPI examples
(tests/fixtures/fr); no network."""
import json
from pathlib import Path

import httpx
import pytest

from world_legal_mcp import _http, registry, server
from world_legal_mcp.base import BadRequest, NotFound, SourceError
from world_legal_mcp.jurisdictions import fr

FIX = Path(__file__).parent / "fixtures" / "fr"


def _fix(name):
    return json.loads((FIX / name).read_text(encoding="utf-8"))


@pytest.fixture
def keys(monkeypatch):
    monkeypatch.setenv(fr.ENV_ID, "test-id")
    monkeypatch.setenv(fr.ENV_SECRET, "test-secret")
    monkeypatch.delenv(fr.ENV_SANDBOX, raising=False)
    fr._token.clear()
    fr._texts.clear()
    monkeypatch.setattr(_http, "_intervals", {})   # no throttling between mocked calls


@pytest.fixture
def nokeys(monkeypatch):
    monkeypatch.delenv(fr.ENV_ID, raising=False)
    monkeypatch.delenv(fr.ENV_SECRET, raising=False)
    fr._token.clear()


class Piste:
    """Mock PISTE: token endpoint + Judilibre + Légifrance, recording every request."""

    def __init__(self, expires_in=3600, reject_first_api_call=False):
        self.calls = []
        self.tokens = 0
        self.expires_in = expires_in
        self.reject_first = reject_first_api_call

    def __call__(self, req: httpx.Request) -> httpx.Response:
        self.calls.append(req)
        path = req.url.path
        if path == "/api/oauth/token":
            self.tokens += 1
            return httpx.Response(200, json={"access_token": f"tok{self.tokens}", "token_type": "Bearer",
                                             "expires_in": self.expires_in, "scope": "openid"})
        if self.reject_first:
            self.reject_first = False
            return httpx.Response(401)
        if req.headers.get("authorization") != f"Bearer tok{self.tokens}":
            return httpx.Response(401)
        if path.endswith("/judilibre/v1.0/search"):
            return httpx.Response(200, json=_fix("judilibre_search.json"))
        if path.endswith("/judilibre/v1.0/decision"):
            if req.url.params["id"] != "5fca7d162a251e6bf9c78514":
                return httpx.Response(404)
            return httpx.Response(200, json=_fix("judilibre_decision.json"))
        if path.endswith("/lf-engine-app/search"):
            return httpx.Response(200, json=_fix("legifrance_search.json"))
        if path.endswith("/consult/legiPart"):
            return httpx.Response(200, json=_fix("legifrance_legipart.json"))
        if path.endswith("/consult/getArticleWithIdAndNum"):
            if json.loads(req.content)["num"] != "1240":
                return httpx.Response(404)
            return httpx.Response(200, json=_fix("legifrance_article.json"))
        return httpx.Response(404)


@pytest.fixture
def piste(monkeypatch, keys):
    mock = Piste()
    monkeypatch.setattr(_http, "_client", httpx.AsyncClient(transport=httpx.MockTransport(mock)))
    return mock


# ------------------------------------------------------------------ no keys
def test_without_keys_nothing_is_offered(nokeys):
    j = registry.get("fr")
    assert j is not None and j.code == "fr"
    assert j.supported() == []
    assert j.coverage() == {"caselaw": False, "legislation": False}
    assert fr.ENV_ID in j.notes and fr.ENV_SECRET in j.notes and "Inactive" in j.notes


async def test_without_keys_tools_refuse_cleanly(nokeys):
    out = await server.search_caselaw("fr", "expropriation")
    assert "not supported for France (fr)" in out and "Supported for fr: none" in out
    listing = await server.list_jurisdictions("france")
    assert "Inactive" in listing and fr.ENV_ID in listing and "needs free key" in listing
    with pytest.raises(SourceError, match=fr.ENV_ID):
        await fr._get_token()


def test_one_key_is_not_enough(monkeypatch, nokeys):
    monkeypatch.setenv(fr.ENV_ID, "only-id")
    assert registry.get("fr").supported() == []


def test_with_keys_everything_is_offered(keys):
    j = registry.get("fr")
    assert j.supported() == ["search_caselaw", "get_decision", "search_legislation",
                             "get_legislation_toc", "get_legislation_provision", "get_legislation_text"]
    assert j.coverage() == {"caselaw": True, "legislation": True}


# --------------------------------------------------------------- token flow
async def test_token_is_fetched_once_and_cached(piste):
    j = registry.get("fr")
    await j.search_caselaw("expropriation", limit=2, page=1, filters={})
    await j.get_decision("5fca7d162a251e6bf9c78514")
    token_calls = [c for c in piste.calls if c.url.path == "/api/oauth/token"]
    assert len(token_calls) == 1
    t = token_calls[0]
    assert t.url.host == "oauth.piste.gouv.fr"
    form = dict(httpx.QueryParams(t.content.decode()))
    assert form == {"grant_type": "client_credentials", "client_id": "test-id",
                    "client_secret": "test-secret", "scope": "openid"}
    api = [c for c in piste.calls if c.url.path != "/api/oauth/token"]
    assert all(c.url.host == "api.piste.gouv.fr" for c in api)
    assert all(c.headers["authorization"] == "Bearer tok1" for c in api)


async def test_expired_token_is_refreshed(monkeypatch, keys):
    mock = Piste(expires_in=0)   # margin makes it live 30 s; force expiry below
    monkeypatch.setattr(_http, "_client", httpx.AsyncClient(transport=httpx.MockTransport(mock)))
    j = registry.get("fr")
    await j.get_decision("5fca7d162a251e6bf9c78514")
    fr._token["expires"] = 0
    await j.get_decision("5fca7d162a251e6bf9c78514")
    assert mock.tokens == 2


async def test_401_drops_token_and_retries_once(monkeypatch, keys):
    mock = Piste(reject_first_api_call=True)
    monkeypatch.setattr(_http, "_client", httpx.AsyncClient(transport=httpx.MockTransport(mock)))
    d = await registry.get("fr").get_decision("5fca7d162a251e6bf9c78514")
    assert d.id == "5fca7d162a251e6bf9c78514" and mock.tokens == 2


async def test_bad_credentials_and_unsubscribed_api(monkeypatch, keys):
    monkeypatch.setattr(_http, "_client", httpx.AsyncClient(transport=httpx.MockTransport(
        lambda req: httpx.Response(401, json={"error": "invalid_client"}))))
    with pytest.raises(SourceError, match="refused the client credentials"):
        await registry.get("fr").get_decision("5fca7d162a251e6bf9c78514")

    def forbidden(req):
        if req.url.path == "/api/oauth/token":
            return httpx.Response(200, json={"access_token": "t", "expires_in": 3600})
        return httpx.Response(403)
    fr._token.clear()
    monkeypatch.setattr(_http, "_client", httpx.AsyncClient(transport=httpx.MockTransport(forbidden)))
    with pytest.raises(SourceError, match="subscribe the application to Légifrance"):
        await registry.get("fr").search_legislation("code civil", limit=5, page=1, filters={})


async def test_sandbox_switch(monkeypatch, piste):
    monkeypatch.setenv(fr.ENV_SANDBOX, "1")
    await registry.get("fr").get_decision("5fca7d162a251e6bf9c78514")
    hosts = {c.url.host for c in piste.calls}
    assert hosts == {"sandbox-oauth.piste.gouv.fr", "sandbox-api.piste.gouv.fr"}
    assert "sandbox" in registry.get("fr").notes


# ----------------------------------------------------------------- Judilibre
async def test_search_caselaw_parses_hits_and_sends_params(piste):
    r = await registry.get("fr").search_caselaw(
        "expropriation", limit=2, page=1,
        filters={"jurisdiction": "cc,ca", "sort": "date", "date_start": "2018-01-01"})
    assert r.total == 341 and len(r.items) == 2
    h = r.items[0]
    assert h.id == "5fca7d162a251e6bf9c78514"
    assert h.title == "Cour de cassation, Troisième chambre civile 17-18.194"
    assert h.date == "2018-12-20" and h.case_number == "17-18.194"
    assert h.snippet.startswith("Le titulaire d'une autorisation")
    assert h.url == "https://www.courdecassation.fr/decision/5fca7d162a251e6bf9c78514"
    ca = r.items[1]
    assert ca.court.startswith("Cour d'appel de Chambéry") and ca.case_number == "20/00804"
    assert ca.snippet == "procédure d'expropriation engagée"   # highlight, <em> stripped
    q = [c for c in piste.calls if c.url.path.endswith("/search")][0].url.params
    assert q.get_list("jurisdiction") == ["cc", "ca"]
    assert q["page"] == "0" and q["page_size"] == "25" and q["sort"] == "date"
    assert q["resolve_references"] == "true" and q["date_start"] == "2018-01-01"


async def test_search_caselaw_caps_limit(piste):
    with pytest.raises(BadRequest, match="at most 100"):
        await registry.get("fr").search_caselaw("expropriation", limit=101, page=1, filters={})


async def test_search_caselaw_pages_by_fixed_25_and_slices(monkeypatch, keys):
    """limit=20 page=2 (hits 21-40) spans source pages 0 and 1 of 25; same requests whatever limit."""
    asked = []

    def handler(req):
        if req.url.path == "/api/oauth/token":
            return httpx.Response(200, json={"access_token": "t", "expires_in": 3600})
        q = req.url.params
        asked.append((q["page"], q["page_size"]))
        p = int(q["page"])
        rows = [{"id": f"{i:024x}", "jurisdiction": "cc", "number": str(i)} for i in range(p * 25, p * 25 + 25)]
        return httpx.Response(200, json={"total": 60, "results": rows})
    monkeypatch.setattr(_http, "_client", httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    r = await registry.get("fr").search_caselaw("x", limit=20, page=2, filters={})
    assert asked == [("0", "25"), ("1", "25")]
    assert [h.case_number for h in r.items] == [str(i) for i in range(20, 40)] and r.total == 60
    assert "different order for the same request" in r.note


async def test_caselaw_filter_validation(keys):
    j = registry.get("fr")
    for f in ({"jurisdiction": "conseil_etat"}, {"sort": "newest"}, {"date_start": "13/05/2021"},
              {"operator": "near"}):
        with pytest.raises(BadRequest):
            await j.search_caselaw("x", limit=5, page=1, filters=f)


async def test_get_decision_parses_full_text(piste):
    d = await registry.get("fr").get_decision(
        "https://www.courdecassation.fr/decision/5fca7d162a251e6bf9c78514")
    assert d.id == "5fca7d162a251e6bf9c78514" and d.date == "2018-12-20"
    assert d.title == "Cour de cassation, Troisième chambre civile 17-18.194"
    assert "\r" not in d.text and "\n\n\n" not in d.text
    assert "Audience publique du 20 décembre 2018" in d.text
    assert d.metadata["ECLI"] == "ECLI:FR:CCASS:2018:C301117"
    assert "L. 322-1" in d.metadata["Visa"] and d.summary.startswith("Le titulaire")


async def test_get_decision_errors(piste):
    j = registry.get("fr")
    with pytest.raises(BadRequest):
        await j.get_decision("17-18.194")
    with pytest.raises(NotFound):
        await j.get_decision("aaaaaaaaaaaaaaaaaaaaaaaa")


# ---------------------------------------------------------------- Légifrance
async def test_search_legislation(piste):
    r = await registry.get("fr").search_legislation("dommage", limit=10, page=2, filters={"fond": "loda"})
    assert r.total == 1560
    assert [h.id for h in r.items] == ["LEGITEXT000006070721", "JORFTEXT000000886460"]
    code, loi = r.items
    assert code.title == "Code civil" and code.status == "VIGUEUR"
    assert code.snippet.startswith("Article 1240: Tout fait quelconque") and "<" not in code.snippet
    assert loi.number == "78-17" and loi.date == "1978-01-06"
    assert loi.url == "https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000000886460"
    body = json.loads([c for c in piste.calls if c.url.path.endswith("/lf-engine-app/search")][0].content)
    assert body["fond"] == "LODA_DATE"
    assert body["recherche"]["pageNumber"] == 2 and body["recherche"]["pageSize"] == 10
    assert body["recherche"]["champs"][0]["criteres"][0]["valeur"] == "dommage"
    with pytest.raises(BadRequest):
        await registry.get("fr").search_legislation("x", limit=5, page=1, filters={"fond": "kali"})


async def test_toc_provision_and_text(piste):
    j = registry.get("fr")
    toc = await j.get_legislation_toc("LEGITEXT000006070721")
    assert toc.title == "Code civil"
    assert toc.url == "https://www.legifrance.gouv.fr/codes/texte_lc/LEGITEXT000006070721"
    assert [(e.title, e.level, e.provision) for e in toc.entries][1:] == [
        ("Sous-titre II : La responsabilité extracontractuelle", 1, ""),
        ("Article 1240", 2, "Article 1240"), ("Article 1241", 2, "Article 1241")]
    for label in ("Article 1240", "art. 1240", "1240"):
        p = await j.get_legislation_provision("LEGITEXT000006070721", label)
        assert p.provision == "Article 1240" and p.law_title == "Code civil"
        assert p.text.startswith("## Article 1240\n\nTout fait quelconque")
        assert p.url == "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000032041571"
        assert p.as_of == "2016-10-01"
    with pytest.raises(NotFound):
        await j.get_legislation_provision("LEGITEXT000006070721", "Article 9999")
    t = await j.get_legislation_text("LEGITEXT000006070721")
    assert "**Article 1241**" in t.text and "<p>" not in t.text
    assert len([c for c in piste.calls if c.url.path.endswith("/legiPart")]) == 1   # cached


def test_provision_label_variants():
    assert fr._norm_provision("Article L. 121-1") == "L121-1"
    assert fr._norm_provision("l121-1") == "L121-1"
    assert fr._norm_provision("Art. R* 123-4") == "R123-4"
    assert fr._norm_provision("1240") == "1240"
    with pytest.raises(BadRequest):
        fr._norm_provision("Article ")


def test_law_id_validation():
    assert fr._text_id("https://www.legifrance.gouv.fr/codes/texte_lc/LEGITEXT000006070721/") == "LEGITEXT000006070721"
    with pytest.raises(BadRequest):
        fr._text_id("Code civil")


# ------------------------------------------------- Légifrance case law + JORF


def test_lf_caselaw_body_courts_dates_sort():
    b = fr._lf_caselaw_body("responsabilité", ["caa", "tc"], 5, 2,
                            {"date_start": "2020-01-01", "sort": "date", "operator": "or"})
    assert b["fond"] == "CETAT" and b["recherche"]["sort"] == "DATE_DESC"
    assert b["recherche"]["pageNumber"] == 2 and b["recherche"]["pageSize"] == 5
    q, title = b["recherche"]["champs"]
    assert q["criteres"][0]["typeRecherche"] == "UN_DES_MOTS"
    assert title["typeChamp"] == "TITLE" and title["operateur"] == "OU"
    assert [c["valeur"] for c in title["criteres"]] == ["CAA", "Cour administrative d'appel",
                                                        "Tribunal des conflits"]
    (d,) = b["recherche"]["filtres"]
    assert d["facette"] == "DATE_DECISION" and d["dates"]["start"] == "2020-01-01"
    c = fr._lf_caselaw_body("liberté", ["constit"], 5, 1, {})
    assert c["fond"] == "CONSTIT" and len(c["recherche"]["champs"]) == 1
    assert c["recherche"]["champs"][0]["criteres"][0]["typeRecherche"] == "TOUS_LES_MOTS_DANS_UN_CHAMP"


async def test_lf_caselaw_validation(keys):
    j = registry.get("fr")
    for f in ({"jurisdiction": "ce,cc"}, {"jurisdiction": "ce,constit"}, {"jurisdiction": "ce", "chamber": "civ1"},
              {"jurisdiction": "ta", "date_end": "2020"}, {"jurisdiction": "caa", "sort": "newest"}):
        with pytest.raises(BadRequest):
            await j.search_caselaw("x", limit=5, page=1, filters=f)


def test_lf_title_parsing_and_urls():
    assert fr._title_number("CAA de PARIS, 1ère chambre, 06/11/2026, 25PA00337, Inédit au recueil Lebon") == "25PA00337"
    assert fr._title_number("Tribunal des Conflits, , 08/02/2021, C4205, Publié") == "C4205"
    assert fr._title_number("Décision 2020-858/859 QPC - 02 octobre 2020 - M. G") == "2020-858/859 QPC"
    assert fr._title_date("Tribunal administratif de Rouen, du 3 février 1999, 981234") == "1999-02-03"
    assert fr._title_date("Conseil d'État, 11/02/2026, 498240") == "2026-02-11"
    assert fr._lf_decision_url("CONSTEXT000043596386").endswith("/cons/id/CONSTEXT000043596386")
    assert fr._lf_decision_url("CETATEXT000053464527").endswith("/ceta/id/CETATEXT000053464527")
    assert fr._ms_date(32472144000000) == ""          # 2999-01-01 = no date
    assert fr._article_url("JORFARTI000028933615").endswith("/jorf/article_jo/JORFARTI000028933615")


def test_jorf_search_body_has_no_version_filter():
    assert fr._search_body("décret", 5, 1, "JORF")["recherche"]["filtres"] == []
    assert fr._search_body("décret", 5, 1, "CODE_DATE")["recherche"]["filtres"][0]["facette"] == "DATE_VERSION"


def test_body_md_keeps_paragraph_breaks():
    from world_legal_mcp.jurisdictions.fr import _body_md
    out = _body_md("<p></p>   Chacun a droit.<p></p><p></p>   Les juges peuvent.<p></p>")
    assert "Chacun a droit." in out and "Les juges peuvent." in out
    assert "droit.Les" not in out and "\n\n" in out


def test_judilibre_date_sort_defaults_to_and_operator():
    assert fr._judilibre_params("bail", 5, 1, {"sort": "date"})["operator"] == "and"
    assert fr._judilibre_params("bail", 5, 1, {"sort": "date", "operator": "or"})["operator"] == "or"
    assert "operator" not in fr._judilibre_params("bail", 5, 1, {})


async def test_lf_caselaw_loose_match_is_flagged(monkeypatch, piste):
    hit = {"titles": [{"cid": "CETATEXT000007607588", "title": "Tribunal des conflits, du 29 février 1908, 00624"}],
           "sections": [{"extracts": [{"values": ["tribunal des conflits"]}]}]}
    real = piste.__call__

    def handler(req):
        if req.url.path.endswith("/lf-engine-app/search"):
            return httpx.Response(200, json={"totalResultNumber": 1, "results": [hit]})
        return real(req)
    monkeypatch.setattr(_http, "_client", httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    j = registry.get("fr")
    r = await j.search_caselaw("Blanco", limit=5, page=1, filters={"jurisdiction": "tc"})
    assert r.items == [] and "No decision matching 'Blanco' was found" in r.note
    r = await j.search_caselaw("tribunal conflits", limit=5, page=1, filters={"jurisdiction": "tc"})
    assert "loose" not in r.note


async def test_judilibre_total_above_cap_is_explained(monkeypatch, piste):
    real = piste.__call__

    def handler(req):
        if req.url.path.endswith("/judilibre/v1.0/search"):
            return httpx.Response(200, json={"total": 549842, "results": []})
        return real(req)
    monkeypatch.setattr(_http, "_client", httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    r = await registry.get("fr").search_caselaw("x", limit=5, page=1, filters={})
    assert "549,842 matches" in r.note and "first 10,000" in r.note


def test_legifrance_limit_over_100_rejected():
    # Légifrance pages are at most 100; a bigger limit used to skip hits on page 2+.
    import pytest
    from world_legal_mcp.base import BadRequest
    from world_legal_mcp.jurisdictions.fr import _lf_body
    assert _lf_body("LODA_DATE", [], [], 100, 2)["recherche"]["pageSize"] == 100
    with pytest.raises(BadRequest):
        _lf_body("LODA_DATE", [], [], 101, 2)
