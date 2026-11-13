"""France: judicial case law from Judilibre (Cour de cassation open data, also appeal courts and
first-instance courts); administrative case law (Conseil d'État, CAA, TA, Tribunal des conflits)
and Conseil constitutionnel decisions from the Légifrance API fonds CETAT and CONSTIT;
legislation (codes, LODA, Journal officiel) from the Légifrance API (DILA). Both run behind the
PISTE gateway and need a free PISTE account: OAuth2 client credentials in
WLM_FR_PISTE_CLIENT_ID and WLM_FR_PISTE_CLIENT_SECRET. Without both, every tool reports
itself as unsupported (supports() is False) and the notes say which keys are missing.
WLM_FR_PISTE_SANDBOX=1 switches to the PISTE sandbox (its data lags production).

Written from the public docs only, before any key existed (2026-11-10):
  * Judilibre OpenAPI 3.0.2 (v1.2.5):
    https://github.com/Cour-de-cassation/judilibre-search/blob/dev/public/JUDILIBRE-public.json
    and its README (base URLs, terms):
    https://github.com/Cour-de-cassation/judilibre-search/blob/dev/README.md
  * Cour de cassation PISTE tutorials (account set-up, production URL, page_size):
    https://github.com/Cour-de-cassation/judilibre-tutoriels
  * Légifrance OpenAPI (Swagger 2.0, v1.6.2.5), linked from data.gouv.fr/dataservices/legifrance:
    https://raw.githubusercontent.com/betagouv/api_gouv_swaggers/main/swaggers/api-legifrance-v2.json
  * PISTE user guide (token URLs, client_credentials form body):
    https://piste.gouv.fr/images/com_apiportal/documentation/UserGuide_navigation_EN.pdf
  * Légifrance API CGU: https://piste.gouv.fr/images/cgu/DILA_Legifrance_Beta_v2.pdf
  * Production Légifrance path /dila/legifrance/lf-engine-app (the Swagger still says
    /dila/legifrance-beta/...): SocialGouv's client, a French government team,
    https://github.com/SocialGouv/dila-api-client/blob/master/src/constants.ts

Unverified until real keys exist (see research/fr.md):
  * Judilibre's docs show a `KeyId` header; we send the PISTE OAuth bearer token instead,
    which PISTE issues for every API an app is subscribed to.
  * Légifrance /search body, `DATE_VERSION` filter, `PERTINENCE` sort and epoch-ms dates
    come from DILA's "exemples d'utilisation" document, not the Swagger.
  * The shape of the search `extracts` and the legiPart tree beyond the Swagger schema.
"""
from __future__ import annotations

import datetime
import os
import re
import time
import unicodedata

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

ENV_ID = "WLM_FR_PISTE_CLIENT_ID"
ENV_SECRET = "WLM_FR_PISTE_CLIENT_SECRET"
ENV_SANDBOX = "WLM_FR_PISTE_SANDBOX"

PROD = {"oauth": "https://oauth.piste.gouv.fr/api/oauth/token", "api": "https://api.piste.gouv.fr"}
SANDBOX = {"oauth": "https://sandbox-oauth.piste.gouv.fr/api/oauth/token",
           "api": "https://sandbox-api.piste.gouv.fr"}
JUDILIBRE = "/cassation/judilibre/v1.0"
LEGIFRANCE = "/dila/legifrance/lf-engine-app"
CC_SITE = "https://www.courdecassation.fr"
LF_SITE = "https://www.legifrance.gouv.fr"

_JURIDICTIONS = {"cc": "Cour de cassation", "ca": "cours d'appel", "tj": "tribunaux judiciaires",
                 "tcom": "tribunaux de commerce",
                 "cph": "conseils de prud'hommes"}
# Courts served from Légifrance instead: code -> (fond, title phrases). The JURIDICTION_NATURE facet
# returns HTTP 500 for plain values (2026-11-11), so courts are picked by an exact title phrase
# (accent- and case-insensitive). CAA titles come as "CAA de ..." and "Cour administrative d'appel de ...".
_LF_COURTS = {"ce": ("CETAT", ("Conseil d'État",)),
              "caa": ("CETAT", ("CAA", "Cour administrative d'appel")),
              "ta": ("CETAT", ("Tribunal administratif",)),
              "tc": ("CETAT", ("Tribunal des conflits",)),
              "constit": ("CONSTIT", ())}
_LF_OPS = {"and": "TOUS_LES_MOTS_DANS_UN_CHAMP", "or": "UN_DES_MOTS", "exact": "EXACTE"}
_LF_DECISION_ID = re.compile(r"(CETATEXT|CONSTEXT|JURITEXT)\d{12}")
_LF_DECISION_PATH = {"CETATEXT": "ceta", "CONSTEXT": "cons", "JURITEXT": "juri"}
_MONTHS = ("janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre",
           "octobre", "novembre", "décembre")
_SORTS = ("score", "scorepub", "date")
_OPERATORS = ("or", "and", "exact")
_FONDS = {"code": "CODE_DATE", "loda": "LODA_DATE", "jorf": "JORF"}
_DECISION_ID = re.compile(r"^[0-9a-f]{20,40}$")
_TEXT_ID = re.compile(r"^(LEGITEXT|JORFTEXT)\d{12}$")
_JUDILIBRE_PAGE_MAX = 25   # tutorial: "pas plus de 25 décisions à la fois" (OpenAPI says 50)
_JUDILIBRE_LIMIT_MAX = 100  # 4-5 source pages per call at most

_token: dict = {}                    # {"key": (oauth url, client id), "value": str, "expires": float}
_texts: dict[str, dict] = {}         # textId -> legiPart JSON (small LRU)


def _creds() -> tuple[str, str] | None:
    cid = os.environ.get(ENV_ID, "").strip()
    secret = os.environ.get(ENV_SECRET, "").strip()
    return (cid, secret) if cid and secret else None


def _env() -> dict:
    return SANDBOX if os.environ.get(ENV_SANDBOX, "").strip().lower() in ("1", "true", "yes") else PROD


# =========================================================================== #
# PISTE OAuth2 client credentials
# =========================================================================== #
async def _get_token() -> str:
    creds = _creds()
    if not creds:
        raise SourceError(f"France needs a free PISTE key: set {ENV_ID} and {ENV_SECRET}.")
    env = _env()
    key = (env["oauth"], creds[0])
    if _token.get("key") == key and _token.get("expires", 0) > time.monotonic():
        return _token["value"]
    r = await _http.post(env["oauth"], data={
        "grant_type": "client_credentials", "client_id": creds[0],
        "client_secret": creds[1], "scope": "openid"})
    if r.status_code in (400, 401):
        raise SourceError(f"PISTE refused the client credentials ({ENV_ID} / {ENV_SECRET}); "
                          "check them on piste.gouv.fr > Applications.", r.status_code)
    if r.status_code != 200:
        raise SourceError("PISTE token request failed", r.status_code)
    try:
        data = r.json()
        value = data["access_token"]
    except (ValueError, KeyError):
        raise SourceError("PISTE token response had no access_token") from None
    ttl = int(data.get("expires_in") or 3600)
    _token.clear()
    _token.update(key=key, value=value, expires=time.monotonic() + max(ttl - 60, 30))
    return value


async def _call(method: str, path: str, *, api: str, **kw):
    """One authenticated call. A 401 drops the cached token and retries once."""
    url = _env()["api"] + path
    for attempt in (1, 2):
        headers = {"Authorization": f"Bearer {await _get_token()}", "Accept": "application/json"}
        r = await _http.request(method, url, headers=headers, **kw)
        if r.status_code == 401 and attempt == 1:
            _token.clear()
            continue
        break
    if r.status_code == 403:
        raise SourceError(f"PISTE denied access to the {api} API: subscribe the application to "
                          f"{api} and accept its CGU on piste.gouv.fr.", 403)
    if r.status_code == 401:
        raise SourceError(f"PISTE rejected the token for {api}.", 401)
    return r


def _json(r, what: str):
    if r.status_code != 200:
        raise SourceError(f"{what} failed", r.status_code)
    try:
        return r.json()
    except ValueError:
        raise SourceError(f"{what}: unexpected non-JSON reply", r.status_code) from None


# =========================================================================== #
# Judilibre (case law)
# =========================================================================== #
def _list(v) -> list[str]:
    return [x.strip() for x in str(v).split(",") if x.strip()]


def _judilibre_params(query: str, limit: int, page: int, filters: dict) -> dict:
    params: dict = {"query": query, "page_size": max(1, min(limit, _JUDILIBRE_PAGE_MAX)),
                    "page": page - 1, "resolve_references": "true"}
    if "jurisdiction" in filters:
        vals = _list(filters["jurisdiction"])
        bad = [v for v in vals if v not in _JURIDICTIONS]
        if bad or not vals:
            raise BadRequest(f"jurisdiction must be one or more of {', '.join([*_JURIDICTIONS, *_LF_COURTS])} "
                             f"(comma-separated), not {filters['jurisdiction']!r}.")
        params["jurisdiction"] = vals
    if "chamber" in filters:
        params["chamber"] = _list(filters["chamber"])
    for k in ("date_start", "date_end"):
        if k in filters:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(filters[k])):
                raise BadRequest(f"{k} must be YYYY-MM-DD, e.g. 2021-05-13.")
            params[k] = str(filters[k])
    if "sort" in filters:
        if filters["sort"] not in _SORTS:
            raise BadRequest(f"sort must be one of {', '.join(_SORTS)}.")
        params["sort"] = filters["sort"]
        params["order"] = "desc"
        if filters["sort"] == "date":
            params["operator"] = "and"   # with OR, date order surfaces newest decisions matching any one word
    if "operator" in filters:
        if filters["operator"] not in _OPERATORS:
            raise BadRequest(f"operator must be one of {', '.join(_OPERATORS)}.")
        params["operator"] = filters["operator"]
    return params


def _number(d: dict) -> str:
    n = d.get("number")
    if isinstance(n, list):
        n = n[0] if n else ""
    return str(n or "")


def _court(d: dict) -> str:
    """'Cour de cassation, Chambre sociale' or 'Cour d'appel de Chambéry'."""
    loc = d.get("location") or ""
    if loc and not re.fullmatch(r"[a-z_]+", loc):   # resolved label, not a code like ca_chambery
        base = loc
    else:
        j = d.get("jurisdiction") or ""
        base = {"cc": "Cour de cassation"}.get(j, j)
    chamber = d.get("chamber") or ""
    return f"{base}, {chamber}" if chamber and chamber not in base else base


def _decision_url(id_: str) -> str:
    return f"{CC_SITE}/decision/{id_}"


def _fold(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if not unicodedata.combining(c))


def _strip_em(s: str) -> str:
    return _http.clean(re.sub(r"</?(?:em|mark)>", "", s or ""))


def _snippet(d: dict) -> str:
    if d.get("summary"):
        return _http.clean(d["summary"])
    for vals in (d.get("highlights") or {}).values():
        if vals:
            return _strip_em(vals[0])
    return ""


def _hit(d: dict) -> DecisionHit:
    court, num = _court(d), _number(d)
    return DecisionHit(id=d["id"], title=f"{court} {num}".strip(), court=court,
                       date=_http.iso_date(d.get("decision_date")), case_number=num,
                       snippet=_snippet(d), url=_decision_url(d["id"]))


def _plain(text: str) -> str:
    """Judilibre text is plain text with CRLF and space runs: keep paragraphs, tidy lines."""
    lines = [_http.clean(ln) for ln in (text or "").replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def _body_md(html: str) -> str:
    """Légifrance separates paragraphs with empty <p></p> pairs, which markdownify drops."""
    return _http.html_to_md(re.sub(r"<p>\s*</p>", "<br><br>", html or ""))


def _decision_id(ref: str) -> str:
    ref = ref.strip().rstrip("/")
    ref = re.sub(r"^https?://(www\.)?courdecassation\.fr/decision/", "", ref)
    if _DECISION_ID.match(ref.lower()):
        ref = ref.lower()
    if not _DECISION_ID.match(ref):
        raise BadRequest(f"bad decision id {ref!r}. Use a Judilibre id like "
                         "'5fca7d162a251e6bf9c78514' (from search_caselaw, or the last part of "
                         "a courdecassation.fr/decision/... link), or a Légifrance id like "
                         "'CETATEXT000053464527' / 'CONSTEXT000043596386' / 'JURITEXT000030279805'.")
    return ref


# =========================================================================== #
# Légifrance case law (CETAT: administrative courts; CONSTIT: Conseil constitutionnel)
# =========================================================================== #
def _lf_decision_url(id_: str) -> str:
    return f"{LF_SITE}/{_LF_DECISION_PATH[id_[:8]]}/id/{id_}"


def _title_date(title: str) -> str:
    """'..., 11/02/2026, 498240' or '... 20 mai 2021 ...' -> ISO date."""
    m = re.search(r"\b(\d{2})/(\d{2})/(\d{4})\b", title)
    if m:
        return f"{m[3]}-{m[2]}-{m[1]}"
    m = re.search(r"\b(\d{1,2})(?:er)? (" + "|".join(_MONTHS) + r") (\d{4})\b", title, flags=re.I)
    if m:
        return f"{m[3]}-{_MONTHS.index(m[2].lower()) + 1:02d}-{int(m[1]):02d}"
    return ""


def _title_number(title: str) -> str:
    """'CAA de PARIS, 1ère chambre, 06/11/2026, 25PA00337, Inédit...' -> '25PA00337';
    'Décision 2021-817 DC - 20 mai 2021 - ...' -> '2021-817 DC'."""
    m = re.match(r"Décision (\S+ [A-Z]+)\b", title)
    if m:
        return m[1]
    parts = [p.strip() for p in title.split(",")]
    for i, p in enumerate(parts[:-1]):
        if _title_date(p) and re.fullmatch(r"[A-Z]?[\dA-Z.\-]*\d[\dA-Z.\-]*", parts[i + 1]):
            return parts[i + 1]
    return ""


def _lf_decision_hit(r: dict) -> DecisionHit | None:
    titles = r.get("titles") or []
    t = titles[0] if titles else {}
    cid = t.get("cid") or t.get("id") or ""
    if not _LF_DECISION_ID.fullmatch(cid):
        return None
    title = _strip_em(t.get("title") or "")
    court = "Conseil constitutionnel" if cid.startswith("CONSTEXT") else title.split(",")[0].strip()
    snippet = ""
    for sec in r.get("sections") or []:
        for ex in sec.get("extracts") or []:
            if ex.get("values"):
                snippet = _strip_em(ex["values"][0])
                break
        if snippet:
            break
    return DecisionHit(id=cid, title=title or cid, court=court, date=_title_date(title),
                       case_number=_http.clean(r.get("num") or "") or _title_number(title),
                       snippet=snippet or _strip_em(r.get("text") or ""), url=_lf_decision_url(cid))


# =========================================================================== #
# Légifrance (legislation)
# =========================================================================== #
def _epoch_ms(iso: str) -> int:
    d = datetime.date.fromisoformat(iso)
    return int(datetime.datetime(d.year, d.month, d.day, tzinfo=datetime.UTC).timestamp() * 1000)


def _ms_date(v) -> str:
    """Légifrance dates come as epoch ms or ISO strings; 2999-01-01 means 'no date'."""
    if isinstance(v, (int, float)) or (isinstance(v, str) and v.lstrip("-").isdigit()):
        try:
            out = datetime.datetime.fromtimestamp(int(v) / 1000, datetime.UTC).date().isoformat()
        except (ValueError, OverflowError, OSError):
            return ""
    else:
        out = _http.iso_date(v)
    return "" if out.startswith("2999") else out


def _text_id(ref: str) -> str:
    ref = ref.strip().rstrip("/")
    m = re.search(r"(LEGITEXT|JORFTEXT)\d{12}", ref.upper())
    if not m or not _TEXT_ID.match(m[0]):
        raise BadRequest(f"bad law id {ref!r}. Use a Légifrance text id like "
                         "'LEGITEXT000006070721' (Code civil) or 'JORFTEXT000000886460'.")
    return m[0]


def _text_url(id_: str, title: str = "") -> str:
    if id_.startswith("JORFTEXT"):
        return f"{LF_SITE}/jorf/id/{id_}"
    if title.lower().startswith("code"):
        return f"{LF_SITE}/codes/texte_lc/{id_}"
    return f"{LF_SITE}/loda/id/{id_}"


def _article_url(article_id: str) -> str:
    if article_id.startswith("JORFARTI"):
        return f"{LF_SITE}/jorf/article_jo/{article_id}"
    return f"{LF_SITE}/codes/article_lc/{article_id}" if article_id else ""


def _has_content(data) -> bool:
    return bool(data and (data.get("sections") or data.get("articles")))


def _norm_provision(p: str) -> str:
    """'Article L. 121-1', 'art. 1240', 'L121-1', '1240' -> the Légifrance num ('L121-1')."""
    p = _http.clean(p)
    p = re.sub(r"^(article|art\.?)\s*", "", p, flags=re.I)
    p = re.sub(r"^([LRDA])\.?\s*\*?\s*(?=\d)", r"\1", p, flags=re.I)   # 'L. 121-1' -> 'L121-1'
    if not p:
        raise BadRequest("give an article number, e.g. 'Article 1240' or 'L121-1'.")
    return p[0].upper() + p[1:] if re.match(r"^[lrda]\d", p) else p


def _champ(field: str, values, how: str, op: str = "ET") -> dict:
    return {"typeChamp": field, "operateur": op,
            "criteres": [{"typeRecherche": how, "valeur": v, "operateur": op} for v in values]}


def _lf_body(fond: str, champs: list, filtres: list, limit: int, page: int,
             sort: str = "PERTINENCE") -> dict:
    if limit > 100:
        raise BadRequest(f"limit must be at most 100 for Légifrance searches, got {limit}; use page to walk further.")
    return {"fond": fond, "recherche": {
        "champs": champs, "filtres": filtres,
        "pageNumber": page, "pageSize": max(1, min(limit, 100)), "operateur": "ET",
        "sort": sort, "typePagination": "DEFAUT"}}


def _search_body(query: str, limit: int, page: int, fond: str) -> dict:
    filtres = [] if fond == "JORF" else [{"facette": "DATE_VERSION",
                                           "singleDate": _epoch_ms(_http.today())}]
    return _lf_body(fond, [_champ("ALL", [query], _LF_OPS["and"])], filtres, limit, page)


def _lf_caselaw_body(query: str, courts: list[str], limit: int, page: int, filters: dict) -> dict:
    fonds = {_LF_COURTS[c][0] for c in courts}
    if len(fonds) > 1:
        raise BadRequest("constit cannot be combined with ce/caa/ta/tc in one search; search them separately.")
    if "chamber" in filters:
        raise BadRequest("chamber applies to the Cour de cassation (Judilibre) only.")
    op = filters.get("operator", "and")
    if op not in _OPERATORS:
        raise BadRequest(f"operator must be one of {', '.join(_OPERATORS)}.")
    champs = [_champ("ALL", [query], _LF_OPS[op])]
    phrases = [p for c in courts for p in _LF_COURTS[c][1]]
    if phrases:
        champs.append(_champ("TITLE", phrases, "EXACTE", "OU"))
    for k in ("date_start", "date_end"):
        if k in filters and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(filters[k])):
            raise BadRequest(f"{k} must be YYYY-MM-DD, e.g. 2021-05-13.")
    filtres = []
    if "date_start" in filters or "date_end" in filters:
        filtres.append({"facette": "DATE_DECISION", "dates": {
            "start": str(filters.get("date_start", "1800-01-01")),
            "end": str(filters.get("date_end", _http.today()))}})
    sort = filters.get("sort", "score")
    if sort not in _SORTS:
        raise BadRequest(f"sort must be one of {', '.join(_SORTS)}.")
    return _lf_body(fonds.pop(), champs, filtres, limit, page,
                    "DATE_DESC" if sort == "date" else "PERTINENCE")


def _law_hit(r: dict, fond: str) -> LawHit | None:
    titles = r.get("titles") or []
    t = titles[0] if titles else {}
    cid = t.get("cid") or t.get("id") or ""
    if not _TEXT_ID.match(cid):
        return None
    title = _strip_em(t.get("title") or r.get("title") or "")
    snippet = ""
    for sec in r.get("sections") or []:
        for ex in sec.get("extracts") or []:
            vals = ex.get("values") or []
            if vals:
                label = f"Article {ex['num']}: " if ex.get("num") else ""
                snippet = label + _strip_em(_http.html_to_md(vals[0]))
                break
        if snippet:
            break
    return LawHit(id=cid, title=title or cid, type=_http.clean(r.get("nature") or t.get("nature") or ""),
                  number=_http.clean(r.get("num") or ""),
                  date=_ms_date(r.get("dateSignature") or r.get("date") or r.get("datePublication") or ""),
                  status=_http.clean(r.get("etat") or t.get("legalStatus") or ""),
                  snippet=snippet,
                  url=f"{LF_SITE}/codes/texte_lc/{cid}" if fond == "CODE_DATE" else _text_url(cid, title))


def _walk(node: dict, level: int):
    """Yield ('section', level, section) and ('article', level, article) in reading order."""
    items = [("article", a) for a in node.get("articles") or []]
    items += [("section", s) for s in node.get("sections") or []]
    items.sort(key=lambda x: x[1].get("intOrdre") or 0)
    for kind, x in items:
        yield kind, level, x
        if kind == "section":
            yield from _walk(x, level + 1)


def _article_label(a: dict) -> str:
    return f"Article {a.get('num')}" if a.get("num") else ""


# =========================================================================== #
# Adapter
# =========================================================================== #
class France(Jurisdiction):
    code = "fr"
    name = "France"
    languages = ("fr",)
    aliases = ("france",)
    sources = (
        Source("Judilibre (Cour de cassation, via PISTE)", "https://www.courdecassation.fr/acces-rapide-judilibre/open-data-et-api",
               covers=("caselaw",), licence="Licence Ouverte / Open Licence 2.0 (Etalab) + Cour de cassation reuse CGU",
               commercial_use=True, ai_use=None, auth="free key",
               rate_limit="unknown; PISTE per-app quotas (README: 'quotas ... sur le portail PISTE'); 1 s spacing",
               terms_url="https://github.com/Cour-de-cassation/judilibre-search#conditions-dutilisation",
               warning=("Pseudonymised decisions: do not try to re-identify people; profiling, comparing or "
                        "rating judges and court clerks is a criminal offence (COJ art. L111-13).")),
        Source("Légifrance API (DILA, via PISTE)", "https://www.legifrance.gouv.fr",
               covers=("caselaw", "legislation"), licence="Licence Ouverte / Open Licence 2.0 (Etalab)",
               commercial_use=True, ai_use=None, auth="free key",
               rate_limit="unknown; PISTE per-app quotas shown in the app's 'Consulter les quotas' (CGU IV.3); 1 s spacing",
               terms_url="https://piste.gouv.fr/images/cgu/DILA_Legifrance_Beta_v2.pdf",
               warning=("Légifrance API data are not legally binding: only the signed PDF Journal officiel is (CGU VI.1). "
                        "Decisions: profiling, comparing or rating judges is a criminal offence "
                        "(COJ art. L111-13, CJA art. L10).")),
    )
    caselaw_filters = {
        "jurisdiction": "court: cc (Cour de cassation, default), ca (cours d'appel), tj (tribunaux "
                        "judiciaires), tcom (tribunaux de commerce), cph (conseils de prud'hommes), "
                        "ce (Conseil d'État), caa (cours administratives d'appel), ta (tribunaux administratifs), "
                        "tc (Tribunal des conflits), constit (Conseil constitutionnel); comma-separated. "
                        "ce/caa/ta/tc and constit come from Légifrance and cannot be mixed with the others",
        "chamber": "Cour de cassation chamber code(s), e.g. civ1, civ2, civ3, comm, soc, cr, mi, pl",
        "date_start": "decisions from this date, YYYY-MM-DD",
        "date_end": "decisions up to this date, YYYY-MM-DD",
        "sort": "score (relevance), scorepub (relevance + publication level, default) or date (newest first)",
        "operator": "or, and, exact (default: or for Judilibre courts, and for Légifrance courts; "
                    "and when sort is date)",
    }
    legislation_filters = {
        "fond": "code (codes, default), loda (lois, ordonnances, décrets, arrêtés, consolidated) or "
                "jorf (Journal officiel: every published text as published, incl. nominations and avis)",
    }
    min_interval = {"api.piste.gouv.fr": 1.0, "sandbox-api.piste.gouv.fr": 1.0,
                    "oauth.piste.gouv.fr": 1.0, "sandbox-oauth.piste.gouv.fr": 1.0}
    gaps = ("Tribunaux administratifs: Légifrance holds only a small selection; the full set is on "
            "opendata.justice-administrative.fr (not built)",)
    samples = {
        "caselaw_query": "expropriation",
        "decision_id": "5fca7d162a251e6bf9c78514",     # Cass. civ3, 20 Dec 2018, 17-18.194 (OpenAPI example)
        "legislation_query": "code civil",
        "law_id": "LEGITEXT000006070721",               # Code civil
        "provision": "Article 1240",
    }

    # Off until both PISTE credentials are set: no tool is offered and the map shows nothing.
    def supports(self, method: str) -> bool:
        return _creds() is not None and super().supports(method)

    @property
    def notes(self) -> str:
        if _creds() is None:
            return (f"Inactive: needs a free PISTE account. Set {ENV_ID} and {ENV_SECRET} (OAuth client "
                    "credentials of a piste.gouv.fr app subscribed to Judilibre and Légifrance).")
        env = " Using the PISTE sandbox (data lag production)." if _env() is SANDBOX else ""
        return ("Judilibre and Légifrance decisions are pseudonymised. Légifrance texts are consolidated "
                "(fond jorf: as published), not authentic." + env)

    # ------------------------------------------------------------- case law
    async def search_caselaw(self, query, *, limit, page, filters):
        vals = _list(filters.get("jurisdiction", ""))
        lf = [v for v in vals if v in _LF_COURTS]
        if lf:
            if len(lf) != len(vals):
                raise BadRequest("ce, caa, ta, tc and constit (Légifrance) cannot be mixed with "
                                 "cc, ca, tj, tcom, cph (Judilibre) in one search.")
            data = _json(await _call("POST", f"{LEGIFRANCE}/search", api="Légifrance",
                                     json=_lf_caselaw_body(query, lf, limit, page, filters)),
                         "Légifrance search")
            hits = [h for h in (_lf_decision_hit(r) for r in data.get("results") or []) if h]
            note = ("Tribunaux administratifs: Légifrance holds only a small selection of their decisions, "
                    "not the full case law." if "ta" in lf else
                    "Légifrance holds only a selection of these courts' decisions (older ones especially); "
                    "a decision missing here may still exist.")
            words = [w for w in re.findall(r"\w+", _fold(query)) if len(w) > 2]
            if hits and len(words) == 1 and not any(words[0] in _fold(h.title + " " + h.snippet)
                                                    for h in hits):
                return Results([], total=0, note=(
                    f"No decision matching {query!r} was found in Légifrance's selection of these courts "
                    "(the source returned only unrelated loose matches, which are hidden). The decision may "
                    "exist but be absent from the selection: try its number or a longer phrase. " + note))
            if hits and words and not any(all(w in _fold(h.title + " " + h.snippet) for w in words)
                                          for h in hits):
                note = (f"No returned decision shows all of {query!r} in its title or excerpt: these are loose "
                        "matches, not decisions known by that name. The decision you want may be absent "
                        "from Légifrance's selection. " + note)
            return Results(hits[:limit], total=data.get("totalResultNumber"), note=note)
        if limit > _JUDILIBRE_LIMIT_MAX:
            raise BadRequest(f"limit is at most {_JUDILIBRE_LIMIT_MAX} for Judilibre; use page to go further.")
        # Judilibre serves at most 25 per page: always ask 25 so the requests (and their order) do
        # not depend on limit, fetch the source pages covering the window and slice it out.
        n, start = _JUDILIBRE_PAGE_MAX, (page - 1) * limit
        params = _judilibre_params(query, n, 1, filters)
        rows: list = []
        for p in range(start // n, (start + limit - 1) // n + 1):
            data = _json(await _call("GET", f"{JUDILIBRE}/search", api="Judilibre",
                                     params={**params, "page": p}), "Judilibre search")
            got = data.get("results") or []
            rows += got
            if len(got) < n:
                break
        items = [_hit(d) for d in rows[start % n:start % n + limit] if d.get("id")]
        total = data.get("total") or 0
        note = (f"Judilibre counts {total:,} matches but returns at most the first 10,000 per query: "
                "narrow the search (dates, court, chamber) to reach the rest." if total > 10000 else "")
        note = (note + " Judilibre sometimes returns a different order for the same request, so pages "
                "can occasionally repeat or skip hits.").strip()
        return Results(items, total=data.get("total"), note=note)

    async def get_decision(self, id):
        m = _LF_DECISION_ID.search((id or "").upper())
        if m:
            return await self._lf_decision(m[0])
        did = _decision_id(id)
        r = await _call("GET", f"{JUDILIBRE}/decision", api="Judilibre",
                        params={"id": did, "resolve_references": "true"})
        if r.status_code == 404:
            raise NotFound(f"no Judilibre decision {did}")
        d = _json(r, "Judilibre decision")
        text = _plain(d.get("text") or "")
        if not text:
            raise SourceError(f"Judilibre decision {did} has no text")
        court, num = _court(d), _number(d)
        meta = {k: v for k, v in {
            "ECLI": d.get("ecli") or "",
            "Formation": d.get("formation") or "",
            "Solution": d.get("solution") or "",
            "Publication": ", ".join(d.get("publication") or []) if isinstance(d.get("publication"), list) else "",
            "Thèmes": "; ".join(d.get("themes") or []),
            "Visa": "; ".join(_http.clean(v.get("title")) for v in d.get("visa") or [] if v.get("title")),
            "Mise à jour": _http.iso_date(d.get("update_date")),
        }.items() if v}
        return Decision(id=did, title=f"{court} {num}".strip(), text=text, url=_decision_url(did),
                        court=court, date=_http.iso_date(d.get("decision_date")), case_number=num,
                        summary=_http.clean(d.get("summary") or ""), metadata=meta)

    async def _lf_decision(self, did: str) -> Decision:
        r = await _call("POST", f"{LEGIFRANCE}/consult/juri", api="Légifrance", json={"textId": did})
        if r.status_code in (400, 404):
            raise NotFound(f"no Légifrance decision {did}")
        t = (_json(r, "Légifrance decision") or {}).get("text") or {}
        text = _body_md(t.get("texteHtml") or "") or _plain(t.get("texte") or "")
        if not text:
            raise NotFound(f"no Légifrance decision {did}")
        court = _http.clean(t.get("juridiction") or "")
        num = _http.clean(t.get("num") or "")
        summary = "\n\n".join(_http.clean(s.get("resumePrincipal")) for s in t.get("sommaire") or []
                              if isinstance(s, dict) and s.get("resumePrincipal"))
        meta = {k: v for k, v in {
            "ECLI": t.get("ecli") or "",
            "Formation": t.get("formation") or "",
            "Nature": t.get("natureQualifiee") or "",
            "Solution": t.get("solution") or "",
            "Publication": t.get("originePubli") or "",
            "Journal officiel": t.get("titreJo") or "",
        }.items() if v}
        return Decision(id=did, title=_http.clean(t.get("titre") or f"{court} {num}"), text=text,
                        url=_lf_decision_url(did), court=court, date=_ms_date(t.get("dateTexte")),
                        case_number=num, summary=summary, metadata=meta)

    # ---------------------------------------------------------- legislation
    async def search_legislation(self, query, *, limit, page, filters):
        f = filters.get("fond", "code")
        if f not in _FONDS:
            raise BadRequest(f"fond must be one of {', '.join(_FONDS)}.")
        fond = _FONDS[f]
        data = _json(await _call("POST", f"{LEGIFRANCE}/search", api="Légifrance",
                                 json=_search_body(query, limit, page, fond)), "Légifrance search")
        hits = [h for h in (_law_hit(r, fond) for r in data.get("results") or []) if h]
        return Results(hits[:limit], total=data.get("totalResultNumber"))

    async def _text(self, tid: str) -> dict:
        """Consolidated version in force today; for a JORF-only text (legiPart answers 400),
        the version published in the Journal officiel (marked with '_jorf')."""
        if tid in _texts:
            return _texts[tid]
        r = await _call("POST", f"{LEGIFRANCE}/consult/legiPart", api="Légifrance",
                        json={"textId": tid, "date": _epoch_ms(_http.today())})
        data = None
        if r.status_code not in (400, 404):
            data = _json(r, "Légifrance text")
        if not _has_content(data) and tid.startswith("JORFTEXT"):
            r = await _call("POST", f"{LEGIFRANCE}/consult/jorf", api="Légifrance", json={"textCid": tid})
            if r.status_code not in (400, 404):
                data = _json(r, "Légifrance JORF text")
                data["_jorf"] = True
        if not _has_content(data):
            raise NotFound(f"no Légifrance text {tid} with content (in force today or in the JORF)")
        _http.lru_put(_texts, tid, data, 4)
        return data

    async def get_legislation_toc(self, id):
        tid = _text_id(id)
        data = await self._text(tid)
        title = _http.clean(data.get("title") or tid)
        entries = []
        for kind, level, x in _walk(data, 0):
            if kind == "section":
                entries.append(TocEntry(_http.clean(x.get("title")), level, ""))
            elif _article_label(x):
                entries.append(TocEntry(_article_label(x), level, _article_label(x)))
        return Toc(id=tid, title=title, url=_text_url(tid, title), entries=entries)

    async def get_legislation_provision(self, id, provision):
        tid = _text_id(id)
        num = _norm_provision(provision)
        r = await _call("POST", f"{LEGIFRANCE}/consult/getArticleWithIdAndNum", api="Légifrance",
                        json={"id": tid, "num": num})
        if r.status_code == 404:
            raise NotFound(f"no article {num} in {tid}")
        a = (_json(r, "Légifrance article") or {}).get("article") or {}
        body = _body_md(a.get("texteHtml") or "") or _plain(a.get("texte") or "")
        if not body and tid.startswith("JORFTEXT"):
            # getArticleWithIdAndNum returns article=null for JORFTEXT ids: look in the text itself.
            data = await self._text(tid)
            for kind, _, x in _walk(data, 0):
                if kind == "article" and str(x.get("num") or "").lower() == num.lower():
                    body = _body_md(x.get("content") or "")
                    a = {"num": x.get("num"), "id": x.get("id"), "dateDebut": data.get("dateParution") if data.get("_jorf") else x.get("dateDebut"),
                         "textTitles": [{"titre": data.get("title")}]}
                    break
        if not body:
            raise NotFound(f"no article {num} in {tid}")
        law_title = ""
        for t in a.get("textTitles") or []:
            law_title = _http.clean(t.get("titre") or t.get("title") or "")
            if law_title:
                break
        label = f"Article {a.get('num') or num}"
        return Provision(law_id=tid, law_title=law_title or tid, provision=label,
                         text=f"## {label}\n\n{body}",
                         url=_article_url(a.get("id") or "") or _text_url(tid, law_title),
                         as_of=_ms_date(a.get("dateDebut")))

    async def get_legislation_text(self, id):
        tid = _text_id(id)
        data = await self._text(tid)
        title = _http.clean(data.get("title") or tid)
        out = []
        for kind, level, x in _walk(data, 0):
            if kind == "section":
                out.append("#" * min(level + 2, 6) + " " + _http.clean(x.get("title")))
            else:
                label = _article_label(x)
                body = _body_md(x.get("content") or "")
                out.append((f"**{label}**\n\n" if label else "") + body)
        text = "\n\n".join(p for p in out if p.strip())
        if not text:
            raise NotFound(f"Légifrance text {tid} has no content")
        jorf = data.get("_jorf")
        return LawText(id=tid, title=title, text=text, url=_text_url(tid, title),
                       as_of=_ms_date(data.get("dateParution")) if jorf else _http.today(),
                       metadata={k: v for k, v in {"NOR": data.get("nor") or "",
                                                   "ELI": data.get("eli") or "",
                                                   "Journal officiel": data.get("jorfText") or "",
                                                   "Version": "as published in the Journal officiel" if jorf else "",
                                                   }.items() if v})

