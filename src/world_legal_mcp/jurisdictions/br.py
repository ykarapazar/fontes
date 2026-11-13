"""Brazil: STF case law (Supremo Tribunal Federal) and consolidated federal legislation
from normas.leg.br (Senado Federal / Câmara dos Deputados).

Gotchas this code encodes (verified 2026-11-05 from a UK IP):
  * STF: POST jurisprudencia.stf.jus.br/api/search/search takes a plain Elasticsearch
    body and returns {"result": <ES reply>}. It is the (undocumented) backend of the
    jurisprudência site. Bases: acordaos (~373k), decisoes (monocratic, ~760k),
    sumulas (~800), plus informativos. Without track_total_hits the total stops at
    10000. Full text is inline: inteiro_teor_texto (acórdãos, PDF-extracted, hard-wrapped,
    page headers and signature footers on every page), decisao_texto (decisões),
    sumula_texto (súmulas). The id is the source's own (sjur254711, despacho1278126,
    seq-sumula819). Party names are not anonymised.
  * Legislation search: legis.senado.leg.br/sigen/api/catalogo/basico (the catalogue
    behind normas.leg.br). Words are AND-ed, quotes make a phrase, results are sorted by
    date (newest first), not relevance; `pagina` is 0-based. A number alone ("10406")
    finds the law.
  * Legislation text: normas.leg.br/api/public/normas?urn=<LexML URN>&tipo_documento=
    maior-detalhe returns the whole consolidated norm as schema.org JSON-LD: a hasPart tree
    (parte/livro/título/capítulo/seção/artigo/caput/parágrafo/inciso/alínea), each node with
    workExample = one version or a list of versions (oldest first). The last version is the
    current text; a repealed provision's last version reads "(Revogado)". There is no
    per-article endpoint (an article URN returns {"urn": ...}), so the norm is fetched once
    (Código Civil: 5 MB, ~10 s) and kept in a small in-memory cache. An unknown URN also
    returns just {"urn": ...}. Some norms have only metadata (no hasPart).
  * Inserted articles have URN fragments like "art48-1,lei-14195-2021-08-26"; a number
    can appear twice (e.g. an MP version that lapsed and the law that re-enacted it). The
    in-force one keeps the plain label, others get the URN fragment as qualifier.
  * Planalto (planalto.gov.br, the usual consolidated text) refuses connections from
    abroad; the LexML SRU search sits behind a WAF challenge. Neither is used.
  * Norms with only metadata in normas.leg.br (Código Penal, CPP, CDC, CLT, CTN): the
    "Compilação Monovigente na CD" (current consolidated text, Câmara) is served as HTML by
    legis.senado.leg.br/norma/<sigen id>/publicacao/<id>. The sigen id is in the metadata's
    sameAs (DetalhaSigen.action?id=), the publication id on the norm page. It is flat
    paragraphs ("Art. 121. Matar alguém:", "§ 1º", "I -"), cut into articles at "Art. N".
"""
from __future__ import annotations

import datetime
import html
import re

from .. import _http
from ..base import BadRequest, Jurisdiction, NotFound, Source, SourceError
from ..models import (Decision, DecisionHit, LawHit, LawText, Provision, Results, Toc,
                      TocEntry)

STF_API = "https://jurisprudencia.stf.jus.br/api/search/search"
STF_PAGE = "https://jurisprudencia.stf.jus.br/pages/search/{id}/false"
CATALOGO = "https://legis.senado.leg.br/sigen/api/catalogo/basico"
NORMAS = "https://normas.leg.br/api/public/normas"
NORMA_PAGE = "https://normas.leg.br/?urn={urn}"
SENADO_NORMA = "https://legis.senado.leg.br/norma/{sen}"

_BASES = {"acordaos": "Acórdão", "decisoes": "Decisão monocrática", "sumulas": "Súmula"}
_STF_ID = re.compile(r"^[A-Za-z][\w-]{2,40}$")
_URN = re.compile(r"^urn:lex:br:federal:[a-z.]+:\d{4}-\d{2}-\d{2};[\w.-]+$")
# Common short names -> LexML URN (each checked against normas.leg.br 2026-11-05)
_ALIASES = {
    "cc": "urn:lex:br:federal:lei:2002-01-10;10406",
    "codigo civil": "urn:lex:br:federal:lei:2002-01-10;10406",
    "cf": "urn:lex:br:federal:constituicao:1988-10-05;1988",
    "constituicao": "urn:lex:br:federal:constituicao:1988-10-05;1988",
    "cpc": "urn:lex:br:federal:lei:2015-03-16;13105",
    "cp": "urn:lex:br:federal:decreto.lei:1940-12-07;2848",
    "cpp": "urn:lex:br:federal:decreto.lei:1941-10-03;3689",
    "cdc": "urn:lex:br:federal:lei:1990-09-11;8078",
    "clt": "urn:lex:br:federal:decreto.lei:1943-05-01;5452",
    "ctn": "urn:lex:br:federal:lei:1966-10-25;5172",
}
_HEADINGS = {"parte", "livro", "titulo", "subtitulo", "capitulo", "secao", "subsecao"}
_SKIP = {"assinaturas"}
_cache: dict[str, dict] = {}


# --------------------------------------------------------------------------- #
# STF
# --------------------------------------------------------------------------- #
_PAGE_HDR = re.compile(r"^(Inteiro Teor do Acórdão - Página \d+ de \d+|Supremo Tribunal Federal)$")
_SIGNED = re.compile(r"^(Documento assinado digitalmente|documento pode ser acessado no endereço)")


def _join_lines(lines: list[str]) -> list[str]:
    """Hard-wrapped lines -> paragraphs: a line ending in . : ; ! ? or a quote closes one."""
    out, cur = [], ""
    for ln in lines:
        ln = _http.clean(ln)
        if not ln:
            if cur:
                out.append(cur)
                cur = ""
            continue
        cur = f"{cur} {ln}" if cur else ln
        if re.search(r"[.:;!?”\"]$", ln):
            out.append(cur)
            cur = ""
    if cur:
        out.append(cur)
    return out


def _stf_text(raw: str) -> str:
    """PDF-extracted STF text -> markdown paragraphs, page headers and signature footers out."""
    paras: list[str] = []
    for pg in (raw or "").replace("\r", "").split("\x0c"):
        lines = pg.split("\n")
        # page header: "Supremo Tribunal Federal" / section label / "Inteiro Teor ... Página n de m"
        for i, ln in enumerate(lines[:6]):
            if ln.startswith("Inteiro Teor do Acórdão - Página"):
                lines = lines[i + 1:]
                break
        keep, skip = [], False
        for ln in lines:
            s = ln.strip()
            if _SIGNED.match(s):
                skip = True
            if skip:
                if not s:
                    skip = False
                continue
            if _PAGE_HDR.match(s):
                continue
            keep.append(ln)
        paras += _join_lines(keep)
    return "\n\n".join(p for p in paras if p)


def _blocks(raw: str) -> str:
    """Text whose paragraphs are separated by blank lines (decisões, súmulas)."""
    parts = re.split(r"\n\s*\n", (raw or "").replace("\r", ""))
    return "\n\n".join(p for p in (_http.clean(x) for x in parts) if p)


def _stf_hit(s: dict) -> DecisionHit:
    base = s.get("base", "")
    title = _http.clean(s.get("titulo")) or s.get("id", "")
    snippet = s.get("ementa_texto") or s.get("sumula_texto") or ""
    return DecisionHit(
        id=s["id"], title=title, court=_court(s), date=_http.iso_date(s.get("julgamento_data")),
        case_number=_http.clean(s.get("processo_codigo_completo")) or ("" if base == "sumulas" else title),
        snippet=_http.clean(snippet)[:300], url=STF_PAGE.format(id=s["id"]))


def _court(s: dict) -> str:
    org = _http.clean(s.get("orgao_julgador"))
    return "STF" + (f" – {org}" if org else "")


async def _stf(body: dict) -> dict:
    r = await _http.post(STF_API, json=body, headers={"Accept": "application/json"})
    if r.status_code != 200:
        raise SourceError(_http.error("STF", "search failed", r.status_code), r.status_code)
    try:
        return r.json()["result"]["hits"]
    except (ValueError, KeyError, TypeError):
        raise SourceError("STF: unexpected reply (not the search JSON)", r.status_code)


def _date_filter(v: str, name: str) -> str:
    iso = _http.iso_date(v)
    if not iso:
        raise BadRequest(f"{name} must be a date like 2024-01-31; got {v!r}")
    return iso


# --------------------------------------------------------------------------- #
# Legislation (normas.leg.br)
# --------------------------------------------------------------------------- #
def _urn(id: str) -> str:
    s = _http.clean(id)
    if s.lower() in _ALIASES:
        return _ALIASES[s.lower()]
    m = re.search(r"(urn:lex:br:federal:[^&#\s!@]+)", s)
    if m and _URN.match(m[1]):
        return m[1]
    raise BadRequest("Brazilian law ids are LexML URNs, e.g. 'urn:lex:br:federal:lei:2002-01-10;10406' "
                     f"(Código Civil), or one of {', '.join(sorted(_ALIASES))}; got {id!r}.")


def _txt(s) -> str:
    """Version text -> one clean line (it carries inline LexML markup: <span xlink:href>, <lx:p>)."""
    return _http.clean(html.unescape(re.sub(r"<[^>]+>", " ", str(s or "")))).replace(" ,", ",").replace(" .", ".")


def _versions(n: dict) -> list[dict]:
    w = n.get("workExample") or []
    return w if isinstance(w, list) else [w]


def _current(n: dict) -> dict:
    """The version in force today: the last one dated on or before today."""
    vs = _versions(n)
    today = _http.today()
    now = [v for v in vs if (v.get("legislationDate") or "") <= today]
    return (now or vs or [{}])[-1]


def _name(n: dict) -> str:
    for v in reversed(_versions(n)):
        if v.get("name"):
            return _txt(v["name"])
    return ""


def _kind(n: dict) -> str:
    return str((n.get("legislationType") or {}).get("@id", "")).rsplit(":", 1)[-1]


def _children(n: dict) -> list[dict]:
    ch = n.get("hasPart") or []
    return [ch] if isinstance(ch, dict) else ch


def _frag(n: dict) -> str:
    return str(n.get("legislationIdentifier", "")).split("!", 1)[-1]


def _art_key(label: str) -> str:
    """'Art. 1.358-A.' / 'artigo 1358-a' / '5º' / 'art 5o' -> '1358-a' / '5'."""
    s = _http.clean(label).lower()
    s = re.sub(r"^(art(igo)?s?\.?\s*)", "", s)
    m = re.fullmatch(r"(\d[\d.]*)\s*(?:º|°|o\b)?\.?(?:[\s\-–]*([a-z]{1,4}))?\.?", s)
    if not m:
        return ""
    num = m[1].replace(".", "").lstrip("0") or "0"
    return num + (f"-{m[2]}" if m[2] else "")


def _art_label(name: str) -> str:
    """'Art. 1.358-A.' -> 'Art. 1.358-A'; 'Art. 1º' stays 'Art. 1º'."""
    return re.sub(r"\.$", "", _http.clean(name))


def _in_force(n: dict) -> bool:
    return n.get("legislationLegalForce") != "NotInForce"


def _render(n: dict, out: list[str]) -> None:
    """One dispositivo (and its sub-dispositivos) as markdown lines."""
    k = _kind(n)
    if k in _SKIP:
        return
    v = _current(n)
    name, text = _name(n), _txt(v.get("text"))
    if k == "artigo":
        head = f"**{name}**" if name else ""
        kids = _children(n)
        if kids and _kind(kids[0]) == "caput":
            cap = _txt(_current(kids[0]).get("text"))
            out.append(f"{head} {cap}".strip())
            for g in _children(kids[0]):
                _render(g, out)
            kids = kids[1:]
        elif head or text:
            out.append(f"{head} {text}".strip())
        for c in kids:
            _render(c, out)
        return
    if k in _HEADINGS:
        out.append("### " + " – ".join(x for x in (name, text) if x))
    elif name or text:
        out.append(" ".join(x for x in (name, text) if x))
    for c in _children(n):
        _render(c, out)


def _parse(urn: str, d: dict) -> dict:
    root = d.get("hasPart")
    if not root:
        sen = next((m[1] for a in d.get("sameAs") or []
                    if (m := re.search(r"DetalhaSigen\.action\?id=(\d+)", str(a)))), "")
        more = f" and https://legis.senado.leg.br/norma/{sen}" if sen else ""
        raise NotFound(f"The official source (normas.leg.br) holds only metadata for {urn}, not the article "
                       "text, so no article or table of contents can be returned from it (this is the "
                       "case for the Código Penal, CPP, CDC, CLT and CTN; Planalto, the usual consolidated "
                       f"text, refuses connections from abroad). Read it at {NORMA_PAGE.format(urn=urn)}{more}")
    toc: list[TocEntry] = []
    arts: dict[str, dict] = {}         # label -> article node
    keys: dict[str, str] = {}          # article key ('1358-a') -> plain label
    seen: dict[str, list[dict]] = {}   # article key -> nodes with that number
    order: list[tuple[TocEntry, dict]] = []

    def walk(n, depth):
        k = _kind(n)
        if k in _HEADINGS:
            toc.append(TocEntry(" – ".join(x for x in (_name(n), _txt(_current(n).get("text"))) if x),
                                level=depth))
            for c in _children(n):
                walk(c, depth + 1)
        elif k == "artigo":
            seen.setdefault(_art_key(_name(n)) or _frag(n), []).append(n)
            order.append((TocEntry("", level=depth), n))
            toc.append(order[-1][0])
        else:
            for c in _children(n):
                walk(c, depth)

    walk(root, 0)
    # A number seen once gets the plain label; among duplicates the in-force one does.
    label_of: dict[int, str] = {}
    for key, nodes in seen.items():
        plain = next((n for n in nodes if _in_force(n)), nodes[0])
        for n in nodes:
            lab = _art_label(_name(n)) or _frag(n)
            if n is plain:
                keys[key] = lab
            else:
                lab = f"{lab} ({_frag(n)})"
            label_of[id(n)] = lab
            arts[lab] = n
    for e, n in order:
        e.provision = label_of[id(n)]
        e.title = e.provision + ("" if _in_force(n) else " (revogado)")
    lines: list[str] = []
    _render(root, lines)
    title = _http.clean(d.get("headline") or d.get("name")) or urn
    alt = [a for a in (d.get("alternateName") or []) if not re.match(r"^[A-Z.]+-\d", a)]
    if alt:
        title += f" ({alt[0]})"
    return {"urn": urn, "title": title, "toc": toc, "arts": arts, "keys": keys,
            "text": "\n\n".join(lines), "as_of": _http.iso_date(d.get("dateModified")) or "",
            "abstract": _http.clean(d.get("abstract")), "date": _http.iso_date(d.get("legislationDate"))}


_FLAT_HEAD = re.compile(r"^(parte|livro|t[íi]tulo|subt[íi]tulo|cap[íi]tulo|se[çc][ãa]o|subse[çc][ãa]o)\s+"
                        r"([IVXLCDM]+(-[A-Z])?|\d+|[úu]nico|geral|especial|final)\b[^.;:]{0,20}$", re.I)
_FLAT_ART = re.compile(r"^Art(?:igo)?\.?\s*(\d[\d.]*\s*(?:º|°|o\b)?(?:\s*-\s*[A-Za-z]{1,4})?)\s*[.\-–]?(?:\s|$)")
_FLAT_END = re.compile(r"^(Rio de Janeiro|Brasília),? .*\d{4}")


def _parse_flat(urn: str, d: dict, page: str, link: str = "") -> dict:
    """'Compilação Monovigente' HTML (flat paragraphs) -> the dict _parse returns, plus 'flat'."""
    paras = [re.sub(r"([º°]) -(?=[A-Z])", r"\1-", re.sub(r"(\d) ([º°])", r"\1\2", _txt(x)))
             for x in re.findall(r"<(?:p|h\d)\b[^>]*>(.*?)</(?:p|h\d)>", page, re.S)]
    paras = [t for t in paras if t]
    toc: list[TocEntry] = []
    flat: dict[str, list[str]] = {}
    keys: dict[str, str] = {}
    cur: list[str] | None = None
    after_head = ended = False
    mark = 0
    for i, t in enumerate(paras):
        if _FLAT_END.match(t) and cur is not None:
            cur, ended, mark = None, True, len(toc)    # signature line: the enacting decree (CLT) or the end of the code
            continue
        m = _FLAT_ART.match(t)
        if m:
            if ended:                  # more articles follow: what came before was the enacting decree
                flat.clear()
                keys.clear()
                del toc[:mark]
                ended = False
            lab = "Art. " + re.sub(r"\s+", "", m[1]).rstrip(".")
            if lab in flat:
                lab = f"{lab} ({len(flat)})"
            cur = flat.setdefault(lab, [f"**{lab}**{t[m.end(1):]}"])
            keys.setdefault(_art_key(lab), lab)
            toc.append(TocEntry(lab, level=1, provision=lab))
            after_head = False
            continue
        if _FLAT_HEAD.match(t):
            toc.append(TocEntry(t, level=0))
            after_head = True
            continue
        nxt = paras[i + 1] if i + 1 < len(paras) else ""
        if after_head and len(t) < 150 and not t.endswith((".", ":", ";")):
            toc[-1].title += " – " + t
            after_head = False
            continue
        if cur is None:
            continue
        after_head = False
        rubric = (not t.endswith((".", ":", ";")) and not re.match(r"^(§|Parágrafo|[IVXL]+\s*[-–]|[a-z]\)|\d|\()", t)
                  and bool(re.match(r"^(§|Parágrafo|Art)", nxt) or _FLAT_HEAD.match(nxt)))
        if rubric:
            continue   # a rubric ("Homicídio simples") that introduces the next provision
        cur.append(t)
    if not flat:
        return {}
    title = _http.clean(d.get("headline") or d.get("name")) or urn
    alt = [a for a in (d.get("alternateName") or []) if not re.match(r"^[A-Z.]+-\d", a)]
    if alt:
        title += f" ({alt[0]})"
    body = {k: "\n\n".join(v) for k, v in flat.items()}
    return {"urn": urn, "title": title, "toc": toc, "arts": {}, "flat": body, "keys": keys, "page": link,
            "text": "\n\n".join(body.values()), "as_of": _http.iso_date(d.get("dateModified")) or "",
            "abstract": _http.clean(d.get("abstract")), "date": _http.iso_date(d.get("legislationDate"))}


def _norm(s) -> str:
    return re.sub(r"[^\w]+", " ", str(s or "").lower()).strip()


def _live(c: dict) -> bool:
    return not any("revogad" in str(x.get("nomeSituacao", "")).lower() for x in c.get("status") or [])


def _exact(q: str, c: dict) -> bool:
    """True when the query is the law's own number, name or short title (not just mentioned in it)."""
    nq = _norm(q)
    if not nq:
        return False
    if re.fullmatch(r"[\d.]+", q.strip()) and q.replace(".", "").strip() == str(c.get("numero") or ""):
        return True
    # "apelido" lists popular names: "LEI-8078-..., Código de Defesa do Consumidor (1990) (CDC)"
    pop = [_norm(re.sub(r"(\s*\([^)]*\))+$", "", a.strip())) for a in str(c.get("apelido") or "").split(",")[1:]]
    return nq in (_norm(c.get("nome")), _norm(c.get("ementa")), *pop)


class Brazil(Jurisdiction):
    code = "br"
    name = "Brazil"
    languages = ("pt",)
    aliases = ("brasil", "brazil", "bra")
    sources = (
        Source(
            name="STF – Pesquisa de Jurisprudência (Supremo Tribunal Federal)",
            url="https://jurisprudencia.stf.jus.br/",
            covers=("caselaw",),
            licence=("unknown: no STF terms of use found; judicial decisions are excluded from "
                     "copyright under Lei 9.610/1998 art. 8, IV"),
            commercial_use=None,
            ai_use=None,
            auth="none",
            rate_limit=("unknown: nothing published; jurisprudencia.stf.jus.br has no robots.txt "
                        "(the SPA answers every path); 1 s spacing, no 429 seen in ~15 requests "
                        "(2026-11-05). Undocumented internal API: may change without notice."),
            terms_url="https://portal.stf.jus.br/",
        ),
        Source(
            name="normas.leg.br (Senado Federal / Câmara dos Deputados) – consolidated federal legislation",
            url="https://normas.leg.br/",
            covers=("legislation",),
            licence=("CC BY 4.0 (declared in every record's license/sdLicense); Senado portal "
                     "policy: reuse allowed for lawful purposes with attribution"),
            commercial_use=True,
            ai_use=None,
            auth="none",
            rate_limit=("unknown: nothing published; normas.leg.br robots.txt allows all; "
                        "legis.senado.leg.br robots.txt answers 403 (no rules readable). 1 s "
                        "spacing, no 429 seen in ~20 requests (2026-11-05)"),
            terms_url="https://www12.senado.leg.br/institucional/documentos/politica-de-uso-do-portal-do-senado-federal",
        ),
    )
    caselaw_filters = {
        "base": "acordaos (default) | decisoes (monocratic decisions) | sumulas",
        "date_from": "judgment date from, YYYY-MM-DD",
        "date_to": "judgment date to, YYYY-MM-DD",
        "sort": "relevance (default) | newest | oldest",
    }
    legislation_filters = {
        "year_from": "signature year from, e.g. 1990",
        "year_to": "signature year to, e.g. 2024",
    }
    min_interval = {"jurisprudencia.stf.jus.br": 1.0, "legis.senado.leg.br": 1.0, "normas.leg.br": 1.0}
    notes = ("Case law: STF only (acórdãos, monocratic decisions, súmulas). Legislation: federal "
             "norms consolidated per article from normas.leg.br; ids are LexML URNs "
             "(aliases cc, cf, cpc, cp, cpp, cdc, clt, ctn). For cp, cpp, cdc, clt and ctn normas.leg.br "
             "has only metadata, so their current text comes from the Câmara compilation on legis.senado.leg.br "
             "(flat text, no per-version history).")
    gaps = (
        ("Superior Tribunal de Justiça (STJ): SCON is behind a Cloudflare JS challenge (not touched). "
         "Open-data portal (CC-BY) not built: text ZIPs are partial (2026-10-09: 100 texts for 1,293 "
         "listed decisions), one file per publication day, no index, robots Crawl-Delay 10"),
        ("Other federal and state courts: CNJ DataJud is metadata only and timed out from the UK; "
         "court sites not researched yet"),
        ("Norms with metadata only in normas.leg.br: text is taken from the Senado-hosted Câmara "
         "compilation when it exists; Planalto (usual consolidated text) refuses connections from abroad"),
        "State and municipal legislation: not researched yet",
    )
    samples = {
        "caselaw_query": "\"dano moral\"",
        "decision_id": "sjur254711",
        "legislation_query": "10406",
        "law_id": "urn:lex:br:federal:lei:2002-01-10;10406",
        "provision": "Art. 186",
    }

    # ---------------------------------------------------------------- case law
    async def search_caselaw(self, query, *, limit=10, page=1, filters=None):
        f = filters or {}
        base = (f.get("base") or "acordaos").strip().lower()
        if base not in _BASES:
            raise BadRequest(f"base must be one of {', '.join(_BASES)}; got {base!r}")
        flt: list[dict] = [{"term": {"base": base}}]
        rng = {}
        if f.get("date_from"):
            rng["gte"] = _date_filter(f["date_from"], "date_from")
        if f.get("date_to"):
            rng["lte"] = _date_filter(f["date_to"], "date_to")
        if "gte" in rng and "lte" in rng and rng["gte"] > rng["lte"]:
            raise BadRequest(f"date_from ({rng['gte']}) is after date_to ({rng['lte']})")
        if rng:
            flt.append({"range": {"julgamento_data": rng}})
        sort = (f.get("sort") or "relevance").strip().lower()
        if sort not in ("relevance", "newest", "oldest"):
            raise BadRequest("sort must be relevance, newest or oldest")
        q = (query or "").strip()
        size, start = max(1, int(limit)), (max(1, int(page)) - 1) * max(1, int(limit))
        if size > 200:
            raise BadRequest(f"STF accepts at most 200 results per page; got limit={size}.")
        if start + size > 10000:
            raise BadRequest("STF only exposes the first 10,000 results of a search (page*limit <= 10000); "
                             "narrow the query with filters (date_from/date_to, base) instead of paging deeper.")
        body = {
            "query": {"bool": {"must": [{"query_string": {"query": q, "default_operator": "AND"}}]
                               if q else [{"match_all": {}}], "filter": flt}},
            "size": size, "from": start,
            "track_total_hits": True,
            "_source": ["id", "base", "titulo", "julgamento_data", "orgao_julgador",
                        "processo_codigo_completo", "ementa_texto", "sumula_texto"],
        }
        if sort != "relevance":
            body["sort"] = [{"julgamento_data": "desc" if sort == "newest" else "asc"}]
        hits = await _stf(body)
        items = [_stf_hit(h["_source"]) for h in hits.get("hits", [])]
        return Results(items=items, total=(hits.get("total") or {}).get("value"),
                       note=("STF only: Superior Tribunal de Justiça (STJ) decisions are NOT available here (its SCON site is behind a "
                             "bot wall, so search the STJ at scon.stj.jus.br yourself). Query syntax: words are AND-ed; \"quotes\" for a phrase; OR / NOT work."))

    async def get_decision(self, id):
        did = _http.clean(id)
        m = re.search(r"/pages/search/([\w-]+)", did)
        did = m[1] if m else did
        if not _STF_ID.match(did):
            raise BadRequest(f"STF ids look like 'sjur254711', 'despacho1278126' or 'seq-sumula819'; got {id!r}.")
        hits = await _stf({"query": {"bool": {"filter": [{"term": {"id": did}}]}}, "size": 1})
        if not hits.get("hits"):
            raise NotFound(f"No STF document with id {did!r}.")
        s = hits["hits"][0]["_source"]
        base = s.get("base", "")
        if base == "acordaos":
            text = _stf_text(s.get("inteiro_teor_texto") or "") or _blocks(s.get("ementa_texto"))
        elif base == "decisoes":
            text = _blocks(s.get("decisao_texto"))
        else:
            text = _blocks(s.get("sumula_texto") or s.get("ementa_texto"))
        meta = {"Tipo": _BASES.get(base, base),
                "Relator": _http.clean(s.get("relator_processo_nome")),
                "Classe": _http.clean(s.get("processo_classe_processual_unificada_extenso")),
                "Procedência": _http.clean(s.get("procedencia_geografica_completo")),
                "Publicação": _http.iso_date(s.get("publicacao_data")),
                "Tese": _http.clean(s.get("documental_tese_texto")),
                "Inteiro teor (PDF)": s.get("inteiro_teor_url") or "",
                "Acompanhamento processual": s.get("acompanhamento_processual_url") or ""}
        hit = _stf_hit(s)
        return Decision(id=did, title=hit.title, text=text, url=hit.url, court=hit.court,
                        date=hit.date, case_number=hit.case_number,
                        summary=_http.clean(s.get("ementa_texto")) if base != "sumulas" else "",
                        metadata={k: v for k, v in meta.items() if v})

    # ------------------------------------------------------------- legislation
    async def search_legislation(self, query, *, limit=10, page=1, filters=None):
        f = filters or {}
        years = []
        for k, dflt in (("year_from", 1500), ("year_to", datetime.date.today().year)):
            v = str(f.get(k) or dflt).strip()
            if not re.fullmatch(r"\d{4}", v):
                raise BadRequest(f"{k} must be a year like 2002; got {v!r}")
            years.append(v)
        if years[0] > years[1]:
            raise BadRequest(f"year_from ({years[0]}) is after year_to ({years[1]})")
        # The catalogue sorts by date only, so amending laws bury the law itself. Fetch a block of
        # 100, move exact number/name matches to the top of it, then cut out the requested page.
        q = (query or "").strip()
        size, start = max(1, int(limit)), (max(1, int(page)) - 1) * max(1, int(limit))
        params = {"q": q, "anoInicial": years[0], "anoFinal": years[1],
                  "pagina": start // 100, "tamanhoPagina": 100}
        r = await _http.get(CATALOGO, params=params, headers={"Accept": "application/json"})
        if r.status_code != 200:
            raise SourceError(_http.error("Senado catálogo", "search failed", r.status_code), r.status_code)
        try:
            d = r.json()
        except ValueError:
            raise SourceError("Senado catálogo: non-JSON reply (block page?)", r.status_code)
        items = []
        hits = list(d.get("searchHits") or [])
        if start < 100 and (d.get("totalHits") or 0) > 100 and not any(_exact(q, h.get("content") or {}) and _live(h["content"]) for h in hits):
            # the law named by the query may sit in a later date block (e.g. Código Penal, 1940)
            for pg in range(1, min(5, (d["totalHits"] - 1) // 100 + 1)):
                r2 = await _http.get(CATALOGO, params={**params, "pagina": pg}, headers={"Accept": "application/json"})
                try:
                    more = r2.json().get("searchHits") or [] if r2.status_code == 200 else []
                except ValueError:
                    break
                ex = [h for h in more if _exact(q, h.get("content") or {}) and _live(h["content"])]
                if ex:
                    hits = ex + hits
                    break
        block = sorted(hits, key=lambda h: (not _exact(q, h.get("content") or {}), not _live(h.get("content") or {})))
        for h in block[start % 100:start % 100 + size]:
            c = h.get("content") or {}
            urn = c.get("urn") or h.get("id")
            alias = [a.strip() for a in str(c.get("apelido") or "").split(",")[1:] if a.strip()]
            title = _http.clean(c.get("nome")) + (f" ({alias[0]})" if alias else "")
            st = c.get("status") or []
            items.append(LawHit(id=urn, title=title or urn, type=c.get("tipo", ""),
                                number=str(c.get("numero") or ""), date=_http.iso_date(c.get("assinatura")),
                                status=_http.clean(st[0].get("nomeSituacao")) if st else "",
                                snippet=_http.clean(c.get("ementa"))[:300], url=NORMA_PAGE.format(urn=urn)))
        return Results(items=items, total=d.get("totalHits"),
                       note="Sorted by date, newest first (not relevance), except that a law whose number or name equals the query comes first. Words are AND-ed; a law number alone finds it.")

    async def _law(self, id) -> dict:
        urn = _urn(id)
        if urn in _cache:
            return _cache[urn]
        r = await _http.get(NORMAS, params={"urn": urn, "tipo_documento": "maior-detalhe"},
                            headers={"Accept": "application/json"}, timeout=120.0)
        if r.status_code != 200:
            raise SourceError(_http.error("normas.leg.br", "norm fetch failed", r.status_code), r.status_code)
        try:
            d = r.json()
        except ValueError:
            raise SourceError("normas.leg.br: non-JSON reply (block page?)", r.status_code)
        if isinstance(d, list):
            d = d[0] if d else {}
        if set(d) <= {"urn"}:
            raise NotFound(f"normas.leg.br has no norm {urn}. Find the URN with search_legislation.")
        law = await self._flat_law(urn, d) if not d.get("hasPart") else None
        return _http.lru_put(_cache, urn, law or _parse(urn, d), 4)

    async def _flat_law(self, urn: str, d: dict) -> dict:
        """Metadata-only norm: its current compilation as HTML from legis.senado.leg.br ({} if unavailable)."""
        sen = next((m[1] for a in d.get("sameAs") or []
                    if (m := re.search(r"DetalhaSigen\.action\?id=(\d+)", str(a)))), "")
        if not sen:
            return {}
        try:
            r = await _http.get(SENADO_NORMA.format(sen=sen), timeout=60.0)
            m = re.search(r"Compila\S+o\s+Monovigente.{0,600}?href=\"(\d+/publicacao/\d+)\"", r.text, re.S) \
                if r.status_code == 200 else None
            if not m:
                return {}
            r = await _http.get(SENADO_NORMA.format(sen=m[1]), timeout=120.0)
        except SourceError:
            return {}
        return _parse_flat(urn, d, r.text, SENADO_NORMA.format(sen=sen)) if r.status_code == 200 else {}

    async def get_legislation_toc(self, id):
        law = await self._law(id)
        return Toc(id=law["urn"], title=law["title"], url=NORMA_PAGE.format(urn=law["urn"]),
                   entries=law["toc"])

    async def get_legislation_provision(self, id, provision):
        law = await self._law(id)
        p = _http.clean(provision)
        have = law["flat"] if "flat" in law else law["arts"]
        lab = p if p in have else law["keys"].get(_art_key(p))
        if not lab:
            raise NotFound(f"No article {provision!r} in {law['title']}. Use labels like 'Art. 186' "
                           "or '1.228'; get_legislation_toc lists them.")
        if "flat" in law:
            text, link = law["flat"][lab], law["page"] or NORMA_PAGE.format(urn=law["urn"])
        else:
            n = law["arts"][lab]
            lines: list[str] = []
            _render(n, lines)
            text, link = "\n\n".join(lines), NORMA_PAGE.format(urn=n.get("legislationIdentifier") or law["urn"])
        return Provision(law_id=law["urn"], law_title=law["title"], provision=lab,
                         text=text, url=link,
                         as_of=law["as_of"])

    async def get_legislation_text(self, id):
        law = await self._law(id)
        meta = {"Ementa": law["abstract"], "Data": law["date"]}
        return LawText(id=law["urn"], title=law["title"], text=law["text"],
                       url=NORMA_PAGE.format(urn=law["urn"]), as_of=law["as_of"],
                       metadata={k: v for k, v in meta.items() if v})
